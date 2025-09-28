Giải pháp khắc phục
Thực hiện theo thứ tự để giải quyết từng lỗi. Ưu tiên khắc phục clock skew và build ngoài shared folder để tránh lỗi symlink.

Khắc phục clock skew và đồng bộ thời gian:

Dừng NTP daemon mặc định:
textsudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd

Cài và chạy ntpdate (nếu chưa có):
textsudo apt update
sudo apt install ntpdate
sudo ntpdate -s pool.ntp.org

Nếu lỗi "socket in use", thử server khác: sudo ntpdate -s 0.debian.pool.ntp.org.


Dùng timedatectl (thay thế):
textsudo timedatectl set-ntp true
timedatectl status

Cập nhật timestamp file trong dự án:
textcd /mnt/shared/opencv-4.8.1
find . -exec touch {} \;

Đồng bộ host/guest: Trong VirtualBox Settings > System > Motherboard, bật "Hardware Clock in UTC". Khởi động lại VM.


Khắc phục "Operation not permitted" và symlink:

Build ngoài shared folder (giải pháp chính):
textcp -r /mnt/shared/opencv-4.8.1 /home/pi/
cp -r /mnt/shared/opencv_contrib-4.8.1 /home/pi/
cd /home/pi/opencv-4.8.1
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=on \
-D INSTALL_C_EXAMPLES=off \
-D OPENCV_ENABLE_NONFREE=on \
-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-4.8.1/modules \
-D PYTHON_EXECUTABLE=$(which python3) \
-D BUILD_EXAMPLES=on \
-D CMAKE_CXX_FLAGS="-std=c++11" ..
make -j2  # Giảm job để tránh quá tải
sudo make install
sudo ldconfig

Cấp quyền thư mục:
textsudo chown -R pi:pi /home/pi/opencv-4.8.1
sudo chmod -R 775 /home/pi/opencv-4.8.1



Khắc phục hằng số IMWRITE_ không khai báo:

Cài thư viện phụ thuộc:
textsudo apt install libjpeg-dev libpng-dev libtiff-dev libwebp-dev

Rebuild sau khi cài.


Nâng cấp CMake (nếu version 2.8.9):

Cài phiên bản mới:
textsudo apt remove cmake
sudo apt install cmake
cmake --version  # Nên >=3.5.1

Nếu repository cũ, tải thủ công (xem hướng dẫn trước).


Khắc phục std::thread không nhận diện:

Đã thêm -D CMAKE_CXX_FLAGS="-std=c++11" trong cmake. Nếu vẫn lỗi, kiểm tra GCC:
textg++ --version
sudo apt install g++ gcc



Kiểm tra tổng quát và tối ưu:

Kiểm tra RAM/disk:
textfree -h
df -h

Thêm swap nếu RAM thấp:
textsudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

Kiểm tra OpenCV sau build:
textpython3 -c "import cv2; print(cv2.__version__)"
