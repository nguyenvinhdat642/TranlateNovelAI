import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys
import time
from datetime import datetime
import json
import re
try:
    from .custom_dialogs import show_success, show_error, show_warning, show_question, show_toast_success, show_toast_error
except ImportError:
    # Fallback to standard messagebox if custom dialogs not available
    from tkinter import messagebox
    def show_success(msg, details=None, parent=None):
        return messagebox.showinfo("Thành công", msg)
    def show_error(msg, details=None, parent=None):
        return messagebox.showerror("Lỗi", msg)
    def show_warning(msg, details=None, parent=None):
        return messagebox.showwarning("Cảnh báo", msg)
    def show_question(msg, details=None, parent=None):
        return messagebox.askyesno("Xác nhận", msg)
    def show_toast_success(msg, duration=3000):
        return messagebox.showinfo("Thành công", msg)
    def show_toast_error(msg, duration=3000):
        return messagebox.showerror("Lỗi", msg)
from PIL import Image, ImageTk

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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
        if self.terminal is not None:
            try:
                self.terminal.write(message)
                self.terminal.flush()
            except:
                pass
        
        if message.strip() and self.gui_log is not None:
            try:
                self.gui_log(message.strip())
            except:
                pass
    
    def flush(self):
        if self.terminal is not None:
            try:
                self.terminal.flush()
            except:
                pass

class ModernTranslateNovelAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("🤖 TranslateNovelAI - Modern Edition")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        # Variables
        self.input_file_var = ctk.StringVar()
        self.output_file_var = ctk.StringVar()
        self.api_key_var = ctk.StringVar()
        self.model_var = ctk.StringVar(value="gemini-2.0-flash")
        self.context_var = ctk.StringVar(value="Bối cảnh hiện đại")
        self.auto_reformat_var = ctk.BooleanVar(value=True)
        self.auto_convert_epub_var = ctk.BooleanVar(value=False)
        self.book_title_var = ctk.StringVar()
        self.book_author_var = ctk.StringVar(value="Unknown Author")
        self.chapter_pattern_var = ctk.StringVar(value=r"^Chương\s+\d+:\s+.*$")
        self.threads_var = ctk.StringVar(value="10")
        self.chunk_size_var = ctk.StringVar(value="100")
        
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
        """Thiết lập giao diện chính"""
        # Configure grid layout (3x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.setup_sidebar()
        
        # Create main content frame
        self.setup_main_content()
        
        # Create right panel (logs)
        self.setup_right_panel()
        
    def setup_sidebar(self):
        """Thiết lập sidebar bên trái"""
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🤖 TranslateNovelAI",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Modern Edition v2.0",
            font=ctk.CTkFont(size=12)
        )
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # API Configuration
        self.api_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🔑 API Configuration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.api_label.grid(row=2, column=0, padx=20, pady=(10, 5))
        
        self.api_key_entry = ctk.CTkEntry(
            self.sidebar_frame,
            placeholder_text="Google AI API Key",
            textvariable=self.api_key_var,
            show="*",
            width=240
        )
        self.api_key_entry.grid(row=3, column=0, padx=20, pady=5)
        
        self.model_combo = ctk.CTkComboBox(
            self.sidebar_frame,
            values=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            variable=self.model_var,
            width=240
        )
        self.model_combo.grid(row=4, column=0, padx=20, pady=5)
        
        self.context_combo = ctk.CTkComboBox(
            self.sidebar_frame,
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
            variable=self.context_var,
            command=self.on_context_changed,
            width=240
        )
        self.context_combo.grid(row=5, column=0, padx=20, pady=5)
        
        # Settings
        self.settings_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.settings_label.grid(row=6, column=0, padx=20, pady=(20, 5))
        
        self.auto_reformat_check = ctk.CTkCheckBox(
            self.sidebar_frame,
            text="Auto reformat",
            variable=self.auto_reformat_var
        )
        self.auto_reformat_check.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        
        self.auto_epub_check = ctk.CTkCheckBox(
            self.sidebar_frame,
            text="Auto convert EPUB",
            variable=self.auto_convert_epub_var
        )
        self.auto_epub_check.grid(row=8, column=0, padx=20, pady=5, sticky="w")
        
        # Control buttons
        self.translate_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🚀 Bắt Đầu Dịch",
            command=self.start_translation,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.translate_btn.grid(row=11, column=0, padx=20, pady=10)
        
        self.save_settings_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="💾 Lưu Cài Đặt",
            command=self.save_settings,
            height=35
        )
        self.save_settings_btn.grid(row=12, column=0, padx=20, pady=5)
        
        # Appearance mode
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Appearance Mode:",
            anchor="w"
        )
        self.appearance_mode_label.grid(row=13, column=0, padx=20, pady=(20, 0), sticky="w")
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=14, column=0, padx=20, pady=(5, 20))
        
    def setup_main_content(self):
        """Thiết lập nội dung chính"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Title
        self.main_title = ctk.CTkLabel(
            self.main_frame,
            text="📁 File Management & Processing",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.main_title.grid(row=0, column=0, padx=20, pady=20)
        
        # File selection frame
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.file_frame.grid_columnconfigure(1, weight=1)
        
        # Input file
        self.input_label = ctk.CTkLabel(
            self.file_frame,
            text="Input File:",
            font=ctk.CTkFont(weight="bold")
        )
        self.input_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.input_entry = ctk.CTkEntry(
            self.file_frame,
            textvariable=self.input_file_var,
            placeholder_text="Chọn file truyện cần dịch..."
        )
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.input_btn = ctk.CTkButton(
            self.file_frame,
            text="📁 Browse",
            command=self.browse_input_file,
            width=100
        )
        self.input_btn.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # Output file
        self.output_label = ctk.CTkLabel(
            self.file_frame,
            text="Output File:",
            font=ctk.CTkFont(weight="bold")
        )
        self.output_label.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.output_entry = ctk.CTkEntry(
            self.file_frame,
            textvariable=self.output_file_var,
            placeholder_text="File output sẽ được tự động tạo..."
        )
        self.output_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.output_btn_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.output_btn_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="w")
        
        self.output_btn = ctk.CTkButton(
            self.output_btn_frame,
            text="📁 Browse",
            command=self.browse_output_file,
            width=100
        )
        self.output_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.reset_output_btn = ctk.CTkButton(
            self.output_btn_frame,
            text="🔄 Reset",
            command=self.reset_output_filename,
            width=100
        )
        self.reset_output_btn.grid(row=0, column=1)
        
        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="📊 Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.progress_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.progress_text = ctk.CTkLabel(
            self.progress_frame,
            text="Sẵn sàng để bắt đầu...",
            font=ctk.CTkFont(size=12)
        )
        self.progress_text.grid(row=1, column=0, padx=20, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.progress_bar.set(0)
        
        # Custom prompt frame (hidden by default)
        self.custom_prompt_frame = ctk.CTkFrame(self.main_frame)
        self.custom_prompt_frame.grid_columnconfigure(0, weight=1)
        
        self.custom_prompt_label = ctk.CTkLabel(
            self.custom_prompt_frame,
            text="Custom Prompt:",
            font=ctk.CTkFont(weight="bold")
        )
        self.custom_prompt_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.custom_prompt_textbox = ctk.CTkTextbox(
            self.custom_prompt_frame,
            height=100
        )
        self.custom_prompt_textbox.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # EPUB Settings (initially hidden)
        self.epub_frame = ctk.CTkFrame(self.main_frame)
        self.epub_frame.grid_columnconfigure(0, weight=1)
        
        self.epub_title_label = ctk.CTkLabel(
            self.epub_frame,
            text="📚 EPUB Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.epub_title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.book_title_entry = ctk.CTkEntry(
            self.epub_frame,
            textvariable=self.book_title_var,
            placeholder_text="Tiêu đề sách"
        )
        self.book_title_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.book_author_entry = ctk.CTkEntry(
            self.epub_frame,
            textvariable=self.book_author_var,
            placeholder_text="Tác giả"
        )
        self.book_author_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.chapter_pattern_entry = ctk.CTkEntry(
            self.epub_frame,
            textvariable=self.chapter_pattern_var,
            placeholder_text="Pattern nhận diện chương (regex)"
        )
        self.chapter_pattern_entry.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")
        
    def setup_right_panel(self):
        """Thiết lập panel logs bên phải"""
        self.right_panel = ctk.CTkFrame(self, width=350)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        self.right_panel.grid_rowconfigure(2, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Logs title
        self.logs_title = ctk.CTkLabel(
            self.right_panel,
            text="📝 Logs & Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.logs_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Log controls
        self.log_controls_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.log_controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        
        self.clear_log_btn = ctk.CTkButton(
            self.log_controls_frame,
            text="🗑️ Clear",
            command=self.clear_logs,
            width=80,
            height=30
        )
        self.clear_log_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.save_log_btn = ctk.CTkButton(
            self.log_controls_frame,
            text="💾 Save",
            command=self.save_logs,
            width=80,
            height=30
        )
        self.save_log_btn.grid(row=0, column=1, padx=5)
        
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        self.auto_scroll_check = ctk.CTkCheckBox(
            self.log_controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var
        )
        self.auto_scroll_check.grid(row=0, column=2, padx=(5, 0))
        
        # Log text area
        self.log_textbox = ctk.CTkTextbox(
            self.right_panel,
            font=ctk.CTkFont(family="Consolas", size=10)
        )
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="nsew")
        
    def on_context_changed(self, choice):
        """Xử lý khi thay đổi bối cảnh dịch"""
        if choice == "Tùy chỉnh":
            self.custom_prompt_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
            # Load default custom prompt
            default_custom = "Dịch văn bản sau sang tiếng Việt. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặt trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung."
            self.custom_prompt_textbox.delete("0.0", "end")
            self.custom_prompt_textbox.insert("0.0", default_custom)
        else:
            self.custom_prompt_frame.grid_remove()
    
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
            "Tùy chỉnh": self.custom_prompt_textbox.get("0.0", "end").strip() if hasattr(self, 'custom_prompt_textbox') else base_instruction
        }
        
        return context_instructions.get(context, base_instruction)
    
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
            
            # Auto-generate output filename
            output_path = generate_output_filename(file_path)
            self.output_file_var.set(output_path)
            self.log(f"📁 Tự động tạo tên file output: {os.path.basename(output_path)}")
            
            # Auto-fill book title from filename
            if not self.book_title_var.get() or self.book_title_var.get() == "Unknown Title":
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.book_title_var.set(filename)
    
    def browse_output_file(self):
        """Chọn file output"""
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
    
    def reset_output_filename(self):
        """Reset output filename to auto-generated name"""
        if not self.input_file_var.get():
            show_warning("Vui lòng chọn file input trước!", parent=self)
            return
            
        output_path = generate_output_filename(self.input_file_var.get())
        self.output_file_var.set(output_path)
        self.log(f"🔄 Đã reset tên file output: {os.path.basename(output_path)}")
    
    def setup_log_capture(self):
        """Thiết lập log capture"""
        if not self.log_capture:
            self.log_capture = LogCapture(self.log_from_translate)
            sys.stdout = self.log_capture
    
    def restore_stdout(self):
        """Khôi phục stdout"""
        if self.log_capture:
            sys.stdout = self.original_stdout
            self.log_capture = None
    
    def log_from_translate(self, message):
        """Nhận log từ translate.py và hiển thị lên GUI"""
        self.after(0, lambda: self._update_log_ui(message))
    
    def _update_log_ui(self, message):
        """Update log UI (thread-safe)"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            
            # Update log textbox
            if hasattr(self, 'log_textbox') and self.log_textbox is not None:
                self.log_textbox.insert("end", log_message + "\n")
            
            # Auto-scroll if enabled
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                if hasattr(self, 'log_textbox') and self.log_textbox is not None:
                    self.log_textbox.see("end")
            
            # Update progress if it's a progress message
            self._update_progress_from_log(message)
            
            if hasattr(self, 'update_idletasks'):
                self.update_idletasks()
        except Exception as e:
            print(f"⚠️ Lỗi update log UI: {e}")
    
    def _update_progress_from_log(self, message):
        """Cập nhật progress bar từ log messages"""
        try:
            import re
            
            # Pattern: "Hoàn thành chunk X/Y"
            match1 = re.search(r'Hoàn thành chunk (\d+)/(\d+)', message)
            if match1:
                current = int(match1.group(1))
                total = int(match1.group(2))
                progress_percent = (current / total)
                self.progress_bar.set(progress_percent)
                self.progress_text.configure(text=f"Hoàn thành chunk {current}/{total} ({progress_percent*100:.1f}%)")
                return
            
            # Pattern: "Tiến độ: X/Y chunks"
            match2 = re.search(r'Tiến độ: (\d+)/(\d+) chunks \((\d+\.?\d*)%\)', message)
            if match2:
                current = int(match2.group(1))
                total = int(match2.group(2))
                percent = float(match2.group(3))
                self.progress_bar.set(percent / 100)
                self.progress_text.configure(text=f"Tiến độ: {current}/{total} chunks ({percent:.1f}%)")
                return
                
        except Exception:
            pass
    
    def log(self, message):
        """Ghi log vào text area"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}"
            
            if hasattr(self, 'log_textbox') and self.log_textbox is not None:
                self.log_textbox.insert("end", log_message + "\n")
            
            if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                if hasattr(self, 'log_textbox') and self.log_textbox is not None:
                    self.log_textbox.see("end")
                
            if hasattr(self, 'update_idletasks'):
                self.update_idletasks()
            
            print(message)  # Also print to console
        except Exception as e:
            print(f"⚠️ Lỗi log GUI: {e} - Message: {message}")
    
    def clear_logs(self):
        """Xóa logs"""
        try:
            if hasattr(self, 'log_textbox') and self.log_textbox is not None:
                self.log_textbox.delete("0.0", "end")
            print("🗑️ Đã xóa logs")
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
                content = self.log_textbox.get("0.0", "end")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"💾 Đã lưu logs vào: {file_path}")
            except Exception as e:
                self.log(f"❌ Lỗi lưu logs: {e}")
    
    def start_translation(self):
        """Bắt đầu quá trình dịch"""
        if not TRANSLATE_AVAILABLE:
            show_error("Không thể import module dịch. Vui lòng kiểm tra lại file translate.py", parent=self)
            return
            
        # Validate inputs
        if not self.api_key_var.get().strip():
            show_error("Vui lòng nhập API Key", parent=self)
            return
            
        if not self.input_file_var.get().strip():
            show_error("Vui lòng chọn file input", parent=self)
            return
            
        if not os.path.exists(self.input_file_var.get()):
            show_error("File input không tồn tại", parent=self)
            return
        
        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = generate_output_filename(self.input_file_var.get())
            self.output_file_var.set(output_file)
            self.log(f"📝 Tự động tạo tên file output: {os.path.basename(output_file)}")
        
        # Check if input and output are the same
        if os.path.abspath(self.input_file_var.get()) == os.path.abspath(output_file):
            show_error("File input và output không thể giống nhau!", parent=self)
            return
        
        # Warn if output file exists
        if os.path.exists(output_file):
            result = show_question(
                f"File output đã tồn tại:\n{os.path.basename(output_file)}\n\nBạn có muốn ghi đè không?",
                parent=self
            )
            if not result:
                return
        
        # Start translation
        self.is_translating = True
        self.translate_btn.configure(state="disabled", text="⏳ Đang dịch...")
        self.progress_bar.set(0)
        self.progress_text.configure(text="Đang dịch...")
        
        # Setup log capture
        self.setup_log_capture()
        
        self.log("🚀 Bắt đầu quá trình dịch...")
        self.log(f"📁 Input: {os.path.basename(self.input_file_var.get())}")
        self.log(f"📁 Output: {os.path.basename(output_file)}")
        self.log(f"🤖 Model: {self.model_var.get()}")
        
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
                self.after(0, lambda: self.progress_text.configure(text="Hoàn thành!"))
                self.after(0, lambda: self.progress_bar.set(1.0))
                show_success(f"Dịch hoàn thành!\nFile: {os.path.basename(output_file)}", 
                           details=f"Đường dẫn: {output_file}", parent=self)
                show_toast_success("Dịch truyện hoàn thành thành công!")
            else:
                self.log("❌ Dịch thất bại")
                show_error("Quá trình dịch thất bại", parent=self)
                
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            show_error(f"Đã xảy ra lỗi: {e}", details=str(e), parent=self)
        finally:
            self.after(0, self.translation_finished)
    
    def translation_finished(self):
        """Kết thúc quá trình dịch"""
        self.is_translating = False
        self.translate_btn.configure(state="normal", text="🚀 Bắt Đầu Dịch")
        
        # Restore stdout
        self.restore_stdout()
        
        if not self.progress_text.cget("text").startswith("Hoàn thành"):
            self.progress_text.configure(text="Sẵn sàng")
    
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
    
    def save_settings(self):
        """Lưu cài đặt"""
        custom_prompt = ""
        if hasattr(self, 'custom_prompt_textbox'):
            custom_prompt = self.custom_prompt_textbox.get("0.0", "end").strip()
            
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
            show_success("Đã lưu cài đặt!", parent=self)
            show_toast_success("Cài đặt đã được lưu")
        except Exception as e:
            self.log(f"❌ Lỗi lưu cài đặt: {e}")
            show_error(f"Lỗi lưu cài đặt: {e}", parent=self)
    
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
                if hasattr(self, 'custom_prompt_textbox') and settings.get("custom_prompt"):
                    self.custom_prompt_textbox.delete("0.0", "end")
                    self.custom_prompt_textbox.insert("0.0", settings.get("custom_prompt"))
                
                # Trigger context change to show/hide custom prompt
                self.on_context_changed(self.context_var.get())
                
                self.log("📂 Đã tải cài đặt")
        except Exception as e:
            self.log(f"⚠️ Lỗi tải cài đặt: {e}")
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Thay đổi appearance mode"""
        ctk.set_appearance_mode(new_appearance_mode)
    
    def on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        try:
            if self.is_translating:
                if show_question("Đang dịch. Bạn có chắc muốn thoát?", parent=self):
                    self.cleanup_and_exit()
            else:
                self.cleanup_and_exit()
        except Exception as e:
            print(f"Lỗi khi đóng: {e}")
            # Force exit
            self.destroy()
    
    def cleanup_and_exit(self):
        """Cleanup và thoát an toàn"""
        try:
            # Restore stdout
            self.restore_stdout()
            
            # Cancel any running threads
            if hasattr(self, 'translation_thread') and self.translation_thread:
                # Note: Can't force stop threads, just set flag
                self.is_translating = False
            
            # Clear any pending after calls
            self.after_cancel("all")
            
        except Exception as e:
            print(f"Lỗi cleanup: {e}")
        finally:
            # Force destroy
            self.destroy()

def main():
    app = ModernTranslateNovelAI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main() 