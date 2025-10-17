#!/usr/bin/env python3
"""
GUI chụp ảnh với Raspberry Pi Camera Module 3 (Picamera2)
- Preview theo tông ấm (giống ảnh mẫu) bằng AWB Tungsten + ColourGains.
- Preview chạy cấu hình still (sRGB + RGB888) để khớp màu/độ nét với ảnh lưu.
- Trước chụp: khóa AE/AWB theo metadata hiện tại để giảm sai khác.
- Lưu ảnh vào /home/hungomctvn (tự tạo thư mục).

Cài đặt đề nghị (Raspberry Pi / Debian):
- sudo apt update && sudo apt install -y python3-picamera2 python3-pil python3-pil.imagetk libcamera libcamera-apps
- Kiểm tra camera: libcamera-hello -t 2000

Chạy:
- python3 gui_chup_anh_6.py
"""

import os
import sys
import tkinter as tk
from datetime import datetime

try:
    from PIL import Image, ImageTk
except Exception:
    print("[LỖI] Thiếu Pillow. Cài đặt: sudo apt install -y python3-pil python3-pil.imagetk")
    sys.exit(1)

# Picamera2 & ColorSpace (fallback nếu ColorSpace không khả dụng)
try:
    from picamera2 import Picamera2, ColorSpace
    _HAS_COLORSPACE = True
except Exception:
    try:
        from picamera2 import Picamera2
        _HAS_COLORSPACE = False
    except Exception:
        print("[LỖI] Thiếu Picamera2. Cài đặt: sudo apt install -y python3-picamera2")
        sys.exit(1)

# controls từ libcamera (AF/AWB/AE)
try:
    from libcamera import controls
except Exception:
    print("[LỖI] Thiếu libcamera. Cài đặt: sudo apt install -y libcamera libcamera-apps")
    sys.exit(1)

# Các tham số điều chỉnh tông màu ấm (có thể chỉnh thêm nếu cần)
WARM_AWB_MODE = getattr(controls.AwbModeEnum, "Tungsten", None)  # ánh sáng đèn vàng trong nhà
WARM_COLOUR_GAINS = (2.0, 1.10)  # (R, B) tăng đỏ, giảm xanh để ấm hơn
PREVIEW_WIDTH, PREVIEW_HEIGHT = 1280, 720
PREVIEW_SHARPNESS = 1.25
PREVIEW_CONTRAST = 1.06
PREVIEW_SATURATION = 1.08


class CameraGUI:
    def __init__(self, root: tk.Tk, save_dir: str = "/home/hungomctvn"):
        self.root = root
        self.root.title("Chụp ảnh Raspberry Pi - Preview tông ấm khớp ảnh lưu")
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Khung preview
        self.preview_width = PREVIEW_WIDTH
        self.preview_height = PREVIEW_HEIGHT
        self.preview_label = tk.Label(self.root, bg="black")
        self.preview_label.pack(padx=8, pady=8)

        # Thanh điều khiển
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=8, pady=8)

        self.capture_btn = tk.Button(control_frame, text="Chụp ảnh", command=self.capture)
        self.capture_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.status_label = tk.Label(control_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=12)

        # Khởi tạo camera
        self.picam2 = Picamera2()

        # Preview dùng cấu hình still để pipeline giống ảnh lưu
        try:
            if _HAS_COLORSPACE:
                self.preview_config = self.picam2.create_still_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                    colour_space=ColorSpace.Srgb,
                )
            else:
                self.preview_config = self.picam2.create_still_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                )
        except Exception:
            # Fallback: preview-config RGB888
            try:
                self.preview_config = self.picam2.create_preview_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                )
            except Exception:
                # Fallback cuối: lores
                self.preview_config = self.picam2.create_preview_configuration(
                    lores={"size": (640, 480), "format": "RGB888"},
                )
        self.picam2.configure(self.preview_config)

        # AF/AWB/AE và tinh chỉnh tông ấm cho preview
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfSpeed": controls.AfSpeedEnum.Fast,
            })
        except Exception:
            pass
        # Đặt AWB Tungsten nếu có, rồi tăng đỏ/giảm xanh để ấm hơn
        try:
            if WARM_AWB_MODE is not None:
                self.picam2.set_controls({"AwbMode": WARM_AWB_MODE})
        except Exception:
            pass
        try:
            self.picam2.set_controls({"ColourGains": (float(WARM_COLOUR_GAINS[0]), float(WARM_COLOUR_GAINS[1]))})
        except Exception:
            pass
        # Tinh chỉnh ISP nhẹ cho preview
        for k, v in (("Sharpness", PREVIEW_SHARPNESS), ("Contrast", PREVIEW_CONTRAST), ("Saturation", PREVIEW_SATURATION)):
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

    def update_preview(self):
        # Lấy khung hình hiện tại từ luồng 'main' và vẽ lên Tkinter
        try:
            frame = self.picam2.capture_array("main")
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
            self.root.after(200, self.update_preview)
            return

        img = Image.fromarray(frame)
        img = img.resize((self.preview_width, self.preview_height))
        imgtk = ImageTk.PhotoImage(image=img)
        # Giữ tham chiếu tránh GC
        self.preview_label.imgtk = imgtk
        self.preview_label.configure(image=imgtk)

        # Cập nhật lại sau ~33ms (~30fps)
        self.root.after(33, self.update_preview)

    def capture(self):
        # Tạo tên file với timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.save_dir, f"IMG_{ts}.jpg")

        # Chuẩn bị nét: chuyển AF sang Auto và kích hoạt AfTrigger
        self.status_var.set("Đang lấy nét...")
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Auto,
                "AfSpeed": controls.AfSpeedEnum.Fast,
            })
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

        # Khóa AE/AWB theo metadata hiện tại để khớp preview
        self.status_var.set("Khóa phơi sáng/màu...")
        try:
            md = self.picam2.capture_metadata()
            gains = md.get("ColourGains")
            exp_us = md.get("ExposureTime")
            again = md.get("AnalogueGain")
            # Áp lại ColourGains (ưu tiên tông ấm đã đặt)
            try:
                self.picam2.set_controls({"ColourGains": (float(WARM_COLOUR_GAINS[0]), float(WARM_COLOUR_GAINS[1]))})
            except Exception:
                if gains and isinstance(gains, (list, tuple)) and len(gains) == 2:
                    try:
                        self.picam2.set_controls({"ColourGains": (float(gains[0]), float(gains[1]))})
                    except Exception:
                        pass
            # Tắt AE rồi áp phơi sáng/gain hiện tại
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
            # Tắt AWB để giữ tông ấm trong ảnh chụp
            self.picam2.set_controls({"AwbEnable": False})
        except Exception:
            pass

        # Cấu hình chụp 12MP (ưu tiên sRGB) và chụp
        try:
            if _HAS_COLORSPACE:
                still_config = self.picam2.create_still_configuration(
                    main={"size": (4608, 3456)},
                    colour_space=ColorSpace.Srgb,
                )
            else:
                still_config = self.picam2.create_still_configuration(
                    main={"size": (4608, 3456)},
                )
        except Exception:
            still_config = self.picam2.create_still_configuration(
                main={"size": (4608, 3456)},
            )

        self.status_var.set("Đang chụp...")
        try:
            self.picam2.switch_mode_and_capture_file(still_config, filename)
            self.status_var.set(f"Đã lưu: {filename}")
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
        finally:
            # Khôi phục preview và bật lại AWB/AE + AF liên tục (giữ AWB mode Tungsten)
            try:
                self.picam2.configure(self.preview_config)
                self.picam2.set_controls({
                    "AwbEnable": True,
                    "AeEnable": True,
                    "AfMode": controls.AfModeEnum.Continuous,
                })
                if WARM_AWB_MODE is not None:
                    self.picam2.set_controls({"AwbMode": WARM_AWB_MODE})
                # Áp lại ColourGains tông ấm cho preview
                try:
                    self.picam2.set_controls({"ColourGains": (float(WARM_COLOUR_GAINS[0]), float(WARM_COLOUR_GAINS[1]))})
                except Exception:
                    pass
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