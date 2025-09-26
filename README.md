Cài đặt thủ công tệp .whl
MediaPipe 0.10.14 có tệp .whl cho Linux x86_64 với Python 3.9. Hãy tải và cài đặt thủ công:

Truy cập PyPI MediaPipe 0.10.14.
Tải tệp .whl phù hợp:

Tệp cần tìm: mediapipe-0.10.14-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.
Lệnh tải:
bashwget https://files.pythonhosted.org/packages/0c/88/91b4846f6b5f6b7c4f6711b03a7cd2bb3eb37bc3cb5c3d8b9be0c1973a5f/mediapipe-0.10.14-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl



Cài đặt:
bashpip3 install mediapipe-0.10.14-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl


Bước 3: Cài đặt phụ thuộc cần thiết
MediaPipe yêu cầu các phụ thuộc sau:
bashpip3 install opencv-python-headless==4.5.5.64 numpy==1.23.5 protobuf==3.20.3 pyttsx3 --timeout=300

Dùng opencv-python-headless để tránh phụ thuộc đồ họa không cần thiết.
protobuf==3.20.3 là phiên bản tương thích với MediaPipe 0.10.14.
Cài espeak cho pyttsx3:
bashsudo apt-get update
sudo apt-get install espeak


Bước 4: Nếu vẫn lỗi, thử môi trường ảo mới
Môi trường ảo hiện tại (myenv) có thể bị xung đột. Tạo môi trường mới:
bashpython3 -m venv myenv_new
source myenv_new/bin/activate
pip install --upgrade pip --timeout=300
pip install mediapipe==0.10.14 --timeout=300
Bước 5: Kiểm tra cài đặt
Kiểm tra MediaPipe:
bashpython3 -c "import mediapipe; print(mediapipe.__version__)"

Kết quả mong đợi: 0.10.14.
Nếu lỗi (ví dụ: ModuleNotFoundError), kiểm tra pip:
bashpip3 --version
Đảm bảo pip liên kết với Python 3.9.2 trong môi trường ảo (myenv_new).


2. Xử lý lỗi nếu vẫn không cài được
Nếu lệnh pip3 install mediapipe==0.10.14 hoặc cài thủ công .whl vẫn thất bại, hãy thử các cách sau:
a. Kiểm tra lỗi cụ thể
Chạy lại lệnh cài đặt và lưu toàn bộ thông báo lỗi:
bashpip3 install mediapipe==0.10.14 --verbose > install_log.txt
Gửi nội dung install_log.txt để tôi phân tích.
b. Cài phiên bản MediaPipe khác
Nếu 0.10.14 không hỗ trợ x86_64 với Python 3.9.2, thử phiên bản mới hơn (ví dụ: 0.10.15):
bashpip3 install mediapipe==0.10.15 --timeout=300
Hoặc cài phiên bản mới nhất:
bashpip3 install mediapipe --timeout=300
c. Cài OpenCV và phụ thuộc thủ công
MediaPipe phụ thuộc nhiều vào OpenCV và protobuf. Cài trước:
bashpip3 install opencv-python-headless==4.5.5.64 numpy==1.23.5 protobuf==3.20.3 --timeout=300
sudo apt-get install -y libopencv-dev python3-opencv
d. Kiểm tra kiến trúc hệ thống
Kiến trúc x86_64 cho thấy bạn không dùng Raspberry Pi ARM mà là hệ thống 64-bit (có thể là máy ảo hoặc PC Linux). Nếu đây là máy ảo, đảm bảo:

Máy ảo có đủ RAM (ít nhất 2GB).
Kết nối mạng không bị chặn bởi tường lửa.

e. Cài từ mã nguồn (nếu cần)
Nếu không có tệp .whl phù hợp, thử cài từ mã nguồn:

Tải mã nguồn MediaPipe 0.10.14:
bashwget https://github.com/google/mediapipe/archive/refs/tags/v0.10.14.tar.gz
tar -xzvf v0.10.14.tar.gz
cd mediapipe-0.10.14

Cài đặt:
bashpip3 install .

Yêu cầu cài Bazel và các phụ thuộc khác. Đây là cách phức tạp, chỉ nên thử nếu các cách trên thất bại.




3. Mã kiểm tra: Nhận diện khuôn mặt và phát tiếng chào
Sau khi cài MediaPipe 0.10.14, dùng mã sau để kiểm tra:
pythonimport cv2
import mediapipe as mp
import pyttsx3
import time

# Khởi tạo engine text-to-speech
engine = pyttsx3.init()
