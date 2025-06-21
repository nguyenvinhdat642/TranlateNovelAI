import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time
from datetime import datetime
import json
import re

# Import translate functions
try:
    from translate import translate_file_optimized, generate_output_filename
    from reformat import fix_text_format
    from ConvertEpub import txt_to_docx, docx_to_epub
    TRANSLATE_AVAILABLE = True
    EPUB_AVAILABLE = True
except ImportError as e:
    TRANSLATE_AVAILABLE = False
    EPUB_AVAILABLE = False
    print(f"⚠️ Lỗi import: {e}")

class TranslateNovelAI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 TranslateNovelAI")
        self.root.geometry("900x700")
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
        
        # Translation state
        self.is_translating = False
        self.translation_thread = None
        self.total_chunks = 0
        self.completed_chunks = 0
        self.start_time = 0
        
        # Setup GUI
        self.setup_gui()
        
        # Load settings
        self.load_settings()
        
    def setup_gui(self):
        """Thiết lập giao diện chính với tabs"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🤖 TranslateNovelAI", 
            font=("Arial", 24, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_translate_tab()
        self.create_settings_tab()
        self.create_epub_tab()
        self.create_logs_tab()
        
    def create_translate_tab(self):
        """Tab chính cho dịch truyện"""
        translate_frame = ttk.Frame(self.notebook)
        self.notebook.add(translate_frame, text="🚀 Dịch Truyện")
        
        # API Configuration
        api_frame = tk.LabelFrame(translate_frame, text="🔑 API Configuration", 
                                 font=("Arial", 10, "bold"), padx=15, pady=15)
        api_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(api_frame, text="Google AI API Key:").pack(anchor=tk.W)
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        api_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Model selection
        model_frame = tk.Frame(api_frame)
        model_frame.pack(fill=tk.X)
        
        tk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            state="readonly",
            width=20
        )
        model_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # File Selection
        file_frame = tk.LabelFrame(translate_frame, text="📁 File Selection", 
                                  font=("Arial", 10, "bold"), padx=15, pady=15)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Input file
        tk.Label(file_frame, text="Input File:").pack(anchor=tk.W)
        input_path_frame = tk.Frame(file_frame)
        input_path_frame.pack(fill=tk.X, pady=(5, 10))
        
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
        tk.Label(file_frame, text="Output File (tự động tạo nếu để trống):").pack(anchor=tk.W)
        output_path_frame = tk.Frame(file_frame)
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
        
        # Options
        options_frame = tk.LabelFrame(translate_frame, text="⚙️ Options", 
                                     font=("Arial", 10, "bold"), padx=15, pady=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        reformat_check = tk.Checkbutton(
            options_frame,
            text="✅ Tự động reformat file sau khi dịch",
            variable=self.auto_reformat_var
        )
        reformat_check.pack(anchor=tk.W)
        
        epub_check = tk.Checkbutton(
            options_frame,
            text="📚 Tự động convert sang EPUB sau khi dịch",
            variable=self.auto_convert_epub_var,
            command=self.toggle_epub_options
        )
        epub_check.pack(anchor=tk.W, pady=(5, 0))
        
        # Control buttons
        control_frame = tk.Frame(translate_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.translate_btn = tk.Button(
            control_frame,
            text="🚀 Bắt Đầu Dịch",
            command=self.start_translation,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
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
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_btn = tk.Button(
            control_frame,
            text="💾 Lưu Cài Đặt",
            command=self.save_settings,
            bg='#f39c12',
            fg='white',
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            width=15
        )
        save_btn.pack(side=tk.RIGHT)
        
        # Progress
        progress_frame = tk.LabelFrame(translate_frame, text="📊 Progress", 
                                      font=("Arial", 10, "bold"), padx=15, pady=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_var = tk.StringVar(value="Sẵn sàng để bắt đầu...")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
    def create_settings_tab(self):
        """Tab cài đặt"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Cài Đặt")
        
        # API Settings
        api_settings_frame = tk.LabelFrame(settings_frame, text="🔑 API Settings", 
                                          font=("Arial", 10, "bold"), padx=15, pady=15)
        api_settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(api_settings_frame, text="Google AI API Key:").pack(anchor=tk.W)
        api_settings_entry = tk.Entry(api_settings_frame, textvariable=self.api_key_var, width=60, show="*")
        api_settings_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(api_settings_frame, text="Model:").pack(anchor=tk.W)
        model_settings_combo = ttk.Combobox(
            api_settings_frame,
            textvariable=self.model_var,
            values=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            state="readonly"
        )
        model_settings_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Translation Settings
        translate_settings_frame = tk.LabelFrame(settings_frame, text="🚀 Translation Settings", 
                                                font=("Arial", 10, "bold"), padx=15, pady=15)
        translate_settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        auto_reformat_check = tk.Checkbutton(
            translate_settings_frame,
            text="Tự động reformat file sau khi dịch",
            variable=self.auto_reformat_var
        )
        auto_reformat_check.pack(anchor=tk.W)
        
        auto_epub_check = tk.Checkbutton(
            translate_settings_frame,
            text="Tự động convert sang EPUB sau khi dịch",
            variable=self.auto_convert_epub_var
        )
        auto_epub_check.pack(anchor=tk.W, pady=(5, 0))
        
        # Performance Settings
        perf_frame = tk.LabelFrame(settings_frame, text="📊 Performance Settings", 
                                  font=("Arial", 10, "bold"), padx=15, pady=15)
        perf_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(perf_frame, text="Số threads (mặc định: 10):").pack(anchor=tk.W)
        self.threads_var = tk.StringVar(value="10")
        threads_entry = tk.Entry(perf_frame, textvariable=self.threads_var, width=10)
        threads_entry.pack(anchor=tk.W, pady=(5, 10))
        
        tk.Label(perf_frame, text="Chunk size (dòng/chunk, mặc định: 100):").pack(anchor=tk.W)
        self.chunk_size_var = tk.StringVar(value="100")
        chunk_entry = tk.Entry(perf_frame, textvariable=self.chunk_size_var, width=10)
        chunk_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Save/Load buttons
        settings_btn_frame = tk.Frame(settings_frame)
        settings_btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_settings_btn = tk.Button(
            settings_btn_frame,
            text="💾 Lưu Cài Đặt",
            command=self.save_settings,
            bg='#27ae60',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT
        )
        save_settings_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_settings_btn = tk.Button(
            settings_btn_frame,
            text="📂 Tải Cài Đặt",
            command=self.load_settings,
            bg='#3498db',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT
        )
        load_settings_btn.pack(side=tk.LEFT)
        
    def create_epub_tab(self):
        """Tab chuyển đổi EPUB"""
        epub_frame = ttk.Frame(self.notebook)
        self.notebook.add(epub_frame, text="📚 EPUB")
        
        # EPUB Settings
        epub_settings_frame = tk.LabelFrame(epub_frame, text="📚 EPUB Settings", 
                                           font=("Arial", 10, "bold"), padx=15, pady=15)
        epub_settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(epub_settings_frame, text="Tiêu đề sách:").pack(anchor=tk.W)
        title_entry = tk.Entry(epub_settings_frame, textvariable=self.book_title_var, width=50)
        title_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(epub_settings_frame, text="Tác giả:").pack(anchor=tk.W)
        author_entry = tk.Entry(epub_settings_frame, textvariable=self.book_author_var, width=50)
        author_entry.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(epub_settings_frame, text="Pattern nhận diện chương (regex):").pack(anchor=tk.W)
        pattern_entry = tk.Entry(epub_settings_frame, textvariable=self.chapter_pattern_var, width=50)
        pattern_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Manual EPUB conversion
        manual_epub_frame = tk.LabelFrame(epub_frame, text="🔄 Manual EPUB Conversion", 
                                         font=("Arial", 10, "bold"), padx=15, pady=15)
        manual_epub_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.epub_input_var = tk.StringVar()
        tk.Label(manual_epub_frame, text="File TXT để convert:").pack(anchor=tk.W)
        epub_input_frame = tk.Frame(manual_epub_frame)
        epub_input_frame.pack(fill=tk.X, pady=(5, 10))
        
        epub_input_entry = tk.Entry(epub_input_frame, textvariable=self.epub_input_var)
        epub_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        epub_browse_btn = tk.Button(
            epub_input_frame,
            text="Browse",
            command=self.browse_epub_input,
            bg='#3498db',
            fg='white',
            relief=tk.FLAT
        )
        epub_browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        convert_epub_btn = tk.Button(
            manual_epub_frame,
            text="📚 Convert to EPUB",
            command=self.convert_to_epub_manual,
            bg='#9b59b6',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT
        )
        convert_epub_btn.pack(anchor=tk.W)
        
        # EPUB Info
        info_frame = tk.LabelFrame(epub_frame, text="ℹ️ Thông tin EPUB", 
                                  font=("Arial", 10, "bold"), padx=15, pady=15)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_content = """
📚 Chuyển đổi EPUB:
• Chuyển đổi từ TXT → DOCX → EPUB
• Tự động nhận diện chương dựa trên pattern regex
• Hỗ trợ metadata (tiêu đề, tác giả)
• Tạo mục lục tự động

⚙️ Yêu cầu:
• Cài đặt Pandoc (https://pandoc.org/installing.html)
• Cập nhật đường dẫn Pandoc trong file ConvertEpub.py

🔧 Pattern mặc định:
• ^Chương\\s+\\d+:\\s+.*$ (Chương 1: Tên chương)
• Có thể tùy chỉnh theo định dạng của bạn
        """
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
    def create_logs_tab(self):
        """Tab logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Log controls
        log_controls_frame = tk.Frame(logs_frame)
        log_controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        clear_log_btn = tk.Button(
            log_controls_frame,
            text="🗑️ Xóa Logs",
            command=self.clear_logs,
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT
        )
        clear_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_log_btn = tk.Button(
            log_controls_frame,
            text="💾 Lưu Logs",
            command=self.save_logs,
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT
        )
        save_log_btn.pack(side=tk.LEFT)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=25,
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
            if not self.output_file_var.get():
                output_path = generate_output_filename(file_path)
                self.output_file_var.set(output_path)
            
            # Auto-fill book title from filename
            if not self.book_title_var.get():
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.book_title_var.set(filename)
    
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
    
    def browse_epub_input(self):
        """Chọn file để convert EPUB"""
        file_path = filedialog.askopenfilename(
            title="Chọn file TXT để convert sang EPUB",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.epub_input_var.set(file_path)
    
    def toggle_epub_options(self):
        """Toggle EPUB options visibility"""
        if self.auto_convert_epub_var.get():
            self.notebook.tab(2, state="normal")  # Enable EPUB tab
        else:
            self.notebook.tab(2, state="disabled")  # Disable EPUB tab
    
    def log(self, message):
        """Ghi log vào text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        print(log_message.strip())  # Also print to console
    
    def clear_logs(self):
        """Xóa logs"""
        self.log_text.delete(1.0, tk.END)
        self.log("🗑️ Đã xóa logs")
    
    def save_logs(self):
        """Lưu logs ra file"""
        file_path = filedialog.asksaveasfilename(
            title="Lưu logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"💾 Đã lưu logs vào: {file_path}")
            except Exception as e:
                self.log(f"❌ Lỗi lưu logs: {e}")
    
    def start_translation(self):
        """Bắt đầu quá trình dịch"""
        if not TRANSLATE_AVAILABLE:
            messagebox.showerror("Lỗi", "Không thể import module dịch. Vui lòng kiểm tra lại file translate.py")
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
        
        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = generate_output_filename(self.input_file_var.get())
            self.output_file_var.set(output_file)
        
        # Start translation
        self.is_translating = True
        self.translate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        self.progress_var.set("Đang dịch...")
        
        self.log("🚀 Bắt đầu quá trình dịch...")
        self.log(f"📁 Input: {os.path.basename(self.input_file_var.get())}")
        self.log(f"📁 Output: {os.path.basename(output_file)}")
        self.log(f"🤖 Model: {self.model_var.get()}")
        
        # Run in thread
        self.translation_thread = threading.Thread(
            target=self.run_translation,
            args=(self.input_file_var.get(), output_file, self.api_key_var.get(), self.model_var.get()),
            daemon=True
        )
        self.translation_thread.start()
    
    def run_translation(self, input_file, output_file, api_key, model_name):
        """Chạy quá trình dịch"""
        try:
            self.start_time = time.time()
            
            # Call translate function
            success = translate_file_optimized(
                input_file=input_file,
                output_file=output_file,
                api_key=api_key,
                model_name=model_name
            )
            
            if success and self.is_translating:
                self.log("✅ Dịch hoàn thành!")
                
                # Auto reformat if enabled
                if self.auto_reformat_var.get():
                    self.log("🔄 Đang reformat file...")
                    try:
                        fix_text_format(output_file)
                        self.log("✅ Reformat hoàn thành!")
                    except Exception as e:
                        self.log(f"⚠️ Lỗi reformat: {e}")
                
                # Auto convert to EPUB if enabled
                if self.auto_convert_epub_var.get() and EPUB_AVAILABLE:
                    self.log("📚 Đang convert sang EPUB...")
                    try:
                        self.convert_to_epub(output_file)
                    except Exception as e:
                        self.log(f"⚠️ Lỗi convert EPUB: {e}")
                
                elapsed_time = time.time() - self.start_time
                self.log(f"⏱️ Thời gian hoàn thành: {elapsed_time:.1f} giây")
                self.progress_var.set("Hoàn thành!")
                messagebox.showinfo("Thành công", f"Dịch hoàn thành!\nFile: {output_file}")
                
            elif not self.is_translating:
                self.log("⏹️ Đã dừng")
            else:
                self.log("❌ Dịch thất bại")
                messagebox.showerror("Lỗi", "Quá trình dịch thất bại")
                
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            self.translation_finished()
    
    def stop_translation(self):
        """Dừng quá trình dịch"""
        self.is_translating = False
        self.log("⏹️ Đang dừng...")
    
    def translation_finished(self):
        """Kết thúc quá trình dịch"""
        self.is_translating = False
        self.translate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        if not self.progress_var.get().startswith("Hoàn thành"):
            self.progress_var.set("Sẵn sàng")
    
    def convert_to_epub(self, txt_file):
        """Convert file to EPUB"""
        if not EPUB_AVAILABLE:
            self.log("❌ Không thể convert EPUB - thiếu module ConvertEpub")
            return
        
        try:
            # Generate file paths
            base_name = os.path.splitext(txt_file)[0]
            docx_file = base_name + ".docx"
            epub_file = base_name + ".epub"
            
            # Get book info
            title = self.book_title_var.get() or os.path.splitext(os.path.basename(txt_file))[0]
            author = self.book_author_var.get() or "Unknown Author"
            pattern = self.chapter_pattern_var.get() or r"^Chương\s+\d+:\s+.*$"
            
            # Convert TXT to DOCX
            self.log("📄 Đang convert TXT → DOCX...")
            if txt_to_docx(txt_file, docx_file, title, pattern):
                self.log("✅ Convert TXT → DOCX hoàn thành!")
                
                # Convert DOCX to EPUB
                self.log("📚 Đang convert DOCX → EPUB...")
                if docx_to_epub(docx_file, epub_file, title, author):
                    self.log(f"✅ Convert EPUB hoàn thành: {epub_file}")
                else:
                    self.log("❌ Convert DOCX → EPUB thất bại")
            else:
                self.log("❌ Convert TXT → DOCX thất bại")
                
        except Exception as e:
            self.log(f"❌ Lỗi convert EPUB: {e}")
    
    def convert_to_epub_manual(self):
        """Convert file to EPUB manually"""
        if not self.epub_input_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn file TXT để convert")
            return
        
        if not os.path.exists(self.epub_input_var.get()):
            messagebox.showerror("Lỗi", "File không tồn tại")
            return
        
        self.log("📚 Bắt đầu convert EPUB manual...")
        
        # Run in thread
        convert_thread = threading.Thread(
            target=self.convert_to_epub,
            args=(self.epub_input_var.get(),),
            daemon=True
        )
        convert_thread.start()
    
    def save_settings(self):
        """Lưu cài đặt"""
        settings = {
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "auto_reformat": self.auto_reformat_var.get(),
            "auto_convert_epub": self.auto_convert_epub_var.get(),
            "book_author": self.book_author_var.get(),
            "chapter_pattern": self.chapter_pattern_var.get(),
            "threads": self.threads_var.get(),
            "chunk_size": self.chunk_size_var.get()
        }
        
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.log("💾 Đã lưu cài đặt")
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
        except Exception as e:
            self.log(f"❌ Lỗi lưu cài đặt: {e}")
            messagebox.showerror("Lỗi", f"Lỗi lưu cài đặt: {e}")
    
    def load_settings(self):
        """Tải cài đặt"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                
                self.api_key_var.set(settings.get("api_key", ""))
                self.model_var.set(settings.get("model", "gemini-2.0-flash"))
                self.auto_reformat_var.set(settings.get("auto_reformat", True))
                self.auto_convert_epub_var.set(settings.get("auto_convert_epub", False))
                self.book_author_var.set(settings.get("book_author", "Unknown Author"))
                self.chapter_pattern_var.set(settings.get("chapter_pattern", r"^Chương\s+\d+:\s+.*$"))
                self.threads_var.set(settings.get("threads", "10"))
                self.chunk_size_var.set(settings.get("chunk_size", "100"))
                
                self.log("📂 Đã tải cài đặt")
        except Exception as e:
            self.log(f"⚠️ Lỗi tải cài đặt: {e}")

def main():
    root = tk.Tk()
    app = TranslateNovelAI(root)
    
    def on_closing():
        if app.is_translating:
            if messagebox.askokcancel("Thoát", "Đang dịch. Bạn có chắc muốn thoát?"):
                app.stop_translation()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
