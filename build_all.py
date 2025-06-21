#!/usr/bin/env python3
"""
Script build exe cho tất cả phiên bản GUI của TranslateNovelAI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """In header cho từng phần"""
    print("\n" + "="*60)
    print(f"🔨 {title}")
    print("="*60)

def check_pyinstaller():
    """Kiểm tra PyInstaller có được cài đặt không"""
    try:
        import PyInstaller
        print("✅ PyInstaller đã được cài đặt")
        return True
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt")
        print("💡 Cài đặt: pip install pyinstaller")
        return False

def create_spec_file(gui_type, entry_script, icon_path="app_icon.ico"):
    """Tạo file .spec cho PyInstaller"""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{entry_script}'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/*.py', 'src'),
        ('assets/*.ico', 'assets'),
        ('assets/*.png', 'assets'),
        ('*.md', '.'),
        ('requirements.txt', '.'),
        ('settings.json', '.') if os.path.exists('settings.json') else None,
    ],
    hiddenimports=[
        'google.generativeai',
        'customtkinter',
        'gradio',
        'PIL',
        'docx',
        'threading',
        'queue',
        'json',
        'os',
        'sys',
        'time',
        'datetime',
        'tempfile',
        're'
    ],
    hookspath=[],
    hooksconfig={{}},
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
    name='TranslateNovelAI_{gui_type}',
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
    icon='{icon_path}' if os.path.exists('{icon_path}') else None,
)
'''

    spec_filename = f"TranslateNovelAI_{gui_type}.spec"
    
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Đã tạo file {spec_filename}")
    return spec_filename

def build_exe(gui_type, spec_file):
    """Build exe từ file .spec"""
    print(f"\n🔨 Đang build {gui_type} GUI...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        spec_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Build {gui_type} thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi build {gui_type}:")
        print(e.stderr)
        return False

def copy_assets(gui_type):
    """Copy assets cần thiết vào thư mục dist"""
    dist_dir = f"dist/TranslateNovelAI_{gui_type}"
    
    if not os.path.exists(dist_dir):
        print(f"⚠️ Thư mục {dist_dir} không tồn tại")
        return
    
    # Copy icon và assets  
    assets_to_copy = [
        ("src/assets/app_icon.ico", "app_icon.ico"),
        ("src/assets/success_icon.png", "success_icon.png"),
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt")
    ]
    
    for src, dst in assets_to_copy:
        if os.path.exists(src):
            try:
                shutil.copy2(src, os.path.join(dist_dir, dst))
                print(f"📄 Đã copy {src}")
            except Exception as e:
                print(f"⚠️ Lỗi copy {src}: {e}")

def create_installer_script():
    """Tạo script installer NSIS (tùy chọn)"""
    nsis_script = '''
; TranslateNovelAI Installer Script
!define APPNAME "TranslateNovelAI"
!define APPVERSION "2.0"

Name "${APPNAME}"
OutFile "TranslateNovelAI_Installer.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"

Page directory
Page instfiles

Section ""
    SetOutPath "$INSTDIR"
    
    ; Copy files
    File /r "dist\\TranslateNovelAI_Web\\*"
    File /r "dist\\TranslateNovelAI_Modern\\*"
    File /r "dist\\TranslateNovelAI_Classic\\*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Web GUI.lnk" "$INSTDIR\\TranslateNovelAI_Web.exe"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Modern GUI.lnk" "$INSTDIR\\TranslateNovelAI_Modern.exe"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Classic GUI.lnk" "$INSTDIR\\TranslateNovelAI_Classic.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\*.*"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\\${APPNAME}\\*.*"
    RMDir "$SMPROGRAMS\\${APPNAME}"
SectionEnd
'''
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    print("📦 Đã tạo script installer.nsi")
    print("💡 Cài đặt NSIS và chạy: makensis installer.nsi để tạo installer")

def main():
    """Main function"""
    print_header("TranslateNovelAI - Build All GUIs")
    
    # Kiểm tra requirements
    if not check_pyinstaller():
        return
    
    # Chuyển đến thư mục script
    os.chdir(Path(__file__).parent)
    
    # Tạo thư mục build và dist
    os.makedirs("build", exist_ok=True)
    os.makedirs("dist", exist_ok=True)
    
    # Định nghĩa các GUI variants
    gui_variants = [
        {
            "type": "Web",
            "script": "src/gui/gui_web.py",
            "description": "Web GUI với Gradio"
        },
        {
            "type": "Modern", 
            "script": "src/gui/gui_modern.py",
            "description": "Desktop GUI hiện đại với CustomTkinter"
        },
        {
            "type": "Classic",
            "script": "src/gui/gui_simple.py", 
            "description": "Desktop GUI truyền thống với Tkinter"
        }
    ]
    
    successful_builds = []
    failed_builds = []
    
    # Build từng variant
    for variant in gui_variants:
        print_header(f"Building {variant['description']}")
        
        # Kiểm tra file script tồn tại
        if not os.path.exists(variant['script']):
            print(f"❌ File {variant['script']} không tồn tại")
            failed_builds.append(variant['type'])
            continue
        
        try:
            # Tạo spec file
            spec_file = create_spec_file(
                variant['type'], 
                variant['script'],
                "src/assets/app_icon.ico" if os.path.exists("src/assets/app_icon.ico") else None
            )
            
            # Build exe
            if build_exe(variant['type'], spec_file):
                # Copy assets
                copy_assets(variant['type'])
                successful_builds.append(variant['type'])
                print(f"🎉 {variant['type']} GUI build hoàn thành!")
            else:
                failed_builds.append(variant['type'])
                
        except Exception as e:
            print(f"❌ Lỗi build {variant['type']}: {e}")
            failed_builds.append(variant['type'])
    
    # Tạo launcher tổng hợp
    print_header("Tạo Launcher Tổng Hợp")
    try:
        launcher_spec = create_spec_file("Launcher", "run_gui.py")
        if build_exe("Launcher", launcher_spec):
            copy_assets("Launcher")
            print("🎉 Launcher build hoàn thành!")
        else:
            print("❌ Launcher build thất bại")
    except Exception as e:
        print(f"❌ Lỗi build Launcher: {e}")
    
    # Tạo installer script
    if successful_builds:
        create_installer_script()
    
    # Summary
    print_header("Kết Quả Build")
    
    if successful_builds:
        print("✅ Build thành công:")
        for build in successful_builds:
            exe_path = f"dist/TranslateNovelAI_{build}/TranslateNovelAI_{build}.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"   📁 {build}: {exe_path} ({size_mb:.1f} MB)")
    
    if failed_builds:
        print("❌ Build thất bại:")
        for build in failed_builds:
            print(f"   ❌ {build}")
    
    # Cleanup spec files
    print("\n🧹 Dọn dẹp files tạm...")
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"   🗑️ Đã xóa {spec_file}")
        except:
            pass
    
    print(f"\n🎉 Hoàn thành! Build thành công {len(successful_builds)}/{len(gui_variants)} GUI variants")
    
    if successful_builds:
        print("\n📋 Hướng dẫn sử dụng:")
        print("   1. Các file exe nằm trong thư mục dist/")
        print("   2. Chạy TranslateNovelAI_Launcher.exe để chọn GUI")
        print("   3. Hoặc chạy trực tiếp từng GUI variant")
        print("   4. Sử dụng installer.nsi để tạo installer (cần NSIS)")

if __name__ == "__main__":
    main() 