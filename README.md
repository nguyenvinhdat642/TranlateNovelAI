# 🤖 TranslateNovelAI

Ứng dụng dịch truyện tự động sử dụng Google AI (Gemini) để dịch truyện từ tiếng Anh sang tiếng Việt với giao diện GUI hiện đại và dễ sử dụng.

## 🚀 Quick Start

### 📥 Download ngay (Không cần cài đặt)
**[⬇️ Tải TranslateNovelAI.exe](https://github.com/nguyenvinhdat642/TranlateNovelAI/releases/download/v1.0.0/TranslateNovelAI.exe)**

✅ Chạy trực tiếp trên Windows  
✅ Không cần Python hay dependencies  
✅ Giao diện GUI đầy đủ với 4 tabs chuyên biệt  

### 🔑 Cần có:
- Google AI API Key (miễn phí tại [aistudio.google.com](https://aistudio.google.com/))
- File truyện định dạng .txt

## ✨ Tính năng chính

- 🚀 **Multi-threading**: Dịch nhanh với 10 threads song song
- 📝 **Tự động reformat**: Loại bỏ dòng trống thừa sau khi dịch
- 📚 **Convert sang EPUB**: Chuyển đổi từ TXT sang DOCX sang EPUB
- 📊 **Progress tracking**: Theo dõi tiến độ dịch real-time với logs chi tiết
- 💾 **Lưu cài đặt**: Tự động lưu API key và preferences
- 🔄 **Resume**: Tự động tiếp tục từ vị trí dừng nếu bị gián đoạn
- 📁 **Tự động tạo tên file**: Không cần chỉ định file output, tự động tạo với suffix "_TranslateAI"
- 🎯 **Smart file management**: Tự động reset tên output khi chọn file mới, tránh ghi đè
- 🔧 **Multi-tab interface**: Giao diện tab quản lý chức năng (Dịch, Cài đặt, EPUB, Logs)
- 📝 **Real-time logging**: Hiển thị logs từ engine dịch lên GUI real-time

## 📋 Yêu cầu

- Python 3.8 trở lên
- Google AI API Key (miễn phí tại [Google AI Studio](https://aistudio.google.com/))
- Internet connection
- Pandoc (cho tính năng convert EPUB)

## 📦 Cài đặt

### 1. Clone repository
```bash
git https://github.com/nguyenvinhdat642/TranlateNovelAI.git
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

### Phương pháp 1: Download file exe (khuyến nghị - không cần cài đặt)
📥 **[Download TranslateNovelAI.exe](https://github.com/nguyenvinhdat642/TranlateNovelAI/releases/download/v1.0.0/TranslateNovelAI.exe)**
- Tải về và chạy trực tiếp
- Không cần cài đặt Python hay dependencies
- Phiên bản portable, chạy được trên Windows

### Phương pháp 2: GUI từ source code
```bash
cd src
python gui_simple.py
```

### Phương pháp 3: Command line
```bash
cd src
python translate.py
```

### Phương pháp 4: Build exe từ source
```bash
# Build exe từ source code
python build.py

# Chạy file exe đã build
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
Tạo/chỉnh sửa file `settings.json`:
```json
{
  "api_key": "your_api_key_here",
  "model": "gemini-2.0-flash",
  "auto_reformat": true,
  "auto_convert_epub": false,
  "book_author": "Unknown Author",
  "chapter_pattern": "^Chương\\s+\\d+:\\s+.*$",
  "threads": "10",
  "chunk_size": "100"
}
```

### Cách 3: Nhập trực tiếp trong GUI
1. Mở ứng dụng
2. Nhập API Key vào ô tương ứng
3. Click "💾 Lưu Cài Đặt" để lưu lại

## 📝 Hướng dẫn sử dụng GUI

### Tab 1: 🚀 Dịch Truyện

#### Bước 1: Cấu hình API
1. Nhập **Google AI API Key** vào ô "API Key"
2. Chọn **Model** (khuyến nghị: `gemini-2.0-flash`)

#### Bước 2: Chọn file
1. Click **Browse** ở phần "Input File"
2. Chọn file truyện (.txt) cần dịch
3. File output sẽ được **tự động tạo tên** (ví dụ: `novel.txt` → `novel_TranslateAI.txt`)
4. Click **🔄 Reset** để tái tạo tên output nếu cần

#### Bước 3: Cấu hình options
- ✅ **Tự động reformat**: Loại bỏ dòng trống thừa (khuyến nghị bật)
- ✅ **Convert EPUB**: Tự động chuyển đổi sang EPUB sau khi dịch

#### Bước 4: Bắt đầu dịch
1. Click **🚀 Bắt Đầu Dịch**
2. Theo dõi progress bar và logs real-time
3. Quá trình sẽ tự động chuyển sang tab Logs để hiển thị chi tiết

### Tab 2: ⚙️ Cài Đặt
- **API Settings**: Cấu hình API key và model
- **Translation Settings**: Tùy chọn reformat và EPUB
- **Performance Settings**: Số threads và chunk size
- **Save/Load**: Lưu và tải cài đặt

### Tab 3: 📚 EPUB
- **EPUB Settings**: Tiêu đề sách, tác giả, pattern chương
- **Manual Conversion**: Convert file TXT sang EPUB thủ công
- **Hướng dẫn**: Thông tin về yêu cầu Pandoc

### Tab 4: 📝 Logs
- **Log Controls**: Xóa logs, lưu logs, auto-scroll
- **Full Log Display**: Hiển thị đầy đủ logs từ quá trình dịch

## 🎨 Giao diện mới

### Tab "🚀 Dịch Truyện"
```
🤖 TranslateNovelAI
┌─────────────────────────────────────────────────────────┐
│ [🚀 Dịch Truyện] [⚙️ Cài Đặt] [📚 EPUB] [📝 Logs]    │
├─────────────────────────────────────────────────────────┤
│ 🔑 API Configuration                                    │
│ Google AI API Key: [**********]                        │
│ Model: [gemini-2.0-flash ▼]                            │
│                                                         │
│ 📁 File Selection                                       │
│ Input File: [C:\novel.txt] [Browse]                     │
│ Output File: [C:\novel_TranslateAI.txt] [Browse][Reset] │
│                                                         │
│ ⚙️ Options                                             │
│ ☑ Tự động reformat file sau khi dịch                   │
│ ☑ Tự động convert sang EPUB sau khi dịch               │
│                                                         │
│ 📝 Logs (Xem chi tiết ở tab Logs)                      │
│ [14:30:25] 🚀 Bắt đầu quá trình dịch...                │
│ [14:30:25] 📁 Input: novel.txt                         │
│ [14:30:26] ✅ Hoàn thành chunk 1/100                   │
└─────────────────────────────────────────────────────────┘
```

## 🚨 Thay đổi quan trọng

### ❌ Đã loại bỏ button "Dừng"
- Để đơn giản hóa giao diện
- Nếu cần dừng, có thể đóng ứng dụng trực tiếp
- Tiến độ vẫn được lưu và có thể tiếp tục sau

### 🎯 Cải thiện Smart File Management
- **Tự động reset tên output** khi chọn file input mới
- **Nút Reset** để tái tạo tên output bất cứ lúc nào
- **Validation**: Cảnh báo khi file output đã tồn tại
- **Auto-sync**: EPUB input tự động đồng bộ với file đang dịch

## 🐛 Xử lý lỗi thường gặp

1. **"Không thể import module dịch"**
   - Đảm bảo files `translate.py`, `reformat.py`, `ConvertEpub.py` ở cùng thư mục
   - Kiểm tra đường dẫn files

2. **"API Key không hợp lệ"**
   - Kiểm tra API key tại [Google AI Studio](https://aistudio.google.com/)
   - Đảm bảo API key có quyền truy cập Gemini

3. **"File input và output không thể giống nhau"**
   - Sử dụng nút **🔄 Reset** để tự động tạo tên output mới
   - Hoặc chọn thư mục khác cho file output

4. **"Dịch chậm"**
   - Kiểm tra kết nối internet
   - Thử giảm số threads trong tab Cài đặt
   - Chọn model nhẹ hơn (gemini-1.5-flash)

5. **"Lỗi convert EPUB"**
   - Kiểm tra đường dẫn Pandoc trong file `src/ConvertEpub.py`
   - Đảm bảo đã cài đặt Pandoc
   - Kiểm tra pattern nhận diện chương

## 🔧 Cấu trúc dự án

```
TranslateNovelAI/
├── src/
│   ├── gui_simple.py       # GUI chính với 4 tabs
│   ├── translate.py        # Engine dịch với multi-threading
│   ├── reformat.py         # Format text loại bỏ dòng trống thừa
│   ├── ConvertEpub.py      # Chuyển đổi TXT → DOCX → EPUB
│   └── settings.json       # Cấu hình người dùng
├── requirements.txt        # Dependencies: google-generativeai, python-docx, pyinstaller
├── build.py               # Build script tạo file exe
└── README.md              # Tài liệu hướng dẫn
```

## 🆕 Tính năng mới

- **🔄 Auto-reset output filename**: Tự động tạo tên file mới khi chọn input mới
- **📊 Real-time progress tracking**: Cập nhật progress bar từ logs engine dịch
- **🎛️ Multi-tab interface**: Tách riêng chức năng thành 4 tabs chuyên biệt
- **📝 Dual logging**: Mini log trong tab dịch + full log riêng biệt
- **🔧 Enhanced validation**: Kiểm tra file trùng lặp, cảnh báo ghi đè
- **🎯 Smart suggestions**: Tự động suggest file dịch cho EPUB conversion

## 💡 Tips sử dụng

1. **Để có kết quả tốt nhất**: Sử dụng model `gemini-2.0-flash`
2. **Tối ưu tốc độ**: Điều chỉnh số threads trong tab Cài đặt (mặc định: 10)
3. **EPUB conversion**: Đảm bảo pattern chương chính xác (mặc định: `^Chương\s+\d+:\s+.*$`)
4. **Theo dõi tiến độ**: Chuyển sang tab Logs để xem chi tiết quá trình dịch
5. **Backup settings**: Click "💾 Lưu Cài Đặt" sau khi cấu hình

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

---

**Happy Translating! 🎉**

*Phiên bản cập nhật với giao diện tabbed, smart file management và real-time logging*

