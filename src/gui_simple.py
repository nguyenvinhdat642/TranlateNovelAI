import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time
from datetime import datetime
import json

# Import translate functions
try:
    from translate import (
        translate_file_optimized, generate_output_filename,
        process_chunk, save_progress, get_progress, 
        CHUNK_SIZE_LINES, NUM_WORKERS, PROGRESS_FILE_SUFFIX
    )
    from reformat import fix_text_format
    TRANSLATE_AVAILABLE = True
except ImportError as e:
    TRANSLATE_AVAILABLE = False
    print(f"⚠️ Lỗi import translate: {e}")

# Import epub convert functions
try:
    from ConvertEpub import txt_to_docx, docx_to_epub
    EPUB_AVAILABLE = True
except ImportError as e:
    EPUB_AVAILABLE = False
    print(f"⚠️ Lỗi import ConvertEpub: {e}")

class TranslateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TranslateNovelAI - Dịch Truyện Tự Động")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar(value="gemini-2.0-flash")
        self.auto_reformat_var = tk.BooleanVar(value=True)
        self.auto_convert_epub_var = tk.BooleanVar(value=False)
        self.book_title_var = tk.StringVar()
        self.book_author_var = tk.StringVar(value="Unknown Author")
        self.chapter_pattern_var = tk.StringVar(value=r"^Chương\s+\d+:\s+.*$")
        self.is_translating = False
        self.translation_thread = None
        
        # Progress tracking variables
        self.total_chunks = 0
        self.completed_chunks = 0
        self.start_time = 0
        self.last_update_time = 0
        
        # Setup GUI first
        self.setup_gui()
        
        # Load saved settings after GUI is setup
        self.load_settings()
        
    def setup_gui(self):
        """Thiết lập giao diện chính"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🤖 TranslateNovelAI", 
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # API Key frame
        api_frame = tk.LabelFrame(main_frame, text="🔑 API Configuration", 
                                 font=("Arial", 10, "bold"), padx=15, pady=15)
        api_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(api_frame, text="Google AI API Key:").pack(anchor=tk.W)
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        api_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Bind event để tự động lưu API key khi thay đổi
        self.api_key_var.trace('w', self.on_api_key_changed)
        
        # Model selection
        model_frame = tk.Frame(api_frame)
        model_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            state="readonly",
            width=20
        )
        model_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # File selection frame
        file_frame = tk.LabelFrame(main_frame, text="📁 File Selection", 
                                  font=("Arial", 10, "bold"), padx=15, pady=15)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input file
        input_frame = tk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(input_frame, text="Input File:").pack(anchor=tk.W)
        
        input_path_frame = tk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        input_entry = tk.Entry(input_path_frame, textvariable=self.input_file_var)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        input_btn = tk.Button(
            input_path_frame,
            text="Browse",
            command=self.browse_input_file,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT
        )
        input_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Output file
        output_frame = tk.Frame(file_frame)
        output_frame.pack(fill=tk.X)
        
        tk.Label(output_frame, text="Output File (tự động tạo nếu để trống):").pack(anchor=tk.W)
        
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=(5, 0))
        
        output_entry = tk.Entry(output_path_frame, textvariable=self.output_file_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        output_btn = tk.Button(
            output_path_frame,
            text="Browse",
            command=self.browse_output_file,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT
        )
        output_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="⚙️ Options", 
                                     font=("Arial", 10, "bold"), padx=15, pady=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        reformat_check = tk.Checkbutton(
            options_frame,
            text="Tự động reformat file sau khi dịch",
            variable=self.auto_reformat_var
        )
        reformat_check.pack(anchor=tk.W)
        
        # EPUB conversion option
        epub_check = tk.Checkbutton(
            options_frame,
            text="Tự động convert sang EPUB sau khi dịch",
            variable=self.auto_convert_epub_var,
            command=self.toggle_epub_options
        )
        epub_check.pack(anchor=tk.W, pady=(5, 0))
        
        # EPUB settings frame (initially hidden)
        self.epub_settings_frame = tk.Frame(options_frame)
        
        # Book title
        title_frame = tk.Frame(self.epub_settings_frame)
        title_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(title_frame, text="Tiêu đề sách:").pack(side=tk.LEFT)
        title_entry = tk.Entry(title_frame, textvariable=self.book_title_var, width=30)
        title_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Book author
        author_frame = tk.Frame(self.epub_settings_frame)
        author_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(author_frame, text="Tác giả:").pack(side=tk.LEFT)
        author_entry = tk.Entry(author_frame, textvariable=self.book_author_var, width=30)
        author_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Chapter pattern
        pattern_frame = tk.Frame(self.epub_settings_frame)
        pattern_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(pattern_frame, text="Pattern chương:").pack(side=tk.LEFT)
        pattern_entry = tk.Entry(pattern_frame, textvariable=self.chapter_pattern_var, width=30)
        pattern_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.translate_btn = tk.Button(
            control_frame,
            text="🚀 Bắt Đầu Dịch",
            command=self.start_translation,
            bg='#27ae60',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            width=20
        )
        self.translate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️ Dừng",
            command=self.stop_translation,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_settings_btn = tk.Button(
            control_frame,
            text="💾 Lưu Cài Đặt",
            command=self.save_settings,
            bg='#f39c12',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            width=15
        )
        save_settings_btn.pack(side=tk.RIGHT)
        
        # Progress frame
        progress_frame = tk.LabelFrame(main_frame, text="📊 Progress", 
                                      font=("Arial", 10, "bold"), padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status text
        self.progress_var = tk.StringVar(value="Sẵn sàng để bắt đầu...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar (determinate mode)
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
        
        # Log frame
        log_frame = tk.LabelFrame(main_frame, text="📝 Logs", 
                                 font=("Arial", 10, "bold"), padx=15, pady=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_input_file(self):
        """Chọn file input"""
        file_path = filedialog.askopenfilename(
            title="Chọn file truyện cần dịch",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file_var.set(file_path)
            # Tự động tạo output filename
            if not self.output_file_var.get():
                output_path = generate_output_filename(file_path)
                self.output_file_var.set(output_path)
            
            # Tự động tạo tên sách từ tên file
            if not self.book_title_var.get():
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                # Loại bỏ "_TranslateAI" nếu có
                clean_name = file_name.replace("_TranslateAI", "")
                self.book_title_var.set(clean_name)
    
    def browse_output_file(self):
        """Chọn file output"""
        file_path = filedialog.asksaveasfilename(
            title="Chọn nơi lưu file đã dịch",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_file_var.set(file_path)
    
    def toggle_epub_options(self):
        """Hiện/ẩn EPUB settings khi checkbox được bật/tắt"""
        if self.auto_convert_epub_var.get():
            self.epub_settings_frame.pack(fill=tk.X, pady=(10, 0))
        else:
            self.epub_settings_frame.pack_forget()
    
    def on_api_key_changed(self, *args):
        """Tự động lưu API key khi thay đổi"""
        # Chỉ lưu nếu API key không rỗng và có độ dài hợp lý
        api_key = self.api_key_var.get().strip()
        if len(api_key) > 10:  # API key Google AI thường dài hơn 10 ký tự
            self.auto_save_settings()
    
    def log(self, message):
        """Ghi log vào text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
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
            self.progress_var.set(f"Đang dịch... {percentage:.1f}%")
        
        self.root.update_idletasks()
    
    def start_translation(self):
        """Bắt đầu quá trình dịch"""
        if not TRANSLATE_AVAILABLE:
            messagebox.showerror("Lỗi", "Không thể import module dịch. Vui lòng kiểm tra lại file translate.py")
            return
        
        # Validate EPUB conversion if enabled
        if self.auto_convert_epub_var.get():
            if not EPUB_AVAILABLE:
                messagebox.showerror("Lỗi", "Không thể import module ConvertEpub. Vui lòng kiểm tra lại file ConvertEpub.py")
                return
            
            if not self.book_title_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tiêu đề sách cho EPUB")
                return
            
        # Validate inputs
        if not self.api_key_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập API Key")
            return
            
        if not self.input_file_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng chọn file input")
            return
            
        if not os.path.exists(self.input_file_var.get()):
            messagebox.showerror("Lỗi", "File input không tồn tại")
            return
        
        # Prepare output file
        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = generate_output_filename(self.input_file_var.get())
            self.output_file_var.set(output_file)
        
        # Start translation in separate thread
        self.is_translating = True
        self.translate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Khởi tạo progress tracking
        self.total_chunks = 0
        self.completed_chunks = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # Reset progress UI
        self.progress_bar['value'] = 0
        self.progress_var.set("Đang khởi tạo...")
        self.progress_details_var.set("")
        self.speed_var.set("")
        
        self.translation_thread = threading.Thread(
            target=self.run_translation,
            args=(
                self.input_file_var.get(),
                output_file,
                self.api_key_var.get(),
                self.model_var.get()
            ),
            daemon=True
        )
        self.translation_thread.start()
    
    def run_translation(self, input_file, output_file, api_key, model_name):
        """Chạy quá trình dịch"""
        try:
            self.log("🚀 Bắt đầu quá trình dịch...")
            self.log(f"📁 Input: {os.path.basename(input_file)}")
            self.log(f"📁 Output: {os.path.basename(output_file)}")
            self.log(f"🤖 Model: {model_name}")
            
            self.progress_var.set("Đang dịch... Vui lòng chờ.")
            
            # Use wrapper function with basic progress
            self.log("🔧 Gọi translate wrapper...")
            success = self.translate_with_basic_progress(input_file, output_file, api_key, model_name)
            self.log(f"🔧 translate wrapper trả về: {success}")
            
            if success and self.is_translating:
                self.log("✅ Dịch hoàn thành!")
                
                # Auto reformat if enabled
                if self.auto_reformat_var.get():
                    self.log("🔧 Đang reformat file...")
                    try:
                        fix_text_format(output_file)
                        self.log("✅ Reformat hoàn thành!")
                    except Exception as e:
                        self.log(f"⚠️ Lỗi reformat: {e}")
                
                # Auto convert to EPUB if enabled
                if self.auto_convert_epub_var.get() and self.is_translating:
                    self.log("📚 Đang convert sang EPUB...")
                    self.progress_var.set("Đang convert EPUB...")
                    
                    try:
                        epub_success = self.convert_to_epub(output_file)
                        if epub_success:
                            self.log("✅ Convert EPUB hoàn thành!")
                        else:
                            self.log("⚠️ Convert EPUB thất bại!")
                    except Exception as e:
                        self.log(f"⚠️ Lỗi convert EPUB: {e}")
                
                self.progress_var.set("Hoàn thành!")
                
                result_message = f"Dịch hoàn thành!\nFile đã lưu: {output_file}"
                if self.auto_convert_epub_var.get():
                    epub_file = os.path.splitext(output_file)[0] + ".epub"
                    if os.path.exists(epub_file):
                        result_message += f"\nEPUB đã lưu: {epub_file}"
                
                messagebox.showinfo("Thành công", result_message)
            
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            self.translation_finished()
    
    def translate_with_basic_progress(self, input_file, output_file, api_key, model_name):
        """Wrapper function với basic progress tracking"""
        try:
            self.log("📊 Đọc file để tính progress...")
            
            # Đọc file để tính total chunks
            with open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
                all_lines = infile.readlines()
            
            total_lines = len(all_lines)
            self.total_chunks = (total_lines + CHUNK_SIZE_LINES - 1) // CHUNK_SIZE_LINES
            self.completed_chunks = get_progress(f"{input_file}{PROGRESS_FILE_SUFFIX}")
            
            self.log(f"📊 Tổng {total_lines} dòng, {self.total_chunks} chunks")
            self.log(f"📈 Đã hoàn thành {self.completed_chunks} chunks trước đó")
            
            # Set initial progress
            self.start_time = time.time()
            self.update_progress(self.completed_chunks, self.total_chunks)
            
            # Call original function
            success = translate_file_optimized(
                input_file=input_file,
                output_file=output_file,
                api_key=api_key,
                model_name=model_name
            )
            
            # Set final progress
            if success:
                self.update_progress(self.total_chunks, self.total_chunks)
            
            return success
            
        except Exception as e:
            self.log(f"❌ Lỗi trong wrapper: {e}")
            return False
    
    def translate_with_progress_OLD(self, input_file, output_file, api_key, model_name):
        """Custom translate function với progress tracking"""
        import concurrent.futures
        from translate import CAN_REFORMAT
        
        self.log("🔧 Khởi tạo translate_with_progress...")
        self.log(f"⚙️ Threads: {NUM_WORKERS}, Chunk size: {CHUNK_SIZE_LINES} dòng")
        
        progress_file_path = f"{input_file}{PROGRESS_FILE_SUFFIX}"
        
        try:
            # Đọc file và tính total chunks
            with open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
                all_lines = infile.readlines()
            
            total_lines = len(all_lines)
            self.total_chunks = (total_lines + CHUNK_SIZE_LINES - 1) // CHUNK_SIZE_LINES  # Ceiling division
            self.completed_chunks = get_progress(progress_file_path)
            
            self.log(f"📊 Tổng {total_lines} dòng, {self.total_chunks} chunks")
            self.log(f"📈 Đã hoàn thành {self.completed_chunks} chunks trước đó")
            
            # Cập nhật initial progress
            self.update_progress(self.completed_chunks, self.total_chunks)
            
            # Kiểm tra nếu đã hoàn thành
            if self.completed_chunks >= self.total_chunks:
                self.log("✅ File đã được dịch hoàn toàn")
                if os.path.exists(progress_file_path):
                    os.remove(progress_file_path)
                return True
            
            # Chia thành chunks
            chunks = []
            for i in range(0, total_lines, CHUNK_SIZE_LINES):
                chunk_lines = all_lines[i:i + CHUNK_SIZE_LINES]
                chunks.append((len(chunks), chunk_lines, i))
            
            # System instruction
            system_instruction = "Dịch văn bản sau sang tiếng Việt. Bối cảnh hiện đại. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặc trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung. Giữ nguyên các từ ngữ thô tục, tình dục."
            
            # Mở file output
            mode = 'a' if self.completed_chunks > 0 else 'w'
            with open(output_file, mode, encoding='utf-8') as outfile:
                
                translated_chunks_results = {}
                next_expected_chunk_to_write = self.completed_chunks
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                    
                    futures = {}
                    chunks_to_process = chunks[self.completed_chunks:]
                    
                    self.log(f"🚀 Bắt đầu xử lý {len(chunks_to_process)} chunks...")
                    
                    # Gửi chunks đến thread pool
                    for chunk_data in chunks_to_process:
                        if not self.is_translating:  # Kiểm tra stop
                            break
                        future = executor.submit(process_chunk, api_key, model_name, system_instruction, chunk_data)
                        futures[future] = chunk_data[0]
                    
                    # Thu thập kết quả
                    for future in concurrent.futures.as_completed(futures):
                        if not self.is_translating:  # Kiểm tra stop
                            break
                            
                        chunk_index = futures[future]
                        try:
                            result = future.result()
                            processed_chunk_index, translated_text, lines_count = result
                            
                            # Lưu kết quả
                            translated_chunks_results[processed_chunk_index] = (translated_text, lines_count)
                            
                            # Ghi các chunks theo thứ tự
                            while next_expected_chunk_to_write in translated_chunks_results:
                                chunk_text, chunk_lines_count = translated_chunks_results.pop(next_expected_chunk_to_write)
                                outfile.write(chunk_text)
                                if not chunk_text.endswith('\n'):
                                    outfile.write('\n')
                                outfile.flush()
                                
                                # Cập nhật progress
                                next_expected_chunk_to_write += 1
                                self.completed_chunks = next_expected_chunk_to_write
                                save_progress(progress_file_path, next_expected_chunk_to_write)
                                
                                # Cập nhật UI progress
                                self.update_progress(self.completed_chunks, self.total_chunks)
                                
                                self.log(f"✅ Chunk {next_expected_chunk_to_write}/{self.total_chunks}")
                                
                        except Exception as e:
                            self.log(f"❌ Lỗi chunk {chunk_index}: {e}")
                    
                    # Ghi chunks còn sót lại
                    if translated_chunks_results and self.is_translating:
                        sorted_remaining_chunks = sorted(translated_chunks_results.items())
                        for chunk_idx, (chunk_text, chunk_lines_count) in sorted_remaining_chunks:
                            try:
                                outfile.write(chunk_text)
                                if not chunk_text.endswith('\n'):
                                    outfile.write('\n')
                                outfile.flush()
                                next_expected_chunk_to_write += 1
                                self.completed_chunks = next_expected_chunk_to_write
                                save_progress(progress_file_path, next_expected_chunk_to_write)
                                self.update_progress(self.completed_chunks, self.total_chunks)
                            except Exception as e:
                                self.log(f"❌ Lỗi ghi chunk {chunk_idx}: {e}")
            
            # Kiểm tra hoàn thành
            if self.completed_chunks >= self.total_chunks and self.is_translating:
                self.log("✅ Dịch hoàn thành!")
                if os.path.exists(progress_file_path):
                    os.remove(progress_file_path)
                return True
            else:
                self.log("⚠️ Dịch bị gián đoạn")
                return False
                
        except FileNotFoundError as e:
            self.log(f"❌ Không tìm thấy file: {input_file}")
            self.log(f"❌ Chi tiết lỗi: {e}")
            return False
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            self.log(f"❌ Loại lỗi: {type(e).__name__}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    def convert_to_epub(self, txt_file):
        """Convert file txt thành epub"""
        try:
            # Tạo đường dẫn file
            base_name = os.path.splitext(txt_file)[0]
            docx_file = base_name + ".docx"
            epub_file = base_name + ".epub"
            
            # Lấy thông tin sách
            book_title = self.book_title_var.get().strip()
            book_author = self.book_author_var.get().strip()
            chapter_pattern = self.chapter_pattern_var.get().strip()
            
            self.log(f"📖 Tiêu đề: {book_title}")
            self.log(f"✍️ Tác giả: {book_author}")
            self.log(f"🔍 Pattern chương: {chapter_pattern}")
            
            # Bước 1: TXT -> DOCX
            self.log("📄 Đang convert TXT sang DOCX...")
            docx_success = txt_to_docx(txt_file, docx_file, book_title, chapter_pattern)
            
            if not docx_success:
                self.log("❌ Lỗi convert TXT sang DOCX")
                return False
            
            self.log("✅ Convert TXT sang DOCX thành công!")
            
            # Bước 2: DOCX -> EPUB
            self.log("📚 Đang convert DOCX sang EPUB...")
            epub_success = docx_to_epub(docx_file, epub_file, book_title, book_author)
            
            if epub_success:
                self.log(f"✅ EPUB đã được tạo: {os.path.basename(epub_file)}")
                # Xóa file DOCX tạm
                try:
                    os.remove(docx_file)
                    self.log("🗑️ Đã xóa file DOCX tạm")
                except:
                    pass
                return True
            else:
                self.log("❌ Lỗi convert DOCX sang EPUB")
                return False
                
        except Exception as e:
            self.log(f"❌ Lỗi convert EPUB: {e}")
            return False
    
    def stop_translation(self):
        """Dừng quá trình dịch"""
        self.is_translating = False
        self.log("⏹️ Đang dừng quá trình dịch...")
        self.progress_var.set("Đang dừng...")
        
    def translation_finished(self):
        """Cleanup sau khi dịch xong"""
        self.is_translating = False
        self.translate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if not self.progress_var.get().startswith("Hoàn thành"):
            self.progress_var.set("Sẵn sàng để bắt đầu...")
            self.progress_bar['value'] = 0
            self.progress_details_var.set("")
            self.speed_var.set("")
    
    def auto_save_settings(self):
        """Tự động lưu cài đặt im lặng (không hiện thông báo)"""
        settings = {
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "auto_reformat": self.auto_reformat_var.get(),
            "auto_convert_epub": self.auto_convert_epub_var.get(),
            "book_author": self.book_author_var.get(),
            "chapter_pattern": self.chapter_pattern_var.get(),
            "last_input_dir": os.path.dirname(self.input_file_var.get()) if self.input_file_var.get() else "",
            "last_output_dir": os.path.dirname(self.output_file_var.get()) if self.output_file_var.get() else ""
        }
        
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            pass  # Im lặng, không log lỗi
    
    def save_settings(self):
        """Lưu cài đặt với thông báo"""
        self.auto_save_settings()
        try:
            self.log("💾 Đã lưu cài đặt")
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
        except Exception as e:
            self.log(f"⚠️ Lỗi lưu cài đặt: {e}")
    
    def load_settings(self):
        """Load cài đặt đã lưu"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                # Load API key và hiển thị thông báo
                api_key = settings.get("api_key", "")
                if api_key:
                    self.api_key_var.set(api_key)
                    print(f"✅ Đã load API key từ settings: {api_key[:10]}***{api_key[-4:]}")
                
                self.model_var.set(settings.get("model", "gemini-2.0-flash"))
                self.auto_reformat_var.set(settings.get("auto_reformat", True))
                self.auto_convert_epub_var.set(settings.get("auto_convert_epub", False))
                self.book_author_var.set(settings.get("book_author", "Unknown Author"))
                self.chapter_pattern_var.set(settings.get("chapter_pattern", r"^Chương\s+\d+:\s+.*$"))
                
                # Update EPUB settings visibility
                self.toggle_epub_options()
                
            else:
                print("ℹ️ Chưa có file settings.json. API key sẽ được lưu tự động khi nhập.")
                
        except Exception as e:
            print(f"⚠️ Lỗi load cài đặt: {e}")

def main():
    """Main function"""
    # Create the main window
    root = tk.Tk()
    
    # Set icon (optional)
    try:
        root.iconbitmap("icon.ico")  # Nếu có file icon
    except:
        pass
    
    # Create and run app
    app = TranslateApp(root)
    
    # Handle window close
    def on_closing():
        if app.is_translating:
            if messagebox.askokcancel("Thoát", "Đang có quá trình dịch. Bạn có chắc muốn thoát?"):
                app.stop_translation()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 