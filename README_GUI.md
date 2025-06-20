# 🤖 TranslateNovelAI - GUI Application

Ứng dụng dịch truyện tự động với UI, sử dụng Google AI (Gemini) để edit truyện convert.

## ✨ Tính năng

- 🖥️ **Giao diện đẹp**: Sử dụng ttkbootstrap với theme hiện đại
- 🚀 **Multi-threading**: Dịch nhanh với 10 threads song song
- 📝 **Tự động reformat**: Loại bỏ dòng trống thừa sau khi dịch
- 💾 **Lưu cài đặt**: Tự động lưu API key và preferences
- 📊 **Progress tracking**: Theo dõi tiến độ real-time
- 📁 **Tự động tạo tên file**: Không cần chỉ định file output
- ⏹️ **Có thể dừng**: Dừng và tiếp tục dịch bất cứ lúc nào

## 📋 Yêu cầu

- Python 3.8 trở lên
- Google AI API Key (miễn phí tại [Google AI Studio](https://aistudio.google.com/))
- Internet connection

## 🚀 Cách cài đặt và chạy

### Phương pháp 1: Chạy từ source code

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Chạy ứng dụng:**
```bash
cd src
python gui_app.py
```

### Phương pháp 2: Build thành file exe

1. **Chạy build script:**
```bash
python build.py
```

2. **Chạy file exe:**
```bash
dist/TranslateNovelAI.exe
```

## 🎯 Cách sử dụng

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

### Bước 4: Bắt đầu dịch
1. Click **🚀 Bắt Đầu Dịch**
2. Theo dõi progress và logs
3. Có thể click **⏹️ Dừng** để dừng bất cứ lúc nào

### Bước 5: Lưu cài đặt
- Click **💾 Lưu Cài Đặt** để lưu API key và preferences

## 📊 Performance

- **Tốc độ**: ~100-500 dòng/giây (tùy thuộc vào network và API response time)
- **Threads**: 10 threads xử lý song song
- **Chunk size**: 100 dòng/chunk
- **Resume**: Tự động tiếp tục từ vị trí dừng nếu bị gián đoạn

## 🎨 Screenshots

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
└─────────────────────────────────────┘

[🚀 Bắt Đầu Dịch] [⏹️ Dừng] [💾 Lưu Cài Đặt]

┌─────────────────────────────────────┐
│ 📊 Progress                         │
│ Đang dịch... 45/100 chunks (45%)   │
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

## ⚙️ Cấu hình nâng cao

### Tùy chỉnh trong code:
- `NUM_WORKERS`: Số threads (mặc định: 10)
- `CHUNK_SIZE_LINES`: Số dòng/chunk (mặc định: 100)
- `MAX_RETRIES_ON_SAFETY_BLOCK`: Số lần retry khi bị chặn (mặc định: 5)

### File settings.json:
```json
{
  "api_key": "your_api_key",
  "model": "gemini-2.0-flash",
  "auto_reformat": true,
  "last_input_dir": "C:\\novels",
  "last_output_dir": "C:\\translated"
}
```

## 🐛 Troubleshooting

### Lỗi thường gặp:

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

4. **"File không tìm thấy"**
   - Đảm bảo đường dẫn file đúng
   - Kiểm tra quyền đọc/ghi file

## 🔧 Development

### Cấu trúc project:
```
TranslateNovelAI/
├── src/
│   ├── gui_app.py          # GUI chính
│   ├── translate.py        # Engine dịch
│   └── reformat.py         # Format text
├── requirements.txt        # Dependencies
├── build.py               # Build script
└── README_GUI.md          # Hướng dẫn này
```

### Build customization:
Chỉnh sửa file `build.py` để:
- Thay đổi icon
- Thêm/bớt files
- Cấu hình PyInstaller options

## 📄 License

MIT License - Sử dụng tự do cho mục đích cá nhân và thương mại.

## 🤝 Đóng góp

Contributions are welcome! Tạo issue hoặc pull request trên GitHub.

---

**Happy Translating! 🎉** 