Hướng Dẫn Chi Tiết Cài Đặt MediaPipe 0.10.14
Thực hiện từng bước trong Terminal của VM "test" (tài khoản robothcc). Nếu bạn chưa có Python 3.11, tôi sẽ hướng dẫn cài thêm.

Bước 1: Kiểm Tra Và Chuẩn Bị Python
Kiểm tra phiên bản Python hiện tại:
text
python3 --version
Nếu là 3.12.x hoặc cao hơn → Tiếp tục Bước 1.2 để downgrade.
Nếu là 3.9–3.11 → Bỏ qua Bước 1.2, đi thẳng Bước 2.
Cài Python 3.11 (nếu cần downgrade):
text
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y  # Thêm repo cho Python mới (nếu chưa có)
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
Cập nhật pip cho Python 3.11:
text
sudo apt install -y python3.11-pip
Từ giờ, dùng python3.11 thay vì python3 trong các lệnh sau.
Bước 2: Cập Nhật Hệ Thống Và Phụ Thuộc
Cập nhật hệ thống:
text
sudo apt update && sudo apt upgrade -y
Cài phụ thuộc cần thiết (cho MediaPipe và OpenCV):
text
sudo apt install -y build-essential libatlas-base-dev libopencv-dev python3-opencv
Nếu dùng Python 3.11: Thay python3-opencv bằng python3.11-opencv nếu có, hoặc dùng pip sau.
Cập nhật pip:
text
python3.11 -m pip install --upgrade pip --user  # Hoặc python3 nếu đã là 3.11
Bước 3: Gỡ Bỏ Phiên Bản Cũ (Nếu Có)
Gỡ MediaPipe cũ:
text
python3.11 -m pip uninstall mediapipe -y  # Hoặc python3
Xóa cache pip để tránh xung đột:
text
rm -rf ~/.cache/pip
Bước 4: Cài Đặt MediaPipe 0.10.14
Cài phiên bản tương thích:
text
python3.11 -m pip install mediapipe==0.10.14 --user  # Hoặc python3 nếu đã là 3.9–3.11
Quá trình tải wheel (~100MB) mất 2–5 phút tùy mạng. Nếu lỗi "No matching distribution", xác nhận lại Python version và thử --no-cache-dir:
text
python3.11 -m pip install mediapipe==0.10.14 --user --no-cache-dir
Cài phụ thuộc bổ sung (cho script face_detector.py):
text
python3.11 -m pip install opencv-python numpy --user  # Hoặc python3
Bước 5: Kiểm Tra Cài Đặt
Kiểm tra phiên bản:
text
python3.11 -c "import mediapipe; print(mediapipe.__version__)"  # Hoặc python3
Kết quả: 0.10.14 (không lỗi) → Thành công.
Nếu lỗi "No module named 'mediapipe'":
Thêm vào PYTHONPATH (chỉnh sửa file ~/.bashrc):
text
nano ~/.bashrc
Thêm dòng: export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH" (thay 3.11 bằng version của bạn).
Lưu (Ctrl+O, Enter, Ctrl+X), rồi:
text
source ~/.bashrc
Bước 6: Cấu Hình Và Chạy Script Face Detector
Tải mô hình (nếu chưa có):
text
wget -O ~/detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
Cập nhật MODEL_PATH = '/home/robothcc/detector.tflite' trong file face_detector.py nếu cần.
Đảm bảo webcam hoạt động:
Tắt VM, vào VirtualBox Settings > Ports > USB > Enable USB Controller > Add webcam filter.
Khởi động VM, kiểm tra: ls /dev/video* (nên thấy /dev/video0).
Chạy script:
text
cd ~
python3.11 face_detector.py  # Hoặc python3
Nhấn 'q' để thoát. Nếu lỗi import, kiểm tra lại Bước 5.
Xử Lý Lỗi Thêm
Lỗi quyền (--user permission): Chạy với sudo cho pip một lần: sudo python3.11 -m pip install mediapipe==0.10.14, nhưng tránh nếu có thể.
Lỗi wheel không tìm thấy: Xác nhận kiến trúc: uname -m (phải là x86_64). Nếu VM là ARM, cần phiên bản khác.
Chậm với 2GB RAM: Tăng RAM lên 4GB (VirtualBox Settings > System > Base Memory) nếu build lỗi.
Nếu vẫn thất bại: Tạo môi trường ảo:
text
python3.11 -m venv ~/mp_env
source ~/mp_env/bin/activate
pip install mediapipe==0.10.14 opencv-python numpy
python face_detector.py
deactivate  # Để thoát
Sau các bước này, MediaPipe sẽ hoạt động ổn định trên VM "test". Nếu gặp lỗi mới, cung cấp output để tôi hỗ trợ!### Phiên Bản MediaPipe Tương Thích Với Cấu Hình Máy Ảo "Test"

Dựa trên cấu hình VM "test" (Debian 64-bit x86_64, 2 GB RAM, KVM acceleration), MediaPipe phiên bản 0.10.21 (mới nhất tính đến 25/09/2025, phát hành 06/02/2025) là hoàn toàn tương thích. Nó hỗ trợ:

Kiến trúc: Linux x86_64 (manylinux_2_28_x86_64, phù hợp với Debian Bullseye/Bookworm).
Python: 3.9 đến 3.12 (mặc định của Debian Bullseye là Python 3.9, nên khớp).
Hệ thống: Debian-based như Raspberry Pi OS, với glibc ≥2.28 (Debian Bullseye dùng 2.31).
Tài nguyên: 2 GB RAM đủ cho cài đặt và chạy cơ bản (face detection), nhưng nếu build từ source hoặc xử lý video nặng, tăng lên 4 GB qua VirtualBox Settings > System > Base Memory.
Nếu Python của bạn là 3.8 hoặc thấp hơn (ít có), dùng phiên bản cũ hơn như 0.10.0. Nhưng với Debian 64-bit, 0.10.21 là lựa chọn tốt nhất cho tính năng mới và ổn định.

Hướng Dẫn Chi Tiết Cài Đặt MediaPipe 0.10.21 (Khắc Phục Lỗi Từ Hình Ảnh)
Lỗi trong hình ảnh ("No matching distribution found for mediapipe==0.10.21", "Invalid version: 'cython'", và "site-packages is not writable") thường do:

Pip không tìm thấy wheel phù hợp (cache cũ, Python version không khớp, hoặc mạng).
Dependency Cython lỗi (phiên bản không hợp lệ).
Quyền ghi vào site-packages (cần --user hoặc virtual env).
Sử dụng virtual environment (venv) để tránh xung đột quyền và dependencies. Không dùng sudo cho pip để tránh ô nhiễm hệ thống.

Bước 1: Khởi Động VM Và Kiểm Tra Môi Trường
Trong Oracle VirtualBox, chọn VM "test" > Start.
Đăng nhập tài khoản robothcc.
Mở Terminal (Ctrl+Alt+T).
Kiểm tra Python và pip:
text
python3 --version  # Nên là 3.9.x hoặc cao hơn
pip3 --version     # Nên là 20.3+
uname -m           # Xác nhận x86_64
Nếu Python <3.9, cài Python 3.9: sudo apt install python3.9 python3.9-venv.
Cập nhật hệ thống:
text
sudo apt update && sudo apt upgrade -y
Cài phụ thuộc hệ thống:
text
sudo apt install -y python3-venv python3-dev libatlas-base-dev build-essential libopencv-dev python3-opencv
Bước 2: Tạo Virtual Environment Và Cài Dependencies
Tạo venv mới (tránh lỗi writable site-packages):
text
python3 -m venv ~/mediapipe_venv
Kích hoạt venv:
text
source ~/mediapipe_venv/bin/activate
Prompt sẽ thay đổi thành (mediapipe_venv) robothcc@raspberry:~ $.
Nâng cấp pip trong venv:
text
pip install --upgrade pip
Khắc phục lỗi Cython: Cài Cython trước (phiên bản ổn định):
text
pip install "cython>=0.29.0,<3.0"
Cài NumPy và OpenCV (dependencies chính):
text
pip install numpy opencv-python
Bước 3: Cài MediaPipe 0.10.21
Xóa cache pip để tránh lỗi "no matching distribution":
text
pip cache purge
Cài phiên bản cụ thể:
text
pip install mediapipe==0.10.21
Nếu vẫn lỗi "no matching", thử không chỉ định version (cài mới nhất):
text
pip install mediapipe
Hoặc chỉ định index URL (nếu mạng chặn PyPI):
text
pip install mediapipe==0.10.21 --index-url https://pypi.org/simple/
Quá trình mất 5-10 phút; theo dõi log để xem lỗi nếu có.
Bước 4: Kiểm Tra Và Thoát Venv
Kiểm tra trong venv:
text
python -c "import mediapipe; print(mediapipe.__version__)"
Nên hiển thị 0.10.21.
Nếu thành công, thoát venv:
text
deactivate
Để chạy script sau, kích hoạt lại: source ~/mediapipe_venv/bin/activate.
Bước 5: Chạy Script Test (Face Detector)
Tải mô hình:
text
wget -O ~/detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
Kích hoạt venv và chạy:
text
source ~/mediapipe_venv/bin/activate
python ~/face_detector.py  # Đảm bảo script ở ~/ và cập nhật MODEL_PATH nếu cần
Cấu hình webcam (nếu lỗi VideoCapture):
Tắt VM > VirtualBox Settings > Ports > USB > Enable USB Controller > Add webcam.
Khởi động lại VM > Kiểm tra: ls /dev/video0.
Xử Lý Lỗi Thêm
"No matching distribution": Kiểm tra mạng (ping pypi.org). Nếu proxy, dùng --trusted-host pypi.org. Hoặc thử Python 3.10: sudo apt install python3.10-venv và tạo venv mới với python3.10 -m venv ~/mediapipe_venv.
Cython invalid version: Cài Cython thủ công trước, hoặc dùng pip install --no-deps mediapipe==0.10.21 rồi cài dependencies riêng.
Writable site-packages: Venv khắc phục; nếu không dùng venv, dùng --user và thêm export PYTHONPATH="$HOME/.local/lib/python3.9/site-packages:$PYTHONPATH" vào ~/.bashrc (source lại).
Chậm trên 2 GB RAM: Tăng RAM VM tạm thời.
Nếu vẫn thất bại: Cài từ source (clone GitHub, dùng bazelisk), nhưng phức tạp hơn – chỉ thử nếu pip lỗi.
Sau cài, MediaPipe sẽ chạy mượt với script của bạn. Nếu lỗi mới, cung cấp log đầy đủ!

Add to chat
