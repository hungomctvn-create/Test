import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
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

AF_TRIGGER_START = getattr(getattr(controls, "AfTriggerEnum", None), "Start", 0) if controls else 0
AF_TRIGGER_CANCEL = getattr(getattr(controls, "AfTriggerEnum", None), "Cancel", 1) if controls else 1

AF_RANGE_MACRO = getattr(getattr(controls, "AfRangeEnum", None), "Macro", None) if controls else None
AF_RANGE_NORMAL = getattr(getattr(controls, "AfRangeEnum", None), "Normal", None) if controls else None

AF_SPEED_FAST = getattr(getattr(controls, "AfSpeedEnum", None), "Fast", None) if controls else None
AF_SPEED_NORMAL = getattr(getattr(controls, "AfSpeedEnum", None), "Normal", None) if controls else None

AF_STATE_MAP = {
    0: "Idle",
    1: "Scanning",
    2: "Focused",
    3: "Failed",
}

class DocumentScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Scanner (Lens & Focus Controls)")
        self.last_image_path = None
        self.current_af_mode = "Unknown"
        self.lens_step = 0.05  # adjust per your camera characteristics

        # Live preview label
        self.label = Label(root)
        self.label.pack()

        # Button row: capture & view
        top_btns = tk.Frame(root)
        top_btns.pack(pady=6)
        self.capture_btn = Button(top_btns, text="Capture", command=self.capture_image_thread, width=14)
        self.capture_btn.grid(row=0, column=0, padx=8)
        self.show_btn = Button(top_btns, text="View Last Image", command=self.show_image_thread, width=18)
        self.show_btn.grid(row=0, column=1, padx=8)

        # AF Controls
        af_frame = tk.LabelFrame(root, text="Điều khiển AF")
        af_frame.pack(pady=6, fill="x")
        Button(af_frame, text="AF liên tục", command=self.set_continuous_af, width=14).grid(row=0, column=0, padx=6, pady=4)
        Button(af_frame, text="AF một lần", command=self.trigger_af_once, width=14).grid(row=0, column=1, padx=6, pady=4)
        Button(af_frame, text="Tạm dừng AF", command=self.pause_af, width=14).grid(row=0, column=2, padx=6, pady=4)
        Button(af_frame, text="Tiếp tục AF", command=self.resume_af, width=14).grid(row=0, column=3, padx=6, pady=4)
        Button(af_frame, text="Chế độ Auto", command=self.set_auto_af, width=14).grid(row=1, column=0, padx=6, pady=4)
        Button(af_frame, text="Chế độ Manual", command=self.set_manual_mode, width=14).grid(row=1, column=1, padx=6, pady=4)
        Button(af_frame, text="Ưu tiên gần (Macro)", command=self.set_macro_range, width=18).grid(row=1, column=2, padx=6, pady=4)
        Button(af_frame, text="Ưu tiên xa (Normal)", command=self.set_normal_range, width=18).grid(row=1, column=3, padx=6, pady=4)
        Button(af_frame, text="AF nhanh", command=self.set_speed_fast, width=14).grid(row=2, column=0, padx=6, pady=4)
        Button(af_frame, text="AF thường", command=self.set_speed_normal, width=14).grid(row=2, column=1, padx=6, pady=4)

        # Lens Controls
        lens_frame = tk.LabelFrame(root, text="Điều chỉnh Lens")
        lens_frame.pack(pady=6, fill="x")
        Button(lens_frame, text="Lens -", command=self.lens_dec, width=10).grid(row=0, column=0, padx=6, pady=4)
        Button(lens_frame, text="Lens +", command=self.lens_inc, width=10).grid(row=0, column=1, padx=6, pady=4)
        Button(lens_frame, text="Đọc vị trí Lens", command=self.read_lens_pos, width=16).grid(row=0, column=2, padx=6, pady=4)

        # Status labels
        self.status_label = Label(root, text="No image captured yet.")
        self.status_label.pack(pady=4)
        self.focus_label = Label(root, text="AF: chưa khởi tạo")
        self.focus_label.pack(pady=2)

        # Initialize camera
        self.picam2 = Picamera2()
        self.picam2.preview_configuration.main.size = (640, 480)
        self.picam2.preview_configuration.main.format = "RGB888"
        self.picam2.configure("preview")
        self.picam2.start()

        # Default to continuous AF
        self.set_continuous_af()

        # Start live preview updates
        self.update_preview()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Utility: safely set controls
    def set_controls_safe(self, d):
        try:
            self.picam2.set_controls(d)
        except Exception as e:
            print(f"Control error: {e}")

    # AF helpers
    def set_continuous_af(self):
        ctrl = {"AfMode": AF_MODE_CONTINUOUS}
        if AF_RANGE_MACRO is not None:
            ctrl["AfRange"] = AF_RANGE_MACRO
        if AF_SPEED_FAST is not None:
            ctrl["AfSpeed"] = AF_SPEED_FAST
        self.set_controls_safe(ctrl)
        self.current_af_mode = "Continuous"

    def set_auto_af(self):
        self.set_controls_safe({"AfMode": AF_MODE_AUTO})
        self.current_af_mode = "Auto"

    def trigger_af_once(self):
        self.set_controls_safe({"AfMode": AF_MODE_AUTO, "AfTrigger": AF_TRIGGER_START})
        self.current_af_mode = "Auto (triggered)"

    def pause_af(self):
        self.set_controls_safe({"AfPause": True})

    def resume_af(self):
        self.set_controls_safe({"AfPause": False})

    def set_macro_range(self):
        if AF_RANGE_MACRO is not None:
            self.set_controls_safe({"AfRange": AF_RANGE_MACRO})

    def set_normal_range(self):
        if AF_RANGE_NORMAL is not None:
            self.set_controls_safe({"AfRange": AF_RANGE_NORMAL})

    def set_speed_fast(self):
        if AF_SPEED_FAST is not None:
            self.set_controls_safe({"AfSpeed": AF_SPEED_FAST})

    def set_speed_normal(self):
        if AF_SPEED_NORMAL is not None:
            self.set_controls_safe({"AfSpeed": AF_SPEED_NORMAL})

    def set_manual_mode(self):
        try:
            meta = self.picam2.capture_metadata()
            pos = meta.get("LensPosition")
        except Exception:
            pos = None
        ctrl = {"AfMode": AF_MODE_MANUAL}
        if pos is not None:
            ctrl["LensPosition"] = pos
        self.set_controls_safe(ctrl)
        self.current_af_mode = "Manual"

    # Lens position adjusters (Manual mode)
    def lens_inc(self):
        try:
            meta = self.picam2.capture_metadata()
            pos = meta.get("LensPosition")
            if pos is None:
                pos = 0.0
            new_pos = float(pos) + float(self.lens_step)
            self.set_controls_safe({"AfMode": AF_MODE_MANUAL, "LensPosition": new_pos})
        except Exception as e:
            print(f"Lens inc error: {e}")

    def lens_dec(self):
        try:
            meta = self.picam2.capture_metadata()
            pos = meta.get("LensPosition")
            if pos is None:
                pos = 0.0
            new_pos = float(pos) - float(self.lens_step)
            self.set_controls_safe({"AfMode": AF_MODE_MANUAL, "LensPosition": new_pos})
        except Exception as e:
            print(f"Lens dec error: {e}")

    def read_lens_pos(self):
        try:
            meta = self.picam2.capture_metadata()
            pos = meta.get("LensPosition")
            self.status_label.config(text=f"LensPosition hiện tại: {pos}")
        except Exception:
            self.status_label.config(text="Không đọc được LensPosition")

    # AF status
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
            self.focus_label.config(text=f"AF mode: {self.current_af_mode} | state: {state} | lens: {pos}")
        except Exception:
            pass

    # Live preview
    def update_preview(self):
        try:
            frame = self.picam2.capture_array()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        except Exception:
            pass
        self.update_af_status()
        self.root.after(30, self.update_preview)

    # Capture image
    def capture_image_thread(self):
        threading.Thread(target=self.capture_image).start()

    def capture_image(self):
        frame = self.picam2.capture_array()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        path = f"scan_{timestamp}.jpg"
        cv2.imwrite(path, frame)
        self.last_image_path = path
        self.status_label.config(text=f"Saved: {path}")
        print(f"Saved image: {path}")

    # View last image
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
                top.title("Captured Image")
                lbl = Label(top, image=imgtk)
                lbl.image = imgtk
                lbl.pack()
            else:
                print("Could not read image.")
        else:
            print("No image captured yet.")

    # Cleanup
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