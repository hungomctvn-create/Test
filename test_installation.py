#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra cài đặt các thư viện trên Raspberry Pi
"""

import sys
import subprocess

def test_import(module_name, package_name=None):
    """Kiểm tra import module"""
    try:
        if module_name == "cv2":
            import cv2
            print(f"✓ OpenCV: {cv2.__version__}")
        elif module_name == "numpy":
            import numpy as np
            print(f"✓ NumPy: {np.__version__}")
        elif module_name == "pygame":
            import pygame
            print(f"✓ Pygame: {pygame.version.ver}")
        elif module_name == "gtts":
            from gtts import gTTS
            print("✓ gTTS: Imported successfully")
        elif module_name == "PIL":
            from PIL import Image
            print("✓ Pillow: Imported successfully")
        elif module_name == "matplotlib":
            import matplotlib
            print(f"✓ Matplotlib: {matplotlib.__version__}")
        elif module_name == "scipy":
            import scipy
            print(f"✓ SciPy: {scipy.__version__}")
        elif module_name == "tkinter":
            import tkinter as tk
            print("✓ Tkinter: Available")
        elif module_name == "pyttsx3":
            import pyttsx3
            print("✓ pyttsx3: Imported successfully")
        else:
            exec(f"import {module_name}")
            print(f"✓ {module_name}: Imported successfully")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        if package_name:
            print(f"  → Cài đặt: pip3 install {package_name}")
        return False
    except Exception as e:
        print(f"✗ {module_name}: Lỗi khác - {e}")
        return False

def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 7:
        print("✓ Python version OK")
        return True
    else:
        print("✗ Cần Python 3.7 trở lên")
        return False

def check_system_packages():
    """Kiểm tra các gói hệ thống"""
    packages = [
        "python3-dev",
        "python3-pip", 
        "libatlas-base-dev",
        "libhdf5-dev",
        "libjpeg-dev",
        "libpng-dev"
    ]
    
    print("\n=== KIỂM TRA GÓI HỆ THỐNG ===")
    for package in packages:
        try:
            result = subprocess.run(['dpkg', '-l', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {package}: Đã cài đặt")
            else:
                print(f"✗ {package}: Chưa cài đặt")
                print(f"  → Cài đặt: sudo apt install {package}")
        except Exception as e:
            print(f"? {package}: Không thể kiểm tra - {e}")

def main():
    """Hàm chính"""
    print("=== KIỂM TRA CÀI ĐẶT THƯ VIỆN ===")
    print(f"Hệ điều hành: {sys.platform}")
    
    # Kiểm tra Python
    check_python_version()
    
    print("\n=== KIỂM TRA THƯ VIỆN PYTHON ===")
    
    # Danh sách thư viện cần kiểm tra
    libraries = [
        ("numpy", "numpy==1.21.0"),
        ("cv2", "opencv-python==4.5.3.56"),
        ("pygame", "pygame==2.1.0"),
        ("gtts", "gtts==2.2.4"),
        ("PIL", "pillow==8.4.0"),
        ("matplotlib", "matplotlib==3.5.3"),
        ("scipy", "scipy==1.7.3"),
        ("tkinter", None),
        ("pyttsx3", "pyttsx3==2.90"),
        ("requests", "requests"),
        ("yaml", "pyyaml"),
        ("tqdm", "tqdm")
    ]
    
    success_count = 0
    total_count = len(libraries)
    
    for module, package in libraries:
        if test_import(module, package):
            success_count += 1
    
    # Kiểm tra gói hệ thống (chỉ trên Linux)
    if sys.platform.startswith('linux'):
        check_system_packages()
    
    print(f"\n=== KẾT QUẢ ===")
    print(f"Thành công: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 Tất cả thư viện đã được cài đặt thành công!")
        
        # Test cơ bản
        print("\n=== TEST CƠ BẢN ===")
        try:
            import numpy as np
            import cv2
            
            # Test NumPy
            arr = np.array([1, 2, 3])
            print(f"✓ NumPy test: {arr}")
            
            # Test OpenCV
            img = np.zeros((100, 100, 3), dtype=np.uint8)
            print(f"✓ OpenCV test: Created image shape {img.shape}")
            
            # Test gTTS
            from gtts import gTTS
            tts = gTTS("Test", lang='vi')
            print("✓ gTTS test: Object created successfully")
            
            print("🎉 Tất cả test cơ bản đều thành công!")
            
        except Exception as e:
            print(f"✗ Lỗi trong test cơ bản: {e}")
    else:
        print("❌ Một số thư viện chưa được cài đặt đúng cách.")
        print("\nHướng dẫn khắc phục:")
        print("1. Chạy script: bash fix_raspberry_pi.sh")
        print("2. Hoặc cài thủ công: pip3 install -r requirements.txt")
        print("3. Chạy lại script này để kiểm tra")

if __name__ == "__main__":
    main()