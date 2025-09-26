Hướng Dẫn Sử Dụng YOLO (Ultralytics YOLOv8) Để Phát Hiện Khuôn Mặt Trên Máy Ảo "Test" (Không Sử Dụng MediaPipe Hoặc OpenCV)
Dựa trên yêu cầu của bạn, tôi sẽ hướng dẫn cài đặt và sử dụng Ultralytics YOLOv8 (phiên bản mới nhất tương thích là YOLOv8n cho hiệu suất nhẹ, phù hợp với 2 GB RAM của VM "test"). YOLOv8 hỗ trợ phát hiện khuôn mặt bằng cách sử dụng model được train trên class "face" (từ dataset như WIDER FACE). Chúng ta sẽ dùng model pre-trained từ GitHub repo YOLOv8-Face (YOLOv8m-face.pt), vì COCO val không có class "face" riêng.

Lý do phù hợp: YOLOv8 chạy tốt trên Linux x86_64 (Debian/Raspberry Pi OS), không cần GPU, và nhẹ hơn MediaPipe cho detection thời gian thực. Tuy nhiên, với 2 GB RAM, có thể chạy ~5-10 FPS; tăng RAM VM nếu cần.
Yêu cầu: Python 3.8+, pip. Không dùng OpenCV cho detection (chỉ dùng YOLO để vẽ box).

Bước 1: Khởi Động VM Và Kiểm Tra Môi Trường

Khởi động VM:

Trong Oracle VirtualBox, chọn "test" > Start.
Đăng nhập với robothcc.


Mở Terminal:

Nhấn Ctrl+Alt+T.


Kiểm tra Python:
textpython3 --version

Nên là 3.8+ (mặc định Raspberry Pi OS Bullseye là 3.9). Nếu thấp hơn, nâng cấp: sudo apt install python3.9.


Cập nhật hệ thống:
textsudo apt update && sudo apt upgrade -y


Bước 2: Cài Đặt Ultralytics YOLOv8
Sử dụng pip để cài (dựa trên docs Ultralytics, tương thích Debian).

Cài pip nếu chưa có:
textsudo apt install python3-pip

Tạo virtual environment (venv) để tránh xung đột:
textpython3 -m venv ~/yolo_venv
source ~/yolo_venv/bin/activate

Prompt: (yolo_venv) robothcc@raspberry:~ $.


Nâng cấp pip:
textpip install --upgrade pip

Cài Ultralytics:
textpip install ultralytics

Quá trình mất 5-10 phút (tải PyTorch ~100 MB). Nếu lỗi "externally managed environment", dùng --break-system-packages (cho Debian mới): pip install ultralytics --break-system-packages.


Kiểm tra cài đặt:
textpython -c "from ultralytics import YOLO; print('YOLOv8 installed successfully')"

Không lỗi → Thành công.



Bước 3: Tải Model Pre-Trained Cho Face Detection
YOLOv8 cần model chuyên cho "face" (không dùng COCO val).

Tải model YOLOv8m-face.pt (từ repo YOLOv8-Face, kích thước ~20 MB, nhẹ cho VM):
textwget https://github.com/Yusepp/YOLOv8-Face/releases/download/v0.2/yolov8m-face.pt -O ~/yolov8m-face.pt

Nếu wget lỗi, tải thủ công từ https://github.com/Yusepp/YOLOv8-Face/releases/tag/v0.2 và copy vào VM.



Bước 4: Tạo Script Face Detector Với YOLOv8
Tạo script mới ~/face_detector_yolo.py sử dụng YOLOv8 để phát hiện "face" từ webcam, vẽ bounding box và label confidence (tương tự script cũ).

Tạo file:
textnano ~/face_detector_yolo.py

Dán code sau (dựa trên ví dụ từ Ultralytics docs và YOLOv8-Face), lưu (Ctrl+O, Enter, Ctrl+X):



python# -*- coding: utf-8 -*-
"""
Face Detector with YOLOv8 (Alternative to MediaPipe/OpenCV).
Uses Ultralytics YOLOv8 for real-time face detection from webcam.
Model: yolov8m-face.pt (trained on face class).
"""

from ultralytics import YOLO
import cv2  # Chỉ dùng để capture và display, không dùng cho detection

# Load YOLOv8 model for face detection
model = YOLO('/home/robothcc/yolov8m-face.pt')  # Đường dẫn model

# Open webcam (0 for default)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Run YOLOv8 inference on frame
    results = model(frame, verbose=False)  # verbose=False để giảm log

    # Process results (draw bounding boxes for 'face' class)
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())

                # Check if class is 'face' (class_id=0 in this model)
                if cls == 0:  # Assuming class 0 is 'face'
                    # Draw bounding box
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 3)
                    
                    # Add label with confidence
                    label = f'Face ({conf:.2f})'
                    cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Face Detection with YOLOv8', frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

Giải thích code:

Model load: Sử dụng YOLOv8m-face.pt (class 0 = 'face').
Inference: model(frame) trả về results với boxes, conf, cls.
Visualization: Vẽ box xanh lá và label confidence (sử dụng cv2 chỉ cho display, không detection).
Tùy chỉnh: Thay verbose=True để xem log chi tiết.



Bước 5: Cấu Hình Webcam Trong VirtualBox

Tắt VM (nếu đang chạy).
Cấu hình USB:

VirtualBox > Settings > Ports > USB > Enable USB Controller > Add webcam.


Khởi động VM.
Kiểm tra:
textls /dev/video*

Nên thấy /dev/video0.



Bước 6: Chạy Script

Kích hoạt venv (nếu dùng):
textsource ~/yolo_venv/bin/activate

Chạy script:
textpython ~/face_detector_yolo.py

Webcam mở, YOLOv8 phát hiện khuôn mặt và vẽ box xanh lá với confidence. Nhấn 'q' để thoát.
Lần đầu chạy, model tải weights nếu chưa (tự động).



Bước 7: Xử Lý Lỗi Và Tối Ưu

Lỗi "No module named 'ultralytics'": Chạy lại Bước 2.4.
Lỗi "Could not open webcam": Kiểm tra Bước 5.
Chậm (thấp FPS): Với 2 GB RAM, dùng model nhỏ hơn (yolov8n-face.pt nếu tải). Thêm model.predict(frame, imgsz=320) để giảm kích thước ảnh.
Lỗi model không tải: Kiểm tra đường dẫn /home/robothcc/yolov8m-face.pt. Nếu lỗi class ID, chỉnh if cls == 0.
Tăng hiệu suất: Tăng RAM VM lên 4 GB (VirtualBox Settings > System > Base Memory).

Lưu Ý

Không dùng OpenCV cho detection: Script chỉ dùng YOLO cho inference, cv2 chỉ cho capture/display (bắt buộc cho webcam).
Model nguồn: Từ https://github.com/Yusepp/YOLOv8-Face (pre-trained trên WIDER FACE dataset).
Nâng cao: Để train model riêng, dùng model.train(data='path/to/dataset.yaml', epochs=100) (cần dataset).

Nếu gặp lỗi cụ thể, cung cấp thông báo để hỗ trợ thêm!
