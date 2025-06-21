# 🏗️ Hướng Dẫn Build TranslateNovelAI thành EXE

## 📋 Yêu Cầu

1. **Python 3.8+** đã được cài đặt
2. **pip** package manager
3. Kết nối internet để tải dependencies

## 🚀 Cách Build Nhanh

### Cách 1: Sử dụng Batch Script (Windows - Khuyến nghị)
```cmd
build.bat
```
- Chọn option 1 để build file exe đơn
- Script sẽ tự động xử lý mọi thứ

### Cách 2: Sử dụng Python Script
```bash
# Cài đặt dependencies trước
pip install -r requirements.txt

# Build file exe
python build.py
```

### Cách 3: Sử dụng PyInstaller trực tiếp
```bash
# Với file spec tùy chỉnh
pyinstaller --onefile TranslateNovelAI.spec

# Hoặc không dùng spec
pyinstaller --onefile --windowed --name=TranslateNovelAI run_gui.py
```

## 📦 Các Loại Build

### 1. **Onefile Build (Khuyến nghị)**
- Đóng gói thành 1 file `.exe` duy nhất
- Dễ phân phối và sử dụng
- File size lớn hơn (50-150MB)

```bash
python build.py
# hoặc
build.bat → chọn option 1
```

### 2. **Directory Build**
- Tạo thư mục chứa exe và dependencies
- Khởi động nhanh hơn
- Nhiều file hơn để phân phối

```bash
python build.py --directory
# hoặc
build.bat → chọn option 2
```

## 🔧 Tùy Chỉnh Build

### Chỉnh sửa `TranslateNovelAI.spec`
```python
# Thêm/bớt hidden imports
hiddenimports = [
    'your_module_here',
    # ...
]

# Exclude modules không cần
excludes = [
    'large_unused_module',
    # ...
]

# Icon file
icon='path/to/your/icon.ico'
```

### Chỉnh sửa `build.py`
```python
# Thêm arguments cho PyInstaller
args = [
    'pyinstaller',
    '--onefile',
    '--noconsole',  # Ẩn console
    '--add-data=extra_file.txt;.',
    # ...
]
```

## 📁 Cấu Trúc Output

Sau khi build thành công:
```
TranlateNovelAI/
├── dist/
│   └── TranslateNovelAI.exe        # File exe chính
├── build/                          # Thư mục tạm (có thể xóa)
├── TranslateNovelAI.spec           # Spec file (có thể giữ lại)
├── TranslateNovelAI.exe            # Được copy ra ngoài (nếu có)
└── README_EXE.txt                  # Hướng dẫn sử dụng exe
```

## 🐛 Khắc Phục Lỗi

### Lỗi: "Failed to execute script"
**Nguyên nhân:** Thiếu hidden imports
**Giải pháp:**
```bash
# Chạy với console để xem lỗi chi tiết
pyinstaller --onefile --console run_gui.py
```

### Lỗi: "No module named 'module_name'"
**Nguyên nhân:** Module không được đóng gói
**Giải pháp:** Thêm vào `hiddenimports` trong file spec

### Lỗi: File quá lớn
**Nguyên nhân:** Đóng gói quá nhiều dependencies
**Giải pháp:** Thêm modules không cần vào `excludes`

### Lỗi: "Permission denied"
**Nguyên nhân:** Antivirus block hoặc file đang được sử dụng
**Giải pháp:** 
- Tạm tắt antivirus
- Đóng tất cả instance của app
- Chạy CMD as Administrator

## 📊 Tối Ưu Kích Thước

### 1. **Exclude modules không cần**
```python
excludes = [
    'matplotlib', 'numpy', 'pandas', 'scipy',
    'jupyter', 'notebook', 'IPython',
    'tensorflow', 'torch', 'cv2'
]
```

### 2. **Sử dụng UPX compression**
```python
upx=True  # trong file spec
```

### 3. **Strip debug symbols**
```python
strip=True  # trong file spec
```

## 🎯 Tips

1. **Test trước khi build:** Đảm bảo app chạy OK với `python run_gui.py`
2. **Clean build:** Xóa thư mục `build/`, `dist/` trước khi build mới
3. **Icon file:** Chuẩn bị file `.ico` cho icon (optional)
4. **Virtual environment:** Build trong venv để tránh dependencies thừa
5. **Test exe:** Luôn test file exe sau khi build trên máy clean

## 📱 Phân Phối

1. **File exe đơn:** Chỉ cần file `TranslateNovelAI.exe`
2. **Kèm hướng dẫn:** Include file `README_EXE.txt`
3. **API Key:** User cần có Google AI API Key riêng
4. **Internet:** Cần kết nối internet để dịch

## 🔒 Antivirus

File exe có thể bị antivirus báo false positive. Giải pháp:
1. Add exception trong antivirus
2. Submit file để whitelist
3. Build với certificate (advanced)
4. Sử dụng `--noupx` nếu UPX gây vấn đề

---

**Lưu ý:** Build process có thể mất 2-10 phút tùy theo máy và kích thước dependencies. 