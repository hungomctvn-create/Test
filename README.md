Bước 3: Cài đặt MediaPipe mới qua pip

Cài phụ thuộc cơ bản:

Cài các thư viện cần thiết:
text
sudo apt install -y python3-dev python3-opencv libatlas-base-dev build-essential



Cài MediaPipe:

Chạy lệnh cài đặt phiên bản mới nhất:
text
python3 -m pip install mediapipe --user

Nếu muốn cài phiên bản cụ thể (kiểm tra trên https://pypi.org/project/mediapipe/):
text
python3 -m pip install mediapipe==0.10.15 --user



Cài phụ thuộc bổ sung:

Đảm bảo OpenCV và NumPy:
text
python3 -m pip install opencv-python numpy --user



Kiểm tra cài đặt:

Chạy:
textpython3 -c "import mediapipe; print(mediapipe.__version__)"

Nếu hiển thị phiên bản (ví dụ: 0.10.15) mà không lỗi, cài đặt thành công.
