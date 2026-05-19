from uuid import uuid4

from app.core.config import settings
from app.core.resilience import build_timeout, resilient_request


class ZaloClient:
    def send(self, receiver: str, message: str) -> dict:
        if not settings.ZALO_OA_TOKEN:
            return {
                "receiver": receiver,
                "status": "missing_token",
                "message_id": None,
                "error": "ZALO_OA_TOKEN chưa được cấu hình",
            }
        try:
            response = resilient_request(
                "POST",
                f"{settings.ZALO_API_BASE_URL.rstrip('/')}/v2.0/oa/message",
                headers={"access_token": settings.ZALO_OA_TOKEN},
                json={"recipient": {"user_id": receiver}, "message": {"text": message}},
                timeout=build_timeout(total=20, connect=5, read=12),
                retries=1,
                service_name="Zalo OA",
            )
            data = response.json()
            status = "sent" if data.get("error", 0) == 0 else "failed"
            return {
                "receiver": receiver,
                "status": status,
                "message_id": str(data.get("message_id") or uuid4()),
                "error": data.get("message") if status == "failed" else None,
            }
        except Exception as exc:
            return {"receiver": receiver, "status": "failed", "message_id": None, "error": str(exc)}


zalo_client = ZaloClient()
