Xử lý lỗi khi chạy QEMU trên Windows 11
Dựa trên hình ảnh bạn cung cấp từ Command Prompt, lỗi xảy ra khi chạy lệnh QEMU với thông báo:
textqemu-system-aarch64: -drive file=2025-05-13-raspios-bookworm-arm64.img,format=raw,if=sd: Could not open '2025-05-13-raspios-bookworm-arm64.img': Access is denied
Nguyên nhân
Lỗi "Access is denied" khi QEMU cố gắng mở file image (2025-05-13-raspios-bookworm-arm64.img) thường do các vấn đề sau:

Quyền truy cập: File image nằm trong thư mục mà tài khoản hiện tại không có quyền đọc/ghi (ví dụ: thư mục hệ thống hoặc được bảo vệ bởi OneDrive).
Đường dẫn không chính xác: File không tồn tại tại vị trí được chỉ định hoặc tên file bị lỗi chính tả.
File đang được sử dụng: File image có thể đang bị khóa bởi một chương trình khác (như OSFMount hoặc 7-Zip).
Cú pháp lệnh: Lệnh QEMU có thể thiếu hoặc có lỗi cú pháp, gây ra việc không đọc được file.

Giải pháp chi tiết
Bước 1: Kiểm tra vị trí và quyền truy cập file

Xác định đường dẫn file:

Kiểm tra xem file 2025-05-13-raspios-bookworm-arm64.img thực sự nằm trong thư mục C:\Program Files\qemu không. Chạy:
textdir 2025-05-13-raspios-bookworm-arm64.img
Nếu không thấy file, bạn cần di chuyển file vào thư mục này hoặc sửa đường dẫn trong lệnh.
Nếu file nằm ở nơi khác (ví dụ: C:\Users\YourName\Desktop), cập nhật lệnh với đường dẫn đầy đủ, ví dụ:
text-drive file=C:\Users\YourName\Desktop\2025-05-13-raspios-bookworm-arm64.img,format=raw,if=sd



Kiểm tra quyền truy cập:

Nhấp phải vào file .img > Properties > Security. Đảm bảo tài khoản hiện tại (hoặc "Users") có quyền "Full control" hoặc ít nhất "Read & Execute".
Nếu không, nhấp "Edit" > Thay đổi quyền > Apply.


Tránh OneDrive:

Nếu file nằm trong thư mục OneDrive (C:\Users\hungo\OneDrive), di chuyển nó ra ngoài (ví dụ: C:\Users\hungo\Desktop) vì OneDrive có thể khóa file khi đồng bộ.



Bước 2: Đóng các chương trình khác

Đảm bảo file .img không bị mở bởi OSFMount, 7-Zip, hoặc bất kỳ công cụ nào khác. Kiểm tra Task Manager (Ctrl+Shift+Esc) > Kết thúc các tiến trình liên quan nếu có.

Bước 3: Sửa lệnh QEMU
Lệnh của bạn thiếu -machine và một số tham số quan trọng, dẫn đến thông báo "No machine specified". Hãy sử dụng lệnh đầy đủ như sau (chạy trong C:\Program Files\qemu hoặc thư mục chứa file):
textqemu-system-aarch64 ^
  -machine raspi4b ^
  -cpu cortex-a72 ^
  -smp 4 ^
  -m 4G ^
  -kernel kernel8.img ^
  -dtb bcm2711-rpi-4-b.dtb ^
  -drive file=2025-05-13-raspios-bookworm-arm64.img,format=raw,if=sd ^
  -device virtio-gpu-pci ^
  -display sdl ^
  -device usb-kbd ^
  -device usb-mouse ^
  -netdev user,id=net0 ^
  -device usb-net,netdev=net0 ^
  -serial stdio

Giải thích:

-machine raspi4b: Chỉ định máy ảo là Raspberry Pi 4B.
-kernel kernel8.img và -dtb bcm2711-rpi-4-b.dtb: Đảm bảo hai file này cũng nằm trong C:\Program Files\qemu. Nếu không, thêm đường dẫn đầy đủ (ví dụ: C:\Users\YourName\Desktop\kernel8.img).
^: Dùng để ngắt dòng trong Command Prompt trên Windows.


Chạy lệnh:

Đảm bảo tất cả file (2025-05-13-raspios-bookworm-arm64.img, kernel8.img, bcm2711-rpi-4-b.dtb) ở cùng thư mục hoặc cập nhật đường dẫn.
Mở Command Prompt với quyền Admin (nhấp phải > Run as administrator) để tránh lỗi quyền.



Bước 4: Kiểm tra và khắc phục lỗi

Nếu vẫn lỗi "Access is denied":

Chạy Command Prompt với quyền Admin.
Di chuyển file .img ra khỏi C:\Program Files (thư mục hệ thống) vào C:\Users\YourName\Desktop và thử lại với đường dẫn mới.


Nếu không tìm thấy kernel/DTB:

Dùng OSFMount (như hướng dẫn trước) để mount file .img và trích xuất lại kernel8.img và bcm2711-rpi-4-b.dtb vào cùng thư mục.


Nếu black screen hoặc không boot:

Thêm -nographic để kiểm tra console, hoặc thử -machine raspi3b với DTB bcm2710-rpi-3-b-plus.dtb.



Bước 5: Thử nghiệm và tối ưu

Sau khi chạy thành công, bạn sẽ thấy desktop Raspberry Pi OS (login: pi/raspberry). Nếu chậm, giảm -m 4G xuống -m 2G.
Để SSH: Thêm -net user,hostfwd=tcp::5555-:22, rồi dùng ssh pi@127.0.0.1 -p 5555 từ Windows.

Mẹo bổ sung

Dùng file batch: Tạo file .bat (ví dụ: runqemu.bat) với nội dung lệnh trên, lưu cùng file, rồi nhấp đôi để chạy.
Kiểm tra version QEMU: Nếu lỗi lạ, cập nhật QEMU mới nhất từ qemu.org.

Nếu vẫn gặp vấn đề (ví dụ: lỗi cụ thể khác), cung cấp output chi tiết hoặc mô tả thêm (đường dẫn file, quyền tài khoản) để mình hỗ trợ tiếp!
