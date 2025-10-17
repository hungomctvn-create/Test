#!/usr/bin/env python3
"""
GUI chụp ảnh không dùng Picamera2.
- Preview: rpicam-vid (ưu tiên), fallback libcamera-vid (MJPEG) đọc từ stdout, hiển thị trong Tkinter.
- Chụp: rpicam-still (ưu tiên), fallback libcamera-still.
- Chỉ dùng sRGB (RGB/JPEG), không dùng ColorSpace khác.
- UI: chọn AwbMode, khoá AWB và sliders ColourGains R/B.
"""
import os
import sys
import io
import time
import queue
import shutil
import threading
import subprocess
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk
except Exception:
    print("[LỖI] Cần Pillow: sudo apt install -y python3-pil python3-pil.imagetk")
    sys.exit(1)

PREVIEW_WIDTH, PREVIEW_HEIGHT = 1280, 720
STILL_W, STILL_H = 4608, 3456
SAVE_DIR = "/home/hungomctvn"
AWB_MODES = ["auto", "daylight", "cloudy", "fluorescent", "tungsten"]
DEFAULT_R_GAIN, DEFAULT_B_GAIN = 2.0, 1.10

if not (shutil.which("rpicam-vid") or shutil.which("libcamera-vid")):
    print("[LỖI] Cần rpicam-vid hoặc libcamera-vid: sudo apt install -y rpicam-apps libcamera-apps libcamera")
    sys.exit(1)
if not (shutil.which("rpicam-still") or shutil.which("libcamera-still")):
    print("[LỖI] Cần rpicam-still hoặc libcamera-still: sudo apt install -y rpicam-apps libcamera-apps libcamera")
    sys.exit(1)

class CameraGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chụp ảnh (libcamera) - sRGB")
        os.makedirs(SAVE_DIR, exist_ok=True)
        self.preview_label = tk.Label(self.root, bg="black")
        self.preview_label.pack(padx=8, pady=8)

        bar = tk.Frame(self.root); bar.pack(fill=tk.X, padx=8, pady=4)
        tk.Button(bar, text="Chụp", command=self.capture).pack(side=tk.LEFT)
        self.status = tk.StringVar(value="Sẵn sàng")
        tk.Label(bar, textvariable=self.status).pack(side=tk.LEFT, padx=12)

        awb = tk.LabelFrame(self.root, text="AWB & Gains"); awb.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(awb, text="AwbMode:").pack(side=tk.LEFT)
        self.awb_mode = tk.StringVar(value="tungsten")
        ttk.OptionMenu(awb, self.awb_mode, self.awb_mode.get(), *AWB_MODES, command=self.on_awb_change).pack(side=tk.LEFT)
        self.awb_lock = tk.BooleanVar(value=False)
        ttk.Checkbutton(awb, text="Khoá AWB (dùng Gains)", variable=self.awb_lock, command=self.on_lock_toggle).pack(side=tk.LEFT, padx=10)

        gains = tk.Frame(self.root); gains.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(gains, text="R gain").pack(side=tk.LEFT)
        self.r_gain = tk.DoubleVar(value=DEFAULT_R_GAIN)
        tk.Scale(gains, from_=0.5, to=4.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.r_gain, command=self.on_gains).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        tk.Label(gains, text="B gain").pack(side=tk.LEFT)
        self.b_gain = tk.DoubleVar(value=DEFAULT_B_GAIN)
        tk.Scale(gains, from_=0.5, to=4.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.b_gain, command=self.on_gains).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        self.preview_proc = None
        self.reader_thread = None
        self.running = False
        self.buf = bytearray()
        self.frames = queue.Queue(maxsize=2)

        self.start_preview()
        self.update_preview()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_vid_cmd(self):
        tool = "rpicam-vid" if shutil.which("rpicam-vid") else "libcamera-vid"
        cmd = [
            tool, "-t", "0", "--width", str(PREVIEW_WIDTH), "--height", str(PREVIEW_HEIGHT),
            "--framerate", "30", "--codec", "mjpeg", "--inline", "--stdout", "--denoise", "cdn_hq"
        ]
        if self.awb_lock.get():
            cmd += ["--awb", "off", "--awbgains", f"{float(self.r_gain.get())},{float(self.b_gain.get())}"]
        else:
            cmd += ["--awb", self.awb_mode.get()]
        return cmd

    def build_still_cmd(self, filename):
        tool = "rpicam-still" if shutil.which("rpicam-still") else "libcamera-still"
        cmd = [
            tool, "-o", filename, "-t", "1", "--immediate",
            "--width", str(STILL_W), "--height", str(STILL_H), "--denoise", "cdn_hq"
        ]
        if self.awb_lock.get():
            cmd += ["--awb", "off", "--awbgains", f"{float(self.r_gain.get())},{float(self.b_gain.get())}"]
        else:
            cmd += ["--awb", self.awb_mode.get()]
        return cmd

    def start_preview(self):
        self.stop_preview()
        try:
            self.preview_proc = subprocess.Popen(self.build_vid_cmd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.running = True
            self.reader_thread = threading.Thread(target=self.read_loop, daemon=True)
            self.reader_thread.start()
            self.status.set("Preview sRGB chạy…")
        except Exception as e:
            self.status.set(f"[LỖI] preview: {e}")

    def stop_preview(self):
        self.running = False
        if self.preview_proc and self.preview_proc.poll() is None:
            try:
                self.preview_proc.terminate()
                self.preview_proc.wait(timeout=1)
            except Exception:
                pass
        self.preview_proc = None

    def read_loop(self):
        JSO, JEO = b"\xff\xd8", b"\xff\xd9"
        while self.running and self.preview_proc and self.preview_proc.stdout:
            chunk = self.preview_proc.stdout.read(8192)
            if not chunk:
                time.sleep(0.01); continue
            self.buf.extend(chunk)
            while True:
                s = self.buf.find(JSO)
                e = self.buf.find(JEO, s+2)
                if s != -1 and e != -1:
                    frame = bytes(self.buf[s:e+2])
                    del self.buf[:e+2]
                    try:
                        img = Image.open(io.BytesIO(frame)).convert("RGB")
                        if not self.frames.full():
                            self.frames.put(img)
                    except Exception:
                        pass
                else:
                    break

    def update_preview(self):
        try:
            while not self.frames.empty():
                img = self.frames.get_nowait()
            if img:
                imgtk = ImageTk.PhotoImage(image=img.resize((PREVIEW_WIDTH, PREVIEW_HEIGHT)))
                self.preview_label.imgtk = imgtk
                self.preview_label.configure(image=imgtk)
        except Exception:
            pass
        self.root.after(33, self.update_preview)

    def on_awb_change(self, *_):
        self.start_preview()
    def on_lock_toggle(self):
        self.start_preview()
    def on_gains(self, *_):
        if self.awb_lock.get():
            self.start_preview()

    def capture(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_DIR, f"IMG_{ts}.jpg")
        self.status.set("Đang chụp…")
        try:
            subprocess.run(self.build_still_cmd(filename), check=True)
            self.status.set(f"Đã lưu: {filename}")
        except Exception as e:
            self.status.set(f"[LỖI] chụp: {e}")
        finally:
            self.start_preview()

    def on_close(self):
        self.stop_preview()
        self.root.destroy()


def main():
    root = tk.Tk()
    CameraGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()