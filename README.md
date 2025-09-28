ài đặt các thư viện phụ thuộc cần thiết:

Cập nhật danh sách gói và cài đặt các thư viện liên quan đến JPEG, PNG, và các codec khác:
text
sudo apt update
sudo apt install libjpeg-dev libpng-dev libtiff-dev libwebp-dev

Các gói này cung cấp các header và thư viện cần thiết để hỗ trợ các định dạng hình ảnh trong OpenCV.


Xóa và tái cấu hình với CMake:

Xóa thư mục build hiện tại để tránh xung đột:
text
rm -rf /mnt/shared/opencv-4.8.1/build
mkdir /mnt/shared/opencv-4.8.1/build
cd /mnt/shared/opencv-4.8.1/build

Chạy lại cmake với các tham số đã dùng trước, đảm bảo chỉ định thư mục nguồn:
textcmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=on \
-D INSTALL_C_EXAMPLES=off \
-D OPENCV_ENABLE_NONFREE=on \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.8.1/modules \
-D PYTHON_EXECUTABLE=$(which python3) \
-D BUILD_EXAMPLES=on ..


Đảm bảo không có lỗi trong quá trình cấu hình.


Chạy lại quá trình biên dịch:

Biên dịch với số job phù hợp:
textmake -j4

Nếu lỗi vẫn xảy ra, giảm số job để tránh quá tải tài nguyên:
textmake -j2re.so*
