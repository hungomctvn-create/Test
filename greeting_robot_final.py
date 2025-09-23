import cv2
import os
import urllib.request
from gtts import gTTS
import pygame
import time

# Thử nghiệm các chỉ số webcam (0, 1, 2)
webcam_found = False
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Webcam được phát hiện tại chỉ số {i}")
        webcam_found = True
        break
    cap.release()
if not webcam_found:
    print("Lỗi: Không thể mở webcam. Kiểm tra kết nối, driver hoặc quyền truy cập.")
    exit()

# Kiểm tra xem webcam có hoạt động không
if not cap.isOpened():
    print("Lỗi: Webcam không khả dụng sau khi thử.")
    exit()

# Đường dẫn mặc định đến file Haar Cascade
cascade_path = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"

# Tải tự động file từ GitHub nếu không tìm thấy
if not os.path.exists(cascade_path):
    print("File Haar Cascade không tồn tại tại đường dẫn mặc định. Bắt đầu tải từ GitHub...")
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    try:
        os.makedirs(os.path.dirname(cascade_path), exist_ok=True)
        urllib.request.urlretrieve(url, cascade_path)
        print(f"Đã tải file thành công và lưu tại: {cascade_path}")
    except Exception as e:
        print(f"Lỗi khi tải file từ GitHub: {e}")
        print("Vui lòng kiểm tra kết nối internet hoặc tải thủ công file haarcascade_frontalface_default.xml.")
        exit()

# Tải mô hình phát hiện khuôn mặt
face_cascade = cv2.CascadeClassifier(cascade_path)

# Kiểm tra xem mô hình có tải thành công không
if face_cascade.empty():
    print("Lỗi: Không thể tải mô hình phát hiện khuôn mặt. Kiểm tra đường dẫn XML.")
    exit()

# Biến để kiểm soát thời gian chào
last_greet_time = 0
greet_interval = 5  # Thời gian chờ giữa các lần chào (giây)

# Hàm tạo và phát âm thanh chào
def speak_greeting():
    try:
        text = "Xin chào! Rất vui được gặp bạn!"
        tts = gTTS(text=text, lang='vi')  # Giọng nói tiếng Việt
        tts.save("greeting.mp3")
        
        pygame.mixer.init()
        pygame.mixer.music.load("greeting.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        os.remove("greeting.mp3")
        print("Đã phát lời chào!")
    except Exception as e:
        print(f"Lỗi khi tạo hoặc phát âm thanh: {e}")
        pygame.mixer.quit()

# Vòng lặp chính
try:
    print("Chương trình đang chạy. Đặt khuôn mặt trước webcam...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Lỗi: Không thể đọc từ webcam")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Khuon mat', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        current_time = time.time()
        if len(faces) > 0 and (current_time - last_greet_time) > greet_interval:
            print(f"Phát hiện {len(faces)} khuôn mặt! Đang chào...")
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