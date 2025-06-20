import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import threading
import os
import sys
import time
from datetime import datetime
import json

# Import translate functions
try:
    from translate import translate_file_optimized, generate_output_filename
    from reformat import fix_text_format
    TRANSLATE_AVAILABLE = True
except ImportError as e:
    TRANSLATE_AVAILABLE = False
    print(f"⚠️ Lỗi import: {e}")

class TranslateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TranslateNovelAI - Dịch Truyện Tự Động")
        self.root.geometry("900x700")
        
        # Variables
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar(value="gemini-2.0-flash")
        self.auto_reformat_var = tk.BooleanVar(value=True)
        self.is_translating = False
        self.translation_thread = None
        
        # Load saved settings
        self.load_settings()
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Thiết lập giao diện chính"""
        # Main frame
        main_frame = ttk_bs.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Title
        title_label = ttk_bs.Label(
            main_frame, 
            text="🤖 TranslateNovelAI", 
            font=("Arial", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # API Key frame
        api_frame = ttk_bs.LabelFrame(main_frame, text="🔑 API Configuration", padding=15)
        api_frame.pack(fill=X, pady=(0, 15))
        
        ttk_bs.Label(api_frame, text="Google AI API Key:").pack(anchor=W)
        api_entry = ttk_bs.Entry(
            api_frame, 
            textvariable=self.api_key_var, 
            width=60,
            show="*"
        )
        api_entry.pack(fill=X, pady=(5, 0))
        
        # Model selection
        model_frame = ttk_bs.Frame(api_frame)
        model_frame.pack(fill=X, pady=(10, 0))
        
        ttk_bs.Label(model_frame, text="Model:").pack(side=LEFT)
        model_combo = ttk_bs.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
            state="readonly",
            width=20
        )
        model_combo.pack(side=LEFT, padx=(10, 0))
        
        # File selection frame
        file_frame = ttk_bs.LabelFrame(main_frame, text="📁 File Selection", padding=15)
        file_frame.pack(fill=X, pady=(0, 15))
        
        # Input file
        input_frame = ttk_bs.Frame(file_frame)
        input_frame.pack(fill=X, pady=(0, 10))
        
        ttk_bs.Label(input_frame, text="Input File:").pack(anchor=W)
        
        input_path_frame = ttk_bs.Frame(input_frame)
        input_path_frame.pack(fill=X, pady=(5, 0))
        
        input_entry = ttk_bs.Entry(input_path_frame, textvariable=self.input_file_var)
        input_entry.pack(side=LEFT, fill=X, expand=True)
        
        input_btn = ttk_bs.Button(
            input_path_frame,
            text="Browse",
            command=self.browse_input_file,
            bootstyle="outline-primary"
        )
        input_btn.pack(side=RIGHT, padx=(10, 0))
        
        # Output file
        output_frame = ttk_bs.Frame(file_frame)
        output_frame.pack(fill=X)
        
        ttk_bs.Label(output_frame, text="Output File (tự động tạo nếu để trống):").pack(anchor=W)
        
        output_path_frame = ttk_bs.Frame(output_frame)
        output_path_frame.pack(fill=X, pady=(5, 0))
        
        output_entry = ttk_bs.Entry(output_path_frame, textvariable=self.output_file_var)
        output_entry.pack(side=LEFT, fill=X, expand=True)
        
        output_btn = ttk_bs.Button(
            output_path_frame,
            text="Browse",
            command=self.browse_output_file,
            bootstyle="outline-primary"
        )
        output_btn.pack(side=RIGHT, padx=(10, 0))
        
        # Options frame
        options_frame = ttk_bs.LabelFrame(main_frame, text="⚙️ Options", padding=15)
        options_frame.pack(fill=X, pady=(0, 15))
        
        reformat_check = ttk_bs.Checkbutton(
            options_frame,
            text="Tự động reformat file sau khi dịch",
            variable=self.auto_reformat_var,
            bootstyle="primary"
        )
        reformat_check.pack(anchor=W)
        
        # Control buttons
        control_frame = ttk_bs.Frame(main_frame)
        control_frame.pack(fill=X, pady=(0, 15))
        
        self.translate_btn = ttk_bs.Button(
            control_frame,
            text="🚀 Bắt Đầu Dịch",
            command=self.start_translation,
            bootstyle="success",
            width=20
        )
        self.translate_btn.pack(side=LEFT, padx=(0, 10))
        
        self.stop_btn = ttk_bs.Button(
            control_frame,
            text="⏹️ Dừng",
            command=self.stop_translation,
            bootstyle="danger",
            width=15,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT, padx=(0, 10))
        
        save_settings_btn = ttk_bs.Button(
            control_frame,
            text="💾 Lưu Cài Đặt",
            command=self.save_settings,
            bootstyle="info",
            width=15
        )
        save_settings_btn.pack(side=RIGHT)
        
        # Progress frame
        progress_frame = ttk_bs.LabelFrame(main_frame, text="📊 Progress", padding=15)
        progress_frame.pack(fill=X, pady=(0, 15))
        
        self.progress_var = tk.StringVar(value="Sẵn sàng để bắt đầu...")
        self.progress_label = ttk_bs.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=W, pady=(0, 10))
        
        self.progress_bar = ttk_bs.Progressbar(
            progress_frame,
            mode='indeterminate',
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X)
        
        # Log frame
        log_frame = ttk_bs.LabelFrame(main_frame, text="📝 Logs", padding=15)
        log_frame.pack(fill=BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=BOTH, expand=True)
        
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
    
    def log(self, message):
        """Ghi log vào text area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
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
        
        # Prepare output file
        output_file = self.output_file_var.get().strip()
        if not output_file:
            output_file = generate_output_filename(self.input_file_var.get())
            self.output_file_var.set(output_file)
        
        # Start translation in separate thread
        self.is_translating = True
        self.translate_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.progress_bar.start()
        
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
            
            # Custom translate function with logging
            success = self.translate_with_logging(input_file, output_file, api_key, model_name)
            
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
                
                self.progress_var.set("Hoàn thành!")
                messagebox.showinfo("Thành công", f"Dịch hoàn thành!\nFile đã lưu: {output_file}")
            
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            self.translation_finished()
    
    def translate_with_logging(self, input_file, output_file, api_key, model_name):
        """Wrapper cho translate function với logging"""
        # Redirect stdout để capture logs từ translate function
        original_print = print
        
        def custom_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)
            self.log(message)
            original_print(*args, **kwargs)
        
        # Temporarily replace print
        import builtins
        builtins.print = custom_print
        
        try:
            result = translate_file_optimized(
                input_file=input_file,
                output_file=output_file,
                api_key=api_key,
                model_name=model_name
            )
            return result
        finally:
            # Restore original print
            builtins.print = original_print
    
    def stop_translation(self):
        """Dừng quá trình dịch"""
        self.is_translating = False
        self.log("⏹️ Đang dừng quá trình dịch...")
        self.progress_var.set("Đang dừng...")
        
    def translation_finished(self):
        """Cleanup sau khi dịch xong"""
        self.is_translating = False
        self.translate_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.progress_bar.stop()
        
        if not self.progress_var.get().startswith("Hoàn thành"):
            self.progress_var.set("Sẵn sàng để bắt đầu...")
    
    def save_settings(self):
        """Lưu cài đặt"""
        settings = {
            "api_key": self.api_key_var.get(),
            "model": self.model_var.get(),
            "auto_reformat": self.auto_reformat_var.get(),
            "last_input_dir": os.path.dirname(self.input_file_var.get()) if self.input_file_var.get() else "",
            "last_output_dir": os.path.dirname(self.output_file_var.get()) if self.output_file_var.get() else ""
        }
        
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
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
                
                self.api_key_var.set(settings.get("api_key", ""))
                self.model_var.set(settings.get("model", "gemini-2.0-flash"))
                self.auto_reformat_var.set(settings.get("auto_reformat", True))
                
        except Exception as e:
            print(f"⚠️ Lỗi load cài đặt: {e}")

def main():
    """Main function"""
    # Create the main window with ttkbootstrap theme
    root = ttk_bs.Window(
        title="TranslateNovelAI",
        themename="cosmo",  # Modern theme
        size=(900, 700),
        position=(100, 100)
    )
    
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