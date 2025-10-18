import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk, ImageDraw
import cv2
import time
import numpy as np
import threading
from picamera2 import Picamera2

# Try to import libcamera controls for autofocus
try:
    from libcamera import controls
except Exception:
    controls = None

# Robust AF enums across libcamera versions
AF_MODE_MANUAL = getattr(getattr(controls, "AfModeEnum", None), "Manual", 0) if controls else 0
AF_MODE_AUTO = getattr(getattr(controls, "AfModeEnum", None), "Auto", 1) if controls else 1
AF_MODE_CONTINUOUS = getattr(getattr(controls, "AfModeEnum", None), "Continuous", 2) if controls else 2
AF_RANGE_MACRO = getattr(getattr(controls, "AfRangeEnum", None), "Macro", None) if controls else None
AF_RANGE_NORMAL = getattr(getattr(controls, "AfRangeEnum", None), "Normal", None) if controls else None
AF_SPEED_FAST = getattr(getattr(controls, "AfSpeedEnum", None), "Fast", None) if controls else None

AF_STATE_MAP = {
    0: "Idle",
    1: "Scanning",
    2: "Focused",
    3: "Failed",
}

class DocumentScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Scanner (Continuous AF, ROI ID card, 75mm)")
        self.last_image_path = None
        self.current_af_mode = "Continuous"
        self.distance_mm = 75  # target distance

        # ID card ratio (ISO ID-1 85.60 x 53.98 mm)
        self.card_ratio = 85.60 / 53.98  # width / height
        self.roi_scale = 0.95            # fallback ROI scale when no detection
        self.roi_margin = 1.12           # enlarge ROI vs detected card (12%)
        self.overlay_line_width = 3

        # Live preview label
        self.label = Label(root)
        self.label.pack()

        # Buttons for capture and view
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=6)
        self.capture_btn = Button(btn_frame, text="Capture", command=self.capture_image_thread, width=15)
        self.capture_btn.grid(row=0, column=0, padx=10)
        self.show_btn = Button(btn_frame, text="View Last Image", command=self.show_image_thread, width=20)
        self.show_btn.grid(row=0, column=1, padx=10)

        # Status labels
        self.status_label = Label(root, text="No image captured yet.")
        self.status_label.pack(pady=4)
        self.focus_label = Label(root, text="AF: initializing...")
        self.focus_label.pack(pady=2)
        self.distance_label = Label(root, text=f"Khoảng cách mục tiêu: {self.distance_mm} mm")
        self.distance_label.pack(pady=2)

        # Initialize camera
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (640, 480)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.configure("preview")
        self.picam2.start()

        # Set AF continuous, prefer macro range if supported (close focus ~75mm)
        self.set_af_defaults()

        # Start live updating the preview
        self.update_preview()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_controls_safe(self, d):
        try:
            self.picam2.set_controls(d)
        except Exception as e:
            print(f"Control error: {e}")

    def set_af_defaults(self):
        # Continuous AF, prefer Macro range for close focus, fast speed if available
        ctrl = {"AfMode": AF_MODE_CONTINUOUS}
        if AF_RANGE_MACRO is not None:
            ctrl["AfRange"] = AF_RANGE_MACRO
        if AF_SPEED_FAST is not None:
            ctrl["AfSpeed"] = AF_SPEED_FAST
        self.set_controls_safe(ctrl)
        self.current_af_mode = "Continuous"

    def map_af_state(self, state):
        if state is None:
            return "Unknown"
        if isinstance(state, str):
            return state
        return AF_STATE_MAP.get(state, str(state))

    def update_af_status(self):
        try:
            meta = self.picam2.capture_metadata()
            pos = meta.get("LensPosition")
            state = self.map_af_state(meta.get("AfState"))
            if pos is not None:
                self.focus_label.config(text=f"AF mode: {self.current_af_mode} | state: {state} | lens: {pos:.2f}")
            else:
                self.focus_label.config(text=f"AF mode: {self.current_af_mode} | state: {state} | lens: N/A")
        except Exception:
            pass

    def detect_card_rect(self, frame_bgr):
        try:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blur, 60, 160)
            contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None
            h, w = gray.shape[:2]
            min_area = max(2000, (w * h) * 0.01)  # ignore tiny shapes
            card_ratio = self.card_ratio

            # sort large contours by area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            for c in contours:
                area = cv2.contourArea(c)
                if area < min_area:
                    continue
                x, y, cw, ch = cv2.boundingRect(c)
                r = cw / max(1, ch)
                # accept either orientation close to ID card ratio
                if 0.6 * card_ratio < r < 1.4 * card_ratio or 0.6 * (1 / card_ratio) < r < 1.4 * (1 / card_ratio):
                    return (x, y, x + cw, y + ch)
            # fallback: largest contour
            c = contours[0]
            x, y, cw, ch = cv2.boundingRect(c)
            return (x, y, x + cw, y + ch)
        except Exception:
            return None

    def compute_roi_rect(self, w, h, det_rect=None):
        # Compute centered ROI rectangle that fully contains detected card with margin
        if det_rect is not None:
            dx1, dy1, dx2, dy2 = det_rect
            cw = max(1, dx2 - dx1)
            ch = max(1, dy2 - dy1)
            # choose target orientation based on detected rectangle
            r_det = cw / ch
            r_target = self.card_ratio if r_det >= 1 else 1 / self.card_ratio
            # enlarge to include card plus margin
            rw = int(max(cw * self.roi_margin, ch * self.roi_margin * r_target))
            rh = int(rw / r_target)
            cx = dx1 + cw // 2
            cy = dy1 + ch // 2
            x1 = max(0, cx - rw // 2)
            y1 = max(0, cy - rh // 2)
            x2 = min(w, x1 + rw)
            y2 = min(h, y1 + rh)
            # adjust if we clipped at borders
            x1 = max(0, x2 - rw)
            y1 = max(0, y2 - rh)
            return (x1, y1, x2, y2)
        else:
            # fallback: fill as much as possible while keeping ratio
            r = self.card_ratio
            rw = int(min(w * self.roi_scale, h * self.roi_scale * r))
            rh = int(rw / r)
            x1 = max(0, (w - rw) // 2)
            y1 = max(0, (h - rh) // 2)
            x2 = x1 + rw
            y2 = y1 + rh
            return (x1, y1, x2, y2)

    def update_preview(self):
        try:
            frame = self.picam2.capture_array()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]

            # detect card and compute ROI to fully include it
            det_rect = self.detect_card_rect(frame)
            x1, y1, x2, y2 = self.compute_roi_rect(w, h, det_rect)

            img = Image.fromarray(rgb)
            draw = ImageDraw.Draw(img)

            # draw ROI
            draw.rectangle([(x1, y1), (x2, y2)], outline="lime", width=self.overlay_line_width)
            # draw detection rectangle if available
            if det_rect is not None:
                dx1, dy1, dx2, dy2 = det_rect
                draw.rectangle([(dx1, dy1), (dx2, dy2)], outline="yellow", width=max(1, self.overlay_line_width - 1))

            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        except Exception:
            pass
        # Update AF status text
        self.update_af_status()
        self.root.after(30, self.update_preview)

    def capture_image_thread(self):
        threading.Thread(target=self.capture_image).start()

    def wait_for_stable_focus(self, timeout_ms=2000, stable_ms=250):
        start = time.time()
        focused_since = None
        while (time.time() - start) * 1000 < timeout_ms:
            try:
                meta = self.picam2.capture_metadata()
                state_val = meta.get("AfState")
                state = self.map_af_state(state_val)
                if state == "Focused" or state_val == 2:
                    if focused_since is None:
                        focused_since = time.time()
                    elif (time.time() - focused_since) * 1000 >= stable_ms:
                        return True
                else:
                    focused_since = None
            except Exception:
                pass
            time.sleep(0.02)
        return False

    def capture_image(self):
        # ensure AF continuous defaults are set
        self.set_af_defaults()
        focused = self.wait_for_stable_focus(timeout_ms=2000, stable_ms=250)

        frame = self.picam2.capture_array()
        h, w = frame.shape[:2]
        det_rect = self.detect_card_rect(frame)
        x1, y1, x2, y2 = self.compute_roi_rect(w, h, det_rect)

        roi = frame[y1:y2, x1:x2].copy()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        path = f"scan_idcard_{timestamp}.jpg"
        cv2.imwrite(path, roi)
        self.last_image_path = path

        status_text = f"Saved: {path}"
        status_text += " (focused)" if focused else " (focus timeout)"
        self.status_label.config(text=status_text)
        print(status_text)

    def show_image_thread(self):
        threading.Thread(target=self.show_last_image).start()

    def show_last_image(self):
        if self.last_image_path:
            img = cv2.imread(self.last_image_path)
            if img is not None:
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(rgb)
                imgtk = ImageTk.PhotoImage(image=img_pil)
                top = tk.Toplevel(self.root)
                top.title("Captured ROI Image")
                lbl = Label(top, image=imgtk)
                lbl.image = imgtk
                lbl.pack()
            else:
                print("Could not read image.")
        else:
            print("No image captured yet.")

    def on_close(self):
        print("Closing application...")
        try:
            self.picam2.stop()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentScannerApp(root)
    root.mainloop()