#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script đơn giản để kiểm tra translate function
"""

import sys
import os
sys.path.append('src')

from translate import translate_file_optimized
import json

def test_translate():
    print("🧪 Test translate function...")
    
    # Load API key
    try:
        with open('src/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            api_key = settings.get('api_key', '')
    except:
        api_key = input("Nhập API key: ")
    
    if not api_key:
        print("❌ Không có API key")
        return
    
    # Test với file nhỏ
    input_file = "test_input.txt"
    output_file = "test_output.txt"
    
    print(f"📁 Input: {input_file}")
    print(f"📁 Output: {output_file}")
    
    try:
        success = translate_file_optimized(
            input_file=input_file,
            output_file=output_file,
            api_key=api_key,
            model_name="gemini-2.0-flash"
        )
        
        if success:
            print("✅ Test thành công!")
            if os.path.exists(output_file):
                print("📄 Nội dung file output:")
                with open(output_file, 'r', encoding='utf-8') as f:
                    print(f.read())
        else:
            print("❌ Test thất bại!")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_translate() 