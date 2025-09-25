Hướng Dẫn Chi Tiết Cài Đặt MediaPipe Trên Máy Ảo "Test"
Giả định VM đang chạy Raspberry Pi OS (biến thể Debian) với Python 3.9 (mặc định của Bullseye). Nếu Python khác, điều chỉnh lệnh tương ứng. Sử dụng tài khoản robothcc (hoặc user mặc định). Cài đặt qua pip là cách đơn giản nhất; tránh build từ source trừ khi cần tùy chỉnh.
Bước 1: Khởi Động Và Chuẩn Bị VM

Trong Oracle VirtualBox, chọn VM "test" và nhấn Start để khởi động.
Đăng nhập với tài khoản robothcc (prompt: robothcc@raspberry:~ $).
Mở Terminal (Ctrl+Alt+T hoặc icon Terminal trên desktop).
Đảm bảo kết nối mạng: Kiểm tra bằng ping google.com. Nếu không kết nối, kiểm tra VirtualBox Settings > Network > Adapter 1 > NAT (đã bật).

Bước 2: Cập Nhật Hệ Thống Và Cài Phụ Thuộc Cơ Bản

Cập nhật hệ thống để tránh lỗi gói:
textsudo apt update && sudo apt upgrade -y

Cài các phụ thuộc cần thiết cho MediaPipe (bao gồm OpenCV cho xử lý hình ảnh và build tools):
textsudo apt install -y python3-pip python3-dev python3-opencv libatlas-base-dev build-essential libopencv-dev

Nếu lỗi thiếu gói, thêm kho đầy đủ: sudo apt install -y software-properties-common rồi thử lại.


Cập nhật pip (yêu cầu phiên bản 20.3+ cho MediaPipe):
textpython3 -m pip install --upgrade pip --user


Bước 3: Cài Đặt MediaPipe Phiên Bản 0.10.21

Cài phiên bản mới nhất (0.10.21) cho user robothcc (sử dụng --user để tránh cần root):
textpython3 -m pip install mediapipe==0.10.21 --user

Nếu muốn phiên bản mới nhất không chỉ định: python3 -m pip install mediapipe --user.
Quá trình tải và cài có thể mất 5–10 phút tùy mạng; với 2 GB RAM, nó sẽ chạy ổn.


Cài phụ thuộc bổ sung (nếu chưa có từ bước 2):
textpython3 -m pip install opencv-python numpy --user


Bước 4: Kiểm Tra Cài Đặt

Kiểm tra phiên bản MediaPipe:
textpython3 -c "import mediapipe; print(mediapipe.__version__)"

Kết quả nên là 0.10.21 (hoặc phiên bản bạn cài).


Nếu lỗi "No module named 'mediapipe'":

Thêm đường dẫn vào PATH (thêm vào file ~/.bashrc):
textecho 'export PYTHONPATH="$HOME/.local/lib/python3.9/site-packages:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc

Thay 3.9 bằng phiên bản Python của bạn (kiểm tra bằng python3 --version).





Bước 5: Cấu Hình Webcam (Nếu Sử Dụng Face Detection)

Tắt VM nếu đang chạy.
Trong VirtualBox Settings > Ports > USB:

Enable USB Controller (chọn USB 1.1 hoặc 2.0 nếu host hỗ trợ).
Thêm webcam của máy host vào danh sách thiết bị (nhấn icon + và chọn webcam).


Khởi động lại VM.
Kiểm tra webcam trong VM: ls /dev/video* (nên thấy /dev/video0).

Bước 6: Chạy Một Script Test (Ví Dụ: Face Detector)

Tải file mô hình (nếu dùng face detection):
textwget -O ~/detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite

Tạo file script ~/face_detector.py (sử dụng nano: nano ~/face_detector.py) và dán code từ trước (hoặc code mẫu từ MediaPipe docs).
Chạy:
textpython3 ~/face_detector.py

Nếu lỗi, kiểm tra code import đúng: import mediapipe as mp.



Lưu Ý Và Xử Lý Lỗi

Với 2 GB RAM: Cài đặt qua pip ổn, nhưng nếu chạy ứng dụng nặng (ví dụ: video real-time), giảm độ phân giải hoặc tăng RAM VM lên 4 GB (VirtualBox Settings > System > Base Memory).
Lỗi pip: Nếu "ERROR: Could not find a version", kiểm tra mạng hoặc thử pip install --no-cache-dir mediapipe==0.10.21 --user.
Build từ source (nếu cần): Nếu pip thất bại (hiếm), clone repo: git clone https://github.com/google/mediapipe.git ~/mediapipe, rồi cd ~/mediapipe và python3 setup.py install --user. Cài bazelisk trước: tải thủ công nếu apt không có (xem hướng dẫn trước).
Tương thích: Đảm bảo glibc ≥2.28 (kiểm tra: ldd --version). Nếu VM cũ, nâng cấp Debian lên phiên bản mới hơn (mount ISO mới vào Optical Drive).
Nếu gặp lỗi cụ thể, chạy pip show mediapipe để kiểm tra và cung cấp log cho hỗ trợ thêm.
2 web pages4.3sExpert
