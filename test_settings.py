"""
Script test để demo tính năng auto-save API key
"""

import json
import os

def test_settings():
    """Test tính năng settings"""
    
    print("=== Test Settings TranslateNovelAI ===\n")
    
    # Kiểm tra file settings hiện tại
    if os.path.exists("settings.json"):
        print("📁 File settings.json đã tồn tại:")
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            api_key = settings.get("api_key", "")
            if api_key:
                print(f"🔑 API Key: {api_key[:10]}***{api_key[-4:]}")
            else:
                print("⚠️ Chưa có API key trong settings")
                
            print(f"🤖 Model: {settings.get('model', 'Chưa set')}")
            print(f"🔧 Auto reformat: {settings.get('auto_reformat', 'Chưa set')}")
            print(f"📚 Auto EPUB: {settings.get('auto_convert_epub', 'Chưa set')}")
            
        except Exception as e:
            print(f"❌ Lỗi đọc settings: {e}")
    else:
        print("ℹ️ Chưa có file settings.json")
        print("💡 Khi bạn nhập API key vào GUI, file sẽ được tạo tự động")
    
    print("\n" + "="*50)
    print("🎯 Cách sử dụng:")
    print("1. Mở GUI: python src/gui_simple.py")
    print("2. Nhập API key vào field 'Google AI API Key'")
    print("3. API key sẽ được lưu tự động")
    print("4. Lần sau mở app, API key sẽ tự động load")
    print("="*50)

if __name__ == "__main__":
    test_settings() 