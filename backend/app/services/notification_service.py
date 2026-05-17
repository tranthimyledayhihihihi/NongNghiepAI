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
        direction = "vượt ngưỡng" if condition.lower() in ("trên", "tren", "above", ">") else "xuống dưới ngưỡng"
        subject = f"[Cảnh báo giá] {crop_name} tại {region} đã {direction}"
        plain = (
            f"Giá {crop_name} tại {region} hiện tại là {current_price:,.0f} VND/kg, "
            f"đã {direction} mục tiêu {target_price:,.0f} VND/kg. "
            "Kiểm tra AgriAI để xem thêm thông tin thị trường."
        )
        html = (
            "<html><body>"
            "<h2>Cảnh báo giá nông sản</h2>"
            f"<p>Giá <strong>{crop_name}</strong> tại <strong>{region}</strong>: "
            f"<strong>{current_price:,.0f} VND/kg</strong>.</p>"
            f"<p>Ngưỡng mục tiêu: {target_price:,.0f} VND/kg. Trạng thái: {direction}.</p>"
            "</body></html>"
        )
        return subject, plain, html


notification_service = NotificationService()
