import asyncio
import logging
import os

from anthropic import Anthropic, AsyncAnthropic
from dotenv import load_dotenv

from app.core.config import settings

logger = logging.getLogger(__name__)

load_dotenv()


class ClaudeClient:
    def __init__(self):
        api_key = settings.CLAUDE_API_KEY or os.getenv("ANTHROPIC_API_KEY") or (
            settings.AI_API_KEY if settings.AI_PROVIDER.lower() == "claude" else ""
        )
        self.model = settings.AI_MODEL_NAME or "claude-3-haiku-20240307"
        if not api_key:
            logger.warning("Claude API key is not set. Claude AI will use fallback answers.")
            self.client = None
            self.sync_client = None
            return

        self.client = AsyncAnthropic(api_key=api_key, timeout=settings.AI_TIMEOUT_SECONDS)
        self.sync_client = Anthropic(api_key=api_key, timeout=settings.AI_TIMEOUT_SECONDS)

    async def get_farming_advice(self, question: str, context_data: str = "") -> str:
        if not self.client:
            return self._fallback_text(question, "Claude API key chua duoc cau hinh.")

        prompt = (
            "Ban la mot chuyen gia nong nghiep AI.\n\n"
            f"Du lieu boi canh: {context_data}\n\n"
            f"Cau hoi cua nong dan: {question}\n\n"
            "Hay dua ra loi khuyen ngan gon, de hieu va thuc te."
        )

        try:
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
            return response.content[0].text
        except asyncio.TimeoutError:
            logger.warning("[Claude] farming advice timed out after %.1fs", settings.AI_TIMEOUT_SECONDS)
            return self._fallback_text(question, "AI phan hoi cham/timeout.")
        except Exception as exc:
            logger.error("Claude API error: %s", exc)
            return self._fallback_text(question, str(exc))

    def complete(self, messages: list[dict], system_prompt: str = "", max_tokens: int = 1024) -> dict:
        if not self.sync_client:
            return self._fallback_completion("Claude API key chua duoc cau hinh.")

        try:
            response = self.sync_client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=messages,
            )
            return {
                "answer": response.content[0].text if response.content else "",
                "provider": "claude",
                "model": self.model,
                "token_usage": {
                    "input_tokens": getattr(response.usage, "input_tokens", None),
                    "output_tokens": getattr(response.usage, "output_tokens", None),
                },
                "is_mock": False,
                "error": None,
            }
        except Exception as exc:
            message = str(exc)
            logger.warning("[Claude] complete failed: %s", message)
            return self._fallback_completion(message)

    @staticmethod
    def _fallback_text(question: str, reason: str) -> str:
        return (
            "AI dang phan hoi cham nen he thong tra loi bang che do du phong. "
            f"Cau hoi: '{question}'. Ly do: {reason}. "
            "Hay kiem tra du lieu thoi tiet, gia va canh bao trong dashboard roi thu lai sau."
        )

    @staticmethod
    def _fallback_completion(reason: str) -> dict:
        timeout = "timeout" in reason.lower() or "timed out" in reason.lower()
        answer = (
            "AI dang phan tich cham, he thong da dung cau tra loi du phong tu du lieu noi bo. "
            "Vui long xem them the thoi tiet, gia thi truong va canh bao tren dashboard; ban co the gui lai cau hoi sau it phut."
        )
        return {
            "answer": answer,
            "provider": "rule_based_fallback",
            "model": "local-context-v1",
            "token_usage": None,
            "is_mock": True,
            "error": reason,
            "timeout": timeout,
        }


ai_client = ClaudeClient()
