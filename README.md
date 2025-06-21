# 🤖 TranslateNovelAI

Ứng dụng dịch truyện tự động sử dụng Google AI (Gemini) để dịch truyện từ tiếng Anh sang tiếng Việt.

## ✨ Tính năng chính

- 🚀 **Multi-threading**: Dịch nhanh với 10 threads song song
- 📝 **Tự động reformat**: Loại bỏ dòng trống thừa sau khi dịch
- 📚 **Convert sang EPUB**: Chuyển đổi từ TXT sang DOCX sang EPUB
- 📊 **Progress tracking**: Theo dõi tiến độ dịch real-time
- 💾 **Lưu cài đặt**: Tự động lưu API key và preferences
- 🔄 **Resume**: Tự động tiếp tục từ vị trí dừng nếu bị gián đoạn
- 📁 **Tự động tạo tên file**: Không cần chỉ định file output
- ⏹️ **Có thể dừng**: Dừng và tiếp tục dịch bất cứ lúc nào

## 📋 Yêu cầu

- Python 3.8 trở lên
- Google AI API Key (miễn phí tại [Google AI Studio](https://aistudio.google.com/))
- Internet connection
- Pandoc (cho tính năng convert EPUB)

## 📦 Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/yourusername/TranslateNovelAI.git
cd TranslateNovelAI
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cài đặt Pandoc (nếu muốn dùng tính năng EPUB)
- Tải tại: https://pandoc.org/installing.html
- Cập nhật đường dẫn Pandoc trong file `src/ConvertEpub.py`

## 🚀 Cách sử dụng

### Phương pháp 1: GUI (khuyến nghị)
```bash
cd src
python gui_simple.py
```

### Phương pháp 2: Command line
```bash
cd src
python translate.py
```

### Phương pháp 3: File exe
```bash
# Build exe
python build.py

# Chạy file exe
dist/TranslateNovelAI.exe
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
Chỉnh sửa file `settings.json`:
```json
{
  "api_key": "your_api_key_here",
  "model": "gemini-2.0-flash",
  "auto_reformat": true,
  "auto_convert_epub": false,
  "book_author": "Unknown Author",
  "chapter_pattern": "^Chương\\s+\\d+:\\s+.*$"
}
```

### Cách 3: Nhập trực tiếp trong GUI
1. Mở ứng dụng
2. Nhập API Key vào ô tương ứng
3. Click "Lưu Cài Đặt" để lưu lại

## 📝 Hướng dẫn sử dụng GUI

### Bước 1: Cấu hình API
1. Mở ứng dụng
2. Nhập **Google AI API Key** vào ô "API Key"
3. Chọn **Model** (khuyến nghị: `gemini-2.0-flash`)

### Bước 2: Chọn file
1. Click **Browse** ở phần "Input File"
2. Chọn file truyện (.txt) cần dịch
3. File output sẽ được tự động tạo tên (có thể chỉnh sửa nếu cần)

### Bước 3: Cấu hình options
- ✅ **Tự động reformat**: Loại bỏ dòng trống thừa (khuyến nghị bật)
- ✅ **Convert EPUB**: Tự động chuyển đổi sang EPUB sau khi dịch

### Bước 4: Bắt đầu dịch
1. Click **🚀 Bắt Đầu Dịch**
2. Theo dõi progress và logs
3. Có thể click **⏹️ Dừng** để dừng bất cứ lúc nào

## 🎨 Giao diện

```
🤖 TranslateNovelAI
┌─────────────────────────────────────┐
│ 🔑 API Configuration                │
│ Google AI API Key: [**********]     │
│ Model: [gemini-2.0-flash ▼]         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📁 File Selection                   │
│ Input File: [C:\novel.txt] [Browse] │
│ Output: [C:\novel_TranslateAI.txt]  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ⚙️ Options                          │
│ ☑ Tự động reformat file sau khi dịch│
│ ☑ Tự động convert sang EPUB         │
└─────────────────────────────────────┘

[🚀 Bắt Đầu Dịch] [⏹️ Dừng] [💾 Lưu Cài Đặt]

┌─────────────────────────────────────┐
│ 📊 Progress                         │
│ Đang dịch... 45/100 chunks (45%)    │
│ ████████████░░░░░░░░░░░░░░░░░░░░░   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📝 Logs                             │
│ [14:30:25] 🚀 Bắt đầu quá trình dịch│
│ [14:30:25] 📁 Input: novel.txt      │
│ [14:30:25] 🤖 Model: gemini-2.0-flash│
│ [14:30:26] ✅ Hoàn thành chunk 1/100│
│ [14:30:27] ✅ Hoàn thành chunk 2/100│
└─────────────────────────────────────┘
```

## 🐛 Xử lý lỗi thường gặp

1. **"Không thể import module dịch"**
   - Đảm bảo files `translate.py` và `reformat.py` ở cùng thư mục
   - Kiểm tra đường dẫn files

2. **"API Key không hợp lệ"**
   - Kiểm tra API key tại [Google AI Studio](https://aistudio.google.com/)
   - Đảm bảo API key có quyền truy cập Gemini

3. **"Dịch chậm"**
   - Kiểm tra kết nối internet
   - Thử giảm số threads trong code
   - Chọn model nhẹ hơn (gemini-1.5-flash)

4. **"Lỗi convert EPUB"**
   - Kiểm tra đường dẫn Pandoc trong file `src/ConvertEpub.py`
   - Đảm bảo đã cài đặt Pandoc

## 🔧 Cấu trúc dự án

```
TranslateNovelAI/
├── src/
│   ├── gui_simple.py       # GUI chính
│   ├── translate.py        # Engine dịch
│   ├── reformat.py         # Format text
│   ├── ConvertEpub.py      # Chuyển đổi EPUB
│   └── settings.json       # Cấu hình
├── requirements.txt        # Dependencies
└── build.py                # Build script
```

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

---

**Happy Translating! 🎉**

