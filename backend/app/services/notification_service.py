from app.integrations.email_client import email_client
from app.integrations.sms_client import sms_client
from app.integrations.zalo_client import zalo_client


class NotificationService:
    def send(
        self,
        channel: str,
        receiver: str,
        subject: str,
        message: str,
        html_message: str | None = None,
    ) -> dict:
        channel = channel.lower().strip()
        if channel == "email":
            result = email_client.send(receiver, subject, message, html_message)
        elif channel == "zalo":
            result = zalo_client.send(receiver, message)
        elif channel == "sms":
            result = sms_client.send(receiver, message)
        else:
            result = {"receiver": receiver, "status": "failed", "message_id": None, "error": f"Unknown channel: {channel}"}
        return {"channel": channel, **result}

    @staticmethod
    def build_price_alert_message(
        crop_name: str,
        region: str,
        current_price: float,
        target_price: float,
        condition: str,
    ) -> tuple[str, str, str]:
        direction = "vuot nguong" if condition.lower() in ("tren", "above", ">") else "xuong duoi nguong"
        subject = f"[Canh bao gia] {crop_name} tai {region} da {direction}"
        plain = (
            f"Gia {crop_name} tai {region} hien tai la {current_price:,.0f} VND/kg, "
            f"da {direction} muc tieu {target_price:,.0f} VND/kg. "
            "Kiem tra AgriAI de xem them thong tin thi truong."
        )
        html = (
            "<html><body>"
            "<h2>Canh bao gia nong san</h2>"
            f"<p>Gia <strong>{crop_name}</strong> tai <strong>{region}</strong>: "
            f"<strong>{current_price:,.0f} VND/kg</strong>.</p>"
            f"<p>Nguong muc tieu: {target_price:,.0f} VND/kg. Trang thai: {direction}.</p>"
            "</body></html>"
        )
        return subject, plain, html


notification_service = NotificationService()
