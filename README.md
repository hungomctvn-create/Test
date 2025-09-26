pip install --upgrade pip

Cài Cython thủ công để tránh lỗi parse:

Cài phiên bản ổn định:
textpip install "cython>=0.29.0,<3.0"




Bước 3: Cài Đặt MediaPipe 0.10.21

Xóa cache pip (để tránh dùng wheel lỗi):
textpip cache purge

Cài MediaPipe:
textpip install mediapipe==0.10.21

Nếu lỗi "No matching distribution", thử không cache:
textpip install mediapipe==0.10.21 --no-cache-dir

Nếu vẫn lỗi, thử phiên bản cũ hơn (0.10.14):
textpip install mediapipe==0.10.14



Cài phụ thuộc bổ sung:
textpip install opencv-python numpy


Bước 4: Kiểm Tra Cài Đặt

Kiểm tra trong venv:
textpython -c "import mediapipe; print(mediapipe.__version__)"

Kết quả: 0.10.21 (hoặc 0.10.14) mà không lỗi → Thành công.
Nếu lỗi, kiểm tra log pip (thường hiển thị chi tiết khi fail).


Thoát venv:
textdeactivate


Bước 5: Cấu Hình Và Chạy Script

Tải mô hình face detector:
textwget -O ~/detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite

Cấu hình webcam:

Tắt VM > VirtualBox Settings > Ports > USB > Enable USB Controller > Add webcam.
Khởi động VM > Kiểm tra: ls /dev/video* (nên thấy /dev/video0).


Chạy script:

Kích hoạt venv:
textsource ~/mediapipe_venv/bin/activate

Chạy:
textpython ~/face_detector.py

Nhấn 'q' để thoát. Cập nhật MODEL_PATH trong script nếu cần (ví dụ: /home/robothcc/detector.tflite).



Xử Lý Lỗi Thêm

Lỗi "Invalid version: 'cpython'" vẫn xuất hiện:

Kiểm tra Python version trong venv: python --version (phải là 3.11 hoặc thấp hơn).
Nếu dùng Python 3.12, tạo venv với Python 3.11: python3.11 -m venv ~/mediapipe_venv.


"No matching distribution":

Kiểm tra mạng (ping pypi.org). Nếu proxy, thêm: pip install --trusted-host pypi.org mediapipe==0.10.21.
Hoặc thử index khác: pip install mediapipe==0.10.21 --index-url https://pypi.org/simple/.


Quyền hoặc site-packages lỗi:

Đảm bảo dùng venv; nếu không, thêm --user: pip install mediapipe==0.10.21 --user.


RAM không đủ (2 GB):

Tăng lên 4 GB trong VirtualBox Settings > System > Base Memory nếu build từ source (khuyến nghị dùng pip).



Lưu Ý

Nếu lỗi dai dẳng, kiểm tra log pip đầy đủ (thêm --verbose khi cài: pip install mediapipe==0.10.21 --verbose) và cung cấp cho tôi.
Với x86_64 và 2 GB RAM, 0.10.21 chạy tốt cho face detection; tránh build từ source trừ khi cần.

Sau các bước này, lỗi "invalid version cpython" sẽ được khắc phục, và MediaPipe sẽ hoạt động. Nếu cần hỗ trợ thêm, gửi log chi tiết!4sFast
