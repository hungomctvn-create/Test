import os
import sys
import time
try:
    import cv2
except Exception:
    cv2 = None

CONF_DEFAULT = 0.5
CLASS_DEFAULT = 0  # class 'cccd'

MODEL_PATH = os.environ.get("MODEL_PATH", "/home/hungomctvn/yolov5/runs/train/exp/weights/best.pt")
SAVE_DIR = os.environ.get("SAVE_DIR", "/home/hungomctvn/cccd_photos")
CONF_THRESH = float(os.environ.get("CONF_THRESH", str(CONF_DEFAULT)))
CLASS_ID = int(os.environ.get("CLASS_ID", str(CLASS_DEFAULT)))
EXPECTED_VENVS = [name.strip() for name in os.environ.get("EXPECTED_VENVS", "yolo5_env,myenv").split(",")]
YOLOV5_REPO = os.environ.get("YOLOV5_REPO", "/home/hungomctvn/yolov5")


def ensure_in_venv():
    venv_path = os.environ.get("VIRTUAL_ENV")
    venv_name = os.path.basename(venv_path) if venv_path else os.path.basename(sys.prefix)
    if venv_name in EXPECTED_VENVS:
        print(f"Đang chạy trong môi trường ảo: {venv_name} ({sys.executable})")
        return True
    else:
        print(f"CẢNH BÁO: Không thấy môi trường ảo tên trong {EXPECTED_VENVS}. Đang dùng: {venv_name or 'hệ thống' }.")
        print("Gợi ý kích hoạt:")
        print("  - Linux: 'source ~/yolo5_env/bin/activate' hoặc 'source ~/myenv/bin/activate'")
        print("  - Windows: '.\\yolo5_env\\Scripts\\activate' hoặc '.\\myenv\\Scripts\\activate'")
        return False


def check_dependencies():
    missing = []
    try:
        import torch  # noqa: F401
    except Exception:
        missing.append("torch")
    # yolov5 package là tùy chọn; nếu không có sẽ dùng torch.hub local
    try:
        import yolov5  # noqa: F401
    except Exception:
        pass
    if cv2 is None:
        # Chỉ cảnh báo, không bắt buộc nếu dùng PiCamera2
        print("CẢNH BÁO: OpenCV (cv2) chưa sẵn sàng. Nếu không có PiCamera2, cần cài 'opencv-python' trong venv.")
    if missing:
        raise RuntimeError(
            "Thiếu các phụ thuộc: " + ", ".join(missing) +
            "\nCài trong venv hiện tại: pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu"
        )


def get_model():
    """Load YOLOv5 model: ưu tiên yolov5 package; fallback torch.hub local repo."""
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
        print(f"yolov5.load thất bại ({e}). Fallback sang torch.hub local: {YOLOV5_REPO}")
        import torch
        if not os.path.exists(YOLOV5_REPO):
            print(f"Cảnh báo: Không tìm thấy YOLOV5_REPO tại '{YOLOV5_REPO}'. Hãy clone: git clone https://github.com/ultralytics/yolov5 {YOLOV5_REPO}")
        model = torch.hub.load(YOLOV5_REPO, 'custom', path=MODEL_PATH, source='local')
        try:
            model.conf = CONF_THRESH
        except Exception:
            pass
        print(f"Đã tải mô hình qua torch.hub local: {MODEL_PATH}")
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
        print(f"Picamera2 không khả dụng ({e}). Thử webcam qua OpenCV.")
        if cv2 is None:
            raise RuntimeError("OpenCV (cv2) không khả dụng trong môi trường ảo hiện tại. Cài: pip install opencv-python")
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
    # Kiểm tra venv và phụ thuộc trước khi chạy
    ensure_in_venv()
    check_dependencies()

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
                    # Vẽ khung để debug/quan sát (nếu có OpenCV)
                    if cv2 is not None:
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
            if camtype == "opencv" and cv2 is not None:
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
            if cv2 is not None:
                cv2.destroyAllWindows()


if __name__ == "__main__":
    main()