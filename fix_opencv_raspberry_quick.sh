#!/bin/bash

echo "🚀 KHẮC PHỤC LỖI OPENCV TRÊN RASPBERRY PI"
echo "========================================"

# Cập nhật hệ thống
echo "📦 Cập nhật hệ thống..."
sudo apt update && sudo apt upgrade -y

# Cài đặt Python pip nếu chưa có
echo "🐍 Cài đặt Python pip..."
sudo apt install python3-pip -y

# Cài đặt các thư viện cần thiết cho OpenCV
echo "📚 Cài đặt dependencies cho OpenCV..."
sudo apt install -y \
    python3-opencv \
    libopencv-dev \
    python3-numpy \
    python3-matplotlib \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test

# Cài đặt OpenCV qua pip (backup method)
echo "🔧 Cài đặt OpenCV qua pip..."
pip3 install opencv-python==4.5.5.64
pip3 install opencv-contrib-python==4.5.5.64

# Cài đặt các thư viện khác cần thiết
echo "📋 Cài đặt các thư viện khác..."
pip3 install numpy
pip3 install ultralytics
pip3 install pygame
pip3 install pillow

# Test OpenCV
echo "🧪 Test OpenCV..."
python3 -c "
try:
    import cv2
    print('✅ OpenCV đã cài đặt thành công!')
    print(f'✅ Phiên bản OpenCV: {cv2.__version__}')
    
    import numpy as np
    print('✅ NumPy OK')
    
    try:
        import ultralytics
        print('✅ YOLO (ultralytics) OK')
    except:
        print('⚠️  YOLO chưa có, đang cài...')
        import subprocess
        subprocess.run(['pip3', 'install', 'ultralytics'])
        
    try:
        import pygame
        print('✅ Pygame OK')
    except:
        print('⚠️  Pygame chưa có, đang cài...')
        import subprocess
        subprocess.run(['pip3', 'install', 'pygame'])
        
except ImportError as e:
    print(f'❌ Lỗi import: {e}')
    print('🔧 Thử cài đặt lại...')
"

# Kiểm tra camera
echo "📷 Kiểm tra camera..."
if [ -e /dev/video0 ]; then
    echo "✅ Camera tìm thấy tại /dev/video0"
else
    echo "⚠️  Không tìm thấy camera, cài đặt v4l2loopback..."
    sudo apt install v4l2loopback-dkms v4l-utils -y
    sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="Virtual Camera" exclusive_caps=1
fi

echo ""
echo "🎉 HOÀN THÀNH! Thử chạy chương trình:"
echo "cd ~/Desktop"
echo "python3 Nhan_dang_nguoi_yolo.py"