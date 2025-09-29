## GIẢI PHÁP KHẮC PHỤC:
### Bước 1: Cài đặt kernel modules
```
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt kernel headers
sudo apt install raspberrypi-kernel-headers 
-y

# Cài đặt build tools
sudo apt install build-essential -y
```
### Bước 2: Kiểm tra kernel modules có sẵn
```
# Tìm module camera
find /lib/modules/$(uname -r) -name "*uvc*"
find /lib/modules/$(uname -r) -name 
"*video*"

# Liệt kê tất cả modules có sẵn
lsmod | grep video
```
### Bước 3: Thử các lệnh thay thế
```
# Thử tải module bằng cách khác
sudo insmod /lib/modules/$(uname -r)/kernel/
drivers/media/usb/uvc/uvcvideo.ko

Builder

Tôi thấy vấn đề nghiêm trọng! Hệ thống Raspberry Pi của bạn có vấn đề với package manager . Tất cả các lệnh apt đều báo lỗi "command not found" .

## 🚨 VẤN ĐỀ CHÍNH:
- APT package manager không hoạt động
- Hệ thống có thể bị hỏng hoặc thiếu PATH
- Không thể cài đặt package mới
## 🔧 GIẢI PHÁP KHẨN CẤP:
### Bước 1: Kiểm tra PATH và APT
```
# Kiểm tra PATH
echo $PATH

# Tìm apt
which apt
whereis apt

# Thử đường dẫn đầy đủ
/usr/bin/apt --version
```
### Bước 2: Khôi phục PATH
```
# Khôi phục PATH mặc định
export PATH="/usr/local/sbin:/usr/local/
bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Thử lại apt
apt --version
```
### Bước 3: Sử dụng dpkg thay thế
```
# Kiểm tra packages đã cài
dpkg -l | grep python

# Cài đặt bằng dpkg (nếu có file .deb)
ls /var/cache/apt/archives/
```
## 🎯 GIẢI PHÁP NHANH:
### Thử ngay các lệnh này:
```
# 1. Kiểm tra hệ thống
uname -a
cat /etc/os-release

# 2. Thử khôi phục apt
sudo /usr/bin/apt update

# 3. Kiểm tra camera trực tiếp
lsusb
dmesg | grep -i usb

# 4. Tìm thiết bị video
find /dev -name "video*" 2>/dev/null
```
## 🔄 NẾU VẪN LỖI:
### Khởi động lại hệ thống:
```
sudo reboot
```
### Hoặc thử chạy script khắc phục:
```
# Nếu có file script
bash fix_camera_raspberry_pi.sh

# Hoặc chạy Python trực tiếp
python3 test_camera_simple.py
```
## 💡 LƯU Ý:

# Hoặc kiểm tra module có sẵn
modinfo uvcvideo
```
### Bước 4: Cài đặt driver camera từ package
```
# Cài đặt gói driver camera
sudo apt install linux-modules-extra-$
(uname -r) -y

# Cài đặt firmware camera
sudo apt install firmware-misc-nonfree -y
```
## 🎯 GIẢI PHÁP NHANH:
### Thử ngay lệnh này:
```
# Kiểm tra camera USB trực tiếp
lsusb | grep -i camera

# Nếu có camera, thử khởi động lại
sudo reboot

# Sau khi khởi động lại, kiểm tra
ls -la /dev/video*
```
## 💡 LƯU Ý:
