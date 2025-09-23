import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import time
import cv2
import threading

class QueueSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống lấy số thứ tự")
        self.root.geometry("400x350")
        
        # Khởi tạo dictionary để theo dõi số thứ tự cho mỗi quầy
        self.ticket_counters = {
            "Quầy 1": 0,
            "Quầy 2": 0,
            "Quầy 3": 0,
            "Quầy 4": 0,
            "Quầy 5": 0,
            "Quầy 6": 0
        }
        
        # Đường dẫn đến file .mp3 (nếu muốn dùng file .mp3 làm giọng phụ)
        self.mp3_files = {
            "Quầy 1": "voice_quay1.mp3",
            "Quầy 2": "voice_quay2.mp3",
            "Quầy 3": "voice_quay3.mp3",
            "Quầy 4": "voice_quay4.mp3",
            "Quầy 5": "voice_quay5.mp3",
            "Quầy 6": "voice_quay6.mp3"
        }
        
        # Tiêu đề
        self.title_label = tk.Label(root, text="Hệ thống lấy số thứ tự", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)
        
        # Khung chứa các nút quầy
        self.queue_frame = tk.Frame(root)
        self.queue_frame.pack(pady=10)
        
        # Danh sách các quầy
        queues = ["Quầy 1", "Quầy 2", "Quầy 3", "Quầy 4", "Quầy 5", "Quầy 6"]
        
        # Tạo nút cho từng quầy
        for i, queue in enumerate(queues):
            btn = tk.Button(self.queue_frame, text=queue, font=("Arial", 12), 
                           command=lambda q=queue: self.get_ticket(q),
                           width=12, height=2)
            btn.grid(row=i//2, column=i%2, padx=10, pady=5)
        
        # Nhãn hướng dẫn
        self.instruction_label = tk.Label(root, text="Vui lòng chọn quầy (Phát hiện khuôn mặt đang chạy)", 
                                        font=("Arial", 12))
        self.instruction_label.pack(pady=10)
        
        # Khởi tạo face detection
        self.face_cascade = cv2.CascadeClassifier('/đường/dẫn/đến/haarcascade_frontalface_default.xml')
        self.cap = cv2.VideoCapture(0)  # Mở webcam
        self.face_detected = False
        self.last_greeting_time = 0
        self.greeting_cooldown = 10  # Thời gian chờ giữa các lời chào (giây)
        
        # Bắt đầu luồng phát hiện khuôn mặt
        self.face_detection_thread = threading.Thread(target=self.face_detection_loop, daemon=True)
        self.face_detection_thread.start()

    def play_audio(self, file_path):
        """Phát file âm thanh bằng pydub"""
        try:
            if os.path.exists(file_path):
                audio = AudioSegment.from_mp3(file_path)
                play(audio)
                print(f"Đã phát file: {file_path}")
            else:
                print(f"File {file_path} không tồn tại.")
        except Exception as e:
            print(f"Lỗi phát file: {e}")
    
    def speak_text(self, text):
        """Hàm đọc to văn bản bằng gTTS hoặc file .mp3"""
        try:
            # Tạo audio từ gTTS và lưu tạm
            tts = gTTS(text=text, lang='vi')  # Ngôn ngữ tiếng Việt
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            temp_file.close()
            
            # Kiểm tra file tồn tại
            if os.path.exists(temp_file.name):
                self.play_audio(temp_file.name)
            else:
                raise Exception("File tạm không được tạo.")
            
            # Xóa file tạm sau khi phát
            time.sleep(0.5)