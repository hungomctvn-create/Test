#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO Object Detection với OpenCV - Thay thế Ultralytics
Phiên bản tối ưu cho Raspberry Pi
"""

import cv2
import numpy as np
import time
import os
import urllib.request
from gtts import gTTS
import pygame
import threading

class YOLODetector:
    def __init__(self):
        self.net = None
        self.output_layers = []
        self.classes = []
        self.colors = []
        
        # Khởi tạo pygame mixer
        pygame.mixer.init()
        
        # Tải mô hình YOLO
        self.load_yolo_model()
    
    def download_yolo_files(self):
        """Tải các file YOLO cần thiết"""
        base_url = "https://github.com/pjreddie/darknet/raw/master/"
        files = {
            "yolov3.cfg": base_url + "cfg/yolov3.cfg",
            "coco.names": base_url + "data/coco.names"
        }
        
        weights_url = "https://pjreddie.com/media/files/yolov3.weights"
        
        print("Đang tải các file YOLO...")
        
        # Tải config và names
        for filename, url in files.items():
            if not os.path.exists(filename):
                print(f"Đang tải {filename}...")
                urllib.request.urlretrieve(url, filename)
        
        # Tải weights (file lớn)
        if not os.path.exists("yolov3.weights"):
            print("Đang tải yolov3.weights (248MB)...")
            print("Quá trình này có thể mất vài phút...")
            urllib.request.urlretrieve(weights_url, "yolov3.weights")
        
        print("Hoàn thành tải file!")
    
    def load_yolo_model(self):
        """Tải mô hình YOLO"""
        try:
            # Kiểm tra và tải file nếu cần
            if not all(os.path.exists(f) for f in ["yolov3.weights", "yolov3.cfg", "coco.names"]):
                self.download_yolo_files()
            
            # Tải mạng YOLO
            print("Đang tải mô hình YOLO...")
            self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
            
            # Lấy tên các layer
            layer_names = self.net.getLayerNames()
            self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            
            # Tải danh sách classes
            with open("coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
            
            # Tạo màu ngẫu nhiên cho mỗi class
            self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
            
            print("Mô hình YOLO đã được tải thành công!")
            
        except Exception as e:
            print(f"Lỗi khi tải mô hình YOLO: {e}")
            return False
        
        return True
    
    def detect_objects(self, frame):
        """Phát hiện đối tượng trong frame"""
        if self.net is None:
            return frame, []
        
        height, width, channels = frame.shape
        
        # Chuẩn bị input cho YOLO
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        
        # Chạy forward pass
        outs = self.net.forward(self.output_layers)
        
        # Xử lý kết quả
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # Ngưỡng confidence
                    # Tọa độ đối tượng
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Tọa độ góc trên trái
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Áp dụng Non-Maximum Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        detected_objects = []
        
        # Vẽ bounding boxes
        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                color = self.colors[class_ids[i]]
                
                # Vẽ bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Vẽ label
                label_text = f"{label} {confidence:.2f}"
                cv2.putText(frame, label_text, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                detected_objects.append({
                    'class': label,
                    'confidence': confidence,
                    'box': [x, y, w, h]
                })
        
        return frame, detected_objects
    
    def speak_vietnamese(self, text):
        """Phát âm thanh tiếng Việt"""
        def play_audio():
            try:
                tts = gTTS(text=text, lang='vi', slow=False)
                temp_file = "temp_audio.mp3"
                tts.save(temp_file)
                
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                os.remove(temp_file)
            except Exception as e:
                print(f"Lỗi phát âm thanh: {e}")
        
        threading.Thread(target=play_audio, daemon=True).start()

def main():
    """Hàm chính"""
    print("=== YOLO Object Detection với OpenCV ===")
    
    # Khởi tạo detector
    detector = YOLODetector()
    
    # Mở camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera!")
        return
    
    # Thiết lập camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Nhấn 'q' để thoát, 's' để chụp ảnh")
    
    frame_count = 0
    start_time = time.time()
    last_detection_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc frame từ camera!")
            break
        
        frame_count += 1
        
        # Chỉ detect mỗi 10 frame để tăng tốc độ
        if frame_count % 10 == 0:
            frame, detected_objects = detector.detect_objects(frame)
            
            # Thông báo âm thanh khi phát hiện người
            current_time = time.time()
            if detected_objects and (current_time - last_detection_time) > 5:  # 5 giây một lần
                people_count = sum(1 for obj in detected_objects if obj['class'] == 'person')
                if people_count > 0:
                    detector.speak_vietnamese(f"Phát hiện {people_count} người")
                    last_detection_time = current_time
        
        # Tính FPS
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        # Hiển thị thông tin
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Objects: {len(detected_objects) if 'detected_objects' in locals() else 0}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Hiển thị frame
        cv2.imshow('YOLO Object Detection', frame)
        
        # Xử lý phím bấm
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Chụp ảnh
            filename = f"capture_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Đã lưu ảnh: {filename}")
    
    # Dọn dẹp
    cap.release()
    cv2.destroyAllWindows()
    print("Chương trình đã kết thúc!")

if __name__ == "__main__":
    main()