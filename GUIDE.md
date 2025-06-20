# 🤖 TranslateNovelAI - Quick Guide

## 🚀 Chạy nhanh

### Phương pháp 1: GUI đơn giản (khuyến nghị)
```bash
cd src
python gui_simple.py
```

### Phương pháp 2: Command line (Interactive)
```bash
cd src
python translate.py
```

**Tính năng Command Line:**
- 🔑 Tự động load API key từ environment hoặc config.json
- 📁 Interactive input/output file selection
- 🤖 Lựa chọn model AI
- 💾 Tùy chọn lưu API key cho lần sau

## 📦 Cài đặt dependencies

```bash
pip install google-generativeai python-docx
```

Hoặc:
```bash
pip install -r requirements_simple.txt
```

**Lưu ý:** Để sử dụng tính năng convert EPUB, bạn cần cài đặt **Pandoc**:
- Tải tại: https://pandoc.org/installing.html
- Cập nhật đường dẫn Pandoc trong file `src/ConvertEpub.py`

## 🔑 Cấu hình API Key

### Cách 1: Environment Variable (khuyến nghị)
```bash
# Windows
set GOOGLE_AI_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_AI_API_KEY=your_api_key_here
```

### Cách 2: File config.json
Copy file `config.example.json` thành `config.json` và thay API key:
```bash
cp config.example.json config.json
# Sau đó chỉnh sửa file config.json
```

Hoặc tạo file `config.json` trong thư mục gốc:
```json
{
  "api_key": "your_api_key_here"
}
```

### Cách 3: Nhập manual mỗi lần chạy
- Command line sẽ hỏi và có tùy chọn lưu vào config.json

## 🔧 Build thành exe

```bash
python build_simple.py
```

## 🎯 Cách dùng GUI

1. **Nhập API Key** từ Google AI Studio
2. **Chọn file truyện** (.txt)
3. **Tùy chọn**: Bật "Tự động convert sang EPUB" và điền thông tin sách
4. **Click "Bắt Đầu Dịch"**
5. **Chờ hoàn thành** - file sẽ được tự động reformat và convert EPUB (nếu bật)

## 📁 Files chính

- `src/gui_simple.py` - GUI app
- `src/translate.py` - Engine dịch
- `src/reformat.py` - Format văn bản
- `build_simple.py` - Build script

## ✨ Tính năng

- ✅ Dịch multi-threading (10 threads)
- ✅ Tự động reformat file
- ✅ **Convert sang EPUB** (TXT → DOCX → EPUB)
- ✅ Tự động nhận diện chương
- ✅ Resume nếu bị gián đoạn
- ✅ Tự động tạo tên file output
- ✅ Lưu/load cài đặt

---
**Happy Translating! 🎉** 