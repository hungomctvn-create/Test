#!/bin/bash

# Script khắc phục nhanh lỗi NumPy và OpenCV trên Raspberry Pi
# Chạy trực tiếp trên Raspberry Pi mà không cần chuyển file

echo "========================================"
echo "  KHẮC PHỤC LỖI NUMPY VÀ OPENCV NHANH"
echo "========================================"
echo

# Kiểm tra quyền sudo
if ! sudo -n true 2>/dev/null; then
    echo "⚠ Script này cần quyền sudo. Vui lòng nhập mật khẩu khi được yêu cầu."
fi

echo "🔧 Bước 1: Gỡ cài đặt NumPy 2.0.2..."
pip3 uninstall numpy -y 2>/dev/null || true
pip uninstall numpy -y 2>/dev/null || true

echo "🔧 Bước 2: Cập nhật hệ thống..."
sudo apt update -qq

echo "🔧 Bước 3: Cài đặt NumPy từ apt (phiên bản tương thích)..."
sudo apt install python3-numpy -y

echo "🔧 Bước 4: Cài đặt OpenCV từ apt..."
sudo apt install python3-opencv -y

echo "🔧 Bước 5: Cài đặt các thư viện cần thiết..."
pip3 install --user pygame==2.1.0
pip3 install --user gtts==2.2.4  
pip3 install --user pyttsx3==2.90
pip3 install --user requests
pip3 install --user pyyaml
pip3 install --user tqdm

echo "🔧 Bước 6: Kiểm tra cài đặt..."
echo "Kiểm tra NumPy..."
python3 -c "import numpy; print(f'✓ NumPy {numpy.__version__} - OK')" 2>/dev/null || echo "✗ NumPy - LỖI"

echo "Kiểm tra OpenCV..."
python3 -c "import cv2; print(f'✓ OpenCV {cv2.__version__} - OK')" 2>/dev/null || echo "✗ OpenCV - LỖI"

echo "Kiểm tra Pygame..."
python3 -c "import pygame; print('✓ Pygame - OK')" 2>/dev/null || echo "✗ Pygame - LỖI"

echo "Kiểm tra gTTS..."
python3 -c "from gtts import gTTS; print('✓ gTTS - OK')" 2>/dev/null || echo "✗ gTTS - LỖI"

echo
echo "========================================"
echo "           HOÀN THÀNH KHẮC PHỤC"
echo "========================================"
echo
echo "📋 Các lệnh hữu ích:"
echo "• Kiểm tra phiên bản: python3 -c \"import numpy, cv2; print(f'NumPy: {numpy.__version__}, OpenCV: {cv2.__version__}')\""
echo "• Chạy test: python3 -c \"import cv2, numpy, pygame, gtts; print('✓ Tất cả thư viện OK')\""
echo
echo "🚀 Bây giờ bạn có thể chạy các ứng dụng Python mà không gặp lỗi!"