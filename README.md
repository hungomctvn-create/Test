mount | grep /mnt/shared
sudo mount -o remount,rw /mnt/shared
sudo reboot
hử biên dịch lại:

Xóa thư mục build hiện tại để bắt đầu lại:
textrm -rf /mnt/shared/opencv-4.8.1/build
mkdir /mnt/shared/opencv-4.8.1/build
cd /mnt/shared/opencv-4.8.1/build

Chạy lại lệnh cmake:
textcmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=on \
-D INSTALL_C_EXAMPLES=off \
-D OPENCV_ENABLE_NONFREE=on \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.8.1/modules \
-D PYTHON_EXECUTABLE=$(which python3) \
-D BUILD_EXAMPLES=on

Biên dịch lại:
textmake -j4



Kiểm tra thư mục đích /usr/local/lib:

Kiểm tra quyền:
textls -ld /usr/local/lib

Cấp quyền nếu cần:
textsudo chmod -R 775 /usr/local/lib
sudo chown -R $USER:$USER /usr/local/lib



Thử biên dịch ngoài /mnt/shared:

Nếu lỗi vẫn xảy ra do hạn chế của Shared Folder, sao chép dự án ra ngoài:
textcp -r /mnt/shared/opencv-4.8.1 /home/$USER/
cd /home/$USER/opencv-4.8.1/build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_PYTHON_EXAMPLES=on \
-D INSTALL_C_EXAMPLES=off \
-D OPENCV_ENABLE_NONFREE=on \
-D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib-4.8.1/modules \
-D PYTHON_EXECUTABLE=$(which python3) \
-D BUILD_EXAMPLES=on
make -j4



Xác nhận kết quả:

Sau khi biên dịch thành công, kiểm tra file:
textls -l /usr/local/lib/libopencv_core.so*
