#!/usr/bin/env python3
"""
GUI Launcher cho TranslateNovelAI v2.0
Launcher tổng hợp để chọn giữa các phiên bản giao diện khác nhau
"""

import sys
import os
import subprocess
import importlib.util

def print_banner():
    """In banner chào mừng"""
    print("=" * 60)
    print("🤖 TranslateNovelAI v2.0 - GUI Launcher")
    print("=" * 60)

def check_dependencies():
    """Kiểm tra dependencies có sẵn"""
    dependencies = {
        'google-generativeai': 'google.generativeai',
        'customtkinter': 'customtkinter', 
        'gradio': 'gradio',
        'pillow': 'PIL',
        'python-docx': 'docx'
    }
    
    missing = []
    available = []
    
    print("🔍 Kiểm tra dependencies...")
    
    for package_name, module_name in dependencies.items():
        try:
            importlib.import_module(module_name)
            print(f"✅ {package_name}")
            available.append(package_name)
        except ImportError:
            print(f"❌ {package_name} - chưa cài đặt")
            missing.append(package_name)
    
    if missing:
        print(f"💡 Cài đặt packages thiếu: pip install {' '.join(missing)}")
    
    return available, missing

def launch_web_gui():
    """Khởi động Web GUI"""
    print("🌐 Khởi động Web GUI...")
    print("📱 Giao diện sẽ mở tại: http://localhost:7860")
    print("⚠️  Nhấn Ctrl+C để dừng server")
    print("-" * 40)
    
    try:
        # Import và chạy web GUI
        sys.path.insert(0, 'src')
        from src.gui.gui_web import main
        main()
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        if "gradio" in str(e):
            print("💡 Cài đặt dependencies: pip install gradio")
        else:
            print("💡 Kiểm tra cấu trúc thư mục và files")
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng Web GUI")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def launch_modern_gui():
    """Khởi động Modern Desktop GUI"""
    print("🖥️  Khởi động Modern Desktop GUI...")
    print("-" * 40)
    
    try:
        # Test import modules
        sys.path.insert(0, 'src')
        from src.core.reformat import fix_text_format
        print("✅ Đã import thành công chức năng reformat")
        
        from src.gui.gui_modern import main
        main()
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        if "customtkinter" in str(e):
            print("💡 Cài đặt dependencies: pip install customtkinter")
        else:
            print("💡 Kiểm tra cấu trúc thư mục và files")
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")

def launch_classic_gui():
    """Khởi động Classic Desktop GUI"""
    print("📱 Khởi động Classic Desktop GUI...")
    print("-" * 40)
    
    try:
        sys.path.insert(0, 'src')
        from src.gui.gui_simple import main
        main()
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("💡 Kiểm tra file src/gui/gui_simple.py")
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")

def show_menu(available_deps):
    """Hiển thị menu chọn GUI"""
    
    # Kiểm tra khả năng của từng GUI
    web_available = 'gradio' in available_deps
    modern_available = 'customtkinter' in available_deps and 'pillow' in available_deps
    classic_available = True  # Always available with standard tkinter
    
    while True:
        print("Chọn phiên bản GUI:")
        
        # Web GUI option
        if web_available:
            print("1. 🌐 Web GUI (Gradio) - Hiện đại, chạy trên trình duyệt")
        else:
            print("1. 🌐 Web GUI (Gradio) - ❌ Thiếu dependencies")
        
        # Modern GUI option  
        if modern_available:
            print("2. 🖥️  Desktop GUI (CustomTkinter) - Giao diện desktop hiện đại")
        else:
            print("2. 🖥️  Desktop GUI (CustomTkinter) - ❌ Thiếu dependencies")
        
        # Classic GUI option
        print("3. 📱 Classic GUI (Tkinter) - Giao diện desktop truyền thống")
        print("4. ❌ Thoát")
        
        try:
            choice = input("Nhập lựa chọn (1-4): ").strip()
            
            if choice == "1":
                if web_available:
                    launch_web_gui()
                else:
                    print("❌ Không thể khởi động Web GUI - thiếu dependencies")
                    print("💡 Cài đặt: pip install gradio")
                    
            elif choice == "2":
                if modern_available:
                    launch_modern_gui()
                else:
                    print("❌ Không thể khởi động Modern GUI - thiếu dependencies")
                    print("💡 Cài đặt: pip install customtkinter pillow")
                    
            elif choice == "3":
                launch_classic_gui()
                
            elif choice == "4":
                print("👋 Tạm biệt!")
                sys.exit(0)
                
            else:
                print("❌ Lựa chọn không hợp lệ. Vui lòng chọn 1-4")
                
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Lỗi: {e}")
        
        print("=" * 60)

def main():
    """Main function"""
    print_banner()
    
    # Kiểm tra dependencies
    available_deps, missing_deps = check_dependencies()
    
    # Hiển thị menu
    show_menu(available_deps)

if __name__ == "__main__":
    main() 