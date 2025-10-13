import tkinter as tk
import os
import datetime
import re
import tempfile

SERVER_URL = os.environ.get("QUEUE_SERVER_URL", "http://192.168.1.27:5000")

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

        for i in range(1, 7):
            btn = tk.Button(grid, text=f"Quầy {i:02d}", font=("Arial", 14), width=10, height=2,
                            command=lambda n=i: self.issue_ticket(n))
            r = (i-1)//3
            c = (i-1)%3
            btn.grid(row=r, column=c, padx=8, pady=8)

    def issue_ticket(self, counter_num: int):
        queue_name = f"Quầy {counter_num:02d}"
        try:
            import requests
            resp = requests.post(f"{SERVER_URL}/api/ticket", json={"counter_id": f"{counter_num:02d}"}, timeout=5)
            data = resp.json()
            ticket_str = data.get("ticket")
            if ticket_str:
                path = create_ticket_image(queue_name, ticket_str)
                self.status_label.config(text=f"Đã cấp số {ticket_str} cho {queue_name}. In: {os.path.basename(path)}")
            else:
                self.status_label.config(text="Không nhận được số từ server.")
        except Exception as e:
            self.status_label.config(text=f"Lỗi kết nối server: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()