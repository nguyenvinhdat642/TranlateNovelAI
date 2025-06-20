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
    from translate import translate_file_optimized, generate_output_filename
    from reformat import fix_text_format
    TRANSLATE_AVAILABLE = True
except ImportError as e:
    TRANSLATE_AVAILABLE = False
    print(f"⚠️ Lỗi import translate: {e}")

class SimpleTranslateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TranslateNovelAI - Simple Test")
        self.root.geometry("600x400")
        
        # Variables
        self.input_file_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.model_var = tk.StringVar(value="gemini-2.0-flash")
        self.is_translating = False
        
        # Load API key
        self.load_api_key()
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🧪 Simple Translate Test", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # API Key
        api_frame = tk.Frame(main_frame)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
        api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Input file
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(input_frame, text="Input:").pack(side=tk.LEFT)
        input_entry = tk.Entry(input_frame, textvariable=self.input_file_var, width=40)
        input_entry.pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT, padx=(5, 0))
        
        # Output file
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(output_frame, text="Output:").pack(side=tk.LEFT)
        output_entry = tk.Entry(output_frame, textvariable=self.output_file_var, width=40)
        output_entry.pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.translate_btn = tk.Button(btn_frame, text="🚀 Dịch", command=self.start_translate, 
                                      bg='#27ae60', fg='white')
        self.translate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹️ Dừng", command=self.stop_translate, 
                                 bg='#e74c3c', fg='white', state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Progress
        self.progress_var = tk.StringVar(value="Sẵn sàng")
        progress_label = tk.Label(main_frame, textvariable=self.progress_var)
        progress_label.pack(pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Log
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def load_api_key(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    api_key = settings.get("api_key", "")
                    if api_key:
                        self.api_key_var.set(api_key)
                        print(f"✅ Loaded API key: {api_key[:10]}***")
        except Exception as e:
            print(f"⚠️ Lỗi load API key: {e}")
    
    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file input",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file_var.set(file_path)
            if not self.output_file_var.get():
                output_path = generate_output_filename(file_path)
                self.output_file_var.set(output_path)
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Chọn file output",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file_var.set(file_path)
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_translate(self):
        if not TRANSLATE_AVAILABLE:
            messagebox.showerror("Lỗi", "Không thể import module dịch")
            return
            
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
        self.progress_bar.start()
        self.progress_var.set("Đang dịch...")
        
        self.log("🚀 Bắt đầu dịch...")
        
        # Run in thread
        self.translate_thread = threading.Thread(
            target=self.run_translate,
            args=(self.input_file_var.get(), output_file, self.api_key_var.get()),
            daemon=True
        )
        self.translate_thread.start()
    
    def run_translate(self, input_file, output_file, api_key):
        try:
            self.log(f"📁 Input: {os.path.basename(input_file)}")
            self.log(f"📁 Output: {os.path.basename(output_file)}")
            
            # Use original translate function
            success = translate_file_optimized(
                input_file=input_file,
                output_file=output_file,
                api_key=api_key,
                model_name=self.model_var.get()
            )
            
            if success and self.is_translating:
                self.log("✅ Dịch thành công!")
                self.progress_var.set("Hoàn thành!")
                messagebox.showinfo("Thành công", f"Dịch hoàn thành!\nFile: {output_file}")
            elif not self.is_translating:
                self.log("⏹️ Đã dừng")
            else:
                self.log("❌ Dịch thất bại")
                messagebox.showerror("Lỗi", "Quá trình dịch thất bại")
                
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            import traceback
            self.log(f"❌ Traceback: {traceback.format_exc()}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        finally:
            self.translation_finished()
    
    def stop_translate(self):
        self.is_translating = False
        self.log("⏹️ Đang dừng...")
    
    def translation_finished(self):
        self.is_translating = False
        self.translate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        if not self.progress_var.get().startswith("Hoàn thành"):
            self.progress_var.set("Sẵn sàng")

def main():
    root = tk.Tk()
    app = SimpleTranslateApp(root)
    
    def on_closing():
        if app.is_translating:
            if messagebox.askokcancel("Thoát", "Đang dịch. Bạn có chắc muốn thoát?"):
                app.stop_translate()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 