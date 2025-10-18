# Giải pháp Camera + AI nhận diện CCCD trên mặt kính (Raspberry Pi + YOLOv5)

Tài liệu này hướng dẫn triển khai hoàn chỉnh: chuẩn bị phần cứng, cài phần mềm, thu thập dataset, train YOLOv5, và chạy nhận diện để tự động chụp ảnh CCCD khi xuất hiện trên mặt kính.

## Cấu trúc thư mục dự án

```
Camera và AI đọc CCCD/
├─ README.md
├─ requirements.txt
├─ scripts/
│  ├─ capture_dataset.py      # Chụp dataset bằng PiCamera2
│  └─ camera_cccd.py          # Nhận diện CCCD và tự động chụp ảnh
└─ yolov5/
   └─ data/
      └─ cccd.yaml            # Cấu hình dataset cho YOLOv5
```

## Phần cứng khuyến nghị
- Raspberry Pi 4/5 (RAM 4GB+ khuyến nghị)
- Pi Camera Module V2/V3 hoặc webcam USB
- Giá đỡ CCCD bằng mặt kính trong suốt (dày < 2 mm) với đèn LED vòng để ánh sáng đều
- Nguồn điện 5V/3A cho Pi

## Cài đặt phần mềm trên Raspberry Pi
1) Cài Raspberry Pi OS (Desktop, 64-bit khuyến nghị)
2) Cập nhật hệ thống và cài gói cơ bản
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-opencv libatlas-base-dev
```
3) Bật camera (PiCamera2/libcamera)
```
sudo raspi-config
# Interface Options > Camera > Enable > Reboot
```
4) Cài Picamera2 (khuyến nghị qua apt)
```
sudo apt install -y python3-picamera2
```
5) Cài PyTorch CPU và YOLOv5
- Cài PyTorch CPU (Pi không có GPU, dùng chỉ mục CPU của PyTorch):
```
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
```
- Cài YOLOv5 (gói Python):
```
pip3 install yolov5
```
Lưu ý: Nếu cài `picamera2` qua pip không thành công, hãy dùng `sudo apt install -y python3-picamera2` như ở bước 4.

## Chuẩn bị dataset (chụp ảnh CCCD)
- Mục tiêu: 100–200 ảnh CCCD trên mặt kính, ánh sáng đều, nhiều góc, nhiều khoảng cách (giữ chuẩn thẻ 3x4 cm trong khung).
- Tạo thư mục dataset:
```
mkdir -p ~/dataset/images/train ~/dataset/images/val
```
- Dùng script chụp nhanh (PiCamera2):
```
python3 scripts/capture_dataset.py
```
Script mặc định lưu 100 ảnh vào `~/dataset/images/train`. Có thể đổi số lượng và thư mục bằng biến môi trường:
```
DATASET_DIR=~/dataset/images/train COUNT=200 python3 scripts/capture_dataset.py
```

## Gắn nhãn (labeling)
- Cài LabelImg và gắn nhãn vùng CCCD trong ảnh:
```
pip3 install labelImg
labelImg ~/dataset/images/train
```
- Lưu định dạng YOLO (`.txt`) với class duy nhất: `cccd` (class_id: 0).
- Chia dataset: 80% vào `dataset/images/train`, 20% vào `dataset/images/val`.

## Cấu hình YOLOv5 cho dataset
Tệp `yolov5/data/cccd.yaml` (đã tạo sẵn) có nội dung:
```
train: /home/pi/dataset/images/train
val: /home/pi/dataset/images/val
nc: 1
names: ['cccd']
```
Điều chỉnh đường dẫn nếu dataset của bạn ở vị trí khác.

## Tải mô hình pre-trained nhẹ (yolov5n) và train
- Tải trọng số nhẹ:
```
cd ~/yolov5
wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.pt
```
- Train trên Raspberry Pi (hoặc train trên PC có GPU rồi copy `best.pt` sang Pi):
```
cd ~/yolov5
python3 train.py --img 640 --batch 16 --epochs 50 \
  --data /home/pi/yolov5/data/cccd.yaml --weights yolov5n.pt --device cpu
```
Kết quả tốt nhất lưu tại: `yolov5/runs/train/exp/weights/best.pt`.

## Chạy nhận diện và tự động chụp ảnh
- Đặt đường dẫn MODEL (trọng số đã train): ví dụ `/home/pi/yolov5/runs/train/exp/weights/best.pt`.
- Tạo thư mục lưu ảnh chụp: `/home/pi/cccd_photos`.
- Chạy chương trình:
```
MODEL_PATH=/home/pi/yolov5/runs/train/exp/weights/best.pt \
SAVE_DIR=/home/pi/cccd_photos \
python3 scripts/camera_cccd.py
```
Chương trình sẽ:
- Khởi tạo PiCamera2 (hoặc tự động fallback sang webcam USB nếu không có PiCamera2)
- Chạy YOLOv5 để phát hiện CCCD (class 0)
- Khi phát hiện hợp lệ, chụp ảnh và lưu với tên thời gian vào `SAVE_DIR`
- Có cơ chế “cooldown” 5 giây để tránh chụp liên tục

### Tham số/biến môi trường tùy chỉnh
- `MODEL_PATH`: đường dẫn tới file `.pt` (mặc định: `/home/pi/yolov5/runs/train/exp/weights/best.pt`)
- `SAVE_DIR`: thư mục lưu ảnh chụp (mặc định: `/home/pi/cccd_photos`)
- `CONF_THRESH`: ngưỡng tin cậy (mặc định: `0.5`)
- `CLASS_ID`: lớp cần phát hiện (mặc định: `0` cho `cccd`)

## Khắc phục sự cố
- Picamera2 không hoạt động: đảm bảo đã bật camera trong `raspi-config` và đã cài `python3-picamera2` qua apt. Nếu vẫn lỗi, script sẽ fallback sang webcam USB (OpenCV).
- Cài `torch` thất bại: dùng chỉ mục CPU của PyTorch như lệnh ở trên. Đảm bảo đủ bộ nhớ swap với Pi 4/5 khi build wheel.
- Hiệu năng thấp: dùng mô hình nhẹ `yolov5n`, giảm `img` hoặc tăng `CONF_THRESH`.
- Không chụp ảnh: kiểm tra quyền ghi thư mục `SAVE_DIR` và rằng class id trong mô hình đúng là `0`.

## Chạy thử trên Windows/PC
- Có thể chạy `scripts/camera_cccd.py` với webcam USB để thử luồng logic (dùng OpenCV, không có Picamera2).
- Cài phụ thuộc từ `requirements.txt` (trên PC):
```
pip install -r requirements.txt
```
- Đặt `MODEL_PATH` tới trọng số `.pt` tương thích YOLOv5.

---
Nếu bạn cần tự động khởi chạy khi bật Pi (systemd service) hoặc xuất log, mình có thể bổ sung cấu hình ngay sau khi bạn xác nhận hoạt động cơ bản OK.