import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from gtts import gTTS
import pygame
from datetime import datetime

class LaySoTuDong:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hệ Thống Lấy Số Tự Động")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Khởi tạo pygame mixer cho âm thanh
        pygame.mixer.init()
        
        # Dữ liệu quầy
        self.so_hien_tai = 1  # Số thứ tự hiện tại (bắt đầu từ 1)
        self.quay_data = {
            f"Quầy {i}": {
                "so_dang_phuc_vu": "000",
                "tong_so_da_phuc_vu": 0,
                "trang_thai": "Sẵn sàng"
            } for i in range(1, 7)
        }
        
        # Tải dữ liệu đã lưu
        self.load_data()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Cập nhật hiển thị
        self.update_display()
    
    def create_widgets(self):
        # Tiêu đề chính
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="HỆ THỐNG LẤY SỐ TỰ ĐỘNG", 
                              font=("Arial", 24, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        # Frame chính
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame trái - Lấy số
        left_frame = tk.Frame(main_frame, bg="#ecf0f1", relief="raised", bd=2)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Tiêu đề lấy số
        tk.Label(left_frame, text="LẤY SỐ THỨ TỰ", font=("Arial", 18, "bold"), 
                bg="#ecf0f1", fg="#2c3e50").pack(pady=20)
        
        # Hiển thị số hiện tại
        self.current_number_frame = tk.Frame(left_frame, bg="#3498db", relief="raised", bd=3)
        self.current_number_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(self.current_number_frame, text="SỐ TIẾP THEO", 
                font=("Arial", 14, "bold"), bg="#3498db", fg="white").pack(pady=5)
        
        self.current_number_label = tk.Label(self.current_number_frame, text="001", 
                                           font=("Arial", 48, "bold"), bg="#3498db", fg="white")
        self.current_number_label.pack(pady=10)
        
        # Nút lấy số
        self.lay_so_btn = tk.Button(left_frame, text="LẤY SỐ", font=("Arial", 20, "bold"),
                                   bg="#e74c3c", fg="white", height=2, width=15,
                                   command=self.lay_so, relief="raised", bd=3)
        self.lay_so_btn.pack(pady=30)
        
        # Thông tin thống kê
        stats_frame = tk.Frame(left_frame, bg="#ecf0f1")
        stats_frame.pack(pady=20, padx=20, fill="x")
        
        tk.Label(stats_frame, text="THỐNG KÊ HÔM NAY", font=("Arial", 14, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack()
        
        self.stats_label = tk.Label(stats_frame, text="Tổng số đã phục vụ: 0", 
                                   font=("Arial", 12), bg="#ecf0f1", fg="#7f8c8d")
        self.stats_label.pack(pady=5)
        
        # Frame phải - Quầy phục vụ
        right_frame = tk.Frame(main_frame, bg="#ecf0f1", relief="raised", bd=2)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Tiêu đề quầy phục vụ
        tk.Label(right_frame, text="QUẦY PHỤC VỤ", font=("Arial", 18, "bold"),
                bg="#ecf0f1", fg="#2c3e50").pack(pady=20)
        
        # Tạo frame cho 6 quầy (2 hàng x 3 cột)
        quay_container = tk.Frame(right_frame, bg="#ecf0f1")
        quay_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.quay_frames = {}
        self.quay_labels = {}
        self.quay_buttons = {}
        
        for i in range(6):
            row = i // 3
            col = i % 3
            
            quay_name = f"Quầy {i+1}"
            
            # Frame cho mỗi quầy
            quay_frame = tk.Frame(quay_container, bg="#34495e", relief="raised", bd=3)
            quay_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Tên quầy
            tk.Label(quay_frame, text=quay_name, font=("Arial", 14, "bold"),
                    bg="#34495e", fg="white").pack(pady=5)
            
            # Số đang phục vụ
            number_frame = tk.Frame(quay_frame, bg="#2ecc71")
            number_frame.pack(pady=5, padx=10, fill="x")
            
            tk.Label(number_frame, text="Đang phục vụ:", font=("Arial", 10),
                    bg="#2ecc71", fg="white").pack()
            
            number_label = tk.Label(number_frame, text="000", font=("Arial", 24, "bold"),
                                  bg="#2ecc71", fg="white")
            number_label.pack()
            
            # Nút gọi số
            call_btn = tk.Button(quay_frame, text="GỌI SỐ TIẾP THEO", 
                               font=("Arial", 10, "bold"), bg="#f39c12", fg="white",
                               command=lambda q=quay_name: self.goi_so_tiep_theo(q))
            call_btn.pack(pady=5, padx=10, fill="x")
            
            # Nút hoàn thành
            complete_btn = tk.Button(quay_frame, text="HOÀN THÀNH", 
                                   font=("Arial", 10, "bold"), bg="#27ae60", fg="white",
                                   command=lambda q=quay_name: self.hoan_thanh(q))
            complete_btn.pack(pady=5, padx=10, fill="x")
            
            # Lưu references
            self.quay_frames[quay_name] = quay_frame
            self.quay_labels[quay_name] = number_label
            self.quay_buttons[quay_name] = {"call": call_btn, "complete": complete_btn}
        
        # Cấu hình grid weights
        for i in range(2):
            quay_container.grid_rowconfigure(i, weight=1)
        for i in range(3):
            quay_container.grid_columnconfigure(i, weight=1)
        
        # Frame điều khiển dưới cùng
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Nút reset
        reset_btn = tk.Button(control_frame, text="RESET HỆ THỐNG", 
                            font=("Arial", 12, "bold"), bg="#e67e22", fg="white",
                            command=self.reset_system)
        reset_btn.pack(side="left", padx=10)
        
        # Hiển thị thời gian
        self.time_label = tk.Label(control_frame, text="", font=("Arial", 12),
                                 bg="#f0f0f0", fg="#7f8c8d")
        self.time_label.pack(side="right", padx=10)
        
        # Cập nhật thời gian
        self.update_time()
    
    def lay_so(self):
        """Lấy số thứ tự mới"""
        so_moi = f"{self.so_hien_tai:03d}"
        
        # Phát âm thanh thông báo
        self.phat_am_thanh(f"Quý khách vừa lấy số {so_moi}. Xin vui lòng chờ được gọi.")
        
        # Cập nhật số hiện tại
        self.so_hien_tai += 1
        self.current_number_label.config(text=f"{self.so_hien_tai:03d}")
        
        # Lưu dữ liệu
        self.save_data()
        
        # Hiển thị thông báo
        messagebox.showinfo("Lấy số thành công", f"Bạn đã lấy số: {so_moi}")
    
    def goi_so_tiep_theo(self, quay_name):
        """Gọi số tiếp theo cho quầy"""
        # Tìm số nhỏ nhất chưa được phục vụ
        so_goi = None
        for i in range(1, self.so_hien_tai):
            so_str = f"{i:03d}"
            # Kiểm tra xem số này đã được gọi chưa
            da_goi = False
            for q_name, q_data in self.quay_data.items():
                if q_data["so_dang_phuc_vu"] == so_str:
                    da_goi = True
                    break
            
            if not da_goi:
                so_goi = so_str
                break
        
        if so_goi:
            # Cập nhật số đang phục vụ
            self.quay_data[quay_name]["so_dang_phuc_vu"] = so_goi
            self.quay_data[quay_name]["trang_thai"] = "Đang phục vụ"
            
            # Cập nhật hiển thị
            self.quay_labels[quay_name].config(text=so_goi)
            
            # Phát âm thanh gọi số
            quay_so = quay_name.split()[1]  # Lấy số quầy
            self.phat_am_thanh(f"Mời số {so_goi} đến {quay_name} để được phục vụ.")
            
            # Lưu dữ liệu
            self.save_data()
        else:
            messagebox.showinfo("Thông báo", "Không có số nào đang chờ!")
    
    def hoan_thanh(self, quay_name):
        """Hoàn thành phục vụ khách hàng"""
        if self.quay_data[quay_name]["so_dang_phuc_vu"] != "000":
            # Cập nhật thống kê
            self.quay_data[quay_name]["tong_so_da_phuc_vu"] += 1
            self.quay_data[quay_name]["so_dang_phuc_vu"] = "000"
            self.quay_data[quay_name]["trang_thai"] = "Sẵn sàng"
            
            # Cập nhật hiển thị
            self.quay_labels[quay_name].config(text="000")
            self.update_stats()
            
            # Lưu dữ liệu
            self.save_data()
            
            messagebox.showinfo("Thông báo", f"{quay_name} đã hoàn thành phục vụ!")
        else:
            messagebox.showwarning("Cảnh báo", f"{quay_name} chưa có khách hàng nào!")
    
    def phat_am_thanh(self, text):
        """Phát âm thanh thông báo"""
        def play_audio():
            try:
                # Tạo file âm thanh tạm thời
                tts = gTTS(text=text, lang='vi', slow=False)
                temp_file = "temp_audio.mp3"
                tts.save(temp_file)
                
                # Phát âm thanh
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                # Chờ phát xong rồi xóa file tạm
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                os.remove(temp_file)
            except Exception as e:
                print(f"Lỗi phát âm thanh: {e}")
        
        # Chạy trong thread riêng để không block UI
        threading.Thread(target=play_audio, daemon=True).start()
    
    def update_stats(self):
        """Cập nhật thống kê"""
        tong_da_phuc_vu = sum(data["tong_so_da_phuc_vu"] for data in self.quay_data.values())
        self.stats_label.config(text=f"Tổng số đã phục vụ: {tong_da_phuc_vu}")
    
    def update_display(self):
        """Cập nhật hiển thị"""
        self.current_number_label.config(text=f"{self.so_hien_tai:03d}")
        
        for quay_name, data in self.quay_data.items():
            self.quay_labels[quay_name].config(text=data["so_dang_phuc_vu"])
        
        self.update_stats()
    
    def update_time(self):
        """Cập nhật thời gian hiện tại"""
        current_time = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def reset_system(self):
        """Reset hệ thống"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn reset hệ thống?"):
            self.so_hien_tai = 1
            for quay_name in self.quay_data:
                self.quay_data[quay_name] = {
                    "so_dang_phuc_vu": "000",
                    "tong_so_da_phuc_vu": 0,
                    "trang_thai": "Sẵn sàng"
                }
            
            self.update_display()
            self.save_data()
            messagebox.showinfo("Thông báo", "Hệ thống đã được reset!")
    
    def save_data(self):
        """Lưu dữ liệu vào file"""
        data = {
            "so_hien_tai": self.so_hien_tai,
            "quay_data": self.quay_data,
            "ngay_luu": datetime.now().strftime("%Y-%m-%d")
        }
        
        try:
            with open("lay_so_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu dữ liệu: {e}")
    
    def load_data(self):
        """Tải dữ liệu từ file"""
        try:
            if os.path.exists("lay_so_data.json"):
                with open("lay_so_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Kiểm tra xem có phải ngày mới không
                ngay_hien_tai = datetime.now().strftime("%Y-%m-%d")
                if data.get("ngay_luu") == ngay_hien_tai:
                    self.so_hien_tai = data.get("so_hien_tai", 1)
                    self.quay_data.update(data.get("quay_data", {}))
                else:
                    # Ngày mới, reset dữ liệu
                    self.reset_system()
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

if __name__ == "__main__":
    # Kiểm tra và cài đặt các thư viện cần thiết
    try:
        import pygame
        from gtts import gTTS
    except ImportError as e:
        print("Vui lòng cài đặt các thư viện cần thiết:")
        print("pip install pygame gtts")
        exit(1)
    
    app = LaySoTuDong()
    app.run()