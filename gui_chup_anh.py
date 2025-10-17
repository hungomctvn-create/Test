#!/usr/bin/env python3
"""
GUI chụp ảnh với Camera Raspberry Pi (Module 3) trên Raspberry Pi 5.
- Hiển thị preview trực tiếp trong cửa sổ (Tkinter).
- Nút "Chụp ảnh" để lưu file vào /home/hungomctvn với timestamp.

Yêu cầu trên Raspberry Pi:
- sudo apt update && sudo apt install -y python3-picamera2 python3-pil python3-pil.imagetk
- Camera hoạt động: rpicam-hello -t 2000

Chạy:
- python3 gui_chup_anh.py
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

try:
    from picamera2 import Picamera2
    from libcamera import controls
except Exception:
    print("[LỖI] Thiếu Picamera2/libcamera. Cài đặt: sudo apt install -y python3-picamera2")
    sys.exit(1)


class CameraGUI:
    def __init__(self, root: tk.Tk, save_dir: str = "/home/hungomctvn"):
        self.root = root
        self.root.title("Chụp ảnh Raspberry Pi")
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Khung preview
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
        # Cấu hình preview nhỏ để hiển thị mượt
        self.preview_config = self.picam2.create_preview_configuration(
            main={"size": (self.preview_width, self.preview_height)}
        )
        self.picam2.configure(self.preview_config)

        # Lấy nét liên tục (Camera V3)
        try:
            self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        except Exception:
            # Bỏ qua nếu không hỗ trợ
            pass

        self.picam2.start()

        # Bắt đầu vòng lặp cập nhật preview
        self.update_preview()

        # Đóng cửa sổ an toàn
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_preview(self):
        # Lấy khung hình hiện tại từ camera và vẽ lên Tkinter
        try:
            frame = self.picam2.capture_array()
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
            self.root.after(200, self.update_preview)
            return

        img = Image.fromarray(frame)
        # Đảm bảo đúng kích thước label
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

        # Tạo cấu hình chụp độ phân giải cao (12MP Camera V3)
        still_config = self.picam2.create_still_configuration(main={"size": (4608, 3456)})

        # Thực hiện chuyển cấu hình và chụp
        self.status_var.set("Đang chụp...")
        try:
            self.picam2.switch_mode_and_capture_file(still_config, filename)
            self.status_var.set(f"Đã lưu: {filename}")
        except Exception as e:
            self.status_var.set(f"[LỖI] {e}")
        finally:
            # Trở về cấu hình preview
            try:
                self.picam2.configure(self.preview_config)
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