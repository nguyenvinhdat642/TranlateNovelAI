# Hướng Dẫn Sử Dụng TranslateNovelAI

## Cài Đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Chạy ứng dụng:**

### Cách 1: Sử dụng file runner (Khuyến nghị)
```bash
python run_gui.py
```

### Cách 2: Chạy từ thư mục src (Nếu cách 1 không hoạt động)
```bash
cd src
python -m gui.gui_modern
```

### Cách 3: Import module (Nếu chạy từ code)
```python
from src.gui.gui_modern import main
main()
```

## Khắc Phục Lỗi

### Lỗi import "attempted relative import with no known parent package"
- **Nguyên nhân:** Chạy file trực tiếp thay vì như một module
- **Giải pháp:** Sử dụng `python run_gui.py` thay vì chạy trực tiếp file gui_modern.py

### Lỗi "name 'generate_output_filename' is not defined"
- **Nguyên nhân:** Không thể import modules từ core
- **Giải pháp:** 
  1. Đảm bảo chạy từ thư mục gốc của project
  2. Sử dụng file `run_gui.py`
  3. Kiểm tra đường dẫn file có đúng không

### Lỗi thiếu dependencies
```bash
pip install customtkinter pillow google-generativeai python-docx
```

## Cấu Trúc Thư Mục
```
TranlateNovelAI/
├── run_gui.py          # File chạy ứng dụng (khuyến nghị)
├── requirements.txt    # Dependencies
├── src/
│   ├── core/          # Modules xử lý dịch
│   └── gui/           # Giao diện
└── settings.json      # Cài đặt (tự động tạo)
```

## Sử Dụng

1. **Khởi chạy:** `python run_gui.py`
2. **Nhập API Key:** Google AI API Key
3. **Chọn file:** Browse để chọn file .txt cần dịch
4. **Cấu hình:** Chọn model và bối cảnh dịch
5. **Bắt đầu:** Click "🚀 Bắt Đầu Dịch"

## Lưu Ý

- Đảm bảo có kết nối internet để sử dụng API
- File input phải là định dạng .txt
- API Key cần có quyền sử dụng Gemini API 