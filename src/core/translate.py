import os
import google.generativeai as genai
import time
import json
import re
import concurrent.futures
import threading
from multiprocessing import cpu_count

# Import reformat function
try:
    from .reformat import fix_text_format
    CAN_REFORMAT = True
    print("✅ Đã import thành công chức năng reformat")
except ImportError:
    CAN_REFORMAT = False
    print("⚠️ Không thể import reformat.py - chức năng reformat sẽ bị tắt")

# --- CẤU HÌNH CÁC HẰNG SỐ ---
MAX_RETRIES_ON_SAFETY_BLOCK = 5
MAX_RETRIES_ON_BAD_TRANSLATION = 5
RETRY_DELAY_SECONDS = 2
PROGRESS_FILE_SUFFIX = ".progress.json"
CHUNK_SIZE = 1024 * 1024  # 1MB (Không còn dùng trực tiếp CHUNK_SIZE cho việc đọc file nữa)

# Kích thước cửa sổ ngữ cảnh (số đoạn văn bản trước đó dùng làm ngữ cảnh)
CONTEXT_WINDOW_SIZE = 5
# Ký tự đặc biệt để đánh dấu phần cần dịch trong prompt gửi đến AI
TRANSLATE_TAG_START = "<translate_this>"
TRANSLATE_TAG_END = "</translate_this>"

# Số dòng gom lại thành một chunk để dịch
CHUNK_SIZE_LINES = 100

# Global stop event để dừng tiến trình dịch
_stop_event = threading.Event()

def set_stop_translation():
    """Dừng tiến trình dịch"""
    global _stop_event
    _stop_event.set()
    print("🛑 Đã yêu cầu dừng tiến trình dịch...")

def clear_stop_translation():
    """Xóa flag dừng để có thể tiếp tục dịch"""
    global _stop_event
    _stop_event.clear()
    print("▶️ Đã xóa flag dừng, sẵn sàng tiếp tục...")

def is_translation_stopped():
    """Kiểm tra xem có yêu cầu dừng không"""
    global _stop_event
    return _stop_event.is_set()

def get_optimal_threads():
    """
    Tự động tính toán số threads tối ưu dựa trên cấu hình máy.
    """
    try:
        # Lấy số CPU cores
        cpu_cores = cpu_count()
        
        # Tính toán threads tối ưu:
        # - Với API calls, I/O bound nên có thể dùng nhiều threads hơn số cores
        # - Nhưng không nên quá nhiều để tránh rate limiting
        # - Formula: min(max(cpu_cores * 2, 4), 20)
        optimal_threads = min(max(cpu_cores * 2, 4), 20)
        
        print(f"🖥️ Phát hiện {cpu_cores} CPU cores")
        print(f"🔧 Threads tối ưu được đề xuất: {optimal_threads}")
        
        return optimal_threads
        
    except Exception as e:
        print(f"⚠️ Lỗi khi phát hiện CPU cores: {e}")
        return 10  # Default fallback

def validate_threads(num_threads):
    """
    Validate số threads để đảm bảo trong khoảng hợp lý.
    """
    try:
        num_threads = int(num_threads)
        if num_threads < 1:
            return 1
        elif num_threads > 50:  # Giới hạn tối đa để tránh rate limiting
            return 50
        return num_threads
    except (ValueError, TypeError):
        return get_optimal_threads()

def validate_chunk_size(chunk_size):
    """
    Validate chunk size để đảm bảo trong khoảng hợp lý.
    """
    try:
        chunk_size = int(chunk_size)
        if chunk_size < 10:
            return 10
        elif chunk_size > 500:  # Tránh chunks quá lớn
            return 500
        return chunk_size
    except (ValueError, TypeError):
        return 100  # Default

# Default values
NUM_WORKERS = get_optimal_threads()  # Tự động tính theo máy

def is_bad_translation(text):
    """
    Kiểm tra xem bản dịch của chunk có đạt yêu cầu không (kiểm tra đơn giản dựa vào độ rỗng và từ chối).
    Trả về True nếu bản dịch không đạt yêu cầu (ví dụ: rỗng hoặc chứa từ từ chối), False nếu đạt yêu cầu.
    """
    if text is None or text.strip() == "":
        # Chunk dịch ra rỗng hoặc chỉ trắng => coi là bad translation
        return True

    # Các từ khóa chỉ báo bản dịch không đạt yêu cầu
    # Các từ khóa này thường xuất hiện khi AI từ chối dịch
    bad_keywords = [
        "tôi không thể dịch",
        "không thể dịch",
        "xin lỗi, tôi không",
        "tôi xin lỗi",
        "nội dung bị chặn", # Thêm kiểm tra thông báo chặn cũng là bản dịch xấu cần retry
        "as an ai", # Từ chối bằng tiếng Anh
        "as a language model",
        "i am unable",
        "i cannot",
        "i'm sorry"
    ]

    text_lower = text.lower()
    for keyword in bad_keywords:
        if keyword in text_lower:
            return True

    return False

def translate_chunk(model, chunk_lines):
    """
    Dịch một chunk gồm nhiều dòng văn bản.
    chunk_lines: danh sách các dòng văn bản
    Trả về (translated_text, is_safety_blocked_flag, is_bad_translation_flag).
    """
    # Gom các dòng thành một chuỗi lớn để gửi đi
    full_text_to_translate = "\n".join(chunk_lines)
    
    # Bỏ qua các chunk chỉ chứa các dòng trống hoặc chỉ trắng
    if not full_text_to_translate.strip():
        return ("", False, False) # Trả về chuỗi rỗng, không bị chặn, không bad translation

    try:
        # Prompt cho dịch chunk
        prompt = f"Dịch đoạn văn bản sau sang tiếng Việt một cách trực tiếp, xác định mối quan hệ và danh xưng phù hợp trước tiên, không từ chối hoặc bình luận, giữ nguyên văn phong gốc và chi tiết nội dung:\n\n{full_text_to_translate}"

        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [prompt],
            }],
            generation_config={
                "response_mime_type": "text/plain",
                # Có thể thêm các tham số khác nếu cần
                # "temperature": 0.5,
                # "top_p": 0.95,
                # "top_k": 64,
                # "max_output_tokens": 8192,
            },
        )

        # 1. Kiểm tra xem prompt (đầu vào) có bị chặn không
        if response.prompt_feedback and response.prompt_feedback.safety_ratings:
            blocked_categories = [
                rating.category.name for rating in response.prompt_feedback.safety_ratings
                if rating.blocked
            ]
            if blocked_categories:
                return (f"[NỘI DUNG GỐC BỊ CHẶN BỞI BỘ LỌC AN TOÀN - PROMPT: {', '.join(blocked_categories)}]", True, False)

        # 2. Kiểm tra xem có bất kỳ ứng cử viên nào được tạo ra không
        if not response.candidates:
            return ("[NỘI DỊCH BỊ CHẶN HOÀN TOÀN BỞI BỘ LỌC AN TOÀN - KHÔNG CÓ ỨNG CỬ VIÊN]", True, False)

        # 3. Kiểm tra lý do kết thúc của ứng cử viên đầu tiên (nếu có)
        first_candidate = response.candidates[0]
        if first_candidate.finish_reason == 'SAFETY':
            blocked_categories = [
                rating.category.name for rating in first_candidate.safety_ratings
                if rating.blocked
            ]
            return (f"[NỘI DỊCH BỊ CHẶN BỞI BỘ LỌC AN TOÀN - OUTPUT: {', '.join(blocked_categories)}]", True, False)

        # Nếu không bị chặn, trả về văn bản dịch
        translated_text = response.text
        is_bad = is_bad_translation(translated_text)
        return (translated_text, False, is_bad)

    except Exception as e:
        # Bắt các lỗi khác (ví dụ: lỗi mạng, lỗi API)
        return (f"[LỖI API KHI DỊCH CHUNK: {e}]", False, True)

def get_progress(progress_file_path):
    """Đọc tiến độ dịch từ file (số chunk đã hoàn thành)."""
    if os.path.exists(progress_file_path):
        try:
            with open(progress_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Lưu số chunk đã hoàn thành
                return data.get('completed_chunks', 0)
        except json.JSONDecodeError:
            print(f"Cảnh báo: File tiến độ '{progress_file_path}' bị hỏng hoặc không đúng định dạng JSON. Bắt đầu từ đầu.")
            return 0
    return 0

def save_progress(progress_file_path, completed_chunks):
    """Lưu tiến độ dịch (số chunk đã hoàn thành) vào file."""
    try:
        with open(progress_file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'completed_chunks': completed_chunks
            }, f)
    except Exception as e:
        print(f"⚠️ Lỗi khi lưu file tiến độ: {e}")

def process_chunk(api_key, model_name, system_instruction, chunk_data, log_callback=None):
    """
    Xử lý dịch một chunk với retry logic.
    chunk_data: tuple (chunk_index, chunk_lines, chunk_start_line_index)
    Trả về: (chunk_index, translated_text, lines_count)
    """
    chunk_index, chunk_lines, chunk_start_line_index = chunk_data
    
    # Kiểm tra flag dừng trước khi bắt đầu
    if is_translation_stopped():
        return (chunk_index, f"[CHUNK {chunk_index} BỊ DỪNG BỞI NGƯỜI DÙNG]", len(chunk_lines))
    
    # Cấu hình API cho thread hiện tại
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
    )
    
    # Thử lại với lỗi bảo mật
    safety_retries = 0
    is_safety_blocked = False  # Khởi tạo biến
    while safety_retries < MAX_RETRIES_ON_SAFETY_BLOCK:
        # Kiểm tra flag dừng trong quá trình retry
        if is_translation_stopped():
            return (chunk_index, f"[CHUNK {chunk_index} BỊ DỪNG BỞI NGƯỜI DÙNG]", len(chunk_lines))
            
        # Thử lại với bản dịch xấu  
        bad_translation_retries = 0
        while bad_translation_retries < MAX_RETRIES_ON_BAD_TRANSLATION:
            # Kiểm tra flag dừng trong quá trình retry
            if is_translation_stopped():
                return (chunk_index, f"[CHUNK {chunk_index} BỊ DỪNG BỞI NGƯỜI DÙNG]", len(chunk_lines))
                
            try:
                translated_text, is_safety_blocked, is_bad = translate_chunk(model, chunk_lines)
                
                if is_safety_blocked:
                    break # Thoát khỏi vòng lặp bad translation, sẽ retry safety
                    
                if not is_bad:
                    return (chunk_index, translated_text, len(chunk_lines)) # Thành công
                    
                # Bản dịch xấu, thử lại
                bad_translation_retries += 1
                if bad_translation_retries < MAX_RETRIES_ON_BAD_TRANSLATION:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    # Hết lần thử bad translation, dùng bản dịch cuối
                    return (chunk_index, translated_text + " [KHÔNG CẢI THIỆN ĐƯỢC]", len(chunk_lines))
                    
            except Exception as e:
                return (chunk_index, f"[LỖI XỬ LÝ CHUNK {chunk_index}: {e}]", len(chunk_lines))
        
        # Nếu bị chặn safety, thử lại
        if is_safety_blocked:
            safety_retries += 1
            if safety_retries < MAX_RETRIES_ON_SAFETY_BLOCK:
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                # Hết lần thử safety, trả về thông báo lỗi
                return (chunk_index, translated_text, len(chunk_lines))
    
    # Fallback (không nên đến đây)
    return (chunk_index, f"[KHÔNG THỂ DỊCH CHUNK {chunk_index}]", len(chunk_lines))

def generate_output_filename(input_filepath):
    """
    Tự động tạo tên file output từ input file.
    Ví dụ: "test.txt" -> "test_TranslateAI.txt"
    """
    # Tách tên file và phần mở rộng
    file_dir = os.path.dirname(input_filepath)
    file_name = os.path.basename(input_filepath)
    name_without_ext, ext = os.path.splitext(file_name)
    
    # Tạo tên file mới
    new_name = f"{name_without_ext}_TranslateAI{ext}"
    
    # Kết hợp với thư mục (nếu có)
    if file_dir:
        return os.path.join(file_dir, new_name)
    else:
        return new_name

def translate_file_optimized(input_file, output_file=None, api_key=None, model_name="gemini-2.0-flash", system_instruction=None, num_workers=None, chunk_size_lines=None):
    """
    Phiên bản dịch file với multi-threading chunks.
    """
    # Clear stop flag khi bắt đầu dịch mới
    clear_stop_translation()
    
    # Validate và thiết lập parameters
    if num_workers is None:
        num_workers = NUM_WORKERS
    else:
        num_workers = validate_threads(num_workers)
        
    if chunk_size_lines is None:
        chunk_size_lines = CHUNK_SIZE_LINES
    else:
        chunk_size_lines = validate_chunk_size(chunk_size_lines)
    
    # Tự động tạo tên file output nếu không được cung cấp
    if output_file is None:
        output_file = generate_output_filename(input_file)
        print(f"📝 Tự động tạo tên file output: {output_file}")
    
    print(f"Bắt đầu dịch file: {input_file}")
    print(f"File output: {output_file}")
    print(f"Số worker threads: {num_workers}")
    print(f"Kích thước chunk: {chunk_size_lines} dòng")

    progress_file_path = f"{input_file}{PROGRESS_FILE_SUFFIX}"

    # Lấy tiến độ từ file - số chunk đã hoàn thành
    completed_chunks = get_progress(progress_file_path)
    print(f"Đã hoàn thành {completed_chunks} chunk trước đó.")

    # Thời gian bắt đầu để tính hiệu suất
    start_time = time.time()
    
    # System instruction cho AI - sử dụng custom hoặc default
    if system_instruction is None:
        system_instruction = "Dịch văn bản sau sang tiếng Việt. Bối cảnh hiện đại. Đảm bảo các câu thoại nhân vật được dịch chính xác và đặc trong dấu "". Đảm bảo giữ nguyên chi tiết nội dung. Giữ nguyên các từ ngữ thô tục, tình dục."
    
    print(f"🎯 System instruction: {system_instruction[:100]}...")  # Log first 100 chars

    try:
        # Đọc toàn bộ file và chia thành chunks
        with open(input_file, 'r', encoding='utf-8', errors='replace') as infile:
            all_lines = infile.readlines()
        
        total_lines = len(all_lines)
        print(f"Tổng số dòng trong file: {total_lines}")
        
        # Chia thành chunks
        chunks = []
        for i in range(0, total_lines, chunk_size_lines):
            chunk_lines = all_lines[i:i + chunk_size_lines]
            chunks.append((len(chunks), chunk_lines, i))  # (chunk_index, chunk_lines, start_line_index)
        
        total_chunks = len(chunks)
        print(f"Tổng số chunks: {total_chunks}")
        
        # Kiểm tra nếu đã dịch hết file rồi
        if completed_chunks >= total_chunks:
            print(f"✅ File đã được dịch hoàn toàn ({completed_chunks}/{total_chunks} chunks).")
            if os.path.exists(progress_file_path):
                os.remove(progress_file_path)
                print(f"Đã xóa file tiến độ: {os.path.basename(progress_file_path)}")
            return True

        # Mở file output để ghi kết quả
        mode = 'a' if completed_chunks > 0 else 'w'  # Append nếu có tiến độ cũ, write nếu bắt đầu mới
        with open(output_file, mode, encoding='utf-8') as outfile:
            
            # Dictionary để lưu trữ kết quả dịch theo thứ tự chunk index
            translated_chunks_results = {}
            next_expected_chunk_to_write = completed_chunks
            total_lines_processed = completed_chunks * chunk_size_lines

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                
                futures = {} # Lưu trữ các future: {future_object: chunk_index}
                
                # Gửi các chunks cần dịch đến thread pool
                chunks_to_process = chunks[completed_chunks:]  # Chỉ xử lý chunks chưa hoàn thành
                
                print(f"Gửi {len(chunks_to_process)} chunks đến thread pool...")
                
                for chunk_data in chunks_to_process:
                    # Kiểm tra flag dừng trước khi submit
                    if is_translation_stopped():
                        print("🛑 Dừng gửi chunks mới do người dùng yêu cầu")
                        break
                        
                    future = executor.submit(process_chunk, api_key, model_name, system_instruction, chunk_data)
                    futures[future] = chunk_data[0]  # chunk_index
                
                # Thu thập kết quả khi các threads hoàn thành
                for future in concurrent.futures.as_completed(futures):
                    # Kiểm tra flag dừng
                    if is_translation_stopped():
                        print("🛑 Dừng xử lý kết quả do người dùng yêu cầu")
                        # Hủy các future chưa hoàn thành
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        break
                        
                    chunk_index = futures[future]
                    try:
                        result = future.result()  # (chunk_index, translated_text, lines_count)
                        processed_chunk_index, translated_text, lines_count = result
                        
                        # Lưu kết quả vào buffer tạm chờ ghi theo thứ tự
                        translated_chunks_results[processed_chunk_index] = (translated_text, lines_count)
                        
                        print(f"✅ Hoàn thành chunk {processed_chunk_index + 1}/{total_chunks}")
                        
                        # Ghi các chunks đã hoàn thành vào file output theo đúng thứ tự
                        while next_expected_chunk_to_write in translated_chunks_results:
                            chunk_text, chunk_lines_count = translated_chunks_results.pop(next_expected_chunk_to_write)
                            outfile.write(chunk_text)
                            if not chunk_text.endswith('\n'):
                                outfile.write('\n')
                            outfile.flush()
                            
                            # Cập nhật tiến độ
                            next_expected_chunk_to_write += 1
                            total_lines_processed += chunk_lines_count
                            
                            # Lưu tiến độ sau mỗi chunk hoàn thành
                            save_progress(progress_file_path, next_expected_chunk_to_write)
                            
                            # Hiển thị thông tin tiến độ
                            current_time = time.time()
                            elapsed_time = current_time - start_time
                            progress_percent = (next_expected_chunk_to_write / total_chunks) * 100
                            avg_speed = total_lines_processed / elapsed_time if elapsed_time > 0 else 0
                            
                            print(f"Tiến độ: {next_expected_chunk_to_write}/{total_chunks} chunks ({progress_percent:.1f}%) - {avg_speed:.1f} dòng/giây")
                            
                    except Exception as e:
                        print(f"❌ Lỗi khi xử lý chunk {chunk_index}: {e}")
                
                # Ghi nốt các chunks còn sót lại trong buffer (nếu có)
                if translated_chunks_results:
                    print("⚠️ Ghi các chunks còn sót lại...")
                    sorted_remaining_chunks = sorted(translated_chunks_results.items())
                    for chunk_idx, (chunk_text, chunk_lines_count) in sorted_remaining_chunks:
                        try:
                            outfile.write(chunk_text)
                            if not chunk_text.endswith('\n'):
                                outfile.write('\n')
                            outfile.flush()
                            next_expected_chunk_to_write += 1
                            save_progress(progress_file_path, next_expected_chunk_to_write)
                            print(f"✅ Ghi chunk bị sót: {chunk_idx + 1}")
                        except Exception as e:
                            print(f"❌ Lỗi khi ghi chunk {chunk_idx}: {e}")

        # Kiểm tra xem có bị dừng giữa chừng không
        if is_translation_stopped():
            print(f"🛑 Tiến trình dịch đã bị dừng bởi người dùng.")
            print(f"Đã xử lý {next_expected_chunk_to_write}/{total_chunks} chunks.")
            print(f"💾 Tiến độ đã được lưu. Bạn có thể tiếp tục dịch sau.")
            return False

        # Hoàn thành
        total_time = time.time() - start_time
        if next_expected_chunk_to_write >= total_chunks:
            print(f"✅ Dịch hoàn thành file: {os.path.basename(input_file)}")
            print(f"Đã dịch {total_chunks} chunks ({total_lines} dòng) trong {total_time:.2f}s")
            print(f"Tốc độ trung bình: {total_lines / total_time:.2f} dòng/giây")
            print(f"File dịch đã được lưu tại: {output_file}")

            # Xóa file tiến độ khi hoàn thành
            if os.path.exists(progress_file_path):
                os.remove(progress_file_path)
                print(f"Đã xóa file tiến độ: {os.path.basename(progress_file_path)}")
            
            # Tự động reformat file sau khi dịch xong
            if CAN_REFORMAT:
                print("\n🔧 Bắt đầu reformat file đã dịch...")
                try:
                    fix_text_format(output_file)
                    print("✅ Reformat hoàn thành!")
                except Exception as e:
                    print(f"⚠️ Lỗi khi reformat: {e}")
            else:
                print("⚠️ Chức năng reformat không khả dụng")
            
            return True
        else:
            print(f"⚠️ Quá trình dịch bị gián đoạn.")
            print(f"Đã xử lý {next_expected_chunk_to_write}/{total_chunks} chunks.")
            print(f"Tiến độ đã được lưu. Bạn có thể chạy lại chương trình để tiếp tục.")
            return False

    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file đầu vào '{input_file}'.")
        return False
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi không mong muốn: {e}")
        print("Tiến độ đã được lưu. Bạn có thể chạy lại chương trình để tiếp tục.")
        return False


def load_api_key():
    """Tự động load API key từ environment variable hoặc file config"""
    # Thử load từ environment variable
    import os
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print(f"✅ Đã load API key từ environment variable")
        return api_key
    
    # Thử load từ file config.json
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('api_key')
                if api_key:
                    print(f"✅ Đã load API key từ config.json")
                    return api_key
    except:
        pass
    
    return None

def main():
    """Interactive main function for command line usage"""
    print("=== TranslateNovelAI - Command Line Version ===\n")
    
    # Thử tự động load API Key
    api_key = load_api_key()
    
    if not api_key:
        # Nhập API Key manually
        api_key = input("Nhập Google AI API Key: ").strip()
        if not api_key:
            print("❌ API Key không được để trống!")
            return
        
        # Hỏi có muốn lưu vào config.json không
        save_key = input("💾 Lưu API key vào config.json? (y/N): ").lower().strip()
        if save_key == 'y':
            try:
                config = {'api_key': api_key}
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                print("✅ Đã lưu API key vào config.json")
            except Exception as e:
                print(f"⚠️ Lỗi lưu config: {e}")
    else:
        print(f"🔑 API Key: {api_key[:10]}***{api_key[-10:]}")
    
    # Nhập đường dẫn file input
    input_file = input("Nhập đường dẫn file truyện cần dịch: ").strip()
    if not input_file:
        print("❌ Đường dẫn file không được để trống!")
        return
    
    # Kiểm tra file tồn tại
    if not os.path.exists(input_file):
        print(f"❌ File không tồn tại: {input_file}")
        return
    
    # Tùy chọn file output (có thể để trống)
    output_file = input("Nhập đường dẫn file output (để trống để tự động tạo): ").strip()
    if not output_file:
        output_file = None
        print("📝 Sẽ tự động tạo tên file output")
    
    # Tùy chọn model
    print("\nChọn model:")
    print("1. gemini-2.0-flash (khuyến nghị)")
    print("2. gemini-1.5-flash")
    print("3. gemini-1.5-pro")
    
    model_choice = input("Nhập lựa chọn (1-3, mặc định 1): ").strip()
    model_map = {
        "1": "gemini-2.0-flash",
        "2": "gemini-1.5-flash", 
        "3": "gemini-1.5-pro",
        "": "gemini-2.0-flash"  # Default
    }
    
    model_name = model_map.get(model_choice, "gemini-2.0-flash")
    print(f"📱 Sử dụng model: {model_name}")
    
    # Xác nhận trước khi bắt đầu
    print(f"\n📋 Thông tin dịch:")
    print(f"  Input: {input_file}")
    print(f"  Output: {output_file or 'Tự động tạo'}")
    print(f"  Model: {model_name}")
    print(f"  Threads: {get_optimal_threads()}")
    print(f"  Chunk size: {CHUNK_SIZE_LINES} dòng")
    
    confirm = input("\n🚀 Bắt đầu dịch? (y/N): ").lower().strip()
    if confirm != 'y':
        print("❌ Hủy bỏ.")
        return
    
    # Bắt đầu dịch
    print("\n" + "="*50)
    try:
        success = translate_file_optimized(
            input_file=input_file,
            output_file=output_file,
            api_key=api_key,
            model_name=model_name
        )
        
        if success:
            print("\n🎉 Dịch hoàn thành thành công!")
        else:
            print("\n⚠️ Dịch chưa hoàn thành.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Người dùng dừng chương trình.")
        print("💾 Tiến độ đã được lưu, có thể tiếp tục sau.")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")


if __name__ == "__main__":
    main()