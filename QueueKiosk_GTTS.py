import tkinter as tk
import os
import datetime
import re
import tempfile
import json
import threading
import time
from gtts import gTTS
import pygame

SERVER_URL = os.environ.get("QUEUE_SERVER_URL", "http://192.168.1.27:5000")

# Lưu mốc ngày lần cuối reset để đảm bảo sang ngày mới bắt đầu lại từ 001
STATE_FILE = os.path.join(os.path.dirname(__file__), "kiosk_last_day.json")

def _load_last_day():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("last_day")
    except Exception:
        pass
    return None

def _save_last_day(day_str: str):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_day": day_str}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def ensure_daily_reset(status_cb=None):
    """Nếu sang ngày mới, gọi API reset cho tất cả các quầy rồi lưu ngày hiện tại.
    status_cb: hàm nhận chuỗi để hiển thị trạng thái lên giao diện (tùy chọn)
    """
    today = datetime.date.today().isoformat()
    last_day = _load_last_day()
    if last_day == today:
        return
    try:
        import requests
        for i in range(1, 7):
            cid = f"{i:02d}"
            try:
                requests.post(f"{SERVER_URL}/api/reset", json={"counter_id": cid}, timeout=4)
            except Exception:
                # Không chặn luồng nếu một quầy reset lỗi; tiếp tục các quầy khác
                pass
        _save_last_day(today)
        if status_cb:
            status_cb(f"Đã reset số thứ tự cho ngày mới: {today}")
    except Exception as e:
        if status_cb:
            status_cb(f"Không reset được cho ngày mới: {e}")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None
    PIL_AVAILABLE = False

def find_vietnamese_font():
    try:
        font_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        for name in ["segoeui.ttf", "arial.ttf", "tahoma.ttf", "verdana.ttf", "DejaVuSans.ttf"]:
            path = os.path.join(font_dir, name)
            if os.path.exists(path):
                return path
    except Exception:
        pass
    return None

def create_ticket_image(queue_name: str, ticket_str: str) -> str:
    out_dir = os.path.join(os.path.dirname(__file__), "tickets")
    os.makedirs(out_dir, exist_ok=True)
    filename = f"ticket_{queue_name.replace(' ', '')}_{ticket_str}.png"
    save_path = os.path.join(out_dir, filename)
    width, height = 400, 300

    data_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if PIL_AVAILABLE:
        base = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(base)
        font_path = find_vietnamese_font()
        try:
            font_title = ImageFont.truetype(font_path, 24) if font_path else None
            font_body  = ImageFont.truetype(font_path, 20) if font_path else None
        except Exception:
            font_title = None
            font_body = None
        print(f"Pillow available, font_path={font_path}")
        draw.text((20, 15), "SỐ THỨ TỰ", fill=(0, 0, 0), font=font_title)
        queue_num = re.findall(r"\d+", queue_name)
        queue_num = queue_num[0] if queue_num else ""
        draw.text((220, 90), f"QUẦY SỐ: {queue_num}", fill=(0, 0, 0), font=font_body)
        draw.text((220, 130), f"SỐ: {ticket_str}", fill=(0, 0, 0), font=font_body)
        draw.text((220, 170), data_time, fill=(0, 0, 0), font=font_body)
        base.save(save_path)
    else:
        save_path = os.path.join(out_dir, f"ticket_{queue_name.replace(' ', '')}_{ticket_str}.txt")
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"SỐ THỨ TỰ\n{queue_name}\nSố: {ticket_str}\n{data_time}\n")
    try:
        if os.name == "nt":
            os.startfile(save_path, "print")
    except Exception:
        try:
            os.startfile(save_path)
        except Exception:
            pass
    return save_path

class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Máy bấm số - Kiosk")
        self.root.geometry("420x320")

        self.title_label = tk.Label(root, text="Chọn quầy để lấy số", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        grid = tk.Frame(root)
        grid.pack(pady=10)

        self.status_label = tk.Label(root, text="", font=("Arial", 11), fg="#006699")
        self.status_label.pack(pady=6)

        # Bảo đảm sang ngày mới thì reset tất cả các quầy về 001
        ensure_daily_reset(status_cb=lambda msg: self.status_label.config(text=msg))

        for i in range(1, 7):
            btn = tk.Button(grid, text=f"Quầy {i:02d}", font=("Arial", 14), width=10, height=2,
                            command=lambda n=i: self.issue_ticket(n))
            r = (i-1)//3
            c = (i-1)%3
            btn.grid(row=r, column=c, padx=8, pady=8)

        # Khởi tạo pygame mixer cho phát âm thanh (nếu chưa có)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            # Không chặn ứng dụng nếu mixer lỗi khởi tạo
            pass

    def speak_text(self, text: str):
        """Chuyển văn bản thành giọng nói tiếng Việt bằng gTTS và phát âm.
        Chạy đồng bộ; nên gọi qua speak_text_async để không chặn UI.
        """
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(tmp_fd)
        try:
            # Sinh file âm thanh từ gTTS
            tts = gTTS(text=text, lang="vi")
            tts.save(tmp_path)

            # Phát bằng pygame nếu khả dụng, fallback mở bằng hệ điều hành
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(tmp_path)
                pygame.mixer.music.play()
                # Chờ phát xong để không xóa file sớm
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception:
                try:
                    # Fallback mở bằng trình phát mặc định của hệ điều hành
                    os.startfile(tmp_path)
                    time.sleep(3)
                except Exception:
                    pass
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def speak_text_async(self, text: str):
        """Phát giọng nói ở nền để không chặn giao diện."""
        threading.Thread(target=self.speak_text, args=(text,), daemon=True).start()

    def issue_ticket(self, counter_num: int):
        queue_name = f"Quầy {counter_num:02d}"
        try:
            # Kiểm tra lại mốc ngày ngay trước khi cấp số (trường hợp app chạy qua đêm)
            ensure_daily_reset(status_cb=lambda msg: self.status_label.config(text=msg))
            import requests
            resp = requests.post(f"{SERVER_URL}/api/ticket", json={"counter_id": f"{counter_num:02d}"}, timeout=5)
            data = resp.json()
            ticket_str = data.get("ticket")
            if ticket_str:
                path = create_ticket_image(queue_name, ticket_str)
                self.status_label.config(text=f"Đã cấp số {ticket_str} cho {queue_name}. In: {os.path.basename(path)}")
                # Đọc to nội dung số vừa cấp bằng gTTS
                message = f"{queue_name}. Số thứ tự của bạn là {ticket_str}."
                self.speak_text_async(message)
            else:
                self.status_label.config(text="Không nhận được số từ server.")
        except Exception as e:
            self.status_label.config(text=f"Lỗi kết nối server: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()