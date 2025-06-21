# 🚀 Hướng Dẫn Build TranslateNovelAI thành File EXE

## 📋 Yêu Cầu Hệ Thống

- Windows 10/11
- Python 3.8+ (khuyến nghị Python 3.9 hoặc 3.10)
- Git (để clone repository)
- Kết nối internet (để tải dependencies)

## 🔧 Cài Đặt Dependencies

### Bước 1: Cài đặt Python
1. Tải Python từ [python.org](https://www.python.org/downloads/)
2. **QUAN TRỌNG**: Chọn "Add Python to PATH" khi cài đặt
3. Kiểm tra cài đặt: mở CMD và gõ `python --version`

### Bước 2: Cài đặt thư viện
```bash
# Cài đặt tất cả dependencies
pip install -r requirements.txt

# Hoặc cài từng cái nếu cần:
pip install customtkinter>=5.2.0
pip install google-generativeai>=0.3.0
pip install Pillow>=10.0.0
pip install python-docx>=1.1.0
pip install pyinstaller>=6.0.0
```

## 🏗️ Build Ứng Dụng

### Cách 1: Sử dụng script tự động (Khuyến nghị)
1. Mở Command Prompt tại thư mục project
2. Chạy: `python build_exe.py`
3. Hoặc double-click file `build.bat`

### Cách 2: Build thủ công
```bash
# Tạo spec file
pyi-makespec --onefile --windowed --icon=src/assets/app_icon.ico run_gui.py

# Chỉnh sửa file run_gui.spec nếu cần

# Build
pyinstaller --clean --noconfirm run_gui.spec
```

## 📁 Cấu Trúc Sau Khi Build

```
TranlateNovelAI/
├── dist/                          # Thư mục chứa file EXE
│   └── TranslateNovelAI.exe      # File EXE chính
├── build/                         # Thư mục build tạm (có thể xóa)
├── TranslateNovelAI.spec         # File cấu hình PyInstaller
└── build_exe.py                  # Script build
```

## ⚡ Tối Ưu Hiệu Suất

### Giảm kích thước file EXE:
```bash
# Sử dụng UPX để nén (tùy chọn)
pip install upx-ucl

# Build với nén
pyinstaller --onefile --windowed --upx-dir=upx TranslateNovelAI.spec
```

### Tùy chọn build khác:
- `--onefile`: Tạo 1 file EXE duy nhất
- `--windowed`: Ẩn console window
- `--clean`: Xóa cache build cũ
- `--noconfirm`: Không hỏi ghi đè

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi: "Module not found"
```bash
# Thêm hidden imports vào spec file
hiddenimports=[
    'customtkinter',
    'PIL._tkinter_finder',
    'google.generativeai',
    # ... thêm modules bị thiếu
]
```

### Lỗi: "Assets not found"
```bash
# Thêm data files vào spec
datas=[
    ('src/assets/*.ico', 'src/assets'),
    ('src/assets/*.png', 'src/assets'),
]
```

### Lỗi: "PyInstaller không được tìm thấy"
```bash
# Cài đặt lại PyInstaller
pip uninstall pyinstaller
pip install pyinstaller
```

### File EXE quá lớn:
- Sử dụng virtual environment để tránh dependencies thừa
- Loại bỏ các modules không cần thiết
- Sử dụng UPX để nén

## 📝 Kiểm Tra File EXE

1. **Test cơ bản**: Double-click file EXE để mở
2. **Test chức năng**: Thử tất cả features của app
3. **Test trên máy khác**: Copy sang máy khác để test

## 🎯 Tips Tối Ưu

1. **Sử dụng Virtual Environment**:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **Build từ source code sạch**:
- Xóa cache: `__pycache__`, `.pyc` files
- Build trên môi trường sạch

3. **Test kỹ trước khi phân phối**:
- Test trên Windows khác nhau
- Test với/không có Python cài sẵn

## 📦 Phân Phối

File EXE cuối cùng sẽ tự chứa:
- ✅ Python runtime
- ✅ Tất cả dependencies
- ✅ Assets và icons
- ✅ GUI components

**Không cần cài Python trên máy đích!**

## 🔍 Debug

Nếu gặp lỗi khi chạy EXE:
1. Tạo version console để xem lỗi:
```bash
pyinstaller --onefile --console run_gui.py
```

2. Check log trong thư mục temp khi chạy EXE

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra Python version: `python --version`
2. Kiểm tra pip: `pip --version`  
3. Kiểm tra PyInstaller: `pyinstaller --version`
4. Xem log chi tiết khi build

---

🎉 **Chúc bạn build thành công!** 