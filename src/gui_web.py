import gradio as gr
import os
import sys
import time
import json
import threading
from datetime import datetime
import queue
import tempfile

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

# CSS styling for modern look
custom_css = """
/* Main container styling */
.gradio-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header styling */
.header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.header h1 {
    color: white;
    font-size: 2.5em;
    font-weight: bold;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.2em;
    margin: 10px 0 0 0;
}

/* Card styling */
.card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

/* Button styling */
.translate-btn {
    background: linear-gradient(45deg, #28a745, #20c997);
    border: none;
    border-radius: 25px;
    padding: 15px 30px;
    font-size: 1.1em;
    font-weight: bold;
    color: white;
    box-shadow: 0 4px 15px 0 rgba(40, 167, 69, 0.4);
    transition: all 0.3s ease;
}

.translate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px 0 rgba(40, 167, 69, 0.6);
}

/* Progress bar styling */
.progress-container {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
}

/* Input field styling */
.input-field {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    color: white;
    padding: 10px;
}

.input-field::placeholder {
    color: rgba(255, 255, 255, 0.7);
}

/* Log area styling */
.log-area {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    padding: 15px;
    color: #00ff00;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    max-height: 400px;
    overflow-y: auto;
}

/* Status indicator */
.status-ready {
    color: #28a745;
    font-weight: bold;
}

.status-working {
    color: #ffc107;
    font-weight: bold;
}

.status-error {
    color: #dc3545;
    font-weight: bold;
}

/* Animated background */
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.animated-bg {
    background: linear-gradient(-45deg, #667eea, #764ba2, #667eea, #764ba2);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
"""

class WebTranslateApp:
    def __init__(self):
        self.is_translating = False
        self.log_queue = queue.Queue()
        self.progress_info = {"current": 0, "total": 0, "status": "Sẵn sàng"}
        
        # Settings
        self.settings = self.load_settings()
        
    def get_system_instruction(self, context, custom_prompt=""):
        """Tạo system instruction dựa trên bối cảnh"""
        base_instruction = "Dịch văn bản sau sang tiếng Việt. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặt trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung."
        
        context_instructions = {
            "Bối cảnh hiện đại": f"{base_instruction} Bối cảnh hiện đại. Giữ nguyên các từ ngữ thô tục, tình dục.",
            "Bối cảnh cổ đại": f"{base_instruction} Bối cảnh cổ đại. Sử dụng ngôn ngữ trang trọng, lịch sự phù hợp thời kỳ cổ đại.",
            "Bối cảnh fantasy/viễn tưởng": f"{base_instruction} Bối cảnh fantasy/viễn tưởng. Giữ nguyên tên thuật ngữ ma thuật, tên kỹ năng.",
            "Bối cảnh học đường": f"{base_instruction} Bối cảnh học đường. Sử dụng ngôn ngữ trẻ trung, năng động.",
            "Bối cảnh công sở": f"{base_instruction} Bối cảnh công sở. Sử dụng ngôn ngữ lịch sự, trang trọng.",
            "Bối cảnh lãng mạn": f"{base_instruction} Bối cảnh lãng mạn. Chú trọng cảm xúc, ngôn ngữ ngọt ngào.",
            "Bối cảnh hành động": f"{base_instruction} Bối cảnh hành động. Giữ nguyên tên kỹ năng, vũ khí.",
            "Tùy chỉnh": custom_prompt if custom_prompt.strip() else base_instruction
        }
        
        return context_instructions.get(context, base_instruction)
    
    def log_message(self, message):
        """Thêm message vào queue để hiển thị log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_queue.put(log_entry)
        print(message)  # Also print to console
    
    def get_logs(self):
        """Lấy tất cả logs từ queue"""
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        return "\n".join(logs) if logs else ""
    
    def load_settings(self):
        """Tải cài đặt"""
        default_settings = {
            "api_key": "",
            "model": "gemini-2.0-flash",
            "context": "Bối cảnh hiện đại",
            "auto_reformat": True,
            "auto_convert_epub": False,
            "book_author": "Unknown Author",
            "chapter_pattern": r"^Chương\s+\d+:\s+.*$"
        }
        
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
            self.log_message("📂 Đã tải cài đặt")
        except Exception as e:
            self.log_message(f"⚠️ Lỗi tải cài đặt: {e}")
        
        return default_settings
    
    def save_settings(self, api_key, model, context, auto_reformat, auto_epub, book_author, chapter_pattern):
        """Lưu cài đặt"""
        settings = {
            "api_key": api_key,
            "model": model,
            "context": context,
            "auto_reformat": auto_reformat,
            "auto_convert_epub": auto_epub,
            "book_author": book_author,
            "chapter_pattern": chapter_pattern
        }
        
        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.log_message("💾 Đã lưu cài đặt")
            return "✅ Đã lưu cài đặt thành công!"
        except Exception as e:
            self.log_message(f"❌ Lỗi lưu cài đặt: {e}")
            return f"❌ Lỗi lưu cài đặt: {e}"
    
    def translate_file(self, input_file, api_key, model, context, custom_prompt, auto_reformat, auto_epub, book_title, book_author, chapter_pattern, progress=gr.Progress()):
        """Thực hiện dịch file"""
        
        if not TRANSLATE_AVAILABLE:
            return None, "❌ Không thể import module dịch"
        
        if not input_file:
            return None, "❌ Vui lòng chọn file input"
        
        if not api_key.strip():
            return None, "❌ Vui lòng nhập API Key"
        
        # Reset progress
        self.progress_info = {"current": 0, "total": 0, "status": "Đang bắt đầu..."}
        
        try:
            self.is_translating = True
            self.log_message("🚀 Bắt đầu quá trình dịch...")
            
            # Generate output filename
            output_file = generate_output_filename(input_file.name)
            self.log_message(f"📁 Input: {os.path.basename(input_file.name)}")
            self.log_message(f"📁 Output: {os.path.basename(output_file)}")
            self.log_message(f"🤖 Model: {model}")
            
            # Get system instruction
            system_instruction = self.get_system_instruction(context, custom_prompt)
            self.log_message(f"🎯 Context: {context}")
            
            # Copy input file to temp location for processing
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            with open(input_file.name, 'rb') as src:
                temp_input.write(src.read())
            temp_input.close()
            
            # Run translation
            success = translate_file_optimized(
                input_file=temp_input.name,
                output_file=output_file,
                api_key=api_key,
                model_name=model,
                system_instruction=system_instruction
            )
            
            if success:
                self.log_message("✅ Dịch hoàn thành!")
                
                # Auto reformat if enabled
                if auto_reformat:
                    self.log_message("🔄 Đang reformat file...")
                    try:
                        fix_text_format(output_file)
                        self.log_message("✅ Reformat hoàn thành!")
                    except Exception as e:
                        self.log_message(f"⚠️ Lỗi reformat: {e}")
                
                # Auto convert to EPUB if enabled
                if auto_epub and EPUB_AVAILABLE:
                    self.log_message("📚 Đang convert sang EPUB...")
                    try:
                        self.convert_to_epub(output_file, book_title, book_author, chapter_pattern)
                    except Exception as e:
                        self.log_message(f"⚠️ Lỗi convert EPUB: {e}")
                
                self.progress_info["status"] = "Hoàn thành!"
                
                # Clean up temp file
                os.unlink(temp_input.name)
                
                return output_file, "✅ Dịch hoàn thành thành công!"
            else:
                return None, "❌ Quá trình dịch thất bại"
                
        except Exception as e:
            self.log_message(f"❌ Lỗi: {e}")
            return None, f"❌ Đã xảy ra lỗi: {e}"
        finally:
            self.is_translating = False
    
    def convert_to_epub(self, txt_file, book_title, book_author, chapter_pattern):
        """Convert file to EPUB"""
        try:
            base_name = os.path.splitext(txt_file)[0]
            docx_file = base_name + ".docx"
            epub_file = base_name + ".epub"
            
            title = book_title or os.path.splitext(os.path.basename(txt_file))[0]
            author = book_author or "Unknown Author"
            pattern = chapter_pattern or r"^Chương\s+\d+:\s+.*$"
            
            # Convert TXT to DOCX
            self.log_message("📄 Đang convert TXT → DOCX...")
            if txt_to_docx(txt_file, docx_file, title, pattern):
                self.log_message("✅ Convert TXT → DOCX hoàn thành!")
                
                # Convert DOCX to EPUB
                self.log_message("📚 Đang convert DOCX → EPUB...")
                if docx_to_epub(docx_file, epub_file, title, author):
                    self.log_message(f"✅ Convert EPUB hoàn thành: {epub_file}")
                else:
                    self.log_message("❌ Convert DOCX → EPUB thất bại")
            else:
                self.log_message("❌ Convert TXT → DOCX thất bại")
                
        except Exception as e:
            self.log_message(f"❌ Lỗi convert EPUB: {e}")

def create_interface():
    """Tạo giao diện Gradio"""
    app = WebTranslateApp()
    
    with gr.Blocks(css=custom_css, title="🤖 TranslateNovelAI", theme=gr.themes.Soft()) as interface:
        
        # Header
        gr.HTML("""
        <div class="header animated-bg">
            <h1>🤖 TranslateNovelAI</h1>
            <p>Modern Web Edition - Dịch truyện bằng AI</p>
        </div>
        """)
        
        with gr.Row():
            # Left column - Main controls
            with gr.Column(scale=2):
                with gr.Group():
                    gr.Markdown("### 📁 File Management")
                    
                    input_file = gr.File(
                        label="📂 Chọn file truyện cần dịch",
                        file_types=[".txt"],
                        elem_classes=["input-field"]
                    )
                    
                    output_file = gr.File(
                        label="📥 File đã dịch",
                        interactive=False
                    )
                
                with gr.Group():
                    gr.Markdown("### 🔑 API Configuration")
                    
                    api_key = gr.Textbox(
                        label="Google AI API Key",
                        type="password",
                        placeholder="Nhập API Key của bạn...",
                        value=app.settings.get("api_key", ""),
                        elem_classes=["input-field"]
                    )
                    
                    with gr.Row():
                        model = gr.Dropdown(
                            label="Model",
                            choices=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
                            value=app.settings.get("model", "gemini-2.0-flash")
                        )
                        
                        context = gr.Dropdown(
                            label="Bối cảnh dịch",
                            choices=[
                                "Bối cảnh hiện đại",
                                "Bối cảnh cổ đại",
                                "Bối cảnh fantasy/viễn tưởng",
                                "Bối cảnh học đường",
                                "Bối cảnh công sở",
                                "Bối cảnh lãng mạn",
                                "Bối cảnh hành động",
                                "Tùy chỉnh"
                            ],
                            value=app.settings.get("context", "Bối cảnh hiện đại")
                        )
                
                # Custom prompt (conditionally visible)
                custom_prompt = gr.Textbox(
                    label="Custom Prompt",
                    placeholder="Nhập prompt tùy chỉnh...",
                    lines=3,
                    visible=False,
                    elem_classes=["input-field"]
                )
                
                with gr.Group():
                    gr.Markdown("### ⚙️ Settings")
                    
                    with gr.Row():
                        auto_reformat = gr.Checkbox(
                            label="Auto reformat after translation",
                            value=app.settings.get("auto_reformat", True)
                        )
                        
                        auto_epub = gr.Checkbox(
                            label="Auto convert to EPUB",
                            value=app.settings.get("auto_convert_epub", False)
                        )
                
                # EPUB settings (conditionally visible)
                with gr.Group(visible=False) as epub_settings:
                    gr.Markdown("### 📚 EPUB Settings")
                    
                    book_title = gr.Textbox(
                        label="Tiêu đề sách",
                        placeholder="Tự động từ tên file...",
                        elem_classes=["input-field"]
                    )
                    
                    with gr.Row():
                        book_author = gr.Textbox(
                            label="Tác giả",
                            value=app.settings.get("book_author", "Unknown Author"),
                            elem_classes=["input-field"]
                        )
                        
                        chapter_pattern = gr.Textbox(
                            label="Pattern nhận diện chương (regex)",
                            value=app.settings.get("chapter_pattern", r"^Chương\s+\d+:\s+.*$"),
                            elem_classes=["input-field"]
                        )
                
                # Action buttons
                with gr.Row():
                    translate_btn = gr.Button(
                        "🚀 Bắt Đầu Dịch",
                        variant="primary",
                        size="lg",
                        elem_classes=["translate-btn"]
                    )
                    
                    save_btn = gr.Button(
                        "💾 Lưu Cài Đặt",
                        variant="secondary"
                    )
            
            # Right column - Status and logs
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### 📊 Progress & Status")
                    
                    status_text = gr.Textbox(
                        label="Trạng thái",
                        value="Sẵn sàng",
                        interactive=False,
                        elem_classes=["status-ready"]
                    )
                    
                    progress_bar = gr.Progress()
                
                with gr.Group():
                    gr.Markdown("### 📝 Logs")
                    
                    log_output = gr.Textbox(
                        label="",
                        lines=15,
                        max_lines=20,
                        interactive=False,
                        elem_classes=["log-area"],
                        show_label=False
                    )
                    
                    with gr.Row():
                        refresh_logs_btn = gr.Button("🔄 Refresh Logs", size="sm")
                        clear_logs_btn = gr.Button("🗑️ Clear Logs", size="sm")
        
        # Event handlers
        def toggle_custom_prompt(context_value):
            return gr.update(visible=(context_value == "Tùy chỉnh"))
        
        def toggle_epub_settings(auto_epub_value):
            return gr.update(visible=auto_epub_value)
        
        def auto_fill_book_title(file):
            if file:
                filename = os.path.splitext(os.path.basename(file.name))[0]
                return gr.update(value=filename)
            return gr.update()
        
        def refresh_logs():
            return app.get_logs()
        
        def clear_logs():
            # Clear the queue
            while not app.log_queue.empty():
                try:
                    app.log_queue.get_nowait()
                except queue.Empty:
                    break
            return ""
        
        # Connect events
        context.change(toggle_custom_prompt, inputs=[context], outputs=[custom_prompt])
        auto_epub.change(toggle_epub_settings, inputs=[auto_epub], outputs=[epub_settings])
        input_file.change(auto_fill_book_title, inputs=[input_file], outputs=[book_title])
        
        translate_btn.click(
            app.translate_file,
            inputs=[input_file, api_key, model, context, custom_prompt, auto_reformat, auto_epub, book_title, book_author, chapter_pattern],
            outputs=[output_file, status_text]
        )
        
        save_btn.click(
            app.save_settings,
            inputs=[api_key, model, context, auto_reformat, auto_epub, book_author, chapter_pattern],
            outputs=[status_text]
        )
        
        refresh_logs_btn.click(refresh_logs, outputs=[log_output])
        clear_logs_btn.click(clear_logs, outputs=[log_output])
        
        # Auto-refresh logs every 2 seconds
        interface.load(refresh_logs, outputs=[log_output], every=2)
    
    return interface

def main():
    """Chạy ứng dụng web"""
    interface = create_interface()
    
    # Launch with custom settings
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,       # Default Gradio port
        share=False,            # Set to True to create public link
        show_error=True,
        favicon_path=None,
        app_kwargs={
            "docs_url": None,   # Disable docs
            "redoc_url": None   # Disable redoc
        }
    )

if __name__ == "__main__":
    main() 