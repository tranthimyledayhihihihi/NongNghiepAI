import os
import logging
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Tìm và đọc file .env một cách tường minh từ thư mục gốc của dự án (backend)
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(override=True)


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        # Thêm log gỡ lỗi để kiểm tra trực tiếp trên terminal
        if api_key:
            masked_key = api_key[:7] + '...' + api_key[-4:]
            logger.info(f"GEMINI_API_KEY loaded: {masked_key}")
        else:
            logger.warning("GEMINI_API_KEY not found in environment.")

        if not api_key:
            logger.warning("GEMINI_API_KEY is not set. Gemini AI will not work.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.5-flash'
            logger.info("Gemini client configured successfully.")

    async def get_farming_advice(self, question: str, context_data: str = "") -> str:
        if not self.client:
            return f"[Chế độ Test] Đây là câu trả lời giả lập từ AI cho câu hỏi: '{question}'. Để dùng AI thật, bạn cần thêm GEMINI_API_KEY vào file .env!"

        system_instruction = """Bạn là chuyên gia nông nghiệp hàng đầu Việt Nam với 20 năm kinh nghiệm thực tiễn,
am hiểu sâu về: kỹ thuật canh tác, sinh lý cây trồng, bảo vệ thực vật, thổ nhưỡng, thủy lợi,
thị trường nông sản và chính sách nông nghiệp Việt Nam.

NGUYÊN TẮC TRẢ LỜI:
1. Luôn dùng Google Search để lấy số liệu giá thị trường, thời tiết, chính sách MỚI NHẤT. Trích dẫn nguồn cụ thể.
2. Trả lời CỤ THỂ cho vùng/địa phương được hỏi (nếu có), không trả lời chung chung.
3. Cung cấp số liệu kỹ thuật chính xác: liều lượng phân bón, nồng độ thuốc, thời điểm xử lý.
4. Phân tích NGUYÊN NHÂN sâu xa của vấn đề, không chỉ mô tả triệu chứng.
5. Đưa ra GIẢI PHÁP CỤ THỂ, có thể thực hiện ngay được, theo thứ tự ưu tiên.
6. Cảnh báo RỦI RO và sai lầm phổ biến liên quan đến câu hỏi.
7. Nếu câu hỏi về chu kỳ sinh trưởng: cung cấp đầy đủ các giai đoạn, không ước lượng thiếu.
8. Kết thúc bằng 1-2 câu khuyến nghị hành động ngay cho nông dân.

ĐỊNH DẠNG: Sử dụng tiêu đề rõ ràng, bullet points khi liệt kê, in đậm các thông tin quan trọng."""

        prompt = f"""--- DỮ LIỆU HỆ THỐNG (ngữ cảnh) ---
{context_data if context_data else "Không có dữ liệu bổ sung."}

--- CÂU HỎI CỦA NÔNG DÂN ---
{question}

--- YÊU CẦU ---
Hãy phân tích kỹ và trả lời đầy đủ, chuyên sâu. Nếu câu hỏi liên quan đến:
- Giá cả/thị trường: Tìm giá hiện tại, so sánh xu hướng, dự báo ngắn hạn.
- Kỹ thuật trồng trọt: Đưa quy trình đầy đủ, thông số kỹ thuật cụ thể.
- Bệnh/sâu hại: Mô tả triệu chứng, nguyên nhân, biện pháp phòng trừ tổng hợp (IPM).
- Thời điểm thu hoạch: Xác định đúng giai đoạn chín, dấu hiệu nhận biết cụ thể."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[{"google_search": {}}]
                    )
                )
                return response.text or ""
            except Exception as e:
                error_msg = str(e)
                if "503 UNAVAILABLE" in error_msg and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Gemini API quá tải (503). Đang thử lại sau {wait_time} giây...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Gemini API error: {e}")
                    return f"Lỗi từ Gemini API (Chi tiết): {error_msg}"