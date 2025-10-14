from flask import Flask, request, jsonify, render_template_string
from collections import deque
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import os
import json
from gtts import gTTS
import tempfile
try:
    import pygame
    _HAVE_PYGAME = True
except Exception:
    pygame = None
    _HAVE_PYGAME = False

app = Flask(__name__)

# State: per-counter queue and ticket issuance
lock = threading.Lock()
counters = {}
for i in range(1, 7):
    cid = f"{i:02d}"
    counters[cid] = {
        "next_ticket": 1,       # next ticket number to issue
        "queue": deque(),       # waiting tickets
        "serving": None,        # currently serving
        "served_count": 0       # served tickets count
    }

# ---- Persistence helpers ----
STATE_FILE = os.path.join(os.path.dirname(__file__), "queue_daily_state.json")

def _serialize_state():
    with lock:
        counters_data = {
            cid: {
                "next_ticket": counters[cid]["next_ticket"],
                "queue": list(counters[cid]["queue"]),
                "serving": counters[cid]["serving"],
                "served_count": counters[cid]["served_count"],
            }
            for cid in counters
        }
        total_waiting = sum(len(counters[c]["queue"]) for c in counters)
    return {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "total_waiting": total_waiting,
        "counters": counters_data,
    }

def _apply_state(state: dict):
    with lock:
        data = state.get("counters", {})
        for cid in counters:
            cdata = data.get(cid, {})
            counters[cid]["next_ticket"] = int(cdata.get("next_ticket", counters[cid]["next_ticket"]))
            q_list = cdata.get("queue", [])
            try:
                counters[cid]["queue"] = deque(q_list)
            except Exception:
                counters[cid]["queue"].clear()
                for item in q_list:
                    counters[cid]["queue"].append(str(item))
            counters[cid]["serving"] = cdata.get("serving")
            counters[cid]["served_count"] = int(cdata.get("served_count", counters[cid]["served_count"]))

def _save_state(path: str = STATE_FILE):
    state = _serialize_state()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return {"path": path, "ok": True}
    except Exception as e:
        return {"path": path, "ok": False, "error": str(e)}

def _load_state(path: str = STATE_FILE):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        _apply_state(state)
        return {"path": path, "ok": True}
    except Exception as e:
        return {"path": path, "ok": False, "error": str(e)}

# ---- In-terminal ASCII statistics table (prints every 5 seconds) ----
def _render_ascii_table():
    col1w, col2w = 10, 30
    border = "+" + "-" * col1w + "+" + "-" * col2w + "+"
    header = f"|{'Số quầy':^{col1w}}|{'Số khách chờ (Số lượng ticket)':^{col2w}}|"
    with lock:
        rows = [(cid, len(counters[cid]['queue'])) for cid in sorted(counters.keys())]
        total_waiting = sum(len(counters[c]['queue']) for c in counters)
    lines = [border, header, border]
    for cid, qlen in rows:
        lines.append(f"|{cid:^{col1w}}|{qlen:^{col2w}}|")
    lines.append(border)
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    return f"\n[Thống kê hàng chờ {ts}]\n" + "\n".join(lines) + f"\nTổng khách chờ: {total_waiting}\n"

def _console_stats_loop(interval_sec: int = 5):
    while True:
        try:
            print(_render_ascii_table(), flush=True)
        except Exception as e:
            print(f"[ConsoleStats] Lỗi khi in thống kê: {e}")
        time.sleep(interval_sec)

# Start background console stats thread
t_console = threading.Thread(target=_console_stats_loop, daemon=True)
t_console.start()

# ---- Autosave loop: save JSON state every N seconds ----
def _autosave_loop(interval_sec: int = 60, path: str = STATE_FILE):
    while True:
        res = _save_state(path)
        try:
            ok = res.get('ok')
            if ok:
                print(f"[Autosave] Saved state -> {res.get('path')} at {time.strftime('%H:%M:%S')}")
            else:
                print(f"[Autosave] Save failed: {res.get('error')}")
        except Exception:
            pass
        time.sleep(interval_sec)

# Start background autosave thread (default: every 60 seconds)
t_autosave = threading.Thread(target=_autosave_loop, daemon=True)
t_autosave.start()

# ---- TTS announcement helpers ----
ENABLE_TTS = True if os.environ.get('QUEUE_ENABLE_TTS', '1') == '1' else False

def _play_audio(file_path: str):
    try:
        if _HAVE_PYGAME:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
        else:
            # Fallback: mở bằng trình phát mặc định trên Windows (không chặn luồng)
            try:
                os.startfile(file_path)
            except Exception as e:
                print(f"[TTS] Fallback open failed: {e}")
    except Exception as e:
        try:
            if _HAVE_PYGAME:
                pygame.mixer.quit()
        except Exception:
            pass
        print(f"[TTS] Lỗi phát âm thanh: {e}")

def _speak_text_vi(text: str):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()
        tts = gTTS(text=text, lang='vi')
        tts.save(temp_path)
        _play_audio(temp_path)
        time.sleep(0.5)
        try:
            os.unlink(temp_path)
        except Exception:
            pass
    except Exception as e:
        print(f"[TTS] Lỗi gTTS: {e}")

def _announce_customer(counter_id: str, ticket_str: str):
    if not ENABLE_TTS:
        return
    try:
        # Ví dụ: "Mời Khách hàng có số thứ tự XXX của quầy số xx , đến quầy XX"
        # Chuẩn hóa: giữ định dạng 2 chữ số cho quầy
        cid2 = str(counter_id).zfill(2)
        message = f"Mời khách hàng có số thứ tự {ticket_str} của quầy số {cid2}, đến quầy {cid2}."
        threading.Thread(target=_speak_text_vi, args=(message,), daemon=True).start()
        print(f"[TTS] Announce -> counter={cid2} ticket={ticket_str}")
    except Exception as e:
        print(f"[TTS] Lỗi tạo thông điệp: {e}")

def format_ticket(n: int) -> str:
    return f"{n:03d}"

@app.get('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.get('/api/status')
def status():
    with lock:
        data = {
            cid: {
                "next_ticket": counters[cid]["next_ticket"],
                "queue_len": len(counters[cid]["queue"]),
                "serving": counters[cid]["serving"],
                "served_count": counters[cid]["served_count"],
            }
            for cid in counters
        }
    try:
        total_waiting = sum(v["queue_len"] for v in data.values())
        print(f"[API] /api/status -> total_waiting={total_waiting}", flush=True)
    except Exception:
        pass
    return jsonify(data)

# Trả về toàn bộ trạng thái chi tiết (bao gồm danh sách queue của từng quầy)
@app.get('/api/state')
def get_state():
    return jsonify(_serialize_state())

# Đếm số ticket chờ theo từng quầy (đơn giản, chỉ trả về số lượng chờ)
@app.get('/api/counts')
def counts():
    with lock:
        waiting_map = {cid: len(counters[cid]["queue"]) for cid in counters}
        issued_map = {cid: max(counters[cid]["next_ticket"] - 1, 0) for cid in counters}
        served_map = {cid: counters[cid]["served_count"] for cid in counters}

        details = {
            cid: {
                "waiting": waiting_map[cid],
                "issued": issued_map[cid],
                "served": served_map[cid],
            }
            for cid in counters
        }

        total_waiting = sum(waiting_map.values())
        total_issued = sum(issued_map.values())
        total_served = sum(served_map.values())

    # Giữ trường "counters" để tương thích ngược (waiting theo quầy)
    return jsonify({
        "counters": waiting_map,
        "details": details,
        "total_waiting": total_waiting,
        "total_issued": total_issued,
        "total_served": total_served
    })

# Simple live dashboard showing per-counter waiting counts
@app.get('/')
def form_view():
    html = """
    <!doctype html>
    <html lang="vi">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Biểu mẫu hàng chờ</title>
        <style>
          body { font-family: Segoe UI, Arial, sans-serif; margin: 20px; }
          h1 { font-size: 22px; margin-bottom: 12px; }
          .row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
          .label { width: 110px; font-weight: 600; }
          input[type="text"] { width: 160px; padding: 6px 8px; font-size: 16px; }
          input[readonly] { background: #f7f7f7; border: 1px solid #ccc; }
          .hint { color: #666; margin-bottom: 8px; }
        </style>
      </head>
      <body>
        <h1>Biểu mẫu hàng chờ</h1>
        <div class="hint">Các ô bên dưới tự cập nhật mỗi 5 giây</div>
        <div id="rows">Đang tải…</div>

        <script>
          const STATUS_URL = '/api/status';
          function refresh() {
            fetch(STATUS_URL).then(r => r.json()).then(data => {
              const keys = Object.keys(data).sort();
              const container = document.getElementById('rows');
              container.innerHTML = '';
              keys.forEach(cid => {
                const qlen = parseInt(data[cid].queue_len || 0);
                const row = document.createElement('div');
                row.className = 'row';
                row.innerHTML = `
                  <div class="label">Quầy số:</div>
                  <input type="text" value="${cid}" readonly />
                  <div class="label">Số khách chờ:</div>
                  <input type="text" value="${qlen}" readonly />
                `;
                container.appendChild(row);
              });
            }).catch(err => {
              document.getElementById('rows').textContent = 'Không lấy được dữ liệu: ' + err;
              console.error('status error', err);
            });
          }
          refresh();
          setInterval(refresh, 5000);
        </script>
      </body>
    </html>
    """
    return render_template_string(html)

# Lưu trạng thái hiện tại xuống file JSON
@app.post('/api/save')
def save_state():
    body = request.get_json(silent=True) or {}
    path = body.get('path')
    if not path:
        path = STATE_FILE
    result = _save_state(path)
    status_code = 200 if result.get('ok') else 500
    return jsonify(result), status_code

# Nạp trạng thái từ file JSON và áp vào bộ nhớ
@app.post('/api/load')
def load_state():
    body = request.get_json(silent=True) or {}
    path = body.get('path') or STATE_FILE
    result = _load_state(path)
    status_code = 200 if result.get('ok') else 500
    return jsonify(result), status_code

@app.post('/api/ticket')
def issue_ticket():
    body = request.get_json(silent=True) or {}
    counter_id = str(body.get('counter_id', '')).zfill(2)
    if counter_id not in counters:
        return jsonify({"error": "invalid counter_id"}), 400
    with lock:
        ticket_num = counters[counter_id]["next_ticket"]
        counters[counter_id]["next_ticket"] += 1
        ticket_str = format_ticket(ticket_num)
        counters[counter_id]["queue"].append(ticket_str)
        q_len = len(counters[counter_id]["queue"])
    print(f"[API] /api/ticket counter={counter_id} -> ticket={ticket_str} queue_len={q_len}", flush=True)
    return jsonify({
        "counter_id": counter_id,
        "ticket": ticket_str,
        "queue_len": q_len
    })

@app.post('/api/next')
def next_ticket():
    body = request.get_json(silent=True) or {}
    counter_id = str(body.get('counter_id', '')).zfill(2)
    if counter_id not in counters:
        return jsonify({"error": "invalid counter_id"}), 400
    with lock:
        if counters[counter_id]["queue"]:
            ticket_str = counters[counter_id]["queue"].popleft()
            counters[counter_id]["serving"] = ticket_str
            counters[counter_id]["served_count"] += 1
            remaining = len(counters[counter_id]["queue"])
            print(f"[API] /api/next counter={counter_id} -> serving={ticket_str} remaining={remaining}", flush=True)
            # Phát âm thanh thông báo (không chặn request)
            try:
                _announce_customer(counter_id, ticket_str)
            except Exception as e:
                print(f"[TTS] Lỗi gọi announce: {e}")
            return jsonify({
                "counter_id": counter_id,
                "ticket": ticket_str,
                "remaining": remaining
            })
        else:
            print(f"[API] /api/next counter={counter_id} -> no_waiting", flush=True)
            return jsonify({
                "counter_id": counter_id,
                "ticket": None,
                "remaining": 0,
                "message": "no_waiting"
            })

@app.post('/api/reset')
def reset_counter():
    body = request.get_json(silent=True) or {}
    counter_id = str(body.get('counter_id', '')).zfill(2)
    if counter_id not in counters:
        return jsonify({"error": "invalid counter_id"}), 400
    with lock:
        counters[counter_id]["next_ticket"] = 1
        counters[counter_id]["queue"].clear()
        counters[counter_id]["serving"] = None
        counters[counter_id]["served_count"] = 0
    return jsonify({"counter_id": counter_id, "status": "reset"})

if __name__ == '__main__':
    # Cho phép bật/tắt GUI qua biến môi trường
    # Mặc định KHÔNG mở GUI Tkinter; bật bằng QUEUE_ENABLE_GUI=1
    _env_flag = os.environ.get('QUEUE_ENABLE_GUI', '1')
    ENABLE_GUI = True if _env_flag == '1' else False

    # Tùy chọn: tự mở trình duyệt khi chạy (mặc định KHÔNG mở)
    # Bật bằng cách đặt biến môi trường QUEUE_OPEN_BROWSER=1
    _open_flag = os.environ.get('QUEUE_OPEN_BROWSER', '0')
    if _open_flag == '1':
        try:
            threading.Timer(1.0, lambda: webbrowser.open("http://192.168.1.27:5000/", new=0)).start()
        except Exception:
            pass

    if ENABLE_GUI:
        # Chạy Flask trong thread riêng để GUI hoạt động song song
        def _run_server():
            app.run(host='0.0.0.0', port=5000, use_reloader=False)

        server_thread = threading.Thread(target=_run_server, daemon=True)
        server_thread.start()

        # Tkinter dashboard giống GUI trong queue_server.py
        root = tk.Tk()
        root.title("Thống kê khách hàng")
        root.geometry("520x360")
        # Global background: deep blue (flight board style)
        root.configure(bg='#062e6f')

        try:
            root.attributes('-topmost', True)
            root.after(300, lambda: root.attributes('-topmost', False))
        except Exception:
            pass

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        # Set label default colors: deep blue background, white text
        style.configure('TLabel', background='#062e6f', foreground='#ffffff')
        # Selected row colors for Treeview
        style.map('Treeview', background=[('selected', '#1f6dbf')], foreground=[('selected', '#ffffff')])

        # Spacer đầu trang: tăng khoảng cách với đầu trang thêm ~80pt (đã +50pt)
        try:
            dpi_x = root.winfo_screenwidth() / (root.winfo_screenmmwidth() / 25.4)
            extra_px = int(dpi_x * (80.0 / 72.0))  # 80pt -> px theo DPI
        except Exception:
            extra_px = 106  # fallback ~80pt ở 96 DPI
        style.configure('Blue.TFrame', background='#062e6f')
        top_spacer = ttk.Frame(root, style='Blue.TFrame', height=extra_px)
        top_spacer.pack(fill='x')
        try:
            top_spacer.pack_propagate(False)
        except Exception:
            pass

        header = ttk.Label(root, text="BẢNG SỐ QUẦY / SỐ KHÁCH CHỜ", font=("Times New Roman", 32, "bold"))
        header.pack(pady=(10, 6))

        ts_label = ttk.Label(root, text="", font=("Times New Roman", 20))
        ts_label.pack(pady=(0, 6))

        # Khung chứa 2 bảng: bảng chính và bảng cột "Số thứ tự kế tiếp"
        table_frame = ttk.Frame(root)
        table_frame.pack(fill='both', expand=True, padx=10, pady=6)

        # Cột "Số quầy" riêng, thu chiều rộng còn 1/3 (≈30px)
        counter_columns = ("counter",)
        tree_counter = ttk.Treeview(table_frame, columns=counter_columns, show='headings')
        tree_counter.heading("counter", text="Số quầy")
        # Tăng 4 lần so với hiện trạng 30px -> 120px và cho phép co giãn
        tree_counter.column("counter", width=120, anchor="center", stretch=True)
        # Áp dụng font Times New Roman cỡ 20 cho hàng và tiêu đề bảng
        # Tăng chiều cao hàng (rowheight) ~ gấp đôi mặc định
        # Table colors: deep blue background, darker header like flight boards
        style.configure('Flat.Treeview', font=("Times New Roman", 20), rowheight=44,
                        background='#062e6f', fieldbackground='#062e6f', foreground='#ffffff',
                        borderwidth=0, relief='flat')
        style.map('Flat.Treeview', background=[('selected', '#1f6dbf')], foreground=[('selected', '#ffffff')])
        style.layout('Flat.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure('Treeview.Heading', font=("Times New Roman", 20, "bold"),
                        background='#0b3d91', foreground='#ffffff', borderwidth=0, relief='flat')
        tree_counter.configure(style='Flat.Treeview')
        # Dùng grid với tỉ lệ đều 1:1:1:1:1 cho 5 cột
        table_frame.columnconfigure(0, weight=1)
        table_frame.columnconfigure(1, weight=1)
        table_frame.columnconfigure(2, weight=1)
        table_frame.columnconfigure(3, weight=1)
        table_frame.columnconfigure(4, weight=1)
        table_frame.rowconfigure(0, weight=1)
        tree_counter.grid(row=0, column=0, sticky='nsew')

        # Cột "Đang phục vụ" tách riêng để chia đều với các cột còn lại
        serving_columns = ("serving",)
        tree_serving = ttk.Treeview(table_frame, columns=serving_columns, show='headings')
        tree_serving.heading("serving", text="Đang phục vụ")
        # Đồng bộ width để chia đều
        tree_serving.column("serving", width=120, anchor="center", stretch=True)
        tree_serving.configure(style='Flat.Treeview')
        tree_serving.grid(row=0, column=1, sticky='nsew')

        # Bảng giữa 1: chỉ cột "Số khách chờ" (màu đỏ sáng, đậm)
        waiting_columns = ("waiting",)
        tree_waiting = ttk.Treeview(table_frame, columns=waiting_columns, show='headings', style='Wait.Treeview')
        tree_waiting.heading("waiting", text="Số khách chờ")
        tree_waiting.column("waiting", width=120, minwidth=120, anchor="center")
        style.configure('Wait.Treeview', font=("Times New Roman", 20, "bold"), rowheight=44,
                        background='#062e6f', fieldbackground='#062e6f', foreground='#ff5252')
        style.map('Wait.Treeview', foreground=[('!selected', '#ff5252'), ('selected', '#ffffff')])
        style.configure('Wait.Treeview.Heading', font=("Times New Roman", 20, "bold"),
                        background='#0b3d91', foreground='#ffffff', borderwidth=0, relief='flat')
        style.layout('Wait.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        tree_waiting.column("waiting", minwidth=120, stretch=True)
        tree_waiting.grid(row=0, column=2, sticky='nsew')

        # Bảng giữa 2: chỉ cột "Đã phục vụ" (màu xanh lá sáng, đậm)
        served_columns = ("served",)
        tree_served = ttk.Treeview(table_frame, columns=served_columns, show='headings', style='Served.Treeview')
        tree_served.heading("served", text="Đã phục vụ")
        tree_served.column("served", width=120, minwidth=120, anchor="center")
        style.configure('Served.Treeview', font=("Times New Roman", 20, "bold"), rowheight=44,
                        background='#062e6f', fieldbackground='#062e6f', foreground='#00e676')
        style.map('Served.Treeview', foreground=[('!selected', '#00e676'), ('selected', '#ffffff')])
        style.configure('Served.Treeview.Heading', font=("Times New Roman", 20, "bold"),
                        background='#0b3d91', foreground='#ffffff', borderwidth=0, relief='flat')
        style.layout('Served.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        tree_served.column("served", minwidth=120, stretch=True)
        tree_served.grid(row=0, column=3, sticky='nsew')

        # Bảng phụ: chỉ cột "Số thứ tự kế tiếp" với style riêng (màu + đậm)
        next_columns = ("next",)
        tree_next = ttk.Treeview(table_frame, columns=next_columns, show='headings', style='Next.Treeview')
        tree_next.heading("next", text="Số thứ tự kế tiếp")
        tree_next.column("next", width=120, minwidth=120, anchor="center", stretch=True)
        style.configure('Next.Treeview', font=("Times New Roman", 20, "bold"), rowheight=44,
                        background='#062e6f', fieldbackground='#062e6f', foreground='#ffd54f')
        # Ép màu chữ vàng cho trạng thái thường, trắng khi được chọn
        style.map('Next.Treeview', foreground=[('!selected', '#ffd54f'), ('selected', '#ffffff')])
        # Làm phẳng bố cục để bỏ đường bao quanh
        style.layout('Next.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure('Next.Treeview.Heading', font=("Times New Roman", 20, "bold"),
                        background='#0b3d91', foreground='#ffffff', borderwidth=0, relief='flat')
        tree_next.grid(row=0, column=4, sticky='nsew')

        # Alternating row stripes (flight board style) cho cả hai bảng
        tree_counter.tag_configure('stripe_even', background='#083b7a', foreground='#ffffff')
        tree_counter.tag_configure('stripe_odd', background='#0d4ea5', foreground='#ffffff')
        tree_serving.tag_configure('stripe_even', background='#083b7a', foreground='#ffffff')
        tree_serving.tag_configure('stripe_odd', background='#0d4ea5', foreground='#ffffff')
        tree_waiting.tag_configure('stripe_even', background='#083b7a', foreground='#ff5252')
        tree_waiting.tag_configure('stripe_odd', background='#0d4ea5', foreground='#ff5252')
        tree_waiting.tag_configure('waiting_value', foreground='#ff5252', font=("Times New Roman", 20, "bold"))
        tree_served.tag_configure('stripe_even', background='#083b7a', foreground='#00e676')
        tree_served.tag_configure('stripe_odd', background='#0d4ea5', foreground='#00e676')
        tree_served.tag_configure('served_value', foreground='#00e676', font=("Times New Roman", 20, "bold"))
        tree_next.tag_configure('stripe_even', background='#083b7a', foreground='#ffd54f')
        tree_next.tag_configure('stripe_odd', background='#0d4ea5', foreground='#ffd54f')
        tree_next.tag_configure('next_value', foreground='#ffd54f', font=("Times New Roman", 20, "bold"))

        style.configure('Shutdown.TButton', font=("Times New Roman", 16, "bold"))
        footer_frame = ttk.Frame(root)
        footer_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        total_label = ttk.Label(footer_frame, text="Tổng khách chờ: 0", font=("Times New Roman", 20, "bold"))
        total_label.pack(side='left')

        def do_shutdown():
            try:
                if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn tắt máy ngay không?"):
                    try:
                        subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
                    except Exception as e:
                        messagebox.showerror("Lỗi", f"Không thể thực hiện tắt máy: {e}")
            except Exception:
                pass

        shutdown_button = ttk.Button(footer_frame, text="Tắt máy", style='Shutdown.TButton', command=do_shutdown)
        shutdown_button.pack(side='right')

        def refresh_gui():
            with lock:
                # Xóa và vẽ lại các bảng
                tree_counter.delete(*tree_counter.get_children())
                tree_serving.delete(*tree_serving.get_children())
                tree_waiting.delete(*tree_waiting.get_children())
                tree_served.delete(*tree_served.get_children())
                tree_next.delete(*tree_next.get_children())
                total_waiting = 0
                for i, cid in enumerate(sorted(counters.keys())):
                    q = counters[cid]["queue"]
                    waiting = len(q)
                    total_waiting += waiting
                    serving = counters[cid]["serving"] or "—"
                    served = counters[cid]["served_count"]
                    next_to_serve = q[0] if q else "—"
                    stripe = 'stripe_even' if i % 2 == 0 else 'stripe_odd'
                    tree_counter.insert('', 'end', values=(cid,), tags=(stripe,))
                    tree_serving.insert('', 'end', values=(serving,), tags=(stripe,))
                    tree_waiting.insert('', 'end', values=(waiting,), tags=(stripe, 'waiting_value'))
                    tree_served.insert('', 'end', values=(served,), tags=(stripe, 'served_value'))
                    tree_next.insert('', 'end', values=(next_to_serve,), tags=(stripe, 'next_value'))
                total_label.config(text=f"Tổng khách chờ: {total_waiting}")
            ts_label.config(text=time.strftime('%Y-%m-%d %H:%M:%S'))
            root.after(1000, refresh_gui)

        refresh_gui()
        root.mainloop()
    else:
        # Không bật GUI thì chỉ chạy server Flask
        app.run(host='0.0.0.0', port=5000, use_reloader=False)