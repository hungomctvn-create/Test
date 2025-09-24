glxinfo | grep "OpenGL version"
python setup.py bdist_wheel --plat-name linux_x86_64 2>&1 | tee build.log
git clone https://github.com/google/mediapipe.git mediapipe
python setup.py bdist_wheel --plat-name linux_x86_64
pip install dist/mediapipe-*.whl
python greeting_robot_final.py


ygame 1.9.6
Hello from the pygame community. https://www.pygame.org/contribute.html
Traceback (most recent call last):
  File "/home/robothcc/greeting_robot_final_1.1.py", line 9, in <module>
    mp_face_detection = mp.solutions.face_detection
AttributeError: module 'mediapipe' has no attribute 'solutions'


------------------
(program exited with code: 1)
Press return to continue

python -c "import mediapipe as mp; print(mp.__version__)"

python -c "import mediapipe as mp; print(mp.__version__)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AttributeError: module 'mediapipe' has no attribute '__version__'



Phương pháp 1: Cài từ PyPI

Tạo môi trường ảo (tùy chọn nhưng khuyến nghị):
textpython3 -m venv /home/robothcc/mediapipe_env
source /home/robothcc/mediapipe_env/bin/activate

Cài MediaPipe:
textpip install mediapipe==0.10.21

Kiểm tra phiên bản:
textpython -c "import mediapipe as mp; print(mp.__version__)"

Đầu ra mong đợi: 0.10.21.



Phương pháp 2: Build từ nguồn

Vào thư mục MediaPipe:
textcd /home/robothcc/mediapipe

Checkout phiên bản:
textgit checkout v0.10.21

Cài dependencies:
textsudo apt update
sudo apt install -y python3-dev python3-pip build-essential cmake pkg-config libprotobuf-dev protobuf-compiler libgl1-mesa-dev libgles2-mesa-dev g++

Build wheel:
textpython setup.py bdist_wheel --plat-name linux_x86_64

Nếu lỗi gl_context.cc, chỉnh sửa setup.py để bỏ qua GPU (xem Bước 4).


Cài wheel:
textpip install dist/mediapipe-*.whl

Kiểm tra:
textpython -c "import mediapipe as mp; print(mp.__version__)"


Bước 4: Khắc phục lỗi trước (nếu cần)
Dựa trên lỗi trước (AttributeError: module 'mediapipe' has no attribute 'solutions'), đảm bảo build đầy đủ:

Nếu build lỗi, mở setup.py:
textnano /home/robothcc/mediapipe/setup.py

Thêm hoặc sửa đường dẫn nguồn, đảm bảo solutions được bao gồm. Nếu không rõ, cung cấp nội dung file để tôi hỗ trợ.
Chạy lại build.

Bước 5: Chạy script

Kích hoạt env (nếu dùng):
textsource /home/robothcc/mediapipe_env/bin/activate

Chạy script:
textpython /home/robothcc/greeting_robot_final_1.1.py


Script tham khảo
textimport cv2
import mediapipe as mp
from gtts import gTTS
import pygame
import time
import os

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Lỗi: Không thể mở webcam. Kiểm tra USB.")
    print("Kiểm tra: ls /dev/video*")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_greet_time = 0
greet_interval = 5

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
        os.remove("greeting.mp3")
    except Exception as e:
        print(f"Lỗi âm thanh: {e}")

try:
    print("Chương trình chạy. Đặt khuôn mặt trước webcam...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Lỗi đọc webcam")
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)
                print("Phát hiện khuôn mặt! Đang chào...")
                current_time = time.time()
                if (current_time - last_greet_time) > greet_interval:
                    speak_greeting()
                    last_greet_time = current_time
        cv2.imshow('Webcam - Greeting Robot', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Dừng bởi Ctrl+C")

cap.release()
cv2.destroyAllWindows()
print("Chương trình kết thúc.")
Khắc phục sự cố

Không thấy mediapipe: Báo kết quả ls -la /home/robothcc/.
Cài lỗi: Cung cấp output pip install hoặc build.log.
Script lỗi: Báo chi tiết.

Lưu ý

Đường dẫn chính là /home/robothcc/mediapipe.
Báo lại kết quả của ls -la /home/robothcc/mediapipe/ hoặc python -c "import mediapipe as mp; print(mp.__version__)" để tôi hỗ trợ thêm!

Chạy các lệnh và cung cấp kết quả!
