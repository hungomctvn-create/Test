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
