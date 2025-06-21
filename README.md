# 🤖 TranslateNovelAI v1.1.0

Ứng dụng dịch truyện tự động sử dụng Google AI (Gemini) 

### **Desktop Modern GUI (CustomTkinter)** 
- Giao diện desktop hiện đại với clean sidebar
- **Stop/Continue functionality** với visual feedback
- Dark/Light theme toggle buttons
- Progress bars và speed monitoring real-time
- Custom dialogs và toast notifications


## 🚀 Quick Start

### 🎮 Launcher tổng hợp
```bash
python run_gui.py
```
### 📥 Download ngay (Classic GUI - Không cần cài đặt)
**[⬇️ Tải TranslateNovelAI.exe](https://github.com/nguyenvinhdat642/TranlateNovelAI/releases/download/v1.0.0/TranslateNovelAI.exe)**

### 🔑 Cần có:
- Google AI API Key (miễn phí tại [aistudio.google.com](https://aistudio.google.com/))
- File truyện định dạng .txt


### ⚡ Performance & Features  
- 🚀 **Smart multi-threading**: Auto-detect CPU và setup threads tối ưu
- 📊 **Real-time monitoring**: Speed tracking với lines/second
- 🎯 **8 bối cảnh dịch**: Hiện đại, cổ đại, fantasy, học đường, công sở, lãng mạn, hành động, tùy chỉnh
- 📝 **Tự động reformat**: Loại bỏ dòng trống thừa sau khi dịch
- 📚 **Convert sang EPUB**: Chuyển đổi từ TXT sang DOCX sang EPUB
- 💾 **Lưu cài đặt**: Tự động lưu API key và preferences
- 📁 **Smart file management**: Auto-generate tên output, prevent overwrites

## 📋 Yêu cầu

### 🔧 Cơ bản
- Python 3.8 trở lên
- Google AI API Key (miễn phí tại [Google AI Studio](https://aistudio.google.com/))
- Internet connection

### 📦 Dependencies (tự động cài với requirements.txt)
- `google-generativeai` - Google AI SDK
- `customtkinter>=5.2.0` - Modern desktop UI framework
- `gradio>=4.0.0` - Web UI framework với CSS custom
- `pillow>=9.0.0` - Xử lý hình ảnh cho icons
- `python-docx` - Xử lý file DOCX
- `pyinstaller` - Build exe files

### 🎨 Tùy chọn
- Pandoc (cho tính năng convert EPUB)
- NSIS (cho tạo installer)

## 📦 Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/nguyenvinhdat642/TranlateNovelAI.git
cd TranslateNovelAI
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cài đặt Pandoc (nếu muốn dùng tính năng EPUB)
- **Windows**: Tải tại https://pandoc.org/installing.html
- **macOS**: `brew install pandoc` 
- **Linux**: `sudo apt install pandoc`
- Cập nhật đường dẫn Pandoc trong file `src/core/ConvertEpub.py`

### 4. Chạy launcher
```bash
python run_gui.py
```

## 🚀 Cách sử dụng

### Phương pháp 1: Download file exe (khuyến nghị - không cần cài đặt)
📥 **[Download TranslateNovelAI.exe](https://github.com/nguyenvinhdat642/TranlateNovelAI/releases/download/v1.0.0/TranslateNovelAI.exe)**
- Tải về và chạy trực tiếp
- Không cần cài đặt Python hay dependencies
- Phiên bản portable, chạy được trên Windows

### Phương pháp 2: GUI từ source code
```bash
# Modern Desktop GUI (Khuyến nghị)
python src/gui/gui_modern.py

# Web GUI với Glass Morphism
python src/gui/gui_web.py

# Classic GUI với Tabs
python src/gui/gui_simple.py
```

### Phương pháp 3: Command line
```bash
cd src/core
python translate.py
```

### Phương pháp 4: Build exe từ source
```bash
# Build tất cả phiên bản GUI
python build_all.py

# Build từng phiên bản riêng lẻ
python build.py          # Classic GUI
python build_simple.py   # Alternative classic build

# Chạy các file exe đã build
dist/TranslateNovelAI_Web/TranslateNovelAI_Web.exe       # Web GUI
dist/TranslateNovelAI_Modern/TranslateNovelAI_Modern.exe # Modern GUI  
dist/TranslateNovelAI_Classic/TranslateNovelAI_Classic.exe # Classic GUI
dist/TranslateNovelAI_Launcher/TranslateNovelAI_Launcher.exe # GUI Launcher
```

## 🔑 Cấu hình API Key

### Cách 1: Environment Variable
```bash
# Windows
set GOOGLE_AI_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_AI_API_KEY=your_api_key_here
```

### Cách 2: File settings.json
Tạo/chỉnh sửa file `settings.json`:
```json
{
  "api_key": "your_api_key_here",
  "model": "gemini-2.0-flash",
  "auto_reformat": true,
  "auto_convert_epub": false,
  "book_author": "Unknown Author",
  "chapter_pattern": "^Chương\\s+\\d+:\\s+.*$",
  "threads": "20",
  "chunk_size": "100"
}
```

### Cách 3: Nhập trực tiếp trong GUI
1. Mở ứng dụng
2. Nhập API Key vào ô tương ứng
3. Click "💾 Lưu Cài Đặt" để lưu lại

## 📝 Hướng dẫn sử dụng Modern GUI

### ⚙️ Settings và Controls

#### Performance Settings
- **Threads**: Auto-detect dựa trên CPU cores (CPU x2, max 20)
- **Chunk Size**: Điều chỉnh dựa trên độ phức tạp nội dung

#### Control Buttons Layout
```
[🚀 Bắt Đầu Dịch]    [💾 Lưu Cài Đặt]
[☀️ Light Mode]      [🌙 Dark Mode]
```

#### EPUB Settings (nếu bật Auto Convert)
- **Tiêu đề sách**: Tự động từ tên file hoặc nhập thủ công
- **Tác giả**: Mặc định "Unknown Author"
- **Chapter Pattern**: Regex để nhận diện chương

## 🎨 Screenshots & Demo

### 💎 Modern Desktop GUI v1.1.0
```
🤖 TranslateNovelAI - Modern Edition
┌────────────────────────────────────────────────────────────────┐
│ 🔑 API Configuration           │  📁 File Management            │
│ API Key: [**********]          │  Input: [novel.txt] [Browse]    │
│ Model: [gemini-2.0-flash ▼]    │  Output: [novel_AI.txt] [Reset] │
│ Context: [Bối cảnh hiện đại ▼] │                                 │
│                                │  📊 Progress                    │
│ ⚡ Performance                 │  ████████░░ 80% (143 lines/s)   │
│ Threads: [20]                  │                                 │
│ Chunk Size: [100]              │  📝 Logs                        │
│                                │  [15:30:25] ✅ Hoàn thành...   │
│ ⚙️ Settings                   │  [15:30:26] 🔄 Auto reformat.. │
│ ☑ Auto reformat               │                                 │
│ ☑ Auto convert EPUB           │                                 │
│                                │                                 │
│ [🚀 Bắt Đầu Dịch] [💾 Lưu]     │                                 │
│ [☀️ Light Mode] [🌙 Dark]      │                                 │
└────────────────────────────────────────────────────────────────┘
```

## 🔧 Performance Tips

### 🚀 Tối ưu tốc độ dịch
1. **Auto-detect threads**: App tự động detect CPU cores và setup tối ưu
2. **Chunk size**: 
   - Nội dung đơn giản: 150-200 dòng
   - Nội dung phức tạp: 50-100 dòng
3. **Model selection**:
   - Nhanh nhất: `gemini-2.0-flash`
   - Cân bằng: `gemini-1.5-flash`
   - Chất lượng cao: `gemini-1.5-pro`

### 💾 Stop/Continue Best Practices
1. **Safe stopping**: Luôn sử dụng button "🛑 Dừng Dịch" thay vì force close
2. **Progress backup**: File `.progress.json` được tạo tự động
3. **Resume smart**: App tự động detect và suggest tiếp tục
4. **Cleanup**: Progress file được xóa khi hoàn thành

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

---

## 🎭 Features Comparison

| Feature | Modern GUI | Web GUI | Classic GUI |
|---------|------------|---------|-------------|
| Stop/Continue | ✅ | ❌ | ❌ |
| Speed Monitoring | ✅ | ✅ | ✅ |
| Auto-detect CPU | ✅ | ✅ | ✅ |
| Custom Dialogs | ✅ | ❌ | ❌ |
| Light/Dark Toggle | ✅ | ❌ | ❌ |
| Progress Recovery | ✅ | ✅ | ✅ |
| EPUB Convert | ✅ | ✅ | ✅ |
| Multi-threading | ✅ | ✅ | ✅ |
---

**Happy Translating! 🎉**

*v1.1.0 - Powered by Stop/Continue, Auto-detect CPU & Modern UI*

**⭐ Star this repo if you find it useful! ⭐**

📧 **Support**: [GitHub Issues](https://github.com/nguyenvinhdat642/TranlateNovelAI/issues)  
🔄 **Updates**: [Releases](https://github.com/nguyenvinhdat642/TranlateNovelAI/releases)  
📖 **Documentation**: [Wiki](https://github.com/nguyenvinhdat642/TranlateNovelAI/wiki) 