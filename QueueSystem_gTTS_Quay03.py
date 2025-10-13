import tkinter as tk
from gtts import gTTS
import os
import tempfile
import time
import pygame

SERVER_URL = os.environ.get("QUEUE_SERVER_URL", "http://192.168.1.27:5000")

class QueueCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quầy 03 - Gọi số")
        self.root.geometry("360x220")

        self.title_label = tk.Label(root, text="Quầy 03", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.btn = tk.Button(root, text="Gọi số kế tiếp", font=("Arial", 14), command=self.call_next, width=16, height=2)
        self.btn.pack(pady=10)

        self.status_label = tk.Label(root, text="", font=("Arial", 11), fg="#006699")
        self.status_label.pack(pady=4)

    def play_audio(self, file_path):
        try:
            if os.path.exists(file_path):
                pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.quit()
            else:
                print(f"File {file_path} không tồn tại.")
        except Exception as e:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
            print(f"Lỗi phát file: {e}")

    def speak_text(self, text):
        try:
            tts = gTTS(text=text, lang='vi')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            temp_file.close()
            if os.path.exists(temp_file.name):
                self.play_audio(temp_file.name)
            time.sleep(0.5)
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass
        except Exception as e:
            print(f"Lỗi gTTS: {e}")

    def call_next(self):
        try:
            import requests
            resp = requests.post(f"{SERVER_URL}/api/next", json={"counter_id": "03"}, timeout=5)
            data = resp.json()
            ticket_str = data.get("ticket")
            if ticket_str:
                message = f"Quầy 03. Mời số {ticket_str}."
                self.speak_text(message)
                self.status_label.config(text=f"Đang phục vụ: {ticket_str} | Còn chờ: {data.get('remaining', 0)}")
            else:
                self.status_label.config(text="Không có khách chờ.")
        except Exception as e:
            self.status_label.config(text=f"Lỗi kết nối server: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QueueCounterApp(root)
    root.mainloop()