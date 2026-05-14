import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)  # noqa

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
            self.model_fallbacks = [
                'gemini-2.0-flash-lite',  # free tier quota cao nhất, ổn định
                'gemini-2.0-flash',
                'gemini-2.5-flash',
            ]
            logger.info("Gemini client configured successfully.")

    async def get_price_answer(self, question: str, region: str, context_data: str = "") -> str:
        """Trả lời ngắn gọn về giá nông sản — không lải nhải."""
        if not self.client:
            return f"[Test] Câu trả lời giả lập cho: '{question}'"

        system_instruction = (
            f"Bạn là hệ thống thông tin giá nông sản tự động tại Việt Nam.\n"
            f"Vùng mặc định: {region}.\n"
            "QUY TẮC NGHIÊM NGẶT:\n"
            "- Trả lời TỐI ĐA 10 dòng, KHÔNG có lời dẫn dài.\n"
            "- Bắt đầu ngay bằng số liệu giá cụ thể (VNĐ/kg).\n"
            "- Dùng bảng Markdown hoặc bullet ngắn.\n"
            "- Ghi rõ vùng địa lý và ngày cập nhật.\n"
            "- Nếu có lịch sử 7 ngày: nêu xu hướng (tăng/giảm/ổn định) + % thay đổi.\n"
            "- Nếu không có dữ liệu vùng yêu cầu: nêu rõ và cho giá vùng gần nhất.\n"
            "- KHÔNG giải thích nguyên nhân, KHÔNG khuyến nghị dài."
        )
        prompt = (
            f"Dữ liệu thực tế:\n{context_data or 'Không có dữ liệu.'}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Trả lời ngắn gọn với số liệu cụ thể."
        )

        for model_name in self.model_fallbacks:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=system_instruction),
                )
                return response.text or ""
            except Exception as e:
                error_msg = str(e)
                if any(k in error_msg for k in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "quota", "404", "NOT_FOUND")):
                    logger.warning(f"[price/{model_name}] {error_msg[:60]}..., chuyển tiếp...")
                    continue
                return f"Lỗi AI: {error_msg}"

        return "Xin lỗi, hệ thống AI đang bận. Vui lòng thử lại sau ít phút."

    async def get_farming_advice(self, question: str, context_data: str = "") -> str:
        if not self.client:
            return f"[Chế độ Test] Đây là câu trả lời giả lập từ AI cho câu hỏi: '{question}'. Để dùng AI thật, bạn cần thêm GEMINI_API_KEY vào file .env!"

        system_instruction = """Bạn là chuyên gia nông nghiệp hàng đầu Việt Nam với 20 năm kinh nghiệm thực tiễn,
am hiểu sâu về: kỹ thuật canh tác, sinh lý cây trồng, bảo vệ thực vật, thổ nhưỡng, thủy lợi,
thị trường nông sản và chính sách nông nghiệp Việt Nam.

NGUYÊN TẮC TRẢ LỜI:
1. Dựa trên dữ liệu hệ thống được cung cấp để trả lời chính xác nhất có thể.
2. Trả lời CỤ THỂ cho vùng/địa phương được hỏi (nếu có), không trả lời chung chung.
3. Cung cấp số liệu kỹ thuật chính xác: liều lượng phân bón, nồng độ thuốc, thời điểm xử lý.
4. Phân tích NGUYÊN NHÂN sâu xa của vấn đề, không chỉ mô tả triệu chứng.
5. Đưa ra GIẢI PHÁP CỤ THỂ, có thể thực hiện ngay được, theo thứ tự ưu tiên.
6. Cảnh báo RỦI RO và sai lầm phổ biến liên quan đến câu hỏi.
7. Kết thúc bằng 1-2 câu khuyến nghị hành động ngay cho nông dân.

ĐỊNH DẠNG: Sử dụng tiêu đề rõ ràng, bullet points khi liệt kê, in đậm các thông tin quan trọng."""

        prompt = f"""--- DỮ LIỆU HỆ THỐNG (ngữ cảnh) ---
{context_data if context_data else "Không có dữ liệu bổ sung."}

--- CÂU HỎI CỦA NÔNG DÂN ---
{question}

--- YÊU CẦU ---
Hãy phân tích kỹ và trả lời đầy đủ, chuyên sâu dựa trên dữ liệu bên trên. Nếu câu hỏi liên quan đến:
- Giá cả/thị trường: Phân tích giá trong dữ liệu, so sánh xu hướng, dự báo ngắn hạn.
- Kỹ thuật trồng trọt: Đưa quy trình đầy đủ, thông số kỹ thuật cụ thể.
- Bệnh/sâu hại: Mô tả triệu chứng, nguyên nhân, biện pháp phòng trừ tổng hợp (IPM).
- Thời điểm thu hoạch: Xác định đúng giai đoạn chín, dấu hiệu nhận biết cụ thể."""

        for model_name in self.model_fallbacks:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                    )
                )
                if model_name != self.model_fallbacks[0]:
                    logger.info(f"Dùng model fallback thành công: {model_name}")
                return response.text or ""
            except Exception as e:
                error_msg = str(e)
                is_quota   = "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower()
                is_overload = "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg
                is_not_found = "404" in error_msg or "NOT_FOUND" in error_msg
                if is_quota or is_overload or is_not_found:
                    logger.warning(f"[{model_name}] không khả dụng ({error_msg[:60]}...), chuyển tiếp...")
                    continue
                else:
                    logger.error(f"Gemini API lỗi không xử lý được ({model_name}): {e}")
                    return f"Lỗi từ Gemini API: {error_msg}"

        # Tất cả Gemini model đều quá tải → thử Claude fallback
        try:
            from app.integrations.claude_client import ClaudeClient
            claude = ClaudeClient()
            if claude.client:
                logger.info("Gemini quá tải, chuyển sang Claude fallback...")
                return await claude.get_farming_advice(question, context_data)
        except Exception as e:
            logger.error(f"Claude fallback cũng lỗi: {e}")

        return "Xin lỗi, hệ thống AI đang bận. Vui lòng thử lại sau ít phút."