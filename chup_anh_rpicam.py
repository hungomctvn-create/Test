#!/usr/bin/env python3
"""
Script Python chụp ảnh với rpicam-still cho Raspberry Pi 5 + Camera Module 3.

- Mặc định dùng "-t 0" (preview vô hạn, nhấn Enter để chụp).
- Hỗ trợ tùy chọn lấy nét (AF), độ phân giải, chất lượng JPEG, xoay ảnh, chọn camera.

Yêu cầu trên Raspberry Pi:
- Raspberry Pi OS (Bookworm), đã cài: sudo apt update && sudo apt install -y rpicam-apps
- Camera đã gắn đúng và hoạt động: rpicam-hello -t 2000

Ví dụ chạy:
- Tương tác với preview, nhấn Enter để chụp:
  python3 chup_anh_rpicam.py -o ~/Pictures/v3.jpg

- Chụp 12MP và AF liên tục:
  python3 chup_anh_rpicam.py -o ~/Pictures/v3_full.jpg --width 4608 --height 3456 \
    --autofocus-mode continuous --autofocus-on-capture 1

- Headless (không preview), tự chụp sau 2 giây:
  python3 chup_anh_rpicam.py -o ~/Pictures/v3.jpg -n -t 2000
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime


def ensure_rpicam_available() -> str:
    """Kiểm tra rpicam-still có sẵn trên hệ thống không."""
    exe = shutil.which("rpicam-still")
    if not exe:
        print("[LỖI] Không tìm thấy 'rpicam-still'. Hãy cài: sudo apt install -y rpicam-apps")
        sys.exit(1)
    return exe


def timestamped_path(path: str) -> str:
    """Chèn timestamp vào tên file đầu ra nếu người dùng yêu cầu."""
    base_dir = os.path.dirname(path)
    base_name = os.path.basename(path)
    stem, ext = os.path.splitext(base_name)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_dir or ".", f"{stem}_{ts}{ext or '.jpg'}")


def build_command(args: argparse.Namespace, rpicam_exe: str, out_path: str) -> list:
    """Tạo danh sách tham số cho lệnh rpicam-still."""
    cmd = [rpicam_exe]

    # Timeout (0 = chờ Enter, >0 = tự chụp sau N mili-giây)
    cmd += ["-t", str(args.timeout)]

    # No preview (headless)
    if args.no_preview:
        cmd.append("-n")

    # Đầu ra
    cmd += ["-o", out_path]

    # Kích thước (độ phân giải)
    if args.width:
        cmd += ["--width", str(args.width)]
    if args.height:
        cmd += ["--height", str(args.height)]

    # Chất lượng JPEG
    if args.quality is not None:
        cmd += ["--quality", str(args.quality)]

    # Xoay ảnh nếu cần
    if args.rotation in (0, 90, 180, 270):
        if args.rotation != 0:
            cmd += ["--rotation", str(args.rotation)]

    # Chọn camera index nếu có nhiều camera
    if args.camera is not None:
        cmd += ["--camera", str(args.camera)]

    # Lấy nét (AF)
    if args.autofocus_mode:
        cmd += ["--autofocus-mode", args.autofocus_mode]
    if args.autofocus_on_capture in (0, 1):
        cmd += ["--autofocus-on-capture", str(args.autofocus_on_capture)]

    # Verbose (tùy)
    if args.verbose:
        cmd.append("--verbose")

    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bọc lệnh rpicam-still -t 0 cho Raspberry Pi 5 + Camera V3"
    )
    parser.add_argument(
        "-o", "--output", default="/home/hungomctvn/v3.jpg",
        help="Đường dẫn file ảnh đầu ra (mặc định: /home/hungomctvn/v3.jpg)"
    )
    parser.add_argument(
        "--timestamp", action="store_true",
        help="Thêm timestamp vào tên file đầu ra"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=0,
        help="Thời gian chờ trước khi chụp (ms). 0 = chờ Enter (mặc định)"
    )
    parser.add_argument(
        "-n", "--no-preview", action="store_true",
        help="Tắt preview (phù hợp chạy headless/SSH)"
    )
    parser.add_argument(
        "--width", type=int, default=4608,
        help="Chiều ngang ảnh (mặc định 4608 cho 12MP Camera V3)"
    )
    parser.add_argument(
        "--height", type=int, default=3456,
        help="Chiều dọc ảnh (mặc định 3456 cho 12MP Camera V3)"
    )
    parser.add_argument(
        "--quality", type=int, default=95,
        help="Chất lượng JPEG (0-100), mặc định 95"
    )
    parser.add_argument(
        "--rotation", type=int, choices=[0, 90, 180, 270], default=0,
        help="Xoay ảnh (độ), mặc định 0"
    )
    parser.add_argument(
        "--camera", type=int, default=None,
        help="Chọn camera index nếu có nhiều camera (ví dụ: 0 hoặc 1)"
    )
    parser.add_argument(
        "--autofocus-mode", choices=["auto", "manual", "continuous"], default="continuous",
        help="Chế độ lấy nét: auto/manual/continuous (mặc định: continuous)"
    )
    parser.add_argument(
        "--autofocus-on-capture", type=int, choices=[0, 1], default=1,
        help="Bật/tắt khóa nét lúc chụp (0/1), mặc định 1"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="In log chi tiết từ rpicam-still"
    )
    parser.add_argument(
        "--enter", action="store_true",
        help="Chụp khi nhấn Enter (lặp lại cho đến khi thoát)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rpicam_exe = ensure_rpicam_available()

    # Nếu bật chế độ chụp khi nhấn Enter (loop tương tác)
    if args.enter:
        # Tạo thư mục nếu chưa có
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
    
        print("=== Chế độ Enter-to-chụp ===")
        print("Nhấn Enter để chụp; gõ 'q' rồi Enter để thoát.")
        try:
            while True:
                user_input = input()
                if user_input.strip().lower() in ("q", "quit", "exit"):
                    print("[Thoát] Đã dừng chế độ Enter-to-chụp.")
                    break
    
                # Luôn thêm timestamp để tránh ghi đè
                out_path_iter = timestamped_path(args.output)
    
                # Sử dụng no-preview và timeout ngắn nếu chưa đặt
                local_args = argparse.Namespace(**vars(args))
                local_args.no_preview = True
                local_args.timeout = args.timeout if args.timeout > 0 else 200
    
                cmd = build_command(local_args, rpicam_exe, out_path_iter)
                print("Lệnh:", " ".join(cmd))
                try:
                    subprocess.run(cmd, check=True)
                    if os.path.exists(out_path_iter):
                        print(f"[OK] Đã lưu ảnh: {out_path_iter}")
                    else:
                        print("[CẢNH BÁO] Lệnh chạy xong nhưng không thấy file đầu ra.")
                except subprocess.CalledProcessError as e:
                    print("[LỖI] rpicam-still trả về lỗi:", e)
                    # tiếp tục vòng lặp
        except KeyboardInterrupt:
            print("[ĐÃ HỦY] Bạn đã hủy thao tác (Ctrl+C).")
        sys.exit(0)

    # Xử lý đường dẫn đầu ra và timestamp nếu yêu cầu
    out_path = args.output
    if args.timestamp:
        out_path = timestamped_path(out_path)

    # Tạo thư mục nếu chưa có
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    cmd = build_command(args, rpicam_exe, out_path)

    # Thông tin thân thiện
    print("=== Chụp ảnh với rpicam-still ===")
    print("Lệnh:", " ".join(cmd))
    if args.timeout == 0 and not args.no_preview:
        print("[Hướng dẫn] Preview sẽ hiển thị vô hạn; nhấn Enter để chụp và kết thúc.")
    elif args.timeout == 0 and args.no_preview:
        print("[Lưu ý] Đang tắt preview (-n) và timeout=0; nhấn Enter trong terminal để chụp.")
    else:
        print(f"[Hướng dẫn] Sẽ tự chụp sau {args.timeout} ms.")

    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(out_path):
            print(f"[OK] Đã lưu ảnh: {out_path}")
        else:
            print("[CẢNH BÁO] Lệnh chạy xong nhưng không thấy file đầu ra.")
    except subprocess.CalledProcessError as e:
        print("[LỖI] rpicam-still trả về lỗi:", e)
        sys.exit(e.returncode or 1)
    except KeyboardInterrupt:
        print("[ĐÃ HỦY] Bạn đã hủy thao tác (Ctrl+C).")


if __name__ == "__main__":
    main()