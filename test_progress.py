#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để demo progress bar với fake translation data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

class ProgressTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Progress Bar")
        self.root.geometry("600x400")
        
        self.total_chunks = 0
        self.completed_chunks = 0
        self.start_time = 0
        self.is_running = False
        
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🧪 Test Progress Bar", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Progress frame
        progress_frame = tk.LabelFrame(main_frame, text="📊 Progress", 
                                      font=("Arial", 10, "bold"), padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status text
        self.progress_var = tk.StringVar(value="Sẵn sàng để bắt đầu...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Progress details frame
        details_frame = tk.Frame(progress_frame)
        details_frame.pack(fill=tk.X)
        
        # Progress percentage and ETA
        self.progress_details_var = tk.StringVar(value="")
        self.progress_details_label = tk.Label(details_frame, textvariable=self.progress_details_var, 
                                              font=("Arial", 9), fg="#666666")
        self.progress_details_label.pack(side=tk.LEFT)
        
        # Speed info
        self.speed_var = tk.StringVar(value="")
        self.speed_label = tk.Label(details_frame, textvariable=self.speed_var, 
                                   font=("Arial", 9), fg="#666666")
        self.speed_label.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_btn = tk.Button(control_frame, text="🚀 Bắt đầu Test", 
                                  command=self.start_test, bg='#27ae60', fg='white')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Dừng", 
                                 command=self.stop_test, bg='#e74c3c', fg='white', 
                                 state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ Test Settings", 
                                      font=("Arial", 10, "bold"), padx=15, pady=15)
        settings_frame.pack(fill=tk.X)
        
        # Total chunks setting
        chunks_frame = tk.Frame(settings_frame)
        chunks_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(chunks_frame, text="Tổng số chunks:").pack(side=tk.LEFT)
        self.total_chunks_var = tk.StringVar(value="50")
        chunks_entry = tk.Entry(chunks_frame, textvariable=self.total_chunks_var, width=10)
        chunks_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Speed setting
        speed_frame = tk.Frame(settings_frame)
        speed_frame.pack(fill=tk.X)
        
        tk.Label(speed_frame, text="Tốc độ (chunks/giây):").pack(side=tk.LEFT)
        self.speed_var_setting = tk.StringVar(value="2.0")
        speed_entry = tk.Entry(speed_frame, textvariable=self.speed_var_setting, width=10)
        speed_entry.pack(side=tk.LEFT, padx=(10, 0))
        
    def format_time(self, seconds):
        """Format seconds thành HH:MM:SS"""
        if seconds < 0:
            return "00:00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def update_progress(self, completed, total, start_time=None):
        """Cập nhật thanh tiến trình và thông tin chi tiết"""
        if total == 0:
            return
            
        # Tính phần trăm
        percentage = (completed / total) * 100
        self.progress_bar['value'] = percentage
        
        # Cập nhật thời gian
        current_time = time.time()
        if start_time is None:
            start_time = self.start_time
        
        elapsed_time = current_time - start_time
        
        # Tính ETA
        if completed > 0 and elapsed_time > 0:
            avg_time_per_chunk = elapsed_time / completed
            remaining_chunks = total - completed
            eta_seconds = avg_time_per_chunk * remaining_chunks
            eta_str = self.format_time(eta_seconds)
        else:
            eta_str = "Đang tính..."
        
        # Tính tốc độ
        if elapsed_time > 0:
            chunks_per_second = completed / elapsed_time
            if chunks_per_second >= 1:
                speed_str = f"{chunks_per_second:.1f} chunks/s"
            else:
                speed_str = f"{60/chunks_per_second:.1f}s/chunk"
        else:
            speed_str = "Đang tính..."
        
        # Cập nhật UI
        self.progress_details_var.set(f"{completed}/{total} chunks ({percentage:.1f}%) • ETA: {eta_str}")
        self.speed_var.set(f"Tốc độ: {speed_str}")
        
        # Update status
        if completed == total:
            self.progress_var.set("Hoàn thành!")
        else:
            self.progress_var.set(f"Đang xử lý... {percentage:.1f}%")
        
        self.root.update_idletasks()
    
    def start_test(self):
        """Bắt đầu test progress"""
        try:
            self.total_chunks = int(self.total_chunks_var.get())
            speed = float(self.speed_var_setting.get())
        except ValueError:
            tk.messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ")
            return
        
        self.completed_chunks = 0
        self.start_time = time.time()
        self.is_running = True
        
        # UI updates
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_var.set("Đang khởi tạo...")
        self.progress_details_var.set("")
        self.speed_var.set("")
        
        # Start simulation thread
        self.test_thread = threading.Thread(target=self.simulate_progress, args=(speed,), daemon=True)
        self.test_thread.start()
    
    def simulate_progress(self, speed):
        """Mô phỏng quá trình dịch"""
        delay = 1.0 / speed  # Delay giữa các chunks
        
        while self.completed_chunks < self.total_chunks and self.is_running:
            time.sleep(delay)
            if not self.is_running:
                break
                
            self.completed_chunks += 1
            self.update_progress(self.completed_chunks, self.total_chunks)
            
            # Simulate random delays (như trong thực tế)
            import random
            if random.random() < 0.1:  # 10% chance of slower chunk
                time.sleep(delay * 2)
        
        # Finished
        self.test_finished()
    
    def stop_test(self):
        """Dừng test"""
        self.is_running = False
        self.progress_var.set("Đã dừng")
        self.test_finished()
    
    def test_finished(self):
        """Cleanup sau khi test xong"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if self.completed_chunks >= self.total_chunks:
            self.progress_var.set("Hoàn thành!")
        elif not self.progress_var.get().startswith("Đã dừng"):
            self.progress_var.set("Sẵn sàng để bắt đầu...")
            self.progress_bar['value'] = 0
            self.progress_details_var.set("")
            self.speed_var.set("")

def main():
    root = tk.Tk()
    app = ProgressTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 