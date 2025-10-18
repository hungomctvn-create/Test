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

AF_STATE_MAP = {
    0: "Idle",
    1: "Scanning",
    2: "Focused",
    3: "Failed",
}

# ====== GUI Class ======
class DocumentScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Scanner (Continuous AF, ROI capture)")
        self.last_image_path = None
        self.current_af_mode = "Continuous"

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

        # Initialize camera
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (640, 480)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.configure("preview")
        self.picam2.start()

        # Set AF to Continuous mode by default
        self.set_controls_safe({"AfMode": AF_MODE_CONTINUOUS})

        # ID card ratio (ISO ID-1 85.60 x 53.98 mm) and scale
        self.card_ratio = 85.60 / 53.98  # width / height
        self.roi_scale = 0.95

        # Start live updating the preview
        self.update_preview()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Safely set controls
    def set_controls_safe(self, d):
        try:
            self.picam2.set_controls(d)
        except Exception as e:
            print(f"Control error: {e}")

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

    def compute_roi_rect(self, w, h):
        # Compute centered ROI with ID-1 card aspect ratio
        r = self.card_ratio  # width / height
        # Pick width so that both width and height fit inside frame with scale
        rw = int(min(w * self.roi_scale, h * self.roi_scale * r))
        rh = int(rw / r)
        x1 = max(0, (w - rw) // 2)
        y1 = max(0, (h - rh) // 2)
        x2 = x1 + rw
        y2 = y1 + rh
        return (x1, y1, x2, y2)

    # Continuously update camera preview with ROI overlay
    def update_preview(self):
        try:
            frame = self.picam2.capture_array()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            x1, y1, x2, y2 = self.compute_roi_rect(w, h)

            img = Image.fromarray(rgb)
            draw = ImageDraw.Draw(img)
            draw.rectangle([(x1, y1), (x2, y2)], outline="lime", width=3)

            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        except Exception:
            pass
        # Update AF status text
        self.update_af_status()
        self.root.after(30, self.update_preview)

    # Start image capture in a separate thread
    def capture_image_thread(self):
        threading.Thread(target=self.capture_image).start()

    def wait_for_focus(self, timeout_ms=1500):
        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            try:
                meta = self.picam2.capture_metadata()
                state_val = meta.get("AfState")
                state = self.map_af_state(state_val)
                # In continuous mode, consider Focused as ready
                if state == "Focused" or state_val == 2:
                    return True
                if state == "Failed" or state_val == 3:
                    return False
            except Exception:
                pass
            time.sleep(0.02)
        return False

    # Capture, crop ROI and save image
    def capture_image(self):
        # Ensure AF is continuous before capture
        self.set_controls_safe({"AfMode": AF_MODE_CONTINUOUS})

        focused = self.wait_for_focus(timeout_ms=1500)

        frame = self.picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        x1, y1, x2, y2 = self.compute_roi_rect(w, h)

        roi = frame[y1:y2, x1:x2].copy()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        path = f"scan_roi_{timestamp}.jpg"
        cv2.imwrite(path, roi)
        self.last_image_path = path

        status_text = f"Saved: {path}"
        if focused:
            status_text += " (focused)"
        else:
            status_text += " (focus timeout)"
        self.status_label.config(text=status_text)
        print(status_text)

    # Start viewing image in a separate thread
    def show_image_thread(self):
        threading.Thread(target=self.show_last_image).start()

    # Open window to display the last captured image
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
                lbl.image = imgtk  # keep reference
                lbl.pack()
            else:
                print("Could not read image.")
        else:
            print("No image captured yet.")

    # Clean up camera and exit
    def on_close(self):
        print("Closing application...")
        try:
            self.picam2.stop()
        except Exception:
            pass
        self.root.destroy()

# ====== Run the app ======
if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentScannerApp(root)
    root.mainloop()