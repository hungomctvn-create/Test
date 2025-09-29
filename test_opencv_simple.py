#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test OpenCV đơn giản cho Raspberry Pi
"""

import sys

def test_opencv():
    print("🧪 KIỂM TRA OPENCV TRÊN RASPBERRY PI")
    print("=" * 40)
    
    # Test import cv2
    try:
        import cv2
        print("✅ OpenCV import thành công!")
        print(f"✅ Phiên bản OpenCV: {cv2.__version__}")
        
        # Kiểm tra build info
        build_info = cv2.getBuildInformation()
        if "GUI" in build_info and "GTK" in build_info:
            print("✅ GUI support: Có")
        else:
            print("⚠️  GUI support: Không có (headless mode)")
            
    except ImportError as e:
        print(f"❌ Lỗi import OpenCV: {e}")
        print("💡 Chạy: sudo apt install python3-opencv")
        return False
    
    # Test numpy
    try:
        import numpy as np
        print("✅ NumPy OK")
    except ImportError:
        print("❌ NumPy không có")
        return False
    
    # Test camera
    print("\n📷 KIỂM TRA CAMERA:")
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera mở thành công tại index 0")
            ret, frame = cap.read()
            if ret:
                print(f"✅ Đọc frame thành công: {frame.shape}")
            else:
                print("⚠️  Không đọc được frame")
            cap.release()
        else:
            print("❌ Không thể mở camera tại index 0")
            # Thử index 1
            cap1 = cv2.VideoCapture(1)
            if cap1.isOpened():
                print("✅ Camera mở thành công tại index 1")
                cap1.release()
            else:
                print("❌ Không có camera nào")
    except Exception as e:
        print(f"❌ Lỗi camera: {e}")
    
    # Test YOLO
    print("\n🎯 KIỂM TRA YOLO:")
    try:
        from ultralytics import YOLO
        print("✅ YOLO (ultralytics) import thành công")
    except ImportError:
        print("⚠️  YOLO chưa cài đặt")
        print("💡 Chạy: pip3 install ultralytics")
    
    # Test pygame
    print("\n🎮 KIỂM TRA PYGAME:")
    try:
        import pygame
        print("✅ Pygame import thành công")
    except ImportError:
        print("⚠️  Pygame chưa cài đặt")
        print("💡 Chạy: pip3 install pygame")
    
    print("\n🎉 KIỂM TRA HOÀN THÀNH!")
    return True

if __name__ == "__main__":
    test_opencv()