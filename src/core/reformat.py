import re
import os

def fix_text_format(filepath):
    """
    Sửa lỗi định dạng file text:
    Thay thế 3 hoặc nhiều hơn ký tự xuống dòng liên tiếp (ví dụ: \n\n\n)
    bằng 2 ký tự xuống dòng liên tiếp (\n\n) để phân cách đoạn đúng chuẩn.
    """
    if not os.path.exists(filepath):
        print(f"Lỗi: Không tìm thấy file tại đường dẫn '{filepath}'")
        return

    print(f"Đang xử lý file: '{filepath}'...")

    try:
        # Bước 1: Đọc toàn bộ nội dung file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Bước 2: Chuẩn hóa nội dung
        # Sử dụng biểu thức chính quy (regex) để tìm kiếm và thay thế:
        # r'\n{3,}' tìm 3 hoặc nhiều hơn ký tự xuống dòng liên tiếp
        # '\n\n' sẽ thay thế chúng bằng 2 ký tự xuống dòng liên tiếp
        fixed_content = re.sub(r'\n{3,}', '\n\n', content)

        # Bước 3: Loại bỏ các dòng trống thừa ở đầu và cuối file (nếu có)
        # và đảm bảo kết thúc bằng một dòng trống đúng chuẩn (nếu cần)
        fixed_content = fixed_content.strip() # Xóa dòng trống đầu/cuối
        if fixed_content: # Nếu nội dung không rỗng, đảm bảo có một dòng trống cuối cùng (để phân cách đoạn cuối)
            fixed_content += '\n' # re.sub có thể đã để lại một \n hoặc không, strip() sẽ xóa tất cả.
                                  # Thêm lại một \n để đảm bảo định dạng file text đúng chuẩn
                                  # (thường các file text kết thúc bằng một ký tự xuống dòng).

        # Bước 4: Ghi nội dung đã sửa vào file gốc
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"Hoàn tất sửa lỗi định dạng cho file '{filepath}'.")
        print("Vui lòng kiểm tra lại file đã được sửa.")

    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình xử lý: {e}")

# --- Cách sử dụng script ---
if __name__ == "__main__":
    # Yêu cầu người dùng nhập đường dẫn file
    file_path = input("Vui lòng nhập đường dẫn đến file .txt cần chỉnh sửa: ")

    # Xác nhận trước khi thực hiện để tránh mất dữ liệu
    confirm = input(f"Bạn có chắc chắn muốn sửa file '{file_path}'? "
                    "Hành động này sẽ ghi đè lên file gốc. (y/n): ").lower()

    if confirm == 'y':
        fix_text_format(file_path)
    else:
        print("Hủy bỏ thao tác. File không bị thay đổi.")