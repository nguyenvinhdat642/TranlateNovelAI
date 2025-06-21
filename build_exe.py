#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script để tạo file EXE cho TranslateNovelAI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command):
    """Chạy command và hiển thị output"""
    print(f"🔧 Chạy: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def build_exe():
    """Build ứng dụng thành file EXE"""
    print("🚀 Bắt đầu build TranslateNovelAI thành file EXE...")
    
    # Kiểm tra Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Kiểm tra requirements
    print("📦 Kiểm tra dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("❌ Không thể cài đặt dependencies!")
        return False
    
    print("✅ Dependencies đã sẵn sàng!")
    
    # Xóa thư mục build và dist cũ nếu có
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        print("🗑️ Xóa thư mục build cũ...")
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print("🗑️ Xóa thư mục dist cũ...")
        shutil.rmtree(dist_dir)
    
    # Tạo spec file cho PyInstaller
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/assets/*.ico', 'src/assets'),
        ('src/assets/*.png', 'src/assets'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'google.generativeai',
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.oxml.parser',
        'docx.oxml.shared',
        'src.core.translate',
        'src.core.reformat', 
        'src.core.ConvertEpub',
        'src.gui.gui_modern',
        'src.gui.custom_dialogs',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TranslateNovelAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/app_icon.ico',
    version_file=None,
)
'''
    
    # Ghi spec file
    with open("TranslateNovelAI.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("📝 Đã tạo file spec")
    
    # Build với PyInstaller
    print("🔨 Bắt đầu build với PyInstaller...")
    build_command = "python -m PyInstaller --clean --noconfirm TranslateNovelAI.spec"
    
    if not run_command(build_command):
        print("❌ Build thất bại!")
        return False
    
    # Kiểm tra file exe đã được tạo
    exe_file = Path("dist/TranslateNovelAI.exe")
    if exe_file.exists():
        file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Build thành công!")
        print(f"📁 File EXE: {exe_file.absolute()}")
        print(f"📏 Kích thước: {file_size:.1f} MB")
        
        # Copy icon và các file cần thiết
        dist_assets = Path("dist/src/assets")
        if not dist_assets.exists():
            dist_assets.mkdir(parents=True, exist_ok=True)
        
        # Copy assets nếu có
        src_assets = Path("src/assets")
        if src_assets.exists():
            for file in src_assets.glob("*"):
                if file.is_file():
                    shutil.copy2(file, dist_assets)
        
        print("\n🎉 Build hoàn thành!")
        print(f"   Bạn có thể chạy file: {exe_file.absolute()}")
        return True
    else:
        print("❌ Không tìm thấy file EXE sau khi build!")
        return False

def main():
    """Hàm main"""
    print("=" * 60)
    print("🤖 TranslateNovelAI - Build Script")
    print("=" * 60)
    
    # Kiểm tra các file cần thiết
    required_files = [
        "run_gui.py",
        "src/gui/gui_modern.py",
        "src/core/translate.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Thiếu các file cần thiết:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    print("✅ Tất cả file cần thiết đều có sẵn")
    
    # Xác nhận build
    print("\n📋 Thông tin build:")
    print(f"   - Entry point: run_gui.py")
    print(f"   - Output: TranslateNovelAI.exe")
    print(f"   - Icon: src/assets/app_icon.ico")
    
    confirm = input("\n🚀 Bắt đầu build? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Hủy build.")
        return
    
    # Build
    success = build_exe()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 BUILD HOÀN THÀNH!")
        print("=" * 60)
        input("Nhấn Enter để thoát...")
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD THẤT BẠI!")
        print("=" * 60)
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main() 