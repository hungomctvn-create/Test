import cv2
import numpy as np
from gtts import gTTS
import pygame
import time
import os
import threading
import urllib.request

# Biến toàn cục để theo dõi trạng thái
is_speaking = False
face_detected = False
program_running = True

# Khởi tạo YOLO với OpenCV (thay thế Ultralytics)
class YOLODetector:
    def __init__(self):
        self.net = None
        self.output_layers = []
        self.classes = []
        self.load_yolo_model()
    
    def download_yolo_files(self):
        """Tải các file YOLO cần thiết"""
        files = {
            "yolov3.cfg": "https://github.com/pjreddie/darknet/raw/master/cfg/yolov3.cfg",
            "coco.names": "https://github.com/pjreddie/darknet/raw/master/data/coco.names"
        }
        
        print("Đang tải các file YOLO...")
        for filename, url in files.items():
            if not os.path.exists(filename):
                print(f"Đang tải {filename}...")
                urllib.request.urlretrieve(url, filename)
        
        # Tải weights (file lớn)
        if not os.path.exists("yolov3.weights"):
            print("Đang tải yolov3.weights (248MB)...")
            weights_url = "https://pjreddie.com/media/files/yolov3.weights"
            urllib.request.urlretrieve(weights_url, "yolov3.weights")
    
    def load_yolo_model(self):
        """Tải mô hình YOLO"""
        try:
            # Kiểm tra và tải file nếu cần
            if not all(os.path.exists(f) for f in ["yolov3.weights", "yolov3.cfg", "coco.names"]):
                self.download_yolo_files()
            
            # Tải mạng YOLO
            self.net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
            
            # Lấy tên các layer
            layer_names = self.net.getLayerNames()
            self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
            
            # Tải danh sách classes
            with open("coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
            
            print("Mô hình YOLO đã được tải thành công!")
            return True
        except Exception as e:
            print(f"Lỗi khi tải mô hình YOLO: {e}")
            return False
    
    def detect_people(self, frame):
        """Phát hiện người trong frame"""
        if self.net is None:
            return []
        
        height, width, channels = frame.shape
        
        # Chuẩn bị input cho YOLO
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        
        # Chạy forward pass
        outs = self.net.forward(self.output_layers)
        
        # Xử lý kết quả
        people_boxes = []
        confidences = []
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Class 0 là 'person' trong COCO dataset
                if class_id == 0 and confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    people_boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
        
        # Áp dụng Non-Maximum Suppression
        if people_boxes:
            indexes = cv2.dnn.NMSBoxes(people_boxes, confidences, 0.5, 0.4)
            if len(indexes) > 0:
                return [people_boxes[i] for i in indexes.flatten()]
        
        return []

# Khởi tạo detector
yolo_detector = YOLODetector()

def check_camera_devices():
    """Kiểm tra các thiết bị camera có sẵn"""
    available_cameras = []
    for i in range(5):  # Kiểm tra 5 thiết bị đầu tiên
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

def initialize_camera(camera_id=0):  # Thay đổi từ 1 thành 0
    """Khởi tạo camera với ID cụ thể"""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        available_cameras = check_camera_devices()
        if available_cameras:
            print(f"Không thể mở camera {camera_id}. Các camera có sẵn: {available_cameras}")
            print(f"Thử mở camera {available_cameras[0]}...")
            cap = cv2.VideoCapture(available_cameras[0])
        else:
            print("Lỗi: Không tìm thấy camera nào. Kiểm tra kết nối USB hoặc driver.")
            print("💡 HƯỚNG DẪN KHẮC PHỤC:")
            print("1. Kiểm tra USB camera đã cắm chưa: lsusb | grep -i camera")
            print("2. Cài đặt v4l2loopback: sudo apt install v4l2loopback-dkms")
            print("3. Tạo virtual camera: sudo modprobe v4l2loopback devices=1")
            print("4. Kiểm tra devices: ls -la /dev/video*")
            return None
    
    # Đặt độ phân giải (tùy chọn, giảm tải cho RPi)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap

# Hàm tạo và phát âm thanh chào
def speak_greeting():
    global is_speaking
    try:
        is_speaking = True
        text = "Xin chào! Rất vui được gặp bạn!"
        tts = gTTS(text=text, lang='vi')
        
        # Đảm bảo thư mục tạm tồn tại
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Lưu file vào thư mục tạm
        greeting_file = os.path.join(temp_dir, "greeting.mp3")
        tts.save(greeting_file)
        
        # Phát âm thanh
        pygame.mixer.init()
        pygame.mixer.music.load(greeting_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        
        # Xóa file tạm sau khi phát xong
        if os.path.exists(greeting_file):
            os.remove(greeting_file)
            
        is_speaking = False
    except Exception as e:
        print(f"Lỗi khi tạo hoặc phát âm thanh: {e}")
        is_speaking = False

def speak_in_thread():
    """Phát âm thanh trong một luồng riêng biệt"""
    if not is_speaking:
        threading.Thread(target=speak_greeting, daemon=True).start()

def draw_status(frame, fps=0):
    """Hiển thị trạng thái trên khung hình"""
    # Vẽ nền cho văn bản trạng thái
    cv2.rectangle(frame, (10, 10), (300, 110), (0, 0, 0), -1)
    
    # Hiển thị trạng thái khuôn mặt
    face_status = "Đã phát hiện khuôn mặt" if face_detected else "Không phát hiện khuôn mặt"
    face_color = (0, 255, 0) if face_detected else (0, 0, 255)
    cv2.putText(frame, face_status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, face_color, 2)
    
    # Hiển thị trạng thái âm thanh
    speak_status = "Đang phát âm thanh" if is_speaking else "Sẵn sàng chào"
    speak_color = (255, 165, 0) if is_speaking else (255, 255, 255)
    cv2.putText(frame, speak_status, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, speak_color, 2)
    
    # Hiển thị FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # Hiển thị hướng dẫn
    cv2.putText(frame, "Nhấn 'q' để thoát", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def main():
    global face_detected, program_running
    
    print("Đang khởi tạo hệ thống nhận dạng người...")
    
    # Khởi tạo camera
    cap = initialize_camera()
    if cap is None:
        print("Không thể khởi tạo camera. Thoát chương trình.")
        return
    
    print("Camera đã sẵn sàng. Nhấn 'q' để thoát.")
    
    # Biến đếm FPS
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0
    
    # Biến theo dõi thời gian phát hiện cuối cùng
    last_detection_time = 0
    detection_cooldown = 3  # 3 giây giữa các lần chào
    
    while program_running:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình từ camera.")
            break
        
        # Lật khung hình theo chiều ngang (tùy chọn)
        frame = cv2.flip(frame, 1)
        
        # Phát hiện người trong khung hình
        people_boxes = yolo_detector.detect_people(frame)
        
        # Cập nhật trạng thái phát hiện
        current_time = time.time()
        if people_boxes:
            face_detected = True
            
            # Vẽ bounding box cho mỗi người được phát hiện
            for box in people_boxes:
                x, y, w, h = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Person", (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Phát âm thanh chào nếu đã đủ thời gian cooldown
            if (current_time - last_detection_time) > detection_cooldown:
                speak_in_thread()
                last_detection_time = current_time
        else:
            face_detected = False
        
        # Tính toán FPS
        fps_counter += 1
        if fps_counter >= 30:  # Cập nhật FPS mỗi 30 khung hình
            fps_end_time = time.time()
            current_fps = fps_counter / (fps_end_time - fps_start_time)
            fps_counter = 0
            fps_start_time = fps_end_time
        
        # Vẽ thông tin trạng thái
        draw_status(frame, current_fps)
        
        # Hiển thị khung hình
        cv2.imshow('Nhận dạng người - YOLO', frame)
        
        # Kiểm tra phím bấm
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            program_running = False
            break
    
    # Dọn dẹp
    cap.release()
    cv2.destroyAllWindows()
    print("Chương trình đã kết thúc.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nChương trình bị ngắt bởi người dùng.")
        program_running = False
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        cv2.destroyAllWindows()