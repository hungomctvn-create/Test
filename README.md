# SSH vào Raspberry Pi và chạy lệnh này:
curl -sSL https://raw.githubusercontent.com/user/repo/main/quick_fix.sh | bash

# HOẶC copy-paste script này:
pip3 uninstall numpy -y
sudo apt update && sudo apt install python3-numpy python3-opencv -y
pip3 install --user pygame==2.1.0 gtts==2.2.4 pyttsx3==2.90
python3 -c "import cv2, numpy; print('✓ Đã khắc phục!')"

# Từ máy tính Windows:
.\upload_to_raspberry_pi.ps1 -RaspberryPiIP "192.168.1.100" -Username "pi"
