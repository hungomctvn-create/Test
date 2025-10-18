import os
import time


def main():
    try:
        from picamera2 import Picamera2
    except Exception as e:
        raise RuntimeError("Picamera2 không khả dụng. Hãy cài đặt python3-picamera2 qua apt trên Raspberry Pi.") from e

    outdir = os.environ.get("DATASET_DIR", "/home/hungomctvn/dataset/images/train")
    count = int(os.environ.get("COUNT", "100"))
    os.makedirs(outdir, exist_ok=True)

    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (1280, 720)}))
    picam2.start()

    try:
        for i in range(count):
            filename = os.path.join(outdir, f"cccd_{i:04d}.jpg")
            picam2.capture_file(filename)
            print(f"Đã lưu: {filename}")
            time.sleep(1)
    finally:
        picam2.stop()


if __name__ == "__main__":
    main()