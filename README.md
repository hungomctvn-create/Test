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
text
cd /home/robothcc/mediapipe

Checkout phiên bản:
text
git checkout v0.10.21

Cài dependencies:
text
sudo apt update
sudo apt install -y python3-dev python3-pip build-essential cmake pkg-config libprotobuf-dev protobuf-compiler libgl1-mesa-dev libgles2-mesa-dev g++

Build wheel:
text
python setup.py bdist_wheel --plat-name linux_x86_64

Nếu lỗi gl_context.cc, chỉnh sửa setup.py để bỏ qua GPU (xem Bước 4).


Cài wheel:
text
pip install dist/mediapipe-*.whl

Kiểm tra:
textpython -c "import mediapipe as mp; print(mp.__version__)"


Bước 4: Khắc phục lỗi trước (nếu cần)
Dựa trên lỗi trước (AttributeError: module 'mediapipe' has no attribute 'solutions'), đảm bảo build đầy đủ:

Nếu build lỗi, mở setup.py:
text
nano /home/robothcc/mediapipe/setup.py

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



  self._finalize_license_expression()
running bdist_wheel
running build
running build_py
running gen_protos
generating proto file: build/lib.linux-x86_64-cpython-39/mediapipe/tasks/cc/genai/inference/proto/transformer_params_pb2.py
Invoking: /usr/bin/protoc -I. --python_out=/home/robothcc/mediapipe/build/lib.linux-x86_64-cpython-39 mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto
mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto: This file contains proto3 optional fields, but --experimental_allow_proto3_optional was not set.
Command '['/usr/bin/protoc', '-I.', '--python_out=/home/robothcc/mediapipe/build/lib.linux-x86_64-cpython-39', 'mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto']' returned non-zero exit status 1.
robothcc@raspberry:~/mediapipe $ pip install dist/mediapipe-*.whl
Defaulting to user installation because normal site-packages is not writeable
WARNING: Requirement 'dist/mediapipe-*.whl' looks like a filename, but the file does not exist
ERROR: Invalid wheel filename (wrong number of parts): 'mediapipe-*'
robothcc@raspberry:~/mediapipe $ 


Chạy các lệnh và cung cấp kết quả!





Phân tích và xử lý tình huống tiếp theo sau lỗi build và cài đặt MediaPipe
Dựa trên thông tin bạn cung cấp, bạn đã chạy các lệnh liên quan đến việc build và cài đặt MediaPipe trên Raspberry Pi ảo (x86_64, Debian 11 Bullseye) với tên người dùng robothcc. Thời gian hiện tại là 12:26 PM +07, Thứ Tư, 24/09/2025 (theo thông tin hệ thống). Dưới đây là phân tích chi tiết và hướng dẫn khắc phục dựa trên hai lỗi bạn gặp phải:
Phân tích Lỗi 1: Build thất bại với protoc
Khi chạy:
textpython setup.py bdist_wheel --plat-name linux_x86_64
Đầu ra cho thấy:
textrunning bdist_wheel
running build
running build_py
running gen_protos
generating proto file: build/lib.linux-x86_64-cpython-39/mediapipe/tasks/cc/genai/inference/proto/transformer_params_pb2.py
Invoking: /usr/bin/protoc -I. --python_out=/home/robothcc/mediapipe/build/lib.linux-x86_64-cpython-39 mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto
mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto: This file contains proto3 optional fields, but --experimental_allow_proto3_optional was not set.
Command '['/usr/bin/protoc', '-I.', '--python_out=/home/robothcc/mediapipe/build/lib.linux-x86_64-cpython-39', 'mediapipe/tasks/cc/genai/inference/proto/transformer_params.proto']' returned non-zero exit status 1.

Nguyên nhân: Lỗi xảy ra trong quá trình gen_protos khi protoc (Protobuf compiler) cố gắng biên dịch file transformer_params.proto. File này sử dụng proto3 optional fields (tính năng thử nghiệm trong Protobuf 3.x), nhưng phiên bản protoc mặc định trên Debian 11 (thường là 3.12.x) không tự động hỗ trợ flag --experimental_allow_proto3_optional mà không được chỉ định rõ ràng.

Phân tích Lỗi 2: Cài đặt wheel thất bại
Khi chạy:
textpip install dist/mediapipe-*.whl
Đầu ra cho thấy:
textDefaulting to user installation because normal site-packages is not writeable
WARNING: Requirement 'dist/mediapipe-*.whl' looks like a filename, but the file does not exist
ERROR: Invalid wheel filename (wrong number of parts): 'mediapipe-*'

Nguyên nhân: Lỗi này xảy ra vì quá trình build trước đó không tạo được file wheel (do lỗi protoc), nên thư mục dist/ không chứa file mediapipe-*.whl. Thông báo Invalid wheel filename là hậu quả của việc pip không tìm thấy file phù hợp với mẫu mediapipe-*.

Giải pháp chi tiết
Bước 1: Nâng cấp hoặc kiểm tra phiên bản protoc
Xác nhận phiên bản protoc hiện tại:
textprotoc --version

Đầu ra mong đợi: libprotoc 3.12.x hoặc cao hơn. Nếu < 3.12, cài lại:
textsudo apt update
sudo apt install -y protobuf-compiler

Nếu đã là 3.12.x, nâng cấp lên phiên bản mới hơn (3.21+ hỗ trợ proto3 optional tốt hơn):

Tải Protobuf 3.21.12:
textwget https://github.com/protocolbuffers/protobuf/releases/download/v21.12/protobuf-21.12.tar.gz
tar -xzf protobuf-21.12.tar.gz
cd protobuf-21.12

Build và cài:
text./configure --prefix=/usr/local
make -j4
sudo make install
sudo ldconfig

Kiểm tra lại: protoc --version.



Bước 2: Thêm flag --experimental_allow_proto3_optional vào build
Chỉnh sửa setup.py để thêm flag cho protoc:

Mở file trong thư mục mediapipe:
textcd /home/robothcc/mediapipe
nano setup.py

Tìm phần gọi protoc (thường trong hàm generate_protos hoặc tương tự):

Ví dụ:
textsubprocess.check_call([
    'protoc', '-I', '.', '--python_out', out_dir, proto_file
])

Thêm flag:
textsubprocess.check_call([
    'protoc', '-I', '.', '--experimental_allow_proto3_optional', '--python_out', out_dir, proto_file
])



Lưu (Ctrl+O, Enter, Ctrl+X) và chạy lại build:
textpython setup.py bdist_wheel --plat-name linux_x86_64


Bước 3: Kiểm tra và cài đặt wheel

Sau khi build thành công, kiểm tra thư mục dist/:
textls -l dist/

Nếu có file như mediapipe-0.10.21-cp39-cp39-linux_x86_64.whl: Cài đặt:
textpip install dist/mediapipe-*.whl

Nếu không có: Xem log build để phân tích:
textpython setup.py bdist_wheel --plat-name linux_x86_64 2>&1 | tee build.log
cat build.log




Bước 4: Khắc phục nếu build vẫn lỗi

Lỗi proto khác: Đảm bảo protoc đường dẫn chính xác:
textwhich protoc

Nếu không phải /usr/local/bin/protoc, cập nhật PATH:
textexport PATH=$PATH:/usr/local/bin



Thiếu dependency: Cài thêm:
textsudo apt install -y g++ libprotobuf-dev


Bước 5: Chạy script

Kích hoạt môi trường ảo (nếu dùng):
textsource /home/robothcc/mediapipe_env/bin/activate

Chạy script:
textpython /home/robothcc/greeting_robot_final_1.1.py

Nếu lỗi webcam: Kiểm tra ls /dev/video*, cấu hình USB trong VirtualBox.
Nếu lỗi âm thanh: Đảm bảo VirtualBox chuyển tiếp audio.

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

Build thất bại: Cung cấp nội dung build.log.
Protoc lỗi: Báo kết quả protoc --version.
Script lỗi: Cung cấp thông báo lỗi chi tiết.

Lưu ý

Tập trung vào thêm flag --experimental_allow_proto3_optional.
Báo lại kết quả của protoc --version và output build mới để tôi hỗ trợ thê
