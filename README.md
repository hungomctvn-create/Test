# Triển khai Camera + AI nhận diện CCCD trên Raspberry Pi 5 (Debian Trixie arm64)

Tài liệu này chỉ hướng dẫn cài đặt và chạy trên Raspberry Pi 5 dùng Debian Trixie arm64. Mục tiêu: dùng Pi Camera/USB webcam với YOLOv5 để phát hiện thẻ CCCD trên mặt kính và tự động chụp ảnh.

## Yêu cầu môi trường
- Thiết bị: Raspberry Pi 5 (RAM 4GB+ khuyến nghị)
- Hệ điều hành: Debian Trixie arm64
- Camera: Pi Camera Module V2/V3 (khuyến nghị) hoặc webcam USB
- Phụ kiện: Giá đỡ CCCD bằng mặt kính trong suốt (< 2 mm), đèn LED vòng để ánh sáng đều
- Nguồn: 5V/3A

## Cài đặt hệ thống (Debian Trixie arm64)
1) Cập nhật hệ thống và cài gói cơ bản:
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-opencv libatlas-base-dev libcamera-apps
```
2) Cài Picamera2 (nếu có sẵn trong kho Debian/Raspberry Pi):
```
sudo apt install -y python3-picamera2
```
3) Kiểm tra camera hoạt động với libcamera:
```
libcamera-hello -t 2000
```
- Nếu không thấy hình, kiểm tra `/boot/firmware/config.txt` có `camera_auto_detect=1`. Nếu chỉnh sửa, hãy reboot.

## Cài PyTorch CPU và YOLOv5
- Cài PyTorch CPU (dùng chỉ mục CPU của PyTorch, bản dành cho arm64 nếu có):
```
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
```
- Cài đặt code YOLOv5 (khuyến nghị clone repo để train):
```
sudo apt install -y git
git clone https://github.com/ultralytics/yolov5.git /home/pi/yolov5
cd /home/pi/yolov5
pip3 install -r requirements.txt
```

## Chuẩn bị dataset
- Tạo thư mục dataset:
```
mkdir -p /home/pi/dataset/images/train /home/pi/dataset/images/val
```
- Chụp nhanh 100–200 ảnh CCCD bằng PiCamera2:
```
DATASET_DIR=/home/pi/dataset/images/train COUNT=200 python3 scripts/capture_dataset.py
```
- Gợi ý: chụp ở nhiều góc/ khoảng cách/ điều kiện sáng, giữ chuẩn thẻ 3×4 cm trong khung.

## Gắn nhãn (Labeling)
- Cài LabelImg và gắn nhãn vùng CCCD theo định dạng YOLO:
```
pip3 install labelImg
labelImg /home/pi/dataset/images/train
```
- Sử dụng class duy nhất `cccd` với `class_id = 0`. Chia 80% train, 20% val.

## Cấu hình YOLOv5
- Sao chép cấu hình `cccd.yaml` vào repo YOLOv5:
```
cp /path/to/project/yolov5/data/cccd.yaml /home/pi/yolov5/data/cccd.yaml
```
- Nội dung tham chiếu:
```
train: /home/pi/dataset/images/train
val: /home/pi/dataset/images/val
nc: 1
names: ['cccd']
```

## Train mô hình
- Tải trọng số nhẹ `yolov5n` và train trên CPU của Pi 5:
```
cd /home/pi/yolov5
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
python3 train.py --img 640 --batch 16 --epochs 50 \
  --data /home/pi/yolov5/data/cccd.yaml --weights yolov5n.pt --device cpu
```
- Kết quả tốt nhất lưu tại: `/home/pi/yolov5/runs/train/exp/weights/best.pt`.

## Chạy nhận diện và tự động chụp ảnh
- Tạo thư mục lưu ảnh chụp:
```
mkdir -p /home/pi/cccd_photos
```
- Chạy chương trình:
```
MODEL_PATH=/home/pi/yolov5/runs/train/exp/weights/best.pt \
SAVE_DIR=/home/pi/cccd_photos \
python3 scripts/camera_cccd.py
```
- Luồng hoạt động:
  - Ưu tiên dùng `Picamera2`; nếu không khả dụng, fallback sang webcam USB (OpenCV).
  - Khi phát hiện `cccd` (class 0) với `CONF_THRESH` đạt ngưỡng, chụp và lưu ảnh vào `SAVE_DIR`.
  - Có “cooldown” 5 giây để tránh chụp liên tục.

### Biến môi trường tùy chỉnh
- `MODEL_PATH`: đường dẫn trọng số `.pt` (mặc định `/home/pi/yolov5/runs/train/exp/weights/best.pt`).
- `SAVE_DIR`: thư mục lưu ảnh (mặc định `/home/pi/cccd_photos`).
- `CONF_THRESH`: ngưỡng tin cậy (mặc định `0.5`).
- `CLASS_ID`: lớp cần phát hiện (mặc định `0` cho `cccd`).

## Khắc phục sự cố
- Picamera2 lỗi: đảm bảo đã cài `python3-picamera2` và kiểm tra `libcamera-hello`. Kiểm tra cấp nguồn đủ ổn định.
- Cài `torch` thất bại: kiểm tra dung lượng bộ nhớ swap, và chỉ mục CPU dành cho arm64.
- Hiệu năng thấp: dùng mô hình `yolov5n`, hạ `--img`, tăng `CONF_THRESH`.
- Không chụp ảnh: kiểm tra quyền ghi tại `SAVE_DIR` và đúng `CLASS_ID`.