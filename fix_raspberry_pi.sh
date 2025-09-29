#!/bin/bash

echo "=== SCRIPT KHẮC PHỤC LỖI RASPBERRY PI ==="
echo "Bắt đầu khắc phục các lỗi NumPy, OpenCV và dependencies..."

# Bước 1: Backup và gỡ cài đặt các thư viện có vấn đề
echo "Bước 1: Gỡ cài đặt các thư viện có vấn đề..."
sudo pip3 uninstall numpy -y
sudo pip3 uninstall opencv-python -y
sudo pip3 uninstall opencv-contrib-python -y
sudo pip3 uninstall ultralytics -y

# Bước 2: Cập nhật hệ thống
echo "Bước 2: Cập nhật hệ thống..."
sudo apt update
sudo apt upgrade -y

# Bước 3: Cài đặt các dependencies cần thiết
echo "Bước 3: Cài đặt dependencies hệ thống..."
sudo apt install -y python3-dev python3-pip
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libatlas3-base libgfortran5 libjasper-dev 
sudo apt install -y libqtgui4 libqt4-test libqtcore4
sudo apt install -y libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install -y libxvidcore-dev libx264-dev libgtk2.0-dev
sudo apt install -y libcanberra-gtk-module libcanberra-gtk3-module

# Bước 4: Cài đặt NumPy phiên bản tương thích
echo "Bước 4: Cài đặt NumPy 1.21.0 (tương thích với Raspberry Pi)..."
sudo pip3 install numpy==1.21.0

# Bước 5: Cài đặt OpenCV từ apt (ổn định hơn)
echo "Bước 5: Cài đặt OpenCV từ repository..."
sudo apt install -y python3-opencv

# Bước 6: Cài đặt các thư viện Python cần thiết
echo "Bước 6: Cài đặt các thư viện Python..."
sudo pip3 install pillow==8.4.0
sudo pip3 install matplotlib==3.5.3
sudo pip3 install scipy==1.7.3
sudo pip3 install requests
sudo pip3 install pyyaml
sudo pip3 install tqdm

# Bước 7: Cài đặt thư viện âm thanh
echo "Bước 7: Cài đặt thư viện âm thanh..."
sudo pip3 install gtts==2.2.4
sudo pip3 install pygame==2.1.0
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev
sudo pip3 install pyttsx3==2.90

# Bước 8: Kiểm tra cài đặt
echo "Bước 8: Kiểm tra cài đặt..."
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
python3 -c "import gtts; print('gTTS imported successfully')"
python3 -c "import pygame; print('Pygame imported successfully')"

echo "=== HOÀN THÀNH KHẮC PHỤC LỖI ==="
echo "Hệ thống đã được cài đặt lại với các phiên bản tương thích!"