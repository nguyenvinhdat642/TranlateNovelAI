"""
Script để build ứng dụng TranslateNovelAI thành file exe
Chạy: python build.py
"""

import PyInstaller.__main__
import os
import sys

def build_app():
    """Build ứng dụng thành file exe"""
    
    # Các tham số cho PyInstaller
    args = [
        'src/gui_simple.py',       # File chính
        '--onefile',                # Tạo 1 file exe duy nhất
        '--windowed',               # Không hiện console (GUI app)
        '--name=TranslateNovelAI',  # Tên file exe
        '--add-data=src/translate.py;.',        # Include translate.py
        '--add-data=src/reformat.py;.',         # Include reformat.py
        '--add-data=src/ConvertEpub.py;.',      # Include ConvertEpub.py
        '--hidden-import=google.generativeai',   # Hidden imports
        '--hidden-import=tkinter',
        '--hidden-import=threading',
        '--hidden-import=json',
        '--distpath=dist',          # Thư mục output
        '--workpath=build',         # Thư mục build tạm
        '--clean',                  # Clean build cache
    ]
    
    print("🚀 Bắt đầu build ứng dụng...")
    print("Tham số PyInstaller:")
    for arg in args:
        print(f"  {arg}")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build thành công!")
        print(f"📁 File exe được tạo tại: dist/TranslateNovelAI.exe")
        
        # Kiểm tra file có tồn tại không
        exe_path = "dist/TranslateNovelAI.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📊 Kích thước file: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ Lỗi build: {e}")
        return False
    
    return True

def install_dependencies():
    """Cài đặt dependencies cần thiết"""
    import subprocess
    
    dependencies = [
        "pyinstaller",
        "google-generativeai",
        "python-docx"
    ]
    
    print("📦 Cài đặt dependencies...")
    for dep in dependencies:
        try:
            print(f"Cài đặt {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Lỗi cài đặt {dep}: {e}")
            return False
    
    print("✅ Đã cài đặt tất cả dependencies!")
    return True

if __name__ == "__main__":
    print("=== TranslateNovelAI Build Tool ===\n")
    
    # Kiểm tra Python version
    if sys.version_info < (3, 8):
        print("❌ Cần Python 3.8 trở lên!")
        sys.exit(1)
    
    print(f"🐍 Python version: {sys.version}")
    
    # Hỏi user có muốn cài dependencies không
    install_deps = input("\n📦 Cài đặt dependencies? (y/n): ").lower().strip()
    if install_deps == 'y':
        if not install_dependencies():
            print("❌ Lỗi cài đặt dependencies!")
            sys.exit(1)
    
    # Build app
    build_confirm = input("\n🚀 Bắt đầu build ứng dụng? (y/n): ").lower().strip()
    if build_confirm == 'y':
        if build_app():
            print("\n🎉 Build hoàn thành!")
            print("Bạn có thể chạy file dist/TranslateNovelAI.exe")
        else:
            print("\n❌ Build thất bại!")
            sys.exit(1)
    else:
        print("Hủy build.") 