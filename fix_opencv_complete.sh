#!/bin/bash

echo "🔧 KHẮC PHỤC TOÀN BỘ LỖI OPENCV VÀ CAMERA"
echo "========================================"

# Bước 1: Gỡ cài đặt OpenCV cũ
echo "📦 Gỡ cài đặt OpenCV cũ..."
sudo apt remove -y python3-opencv opencv-data libopencv-dev
pip3 uninstall -y opencv-python opencv-contrib-python opencv-python-headless

# Bước 2: Cài đặt dependencies cần thiết
echo "📦 Cài đặt dependencies..."
sudo apt update
sudo apt install -y \
    python3-pip \
    libgtk-3-dev \
    libcanberra-gtk3-module \
    libqt5gui5 \
    libqt5test5 \
    libqt5widgets5 \
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

# Bước 3: Cài đặt OpenCV với GUI support
echo "📦 Cài đặt OpenCV với GUI support..."
pip3 install --upgrade pip
pip3 install opencv-contrib-python==4.5.5.64

# Bước 4: Cài đặt camera drivers
echo "📦 Cài đặt camera drivers..."
sudo apt install -y v4l-utils v4l2loopback-dkms fswebcam

# Bước 5: Tạo virtual camera
echo "📦 Tạo virtual camera..."
sudo modprobe v4l2loopback devices=2 video_nr=0,1 card_label="Virtual Camera 1","Virtual Camera 2"

# Bước 6: Cấu hình permissions
echo "📦 Cấu hình permissions..."
sudo usermod -a -G video $USER
sudo chmod 666 /dev/video*

# Bước 7: Test OpenCV
echo "🧪 Test OpenCV..."
python3 -c "
import cv2
print(f'✅ OpenCV version: {cv2.__version__}')
print(f'✅ GUI support: {cv2.getBuildInformation().find(\"GUI\") != -1}')
print(f'✅ V4L2 support: {cv2.getBuildInformation().find(\"V4L/V4L2\") != -1}')

# Test camera
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Camera test: SUCCESS')
    cap.release()
else:
    print('❌ Camera test: FAILED')
"

# Bước 8: Kiểm tra video devices
echo "📹 Kiểm tra video devices..."
ls -la /dev/video*
v4l2-ctl --list-devices

echo ""
echo "✅ HOÀN THÀNH! Khởi động lại terminal và chạy lại chương trình."
echo "💡 Nếu vẫn lỗi, chạy: source ~/.bashrc && python3 Nhan_dang_nguoi_yolo.py"