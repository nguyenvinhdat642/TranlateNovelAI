# ⚡ Build EXE Nhanh - TranslateNovelAI

## 🚀 3 Bước Đơn Giản

### Bước 1: Cài Dependencies
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy Build Script
```bash
# Windows (khuyến nghị)
build.bat

# Hoặc Python
python build.py
```

### Bước 3: Lấy File EXE
```
📦 File exe sẽ ở: dist/TranslateNovelAI.exe
```

## 🎯 Tất Cả Trong 1 Lệnh

```batch
pip install -r requirements.txt && python build.py
```

## 📋 Checklist

- [ ] ✅ Python đã cài đặt
- [ ] ✅ Đã chạy `pip install -r requirements.txt`
- [ ] ✅ Ứng dụng chạy OK với `python run_gui.py`
- [ ] ✅ Chạy `python build.py` hoặc `build.bat`
- [ ] ✅ Kiểm tra file `dist/TranslateNovelAI.exe`

## ⚠️ Lưu Ý

- Quá trình build mất 2-10 phút
- File exe khoảng 50-150MB
- Cần kết nối internet để build
- Antivirus có thể báo false positive

## 🆘 Có Lỗi?

1. **Lỗi dependencies:** `pip install pyinstaller customtkinter pillow`
2. **Lỗi build:** Xem file `BUILD_GUIDE.md` để biết chi tiết
3. **Lỗi chạy exe:** Build lại với `--console` để debug

---
💡 **Tip:** Sử dụng `build.bat` cho trải nghiệm đơn giản nhất! 