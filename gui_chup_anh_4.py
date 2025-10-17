#!/usr/bin/env python3
"""
GUI chụp ảnh với Raspberry Pi Camera Module 3 (Picamera2)
- Preview màu trung thực (ưu tiên sRGB + RGB888 nếu khả dụng).
- Nút "Chụp ảnh" lưu ảnh vào /home/hungomctvn (tạo thư mục nếu thiếu).
- Tương thích với các phiên bản Picamera2/libcamera khác nhau (fallback tự động).

Yêu cầu trên Raspberry Pi:
- sudo apt update && sudo apt install -y python3-picamera2 python3-pil python3-pil.imagetk libcamera libcamera-apps
- Kiểm tra camera: libcamera-hello -t 2000

Chạy:
- python3 gui_chup_anh_4.py
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


class CameraGUI:
    def __init__(self, root: tk.Tk, save_dir: str = "/home/hungomctvn"):
        self.root = root
        self.root.title("Chụp ảnh Raspberry Pi - Preview màu trung thực")
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Kích thước preview (dùng luồng 'main' để màu/độ nét gần khớp ảnh chụp)
        self.preview_width = 960
        self.preview_height = 540
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

        # Preview: ưu tiên luồng 'main' sRGB + RGB888; fallback 'lores' nếu cần
        self.preview_stream = "main"
        try:
            if _HAS_COLORSPACE:
                self.preview_config = self.picam2.create_preview_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                    colour_space=ColorSpace.Srgb,
                )
            else:
                self.preview_config = self.picam2.create_preview_configuration(
                    main={"size": (self.preview_width, self.preview_height), "format": "RGB888"},
                )
        except Exception:
            # Fallback: dùng lores nếu main không hỗ trợ trên môi trường hiện tại
            try:
                self.preview_config = self.picam2.create_preview_configuration(
                    lores={"size": (640, 480), "format": "RGB888"},
                )
                self.preview_stream = "lores"
            except Exception:
                # Fallback cuối: main không đặt colour_space/format
                self.preview_config = self.picam2.create_preview_configuration(
                    main={"size": (640, 480)},
                )
                self.preview_stream = "main"
        self.picam2.configure(self.preview_config)

        # AF/AWB mặc định trong chế độ preview
        try:
            self.picam2.set_controls({
                "AfMode": controls.AfModeEnum.Continuous,
                "AfSpeed": controls.AfSpeedEnum.Fast,
                "AwbMode": controls.AwbModeEnum.Auto,
            })
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
            frame = self.picam2.capture_array(self.preview_stream)
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

        # Chuẩn bị nét: chuyển AF sang Auto và kích hoạt AfTrigger để khóa nét
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

        # Khóa AWB/AE ngay trước khi chụp để màu/phơi sáng khớp preview
        try:
            md = self.picam2.capture_metadata()
            gains = md.get("ColourGains")
            if gains and isinstance(gains, (list, tuple)) and len(gains) == 2:
                # Áp dụng lại gains hiện tại để giữ AWB ổn định
                self.picam2.set_controls({"ColourGains": (float(gains[0]), float(gains[1]))})
            # Tắt AWB/AE tạm thời (giữ các giá trị vừa áp dụng)
            self.picam2.set_controls({"AwbEnable": False})
            self.picam2.set_controls({"AeEnable": False})
        except Exception:
            pass

        # Cấu hình chụp độ phân giải cao (12MP) ưu tiên sRGB; fallback nếu không hỗ trợ
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

        # Thực hiện chụp
        self.status_var.set("Đang chụp...")
        try:
            self.picam2.switch_mode_and_capture_file(still_config, filename)
            self.status_var.set(f"Đã lưu: {filename}")
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
        finally:
            # Khôi phục preview và bật lại AWB/AE + AF liên tục
            try:
                self.picam2.configure(self.preview_config)
                self.picam2.set_controls({
                    "AwbEnable": True,
                    "AeEnable": True,
                    "AfMode": controls.AfModeEnum.Continuous,
                    "AwbMode": controls.AwbModeEnum.Auto,
                })
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