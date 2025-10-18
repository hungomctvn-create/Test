import os
import sys
import time
import cv2

CONF_DEFAULT = 0.5
CLASS_DEFAULT = 0  # class 'cccd'

MODEL_PATH = os.environ.get("MODEL_PATH", "/home/pi/yolov5/runs/train/exp/weights/best.pt")
SAVE_DIR = os.environ.get("SAVE_DIR", "/home/pi/cccd_photos")
CONF_THRESH = float(os.environ.get("CONF_THRESH", str(CONF_DEFAULT)))
CLASS_ID = int(os.environ.get("CLASS_ID", str(CLASS_DEFAULT)))


def get_model():
    """Load YOLOv5 model via yolov5 package; fallback to torch.hub if needed."""
    try:
        import yolov5
        model = yolov5.load(MODEL_PATH)
        try:
            model.conf = CONF_THRESH
        except Exception:
            pass
        print(f"Đã tải mô hình qua yolov5.load: {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"yolov5.load thất bại ({e}). Fallback sang torch.hub.")
        import torch
        # 'custom' sẽ tải mô hình từ trọng số local nếu có
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, source='local')
        try:
            model.conf = CONF_THRESH
        except Exception:
            pass
        print(f"Đã tải mô hình qua torch.hub: {MODEL_PATH}")
        return model


def setup_camera():
    """Try Picamera2 first; fallback to OpenCV webcam."""
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        print("Đã khởi tạo PiCamera2 ở 640x480")
        return ("picamera2", picam2)
    except Exception as e:
        print(f"Picamera2 không khả dụng ({e}). Dùng webcam qua OpenCV.")
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not cap.isOpened():
            raise RuntimeError("Không thể mở webcam (OpenCV)")
        return ("opencv", cap)


def read_frame(camtype, cam):
    if camtype == "picamera2":
        frame = cam.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame
    else:
        ret, frame = cam.read()
        if not ret:
            raise RuntimeError("Không đọc được khung hình từ webcam")
        return frame


def capture_image(camtype, cam, filename):
    # Với PiCamera2, chụp trực tiếp từ cảm biến để có chất lượng cao
    if camtype == "picamera2":
        time.sleep(1)  # ngắn để ổn định/ảnh rõ nét
        cam.capture_file(filename)
    else:
        frame = read_frame(camtype, cam)
        cv2.imwrite(filename, frame)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def parse_boxes(results):
    """Chuẩn hóa kết quả YOLOv5 về danh sách box: [x1,y1,x2,y2,conf,cls]."""
    if hasattr(results, "pred") and len(results.pred) > 0:
        return results.pred[0]
    if hasattr(results, "xyxy") and len(results.xyxy) > 0:
        return results.xyxy[0]
    # Một số bản có dạng .boxes.xyxy, .boxes.cls, .boxes.conf (như YOLOv8) – không dùng ở đây
    return []


def main():
    ensure_dir(SAVE_DIR)
    model = get_model()
    camtype, cam = setup_camera()

    cooldown_until = 0.0
    try:
        while True:
            frame = read_frame(camtype, cam)
            results = model(frame)
            boxes = parse_boxes(results)

            found = False
            # Lặp qua các detection
            for det in boxes:
                # det: [x1,y1,x2,y2,conf,cls]
                x1, y1, x2, y2 = map(int, det[:4])
                conf = float(det[4]) if len(det) > 4 else CONF_THRESH
                cls = int(det[5]) if len(det) > 5 else CLASS_ID
                if cls == CLASS_ID and conf >= CONF_THRESH:
                    found = True
                    # Vẽ khung để debug/quan sát
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"cccd {conf:.2f}",
                        (x1, max(0, y1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                    )

            now = time.time()
            if found and now >= cooldown_until:
                ts = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SAVE_DIR, f"cccd_{ts}.jpg")
                capture_image(camtype, cam, filename)
                print(f"Đã chụp: {filename}")
                cooldown_until = now + 5.0  # tránh chụp liên tục

            # Nếu dùng webcam (PC), hiển thị khung để quan sát
            if camtype == "opencv":
                cv2.imshow("CCCD Detector", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC để thoát
                    break

            time.sleep(0.1)  # giảm tải CPU

    except KeyboardInterrupt:
        pass
    finally:
        if camtype == "picamera2":
            try:
                cam.stop()
            except Exception:
                pass
        else:
            cam.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()