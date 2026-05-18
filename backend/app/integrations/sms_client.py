from uuid import uuid4

from app.core.config import settings
from app.core.resilience import build_timeout, resilient_request

_ESMS_URL = "https://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_post_json/"


class SmsClient:
    def send(self, phone: str, message: str) -> dict:
        if not settings.ESMS_API_KEY or not settings.ESMS_SECRET_KEY:
            return {
                "receiver": phone,
                "status": "mock_sent",
                "message_id": f"mock-sms-{uuid4()}",
                "error": "ESMS_API_KEY / ESMS_SECRET_KEY chưa cấu hình",
            }
        try:
            payload = {
                "ApiKey": settings.ESMS_API_KEY,
                "SecretKey": settings.ESMS_SECRET_KEY,
                "Phone": phone,
                "Content": message,
                "IsUnicode": "1",
                "Brandname": settings.ESMS_BRAND_NAME,
                "SmsType": str(settings.ESMS_SMS_TYPE),
            }
            response = resilient_request(
                "POST",
                _ESMS_URL,
                json=payload,
                timeout=build_timeout(total=20, connect=5, read=12),
                retries=1,
                service_name="ESMS",
            )
            data = response.json()
            # ESMS trả về CodeResult == "100" là thành công
            if str(data.get("CodeResult", "")) == "100":
                return {
                    "receiver": phone,
                    "status": "sent",
                    "message_id": str(data.get("SMSID") or uuid4()),
                    "error": None,
                }
            return {
                "receiver": phone,
                "status": "failed",
                "message_id": None,
                "error": data.get("ErrorMessage") or f"CodeResult={data.get('CodeResult')}",
            }
        except Exception as exc:
            return {"receiver": phone, "status": "failed", "message_id": None, "error": str(exc)}


sms_client = SmsClient()
