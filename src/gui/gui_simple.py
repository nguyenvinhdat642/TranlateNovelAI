import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time
from datetime import datetime
import json
import re
import io
from contextlib import redirect_stdout

# Import translate functions
try:
    from ..core.translate import translate_file_optimized, generate_output_filename
    from ..core.reformat import fix_text_format
    from ..core.ConvertEpub import txt_to_docx, docx_to_epub
    TRANSLATE_AVAILABLE = True
    EPUB_AVAILABLE = True
except ImportError as e:
    TRANSLATE_AVAILABLE = False
    EPUB_AVAILABLE = False
    print(f"⚠️ Lỗi import: {e}")

class LogCapture:
    """Class để capture print statements và chuyển về GUI"""
    def __init__(self, gui_log_function):
        self.gui_log = gui_log_function
        self.terminal = sys.stdout
        
    def write(self, message):
        # Ghi vào terminal như bình thường (kiểm tra None trước)
        if self.terminal is not None:
            try:
                self.terminal.write(message)
                self.terminal.flush()
            except:
                pass  # Bỏ qua lỗi terminal write
        
        # Gửi về GUI (loại bỏ newline để GUI tự xử lý)
        if message.strip() and self.gui_log is not None:
            try:
                self.gui_log(message.strip())
            except:
                pass  # Bỏ qua lỗi GUI update
    
    def flush(self):
        if self.terminal is not None:
            try:
                self.terminal.flush()
            except:
                pass

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
        self.context_var = tk.StringVar(value="Bối cảnh hiện đại")
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
        
        # Log capture
        self.original_stdout = sys.stdout
        self.log_capture = None
        
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
        
        # Context selection
        context_frame = tk.Frame(api_frame)
        context_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(context_frame, text="Bối cảnh dịch:").pack(side=tk.LEFT)
        context_combo = ttk.Combobox(
            context_frame,
            textvariable=self.context_var,
            values=[
                "Bối cảnh hiện đại",
                "Bối cảnh cổ đại", 
                "Bối cảnh fantasy/viễn tưởng",
                "Bối cảnh học đường",
                "Bối cảnh công sở",
                "Bối cảnh lãng mạn",
                "Bối cảnh hành động",
                "Tùy chỉnh"
            ],
            state="readonly",
            width=25
        )
        context_combo.pack(side=tk.LEFT, padx=(10, 0))
        context_combo.set("Bối cảnh hiện đại")  # Set default
        
        # Custom prompt frame (initially hidden)
        self.custom_prompt_frame = tk.Frame(api_frame)
        
        tk.Label(self.custom_prompt_frame, text="Custom Prompt:").pack(anchor=tk.W, pady=(10, 5))
        self.custom_prompt_var = tk.StringVar()
        self.custom_prompt_entry = tk.Text(
            self.custom_prompt_frame,
            height=3,
            width=60,
            wrap=tk.WORD,
            font=("Arial", 9)
        )
        self.custom_prompt_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Bind context selection to show/hide custom prompt
        context_combo.bind('<<ComboboxSelected>>', self.on_context_changed)
        
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
        tk.Label(file_frame, text="Output File (tự động tạo nếu để trống, nút Reset để tạo lại):").pack(anchor=tk.W)
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
            relief=tk.FLAT,
            width=8
        )
        output_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        reset_output_btn = tk.Button(
            output_path_frame,
            text="🔄 Reset",
            command=self.reset_output_filename,
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            width=8
        )
        reset_output_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
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
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Mini log area in translate tab
        mini_log_frame = tk.LabelFrame(translate_frame, text="📝 Logs (Xem chi tiết ở tab Logs)", 
                                      font=("Arial", 9, "bold"), padx=10, pady=10)
        mini_log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.mini_log_text = scrolledtext.ScrolledText(
            mini_log_frame,
            height=8,
            font=("Consolas", 8),
            wrap=tk.WORD
        )
        self.mini_log_text.pack(fill=tk.BOTH, expand=True)
        
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
        model_settings_combo.pack(fill=tk.X, pady=(5, 10))
        
        tk.Label(api_settings_frame, text="Bối cảnh dịch:").pack(anchor=tk.W)
        context_settings_combo = ttk.Combobox(
            api_settings_frame,
            textvariable=self.context_var,
            values=[
                "Bối cảnh hiện đại",
                "Bối cảnh cổ đại", 
                "Bối cảnh fantasy/viễn tưởng",
                "Bối cảnh học đường",
                "Bối cảnh công sở",
                "Bối cảnh lãng mạn",
                "Bối cảnh hành động",
                "Tùy chỉnh"
            ],
            state="readonly"
        )
        context_settings_combo.pack(fill=tk.X, pady=(5, 0))
        context_settings_combo.bind('<<ComboboxSelected>>', self.on_context_changed)
        
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
        save_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(
            log_controls_frame,
            text="🔄 Auto-scroll",
            variable=auto_scroll_var
        )
        auto_scroll_check.pack(side=tk.LEFT, padx=(10, 0))
        self.auto_scroll_var = auto_scroll_var
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=25,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_log_capture(self):
        """Thiết lập log capture để chuyển print statements từ translate.py lên GUI"""
        if not self.log_capture:
            self.log_capture = LogCapture(self.log_from_translate)
            sys.stdout = self.log_capture
    
    def restore_stdout(self):
        """Khôi phục stdout về trạng thái ban đầu"""
        if self.log_capture:
            sys.stdout = self.original_stdout
            self.log_capture = None
    
    def log_from_translate(self, message):
        """Nhận log từ translate.py và hiển thị lên GUI"""
        # Sử dụng thread-safe method để update GUI
        self.root.after(0, lambda: self._update_log_ui(message))
    
    def _update_log_ui(self, message):
        """Update log UI (thread-safe)"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            
            # Update both main log and mini log (kiểm tra tồn tại trước)
            if hasattr(self, 'log_text') and self.log_text is not None:
                self.log_text.insert(tk.END, log_message + "\n")
            if hasattr(self, 'mini_log_text') and self.mini_log_text is not None:
                self.mini_log_text.insert(tk.END, log_message + "\n")
            
            # Auto-scroll if enabled
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                if hasattr(self, 'log_text') and self.log_text is not None:
                    self.log_text.see(tk.END)
                if hasattr(self, 'mini_log_text') and self.mini_log_text is not None:
                    self.mini_log_text.see(tk.END)
            
            # Limit log size (keep last 1000 lines)
            self._limit_log_size()
            
            # Update progress if it's a progress message
            self._update_progress_from_log(message)
            
            if hasattr(self, 'root') and self.root is not None:
                self.root.update_idletasks()
        except Exception as e:
            # Nếu có lỗi, in ra console để debug
            print(f"⚠️ Lỗi update log UI: {e}")
    
    def _limit_log_size(self):
        """Giới hạn số dòng log để tránh tràn bộ nhớ"""
        try:
            max_lines = 1000
            
            # Kiểm tra từng widget riêng biệt
            for attr_name in ['log_text', 'mini_log_text']:
                if hasattr(self, attr_name):
                    log_widget = getattr(self, attr_name)
                    if log_widget is not None:
                        try:
                            lines = log_widget.get("1.0", tk.END).split('\n')
                            if len(lines) > max_lines:
                                # Xóa các dòng cũ, giữ lại max_lines dòng cuối
                                log_widget.delete("1.0", f"{len(lines) - max_lines}.0")
                        except Exception:
                            pass  # Bỏ qua lỗi từng widget
        except Exception:
            pass  # Bỏ qua lỗi tổng thể
    
    def _update_progress_from_log(self, message):
        """Cập nhật progress bar từ log messages"""
        try:
            # Tìm pattern tiến độ: "Hoàn thành chunk X/Y" hoặc "Tiến độ: X/Y chunks"
            import re
            
            # Pattern 1: "✅ Hoàn thành chunk 5/100"
            match1 = re.search(r'Hoàn thành chunk (\d+)/(\d+)', message)
            if match1:
                current = int(match1.group(1))
                total = int(match1.group(2))
                progress_percent = (current / total) * 100
                self.progress_bar.config(mode='determinate', value=progress_percent)
                self.progress_var.set(f"Hoàn thành chunk {current}/{total} ({progress_percent:.1f}%)")
                return
            
            # Pattern 2: "Tiến độ: 45/100 chunks (45.0%)"
            match2 = re.search(r'Tiến độ: (\d+)/(\d+) chunks \((\d+\.?\d*)%\)', message)
            if match2:
                current = int(match2.group(1))
                total = int(match2.group(2))
                percent = float(match2.group(3))
                self.progress_bar.config(mode='determinate', value=percent)
                self.progress_var.set(f"Tiến độ: {current}/{total} chunks ({percent:.1f}%)")
                return
            
            # Pattern 3: "Tổng số chunks: X"
            match3 = re.search(r'Tổng số chunks: (\d+)', message)
            if match3:
                self.total_chunks = int(match3.group(1))
                self.progress_bar.config(mode='determinate', maximum=100)
                return
            
            # Pattern 4: "Đã hoàn thành X chunk trước đó"
            match4 = re.search(r'Đã hoàn thành (\d+) chunk trước đó', message)
            if match4:
                self.completed_chunks = int(match4.group(1))
                if self.total_chunks > 0:
                    progress_percent = (self.completed_chunks / self.total_chunks) * 100
                    self.progress_bar.config(value=progress_percent)
                return
                
        except Exception:
            # Nếu có lỗi trong việc parse, bỏ qua
            pass
    
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
            
            # ALWAYS auto-generate output filename when selecting new input
            output_path = generate_output_filename(file_path)
            self.output_file_var.set(output_path)
            self.log(f"📁 Tự động tạo tên file output: {os.path.basename(output_path)}")
            
            # Auto-fill book title from filename
            if not self.book_title_var.get() or self.book_title_var.get() == "Unknown Title":
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.book_title_var.set(filename)
                
            # Reset EPUB input to match current input file
            self.epub_input_var.set(file_path)
    
    def browse_output_file(self):
        """Chọn file output"""
        # Get the directory of input file for better UX
        initial_dir = ""
        if self.input_file_var.get():
            initial_dir = os.path.dirname(self.input_file_var.get())
            
        file_path = filedialog.asksaveasfilename(
            title="Chọn nơi lưu file đã dịch",
            initialdir=initial_dir,
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_file_var.set(file_path)
            self.log(f"📁 Đã chọn file output: {os.path.basename(file_path)}")
    
    def browse_epub_input(self):
        """Chọn file để convert EPUB"""
        # Default to current input file's directory
        initial_dir = ""
        initial_file = ""
        if self.input_file_var.get():
            initial_dir = os.path.dirname(self.input_file_var.get())
            # Suggest the translated file if it exists
            if self.output_file_var.get() and os.path.exists(self.output_file_var.get()):
                initial_file = self.output_file_var.get()
            else:
                initial_file = self.input_file_var.get()
                
        file_path = filedialog.askopenfilename(
            title="Chọn file TXT để convert sang EPUB",
            initialdir=initial_dir,
            initialfile=os.path.basename(initial_file) if initial_file else "",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.epub_input_var.set(file_path)
            
            # Auto-fill book title from selected file if not set
            if not self.book_title_var.get() or self.book_title_var.get() == "Unknown Title":
                filename = os.path.splitext(os.path.basename(file_path))[0]
                # Remove _TranslateAI suffix if present
                if filename.endswith("_TranslateAI"):
                    filename = filename[:-12]
                self.book_title_var.set(filename)
    
    def reset_output_filename(self):
        """Reset output filename to auto-generated name"""
        if not self.input_file_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file input trước!")
            return
            
        output_path = generate_output_filename(self.input_file_var.get())
        self.output_file_var.set(output_path)
        self.log(f"🔄 Đã reset tên file output: {os.path.basename(output_path)}")
    
    def on_context_changed(self, event=None):
        """Xử lý khi thay đổi bối cảnh dịch"""
        if self.context_var.get() == "Tùy chỉnh":
            self.custom_prompt_frame.pack(fill=tk.X, pady=(10, 0))
            # Load default custom prompt
            default_custom = "Dịch văn bản sau sang tiếng Việt. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặt trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung."
            self.custom_prompt_entry.delete(1.0, tk.END)
            self.custom_prompt_entry.insert(1.0, default_custom)
        else:
            self.custom_prompt_frame.pack_forget()
    
    def get_system_instruction(self):
        """Tạo system instruction dựa trên bối cảnh đã chọn"""
        context = self.context_var.get()
        
        base_instruction = "Dịch văn bản sau sang tiếng Việt. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặt trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung."
        
        context_instructions = {
            "Bối cảnh hiện đại": f"{base_instruction} Bối cảnh hiện đại. Giữ nguyên các từ ngữ thô tục, tình dục.",
            "Bối cảnh cổ đại": f"{base_instruction} Bối cảnh cổ đại. Sử dụng ngôn ngữ trang trọng, lịch sự phù hợp thời kỳ cổ đại. Dùng danh xưng cổ điển như 'ngươi', 'ta', 'hạ thần'.",
            "Bối cảnh fantasy/viễn tưởng": f"{base_instruction} Bối cảnh fantasy/viễn tưởng. Giữ nguyên tên thuật ngữ ma thuật, tên kỹ năng, tên vũ khí đặc biệt. Dịch sát nghĩa các thuật ngữ fantasy.",
            "Bối cảnh học đường": f"{base_instruction} Bối cảnh học đường. Sử dụng ngôn ngữ trẻ trung, năng động. Dịch chính xác các danh xưng học sinh, thầy cô.",
            "Bối cảnh công sở": f"{base_instruction} Bối cảnh công sở. Sử dụng ngôn ngữ lịch sự, trang trọng phù hợp môi trường làm việc. Dịch chính xác chức danh, thuật ngữ kinh doanh.",
            "Bối cảnh lãng mạn": f"{base_instruction} Bối cảnh lãng mạn. Chú trọng cảm xúc, ngôn ngữ ngọt ngào, lãng mạn. Dịch tinh tế các câu tỏ tình, biểu đạt tình cảm.",
            "Bối cảnh hành động": f"{base_instruction} Bối cảnh hành động. Giữ nguyên tên kỹ năng, vũ khí, thuật ngữ chiến đấu. Dịch mạnh mẽ, năng động các cảnh hành động.",
            "Tùy chỉnh": self.custom_prompt_entry.get(1.0, tk.END).strip() if hasattr(self, 'custom_prompt_entry') else base_instruction
        }
        
        return context_instructions.get(context, base_instruction)
    
    def toggle_epub_options(self):
        """Toggle EPUB options visibility"""
        if self.auto_convert_epub_var.get():
            self.notebook.tab(2, state="normal")  # Enable EPUB tab
        else:
            self.notebook.tab(2, state="disabled")  # Disable EPUB tab
    
    def log(self, message):
        """Ghi log vào text area (method cho GUI logs)"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            
            # Kiểm tra tồn tại của các widget trước khi sử dụng
            if hasattr(self, 'log_text') and self.log_text is not None:
                self.log_text.insert(tk.END, log_message + "\n")
            if hasattr(self, 'mini_log_text') and self.mini_log_text is not None:
                self.mini_log_text.insert(tk.END, log_message + "\n")
            
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                if hasattr(self, 'log_text') and self.log_text is not None:
                    self.log_text.see(tk.END)
                if hasattr(self, 'mini_log_text') and self.mini_log_text is not None:
                    self.mini_log_text.see(tk.END)
                
            if hasattr(self, 'root') and self.root is not None:
                self.root.update_idletasks()
            
            print(message)  # Also print to console
        except Exception as e:
            # Nếu có lỗi, chỉ in ra console
            print(f"⚠️ Lỗi log GUI: {e} - Message: {message}")
    
    def clear_logs(self):
        """Xóa logs"""
        try:
            if hasattr(self, 'log_text') and self.log_text is not None:
                self.log_text.delete(1.0, tk.END)
            if hasattr(self, 'mini_log_text') and self.mini_log_text is not None:
                self.mini_log_text.delete(1.0, tk.END)
            print("🗑️ Đã xóa logs")  # Sử dụng print thay vì self.log để tránh vòng lặp
        except Exception as e:
            print(f"⚠️ Lỗi xóa logs: {e}")
    
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
            self.log(f"📝 Tự động tạo tên file output: {os.path.basename(output_file)}")
        
        # Check if input and output are the same
        if os.path.abspath(self.input_file_var.get()) == os.path.abspath(output_file):
            messagebox.showerror("Lỗi", "File input và output không thể giống nhau!")
            return
        
        # Warn if output file exists
        if os.path.exists(output_file):
            result = messagebox.askyesno(
                "Cảnh báo", 
                f"File output đã tồn tại:\n{os.path.basename(output_file)}\n\nBạn có muốn ghi đè không?",
                icon='warning'
            )
            if not result:
                return
        
        # Start translation
        self.is_translating = True
        self.translate_btn.config(state=tk.DISABLED)
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        self.progress_var.set("Đang dịch...")
        
        # Setup log capture
        self.setup_log_capture()
        
        self.log("🚀 Bắt đầu quá trình dịch...")
        self.log(f"📁 Input: {os.path.basename(self.input_file_var.get())}")
        self.log(f"📁 Output: {os.path.basename(output_file)}")
        self.log(f"🤖 Model: {self.model_var.get()}")
        
        # Automatically switch to logs tab to show progress
        self.notebook.select(3)  # Select logs tab (index 3)
        
        # Run in thread
        self.translation_thread = threading.Thread(
            target=self.run_translation,
            args=(self.input_file_var.get(), output_file, self.api_key_var.get(), self.model_var.get(), self.get_system_instruction()),
            daemon=True
        )
        self.translation_thread.start()
    
    def run_translation(self, input_file, output_file, api_key, model_name, system_instruction):
        """Chạy quá trình dịch"""
        try:
            self.start_time = time.time()
            
            # Call translate function (logs will be captured automatically)
            success = translate_file_optimized(
                input_file=input_file,
                output_file=output_file,
                api_key=api_key,
                model_name=model_name,
                system_instruction=system_instruction
            )
            
            if success:
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
                self.progress_bar.config(mode='determinate', value=100)
                messagebox.showinfo("Thành công", f"Dịch hoàn thành!\nFile: {output_file}")
            else:
                self.log("❌ Dịch thất bại")
                messagebox.showerror("Lỗi", "Quá trình dịch thất bại")
                
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            self.translation_finished()
    
    def translation_finished(self):
        """Kết thúc quá trình dịch"""
        self.is_translating = False
        self.translate_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        
        # Restore stdout
        self.restore_stdout()
        
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
        
        # Setup log capture for EPUB conversion
        self.setup_log_capture()
        
        # Run in thread
        convert_thread = threading.Thread(
            target=self._convert_epub_thread,
            args=(self.epub_input_var.get(),),
            daemon=True
        )
        convert_thread.start()
    
    def _convert_epub_thread(self, file_path):
        """Thread wrapper for EPUB conversion"""
        try:
            self.convert_to_epub(file_path)
        finally:
            self.restore_stdout()
    
    def save_settings(self):
        """Lưu cài đặt"""
        # Get custom prompt if exists
        custom_prompt = ""
        if hasattr(self, 'custom_prompt_entry'):
            custom_prompt = self.custom_prompt_entry.get(1.0, tk.END).strip()
            
        settings = {
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "context": self.context_var.get(),
            "custom_prompt": custom_prompt,
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
                self.context_var.set(settings.get("context", "Bối cảnh hiện đại"))
                self.auto_reformat_var.set(settings.get("auto_reformat", True))
                self.auto_convert_epub_var.set(settings.get("auto_convert_epub", False))
                self.book_author_var.set(settings.get("book_author", "Unknown Author"))
                self.chapter_pattern_var.set(settings.get("chapter_pattern", r"^Chương\s+\d+:\s+.*$"))
                self.threads_var.set(settings.get("threads", "10"))
                self.chunk_size_var.set(settings.get("chunk_size", "100"))
                
                # Load custom prompt if exists
                if hasattr(self, 'custom_prompt_entry') and settings.get("custom_prompt"):
                    self.custom_prompt_entry.delete(1.0, tk.END)
                    self.custom_prompt_entry.insert(1.0, settings.get("custom_prompt"))
                
                # Trigger context change to show/hide custom prompt
                self.on_context_changed()
                
                self.log("📂 Đã tải cài đặt")
        except Exception as e:
            self.log(f"⚠️ Lỗi tải cài đặt: {e}")
            
    def __del__(self):
        """Destructor để đảm bảo stdout được khôi phục"""
        self.restore_stdout()

def main():
    root = tk.Tk()
    app = TranslateNovelAI(root)
    
    def on_closing():
        if app.is_translating:
            if messagebox.askokcancel("Thoát", "Đang dịch. Bạn có chắc muốn thoát?"):
                app.restore_stdout()  # Ensure stdout is restored
                root.destroy()
        else:
            app.restore_stdout()  # Ensure stdout is restored
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
