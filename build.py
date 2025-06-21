#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for TranslateNovelAI
Đóng gói ứng dụng thành file exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Xóa các thư mục build cũ"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🗑️ Xóa thư mục: {dir_name}")
            shutil.rmtree(dir_name)
    
    # Xóa file .spec cũ
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        print(f"🗑️ Xóa file spec: {spec_file}")
        os.remove(spec_file)

def check_dependencies():
    """Kiểm tra dependencies"""
    print("📦 Kiểm tra dependencies...")
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt!")
        print("Cài đặt bằng: pip install pyinstaller")
        return False
    
    try:
        import customtkinter
        print(f"✅ CustomTkinter version: {customtkinter.__version__}")
    except ImportError:
        print("❌ CustomTkinter chưa được cài đặt!")
        return False
    
    return True

def build_exe():
    """Build file exe"""
    if not check_dependencies():
        return False
    
    print("🚀 Bắt đầu build file exe...")
    
    # Sử dụng file spec tùy chỉnh
    spec_file = 'TranslateNovelAI.spec'
    
    if os.path.exists(spec_file):
        print(f"📋 Sử dụng file spec: {spec_file}")
        args = ['pyinstaller', '--onefile', spec_file]
    else:
        print("⚠️ Không tìm thấy file spec, sử dụng arguments mặc định...")
        # Các arguments cho PyInstaller
        args = [
            'pyinstaller',
            '--onefile',                    # Đóng gói thành 1 file exe duy nhất
            '--windowed',                   # Không hiện console window
            '--name=TranslateNovelAI',      # Tên file exe
            '--icon=src/assets/app_icon.ico',  # Icon (nếu có)
            
            # Thêm data files
            '--add-data=src;src',
            '--add-data=requirements.txt;.',
            '--add-data=USAGE.md;.',
            '--add-data=README.md;.',
            
            # Hidden imports để đảm bảo các module được include
            '--hidden-import=customtkinter',
            '--hidden-import=PIL',
            '--hidden-import=PIL._tkinter_finder',
            '--hidden-import=google.generativeai',
            '--hidden-import=docx',
            '--hidden-import=tkinter',
            '--hidden-import=tkinter.filedialog',
            '--hidden-import=tkinter.messagebox',
            
            # Exclude một số modules không cần thiết để giảm kích thước
            '--exclude-module=matplotlib',
            '--exclude-module=numpy',
            '--exclude-module=pandas',
            '--exclude-module=scipy',
            '--exclude-module=pytest',
            
            # Entry point
            'run_gui.py'
        ]
        
        # Kiểm tra icon file
        icon_path = 'src/assets/app_icon.ico'
        if not os.path.exists(icon_path):
            print(f"⚠️ Không tìm thấy icon: {icon_path}")
            # Loại bỏ argument icon
            args = [arg for arg in args if not arg.startswith('--icon')]
    
    try:
        # Chạy PyInstaller
        print("⚙️ Chạy PyInstaller...")
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print("✅ Build thành công!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi build: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False

def build_directory():
    """Build thành thư mục (không onefile)"""
    if not check_dependencies():
        return False
    
    print("🚀 Build thành thư mục...")
    
    args = [
        'pyinstaller',
        '--onedir',                     # Build thành thư mục
        '--windowed',
        '--name=TranslateNovelAI',
        '--icon=src/assets/app_icon.ico',
        
        '--add-data=src;src',
        '--add-data=requirements.txt;.',
        '--add-data=USAGE.md;.',
        '--add-data=README.md;.',
        
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=google.generativeai',
        '--hidden-import=docx',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        
        'run_gui.py'
    ]
    
    icon_path = 'src/assets/app_icon.ico'
    if not os.path.exists(icon_path):
        args = [arg for arg in args if not arg.startswith('--icon')]
    
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print("✅ Build thư mục thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi build: {e}")
        return False

def post_build_cleanup():
    """Cleanup sau khi build"""
    print("🧹 Dọn dẹp sau build...")
    
    # Di chuyển file exe ra ngoài nếu cần
    exe_path = os.path.join('dist', 'TranslateNovelAI.exe')
    if os.path.exists(exe_path):
        target_path = 'TranslateNovelAI.exe'
        if os.path.exists(target_path):
            os.remove(target_path)
        shutil.move(exe_path, target_path)
        print(f"📦 File exe: {target_path}")
    
    # Tạo file thông tin
    info_content = """# TranslateNovelAI - Standalone Executable

## Cách sử dụng:
1. Chạy file TranslateNovelAI.exe
2. Nhập Google AI API Key
3. Chọn file txt cần dịch
4. Cấu hình và bắt đầu dịch

## Lưu ý:
- Cần có kết nối internet
- API Key phải có quyền sử dụng Gemini API
- File input phải là định dạng .txt

## Hỗ trợ:
- Xem file USAGE.md để biết thêm chi tiết
"""
    
    with open('README_EXE.txt', 'w', encoding='utf-8') as f:
        f.write(info_content)

def main():
    """Main function"""
    print("🏗️ TranslateNovelAI Build Script")
    print("=" * 50)
    
    # Parse arguments
    build_type = 'onefile'  # default
    if len(sys.argv) > 1:
        if sys.argv[1] == '--directory':
            build_type = 'directory'
        elif sys.argv[1] == '--help':
            print("Cách sử dụng:")
            print("  python build.py           # Build file exe đơn")
            print("  python build.py --directory # Build thành thư mục")
            print("  python build.py --help    # Hiện help")
            return
    
    print(f"📋 Build type: {build_type}")
    
    # Clean old builds
    clean_build_dirs()
    
    # Build
    success = False
    if build_type == 'onefile':
        success = build_exe()
    else:
        success = build_directory()
    
    if success:
        post_build_cleanup()
        print("\n🎉 Build hoàn thành!")
        print("📂 Kiểm tra thư mục dist/ hoặc file .exe")
    else:
        print("\n❌ Build thất bại!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 