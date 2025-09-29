#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script để kiểm tra OpenCV và camera functionality
"""

import cv2
import sys
import os

def test_opencv_installation():
    """Test OpenCV installation và build info"""
    print("🔍 KIỂM TRA OPENCV INSTALLATION")
    print("=" * 50)
    
    try:
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Kiểm tra build information
        build_info = cv2.getBuildInformation()
        
        # Kiểm tra GUI support
        gui_support = "GTK" in build_info or "QT" in build_info
        print(f"{'✅' if gui_support else '❌'} GUI Support: {gui_support}")
        
        # Kiểm tra V4L2 support
        v4l2_support = "V4L/V4L2" in build_info or "V4L2" in build_info
        print(f"{'✅' if v4l2_support else '❌'} V4L2 Support: {v4l2_support}")
        
        # Kiểm tra video codec support
        ffmpeg_support = "FFMPEG" in build_info
        print(f"{'✅' if ffmpeg_support else '❌'} FFMPEG Support: {ffmpeg_support}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenCV Error: {e}")
        return False

def test_camera_devices():
    """Test camera devices có sẵn"""
    print("\n🎥 KIỂM TRA CAMERA DEVICES")
    print("=" * 50)
    
    available_cameras = []
    
    # Test từ 0 đến 4
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                height, width = frame.shape[:2]
                print(f"✅ Camera {i}: {width}x{height}")
                available_cameras.append(i)
            else:
                print(f"⚠️  Camera {i}: Opened but no frame")
            cap.release()
        else:
            print(f"❌ Camera {i}: Cannot open")
    
    return available_cameras

def test_camera_functionality(camera_id=0):
    """Test camera functionality chi tiết"""
    print(f"\n📹 TEST CAMERA {camera_id} FUNCTIONALITY")
    print("=" * 50)
    
    try:
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"❌ Cannot open camera {camera_id}")
            return False
        
        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Get actual properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"✅ Resolution: {width}x{height}")
        print(f"✅ FPS: {fps}")
        
        # Test frame capture
        ret, frame = cap.read()
        if ret and frame is not None:
            print("✅ Frame capture: SUCCESS")
            print(f"✅ Frame shape: {frame.shape}")
            
            # Test GUI display (nếu có)
            try:
                cv2.imshow('Test Camera', frame)
                cv2.waitKey(1000)  # Show for 1 second
                cv2.destroyAllWindows()
                print("✅ GUI Display: SUCCESS")
            except Exception as e:
                print(f"⚠️  GUI Display: {e}")
            
        else:
            print("❌ Frame capture: FAILED")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera test error: {e}")
        return False

def check_system_info():
    """Kiểm tra system information"""
    print("\n💻 SYSTEM INFORMATION")
    print("=" * 50)
    
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Platform: {sys.platform}")
    
    # Kiểm tra video devices trên Linux
    if sys.platform.startswith('linux'):
        try:
            video_devices = os.listdir('/dev/')
            video_devices = [d for d in video_devices if d.startswith('video')]
            print(f"✅ Video devices: {video_devices}")
        except:
            print("❌ Cannot list video devices")

def main():
    """Main test function"""
    print("🚀 OPENCV VÀ CAMERA TEST SUITE")
    print("=" * 60)
    
    # Test 1: OpenCV installation
    opencv_ok = test_opencv_installation()
    
    # Test 2: System info
    check_system_info()
    
    # Test 3: Camera devices
    available_cameras = test_camera_devices()
    
    # Test 4: Camera functionality
    if available_cameras:
        for camera_id in available_cameras[:2]:  # Test first 2 cameras
            camera_ok = test_camera_functionality(camera_id)
            if not camera_ok:
                break
    else:
        print("\n❌ No cameras available for testing")
    
    # Summary
    print("\n📋 SUMMARY")
    print("=" * 50)
    print(f"OpenCV: {'✅ OK' if opencv_ok else '❌ ERROR'}")
    print(f"Cameras: {'✅ OK' if available_cameras else '❌ ERROR'}")
    print(f"Available cameras: {available_cameras}")
    
    if opencv_ok and available_cameras:
        print("\n🎉 ALL TESTS PASSED! Ready to run main program.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED! Check errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)