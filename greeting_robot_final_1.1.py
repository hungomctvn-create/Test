import cv2
import mediapipe as mp
from gtts import gTTS
import pygame
import time
import os

# Khởi tạo Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Khởi tạo webcam USB tại /dev/video1
cap = cv2.VideoCapture(1)  # Sử dụng /dev/video1 (webcam USB)
if not cap.isOpened():
    print("Lỗi: Không thể mở webcam. Kiểm tra kết nối USB hoặc driver.")
    print("Kiểm tra thiết bị: ls /dev/video*")
    exit()

# Đặt độ phân giải (tùy chọn, giảm tải cho RPi)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_greet_time = 0
greet_interval = 5  # Thời gian chờ giữa các lần chào (giây)

# Hàm tạo và phát âm thanh chào
def speak_greeting():
    try:
        text = "Xin chào! Rất vui được gặp bạn!"
        tts = gTTS(text=text, lang='vi')
        tts.save("greeting.mp3")
        
        pygame.mixer.init()
        pygame.mixer.music.load("greeting.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove("greeting.mp3")  # Xóa file tạm
    except Exception as e:
        print(f"Lỗi khi tạo hoặc phát âm thanh: {e}")

# Vòng lặp chính
try:
    print("Chương trình đang chạy. Đặt khuôn mặt trước webcam...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Lỗi: Không thể đọc từ webcam")
            break

        # Chuyển đổi sang RGB (Mediapipe yêu cầu)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                # Vẽ hình chữ nhật quanh khuôn mặt
                mp_drawing.draw_detection(frame, detection)
                print(f"Phát hiện khuôn mặt! Đang chào...")

                current_time = time.time()
                if (current_time - last_greet_time) > greet_interval:
                    speak_greeting()
                    last_greet_time = current_time

        cv2.imshow('Webcam - Greeting Robot', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Đã dừng chương trình bởi người dùng (Ctrl+C)")

cap.release()
cv2.destroyAllWindows()
print("Chương trình đã kết thúc.")