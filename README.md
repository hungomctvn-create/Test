### Bước 1: Kiểm tra kết nối USB camera
```
# Kiểm tra thiết bị USB
lsusb

# Tìm camera USB
lsusb | grep -i camera
lsusb | grep -i video
```
### Bước 2: Cắm lại camera và kiểm tra
```
# Sau khi cắm lại camera USB
dmesg | tail -20

# Kiểm tra lại thiết bị video
ls -la /dev/video*
```
### Bước 3: Tải driver camera
```
# Tải driver UVC (USB Video Class)
sudo modprobe uvcvideo

# Kiểm tra driver đã tải
lsmod | grep uvc
```
### Bước 4: Test camera sau khi cắm
```
# Chạy script test camera
python3 test_camera_simple.py

# Hoặc test thủ công
v4l2-ctl --list-devices
```
## 💡 GỢI Ý:
