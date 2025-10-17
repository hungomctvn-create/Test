#!/usr/bin/env python3
"""
GUI chụp ảnh với Raspberry Pi Camera Module 3 (Picamera2)
- Thêm nút chuyển AwbMode (Auto/Daylight/Cloudy/Fluorescent/Tungsten nếu hỗ trợ).
- Thêm thanh trượt ColourGains (R/B) để tinh chỉnh trực tiếp; có tuỳ chọn Khoá AWB.
- Chỉ dùng bảng màu sRGB cho preview và chụp (RGB888).
- Trước chụp: khoá AE/AWB theo trạng thái UI để giảm sai khác.
- Lưu ảnh vào /home/hungomctvn (tự tạo thư mục).

Cài đặt đề nghị (Raspberry Pi / Debian):
- sudo apt update && sudo apt install -y python3-picamera2 python3-pil python3-pil.imagetk libcamera libcamera-apps
- Kiểm tra camera: libcamera-hello -t 2000

Chạy:
- python3 gui_chup_anh_7.py
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from datetime import datetime

try:
    from PIL import Image, ImageTk
except Exception:
    print("[LỖI] Thiếu Pillow. Cài đặt: sudo apt install -y python3-pil python3-pil.imagetk")
    sys.exit(1)

# Picamera2 & ColorSpace (bắt buộc sRGB)
try:
    from picamera2 import Picamera2, ColorSpace
except Exception:
    print("[LỖI] Yêu cầu Picamera2 với ColorSpace.Srgb. Cài đặt: sudo apt install -y python3-picamera2")
    sys.exit(1)

# controls từ libcamera (AF/AWB/AE)
try:
    from libcamera import controls
except Exception:
    print("[LỖI] Thiếu libcamera. Cài đặt: sudo apt install -y libcamera libcamera-apps")
    sys.exit(1)

PREVIEW_WIDTH, PREVIEW_HEIGHT = 1280, 720
DEFAULT_R_GAIN = 2.0
DEFAULT_B_GAIN = 1.10

# Các AwbMode ứng viên; chỉ hiển thị các mode thực sự tồn tại trong môi trường
AWB_CANDIDATES = ["Auto", "Daylight", "Cloudy", "Fluorescent", "Tungsten"]

def awb_enum(name):
    return getattr(controls.AwbModeEnum, name, None)


a = awb_enum  # alias
AVAILABLE_AWB = [n for n in AWB_CANDIDATES if a(n) is not None]
if not AVAILABLE_AWB:
    AVAILABLE_AWB = ["Auto"]


class CameraGUI:
    def __init__(self, root: tk.Tk, save_dir: str = "/home/hungomctvn"):
        self.root = root
        self.root.title("Chụp ảnh Raspberry Pi - AWB & ColourGains trực tiếp")
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Khung preview
        self.preview_width = PREVIEW_WIDTH
        self.preview_height = PREVIEW_HEIGHT
        self.preview_label = tk.Label(self.root, bg="black")
        self.preview_label.pack(padx=8, pady=8)

        # Thanh điều khiển chính
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=8, pady=4)

        self.capture_btn = tk.Button(control_frame, text="Chụp ảnh", command=self.capture)
        self.capture_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.status_label = tk.Label(control_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=12)

        # Khung điều chỉnh AWB & Gains
        awb_frame = tk.LabelFrame(self.root, text="Cân bằng trắng (AWB) & ColourGains")
        awb_frame.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(awb_frame, text="AwbMode:").pack(side=tk.LEFT, padx=(6, 4))
        self.awb_mode_var = tk.StringVar(value=("Tungsten" if "Tungsten" in AVAILABLE_AWB else AVAILABLE_AWB[0]))
        self.awb_menu = ttk.OptionMenu(awb_frame, self.awb_mode_var, self.awb_mode_var.get(), *AVAILABLE_AWB, command=self.on_awb_mode_change)
        self.awb_menu.pack(side=tk.LEFT)

        self.awb_lock_var = tk.BooleanVar(value=False)
        self.awb_lock_check = ttk.Checkbutton(awb_frame, text="Khoá AWB (dùng ColourGains)", variable=self.awb_lock_var, command=self.on_awb_lock_toggle)
        self.awb_lock_check.pack(side=tk.LEFT, padx=12)

        gains_frame = tk.Frame(self.root)
        gains_frame.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(gains_frame, text="R gain").pack(side=tk.LEFT)
        self.r_gain = tk.DoubleVar(value=DEFAULT_R_GAIN)
        self.r_slider = tk.Scale(gains_frame, from_=0.5, to=4.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.r_gain, command=self.on_gain_change)
        self.r_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        tk.Label(gains_frame, text="B gain").pack(side=tk.LEFT)
        self.b_gain = tk.DoubleVar(value=DEFAULT_B_GAIN)
        self.b_slider = tk.Scale(gains_frame, from_=0.5, to=4.0, resolution=0.01, orient=tk.HORIZONTAL, variable=self.b_gain, command=self.on_gain_change)
        self.b_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        # Khởi tạo camera
        self.picam2 = Picamera2()

        # Preview chỉ dùng sRGB; fallback vẫn sRGB
        self.preview_stream = "main"
        try:
            self.preview_config = self.picam2.create_still_configuration(
                main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                colour_space=ColorSpace.Srgb,
            )
        except Exception as e:
            try:
                self.preview_config = self.picam2.create_preview_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                    colour_space=ColorSpace.Srgb,
                )
            except Exception as e1:
                try:
                    self.preview_config = self.picam2.create_preview_configuration(
                        lores={"size": (640, 480), "format": "RGB888"},
                        colour_space=ColorSpace.Srgb,
                    )
                    self.preview_stream = "lores"
                except Exception as e2:
                    self.status_var.set(f"[LỖI] Không thể tạo preview sRGB: {e2}")
                    raise
        self.picam2.configure(self.preview_config)

        # Thiết lập AF/AWB/AE mặc định
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfSpeed": controls.AfSpeedEnum.Fast,
            })
        except Exception:
            pass
        # Áp AwbMode mặc định và ColourGains ban đầu nếu có
        self.apply_awb_mode()
        self.apply_gains_if_locked()

        # Tinh chỉnh ISP nhẹ cho preview
        for k, v in (("Sharpness", 1.20), ("Contrast", 1.05), ("Saturation", 1.06)):
            try:
                self.picam2.set_controls({k: v})
            except Exception:
                pass
        try:
            self.picam2.set_controls({"NoiseReductionMode": controls.NoiseReductionModeEnum.HighQuality})
        except Exception:
            pass

        self.picam2.start()

        # Bắt đầu vòng lặp cập nhật preview
        self.update_preview()

        # Đóng cửa sổ an toàn
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ===== UI handlers & helpers =====
    def apply_awb_mode(self):
        try:
            mode_name = self.awb_mode_var.get()
            enum_val = awb_enum(mode_name)
            if enum_val is not None:
                self.picam2.set_controls({"AwbMode": enum_val})
                # Khi chọn mode, bật AWB nếu chưa khoá
                if not self.awb_lock_var.get():
                    self.picam2.set_controls({"AwbEnable": True})
        except Exception:
            pass

    def apply_gains_if_locked(self):
        if not self.awb_lock_var.get():
            return
        try:
            self.picam2.set_controls({"AwbEnable": False})
            self.picam2.set_controls({"ColourGains": (float(self.r_gain.get()), float(self.b_gain.get()))})
        except Exception:
            pass

    def on_awb_mode_change(self, *_):
        # Thay đổi mode: bật AWB (nếu không khoá) và áp enum
        self.apply_awb_mode()

    def on_awb_lock_toggle(self):
        # Bật/tắt khoá AWB; nếu bật thì áp ColourGains hiện tại
        if self.awb_lock_var.get():
            self.apply_gains_if_locked()
        else:
            try:
                self.picam2.set_controls({"AwbEnable": True})
                self.apply_awb_mode()
            except Exception:
                pass

    def on_gain_change(self, *_):
        # Thay đổi sliders: chỉ áp dụng nếu AWB đang khoá
        self.apply_gains_if_locked()

    # ===== Camera operations =====
    def update_preview(self):
        try:
            frame = self.picam2.capture_array(self.preview_stream)
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
            self.root.after(200, self.update_preview)
            return

        img = Image.fromarray(frame)
        img = img.resize((self.preview_width, self.preview_height))
        imgtk = ImageTk.PhotoImage(image=img)
        self.preview_label.imgtk = imgtk
        self.preview_label.configure(image=imgtk)

        self.root.after(33, self.update_preview)

    def capture(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_dir, f"IMG_{ts}.jpg")

        # Khoá nét trước chụp
        self.status_var.set("Đang lấy nét...")
        try:
            self.picam2.set_controls({"AfMode": controls.AfModeEnum.Auto, "AfSpeed": controls.AfSpeedEnum.Fast})
            try:
                self.picam2.set_controls({"AfTrigger": controls.AfTrigger.Start})
            except Exception:
                pass
            import time as _time
            t0 = _time.time()
            while _time.time() - t0 < 2.0:
                md = self.picam2.capture_metadata()
                st = md.get("AfState")
                if st == controls.AfStateEnum.Focused:
                    break
                _time.sleep(0.05)
        except Exception:
            pass

        # Khóa AE/AWB theo trạng thái UI để khớp preview
        self.status_var.set("Khóa phơi sáng/màu...")
        try:
            md = self.picam2.capture_metadata()
            exp_us = md.get("ExposureTime")
            again = md.get("AnalogueGain")
            if exp_us and again:
                self.picam2.set_controls({"AeEnable": False})
                try:
                    self.picam2.set_controls({"ExposureTime": int(exp_us)})
                except Exception:
                    pass
                try:
                    self.picam2.set_controls({"AnalogueGain": float(again)})
                except Exception:
                    pass
            # AWB: nếu khoá, giữ Gains; nếu không, tạm khoá để giữ màu hiện tại
            if self.awb_lock_var.get():
                self.apply_gains_if_locked()
            else:
                try:
                    self.picam2.set_controls({"AwbEnable": False})
                    # Giữ gains hiện tại nếu đọc được
                    gains = md.get("ColourGains")
                    if gains and isinstance(gains, (list, tuple)) and len(gains) == 2:
                        self.picam2.set_controls({"ColourGains": (float(gains[0]), float(gains[1]))})
                except Exception:
                    pass
        except Exception:
            pass

        # Cấu hình chụp 12MP (chỉ sRGB) và chụp
        try:
            still_config = self.picam2.create_still_configuration(
                main={"size": (4608, 3456)},
                colour_space=ColorSpace.Srgb,
            )
        except Exception as e:
            self.status_var.set(f"[LỖI] Không thể tạo cấu hình chụp sRGB: {e}")
            return

        self.status_var.set("Đang chụp...")
        try:
            self.picam2.switch_mode_and_capture_file(still_config, filename)
            self.status_var.set(f"Đã lưu: {filename}")
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
        finally:
            # Khôi phục preview và trạng thái AWB/AE/AF theo UI
            try:
                self.picam2.configure(self.preview_config)
                self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous, "AwbMode": awb_enum(self.awb_mode_var.get())})
                # AE bật lại
                self.picam2.set_controls({"AeEnable": True})
                # AWB theo checkbox
                self.picam2.set_controls({"AwbEnable": (False if self.awb_lock_var.get() else True)})
                # Nếu khoá, áp lại gains từ sliders
                self.apply_gains_if_locked()
                self.picam2.start()
            except Exception:
                pass

    def on_close(self):
        try:
            self.picam2.stop()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CameraGUI(root, save_dir="/home/hungomctvn")
    root.mainloop()


if __name__ == "__main__":
    main()