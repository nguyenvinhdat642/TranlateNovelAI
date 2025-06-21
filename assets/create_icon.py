#!/usr/bin/env python3
"""
Script tạo icon cho TranslateNovelAI
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """Tạo icon ứng dụng với gradient và text"""
    
    # Kích thước icon
    sizes = [16, 32, 48, 64, 128, 256]
    
    for size in sizes:
        # Tạo image với gradient background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Vẽ gradient background (blue to purple)
        for y in range(size):
            # Tính toán màu gradient
            ratio = y / size
            r = int(102 + (118 - 102) * ratio)  # 667eea to 764ba2
            g = int(126 + (75 - 126) * ratio)
            b = int(234 + (162 - 234) * ratio)
            
            draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
        # Vẽ border
        border_width = max(1, size // 32)
        draw.rectangle([0, 0, size-1, size-1], outline=(255, 255, 255, 200), width=border_width)
        
        # Vẽ icon robot/AI
        center_x, center_y = size // 2, size // 2
        
        if size >= 32:
            # Vẽ robot head
            head_size = size // 3
            head_x = center_x - head_size // 2
            head_y = center_y - head_size // 2 - size // 8
            
            # Robot head (rounded rectangle)
            draw.rounded_rectangle(
                [head_x, head_y, head_x + head_size, head_y + head_size],
                radius=head_size // 6,
                fill=(255, 255, 255, 230),
                outline=(200, 200, 200, 255),
                width=max(1, size // 64)
            )
            
            # Eyes
            eye_size = head_size // 6
            eye_y = head_y + head_size // 3
            left_eye_x = head_x + head_size // 3 - eye_size // 2
            right_eye_x = head_x + 2 * head_size // 3 - eye_size // 2
            
            draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(50, 50, 255, 255))
            draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(50, 50, 255, 255))
            
            # Mouth (smile)
            mouth_y = head_y + 2 * head_size // 3
            mouth_width = head_size // 2
            mouth_x = center_x - mouth_width // 2
            
            if size >= 48:
                draw.arc([mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_width // 2], 
                        start=0, end=180, fill=(100, 100, 100, 255), width=max(1, size // 32))
        
        # Thêm text "AI" nếu icon đủ lớn
        if size >= 64:
            try:
                # Sử dụng font mặc định
                font_size = size // 6
                font = ImageFont.load_default()
                
                # Vẽ text "AI" ở dưới
                text = "AI"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_x = center_x - text_width // 2
                text_y = center_y + size // 4
                
                # Shadow
                draw.text((text_x + 1, text_y + 1), text, fill=(0, 0, 0, 150), font=font)
                # Main text
                draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
                
            except:
                pass  # Nếu không load được font thì bỏ qua
        
        # Lưu icon
        icon_path = f"icon_{size}x{size}.png"
        img.save(icon_path, "PNG")
        print(f"✅ Đã tạo icon: {icon_path}")
    
    # Tạo file .ico từ nhiều kích thước
    try:
        # Load tất cả các kích thước
        icons = []
        for size in sizes:
            icons.append(Image.open(f"icon_{size}x{size}.png"))
        
        # Lưu thành file .ico
        icons[0].save("app_icon.ico", format="ICO", sizes=[(s, s) for s in sizes])
        print("✅ Đã tạo file app_icon.ico")
        
        # Clean up temporary files
        for size in sizes:
            try:
                os.remove(f"icon_{size}x{size}.png")
            except:
                pass
                
    except Exception as e:
        print(f"⚠️ Lỗi tạo file .ico: {e}")

def create_notification_icon():
    """Tạo icon cho notification"""
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Vẽ check mark (success icon)
    center = size // 2
    
    # Green circle background
    draw.ellipse([2, 2, size-2, size-2], fill=(40, 167, 69, 255), outline=(34, 139, 58, 255), width=1)
    
    # White check mark
    check_points = [
        (size * 0.25, size * 0.5),
        (size * 0.45, size * 0.7),
        (size * 0.75, size * 0.3)
    ]
    
    # Draw check mark with lines
    draw.line([check_points[0], check_points[1]], fill=(255, 255, 255, 255), width=3)
    draw.line([check_points[1], check_points[2]], fill=(255, 255, 255, 255), width=3)
    
    img.save("success_icon.png", "PNG")
    print("✅ Đã tạo success_icon.png")

if __name__ == "__main__":
    # Tạo thư mục assets nếu chưa có
    os.makedirs(".", exist_ok=True)
    
    print("🎨 Đang tạo icons cho TranslateNovelAI...")
    create_app_icon()
    create_notification_icon()
    print("🎉 Hoàn thành tạo icons!") 