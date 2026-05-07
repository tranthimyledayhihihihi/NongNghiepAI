import httpx

from app.core.config import settings


class AIClient:
    def complete(self, messages: list[dict], system_prompt: str | None = None) -> dict:
        provider = settings.AI_PROVIDER.lower()
        if provider == "openai":
            return self._complete_openai(messages, system_prompt)
        return self._complete_anthropic(messages, system_prompt)

    def _complete_anthropic(self, messages: list[dict], system_prompt: str | None = None) -> dict:
        api_key = settings.CLAUDE_API_KEY or settings.AI_API_KEY
        if not api_key:
            raise RuntimeError("CLAUDE_API_KEY or AI_API_KEY is not configured")
        payload = {
            "model": settings.AI_MODEL_NAME,
            "max_tokens": 900,
            "messages": messages,
        }
        if system_prompt:
            payload["system"] = system_prompt
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        text = "\n".join(part.get("text", "") for part in data.get("content", []) if part.get("type") == "text")
        return {
            "answer": text.strip(),
            "provider": "anthropic",
            "model": data.get("model") or settings.AI_MODEL_NAME,
            "token_usage": data.get("usage"),
            "is_mock": False,
        }

    def _complete_openai(self, messages: list[dict], system_prompt: str | None = None) -> dict:
        if not settings.AI_API_KEY:
            raise RuntimeError("AI_API_KEY is not configured")
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        openai_messages.extend(messages)
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.AI_API_KEY}", "content-type": "application/json"},
            json={"model": settings.AI_MODEL_NAME, "messages": openai_messages, "temperature": 0.2},
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        choice = data.get("choices", [{}])[0]
        return {
            "answer": (choice.get("message") or {}).get("content", "").strip(),
            "provider": "openai",
            "model": data.get("model") or settings.AI_MODEL_NAME,
            "token_usage": data.get("usage"),
            "is_mock": False,
        }


ai_client = AIClient()
claude_client = ai_client

__all__ = ["ai_client", "claude_client", "AIClient"]
