import os
import logging
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()  # Đảm bảo đọc biến môi trường từ file .env vào hệ thống

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY is not set. Claude AI will not work.")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=api_key)
        # Sử dụng model haiku cho tốc độ phản hồi nhanh, tiết kiệm chi phí cho MVP
        self.model = "claude-3-haiku-20240307"

    async def get_farming_advice(self, question: str, context_data: str = "") -> str:
        if not self.client:
            return f"[Chế độ Test] Đây là câu trả lời giả lập từ AI cho câu hỏi: '{question}'. Để dùng AI thật, bạn cần thêm ANTHROPIC_API_KEY vào file .env!"
            
        prompt = f"Bạn là một chuyên gia nông nghiệp AI.\n\nDữ liệu bối cảnh: {context_data}\n\nCâu hỏi của nông dân: {question}\n\nHãy đưa ra lời khuyên ngắn gọn, dễ hiểu và thực tế."
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            error_msg = str(e)
            if "credit balance is too low" in error_msg:
                return f"[Hết Tiền API] Tài khoản Claude của bạn chưa được nạp tiền. Đây là câu trả lời giả lập cho: '{question}'"
            return f"Lỗi từ Claude API (Chi tiết): {error_msg}"


ai_client = ClaudeClient()