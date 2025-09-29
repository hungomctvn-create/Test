#!/bin/bash

# Script khắc phục lỗi camera trên Raspberry Pi
echo "========================================"
echo "  KHẮC PHỤC LỖI CAMERA RASPBERRY PI"
echo "========================================"

echo "🔧 Bước 1: Kiểm tra camera hiện có..."
ls -la /dev/video*
echo

echo "🔧 Bước 2: Kiểm tra USB camera..."
lsusb | grep -i camera
lsusb | grep -i video
echo

echo "🔧 Bước 3: Cài đặt driver camera..."
sudo apt update
sudo apt install -y v4l-utils
sudo apt install -y fswebcam
sudo apt install -y guvcview

echo "🔧 Bước 4: Kiểm tra thông tin camera..."
v4l2-ctl --list-devices
echo

echo "🔧 Bước 5: Test camera với fswebcam..."
fswebcam -d /dev/video0 --no-banner -r 640x480 test_camera.jpg 2>/dev/null && echo "✓ Camera /dev/video0 hoạt động" || echo "✗ Camera /dev/video0 lỗi"

echo "🔧 Bước 6: Thử các video device khác..."
for i in {0..4}; do
    if [ -e "/dev/video$i" ]; then
        echo "Thử camera /dev/video$i..."
        timeout 3s fswebcam -d /dev/video$i --no-banner -r 320x240 test$i.jpg 2>/dev/null && echo "✓ /dev/video$i OK" || echo "✗ /dev/video$i không hoạt động"
    fi
done

echo
echo "🔧 Bước 7: Cấu hình quyền truy cập camera..."
sudo usermod -a -G video $USER
echo "✓ Đã thêm user vào group video"

echo
echo "🔧 Bước 8: Khởi động lại service camera..."
sudo modprobe uvcvideo
sudo systemctl restart systemd-udevd

echo
echo "========================================"
echo "  HOÀN THÀNH KHẮC PHỤC CAMERA"
echo "========================================"
echo "📝 Ghi chú:"
echo "- Nếu vẫn lỗi, hãy khởi động lại Raspberry Pi"
echo "- Kiểm tra kết nối USB camera"
echo "- Thử sử dụng camera index khác (0,1,2...)"
echo