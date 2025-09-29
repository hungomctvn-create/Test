#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script test camera đơn giản cho Raspberry Pi
Kiểm tra camera có hoạt động không và tìm camera index đúng
"""

import cv2
import sys
import time

def test_camera_index(index):
    """Test camera với index cụ thể"""
    print(f"🔍 Đang test camera index {index}...")
    
    try:
        cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            print(f"✗ Camera index {index}: Không thể mở")
            return False
            
        # Thử đọc frame
        ret, frame = cap.read()
        
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"✓ Camera index {index}: OK - Độ phân giải {width}x{height}")
            
            # Lưu ảnh test
            cv2.imwrite(f'test_camera_{index}.jpg', frame)
            print(f"  📸 Đã lưu ảnh test: test_camera_{index}.jpg")
            
            cap.release()
            return True
        else:
            print(f"✗ Camera index {index}: Không đọc được frame")
            cap.release()
            return False
            
    except Exception as e:
        print(f"✗ Camera index {index}: Lỗi - {str(e)}")
        return False

def main():
    print("======================================")
    print("    TEST CAMERA RASPBERRY PI")
    print("======================================")
    
    # Kiểm tra OpenCV
    print(f"📋 OpenCV version: {cv2.__version__}")
    
    working_cameras = []
    
    # Test các camera index từ 0 đến 4
    for i in range(5):
        if test_camera_index(i):
            working_cameras.append(i)
        time.sleep(0.5)  # Delay nhỏ giữa các test
    
    print("\n======================================")
    print("         KẾT QUẢ TEST CAMERA")
    print("======================================")
    
    if working_cameras:
        print(f"✅ Tìm thấy {len(working_cameras)} camera hoạt động:")
        for cam in working_cameras:
            print(f"   - Camera index {cam}")
        
        print(f"\n💡 Khuyến nghị: Sử dụng camera index {working_cameras[0]} trong code")
        print(f"   Thay đổi: cv2.VideoCapture({working_cameras[0]})")
        
    else:
        print("❌ Không tìm thấy camera nào hoạt động!")
        print("\n🔧 Hướng dẫn khắc phục:")
        print("1. Kiểm tra kết nối USB camera")
        print("2. Chạy: bash fix_camera_raspberry_pi.sh")
        print("3. Khởi động lại Raspberry Pi")
        print("4. Kiểm tra: ls -la /dev/video*")
    
    print("\n📝 File ảnh test đã được lưu (nếu có camera hoạt động)")

if __name__ == "__main__":
    main()