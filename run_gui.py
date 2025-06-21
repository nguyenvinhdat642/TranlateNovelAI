#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TranslateNovelAI - GUI Runner
Chạy ứng dụng GUI từ thư mục gốc
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    try:
        from src.gui.gui_modern import main
        main()
    except ImportError as e:
        print(f"❌ Lỗi import GUI: {e}")
        print("Đảm bảo bạn đã cài đặt các dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi khởi chạy: {e}")
        sys.exit(1) 