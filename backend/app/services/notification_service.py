"""
P2-14: Notification Service
Tạo interface gửi email/Zalo; email thật, Zalo có thể mock trong MVP.
alert_service gọi được notification.
"""
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service gửi thông báo qua Email và Zalo.
    Email: dùng SMTP thật nếu có cấu hình, fallback log.
    Zalo:  mock trong MVP (log message).
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASSWORD", "")
        self.sender    = os.getenv("EMAIL_SENDER", self.smtp_user)
        self.zalo_token = os.getenv("ZALO_OA_TOKEN", "")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def send(
        self,
        channel: str,
        receiver: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
    ) -> bool:
        """
        Gửi thông báo qua kênh được chỉ định.

        Args:
            channel:      "email" | "zalo" | "sms"
            receiver:     Địa chỉ email hoặc số điện thoại / Zalo ID
            subject:      Tiêu đề
            message:      Nội dung plain text
            html_message: Nội dung HTML (tùy chọn, chỉ dùng cho email)

        Returns:
            True nếu gửi thành công
        """
        channel = channel.lower().strip()
        if channel == "email":
            return self.send_email(receiver, subject, message, html_message)
        elif channel == "zalo":
            return self.send_zalo(receiver, message)
        elif channel == "sms":
            return self.send_sms(receiver, message)
        else:
            logger.warning(f"Unknown notification channel: {channel}")
            return False

    def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
    ) -> bool:
        """Gửi email qua SMTP."""
        if not self.smtp_user or not self.smtp_pass:
            logger.info(
                f"[EMAIL MOCK] To: {to_email} | Subject: {subject} | Body: {message[:100]}"
            )
            return True  # Mock thành công

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = self.sender
            msg["To"]      = to_email

            msg.attach(MIMEText(message, "plain", "utf-8"))
            if html_message:
                msg.attach(MIMEText(html_message, "html", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.sender, to_email, msg.as_string())

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_zalo(self, zalo_id: str, message: str) -> bool:
        """
        Gửi tin nhắn Zalo OA.
        MVP: log mock. Production: gọi Zalo OA API.
        """
        if not self.zalo_token:
            logger.info(f"[ZALO MOCK] To: {zalo_id} | Message: {message[:100]}")
            return True

        try:
            import httpx
            resp = httpx.post(
                "https://openapi.zalo.me/v2.0/oa/message",
                headers={"access_token": self.zalo_token},
                json={
                    "recipient": {"user_id": zalo_id},
                    "message":   {"text": message},
                },
                timeout=10,
            )
            success = resp.status_code == 200
            if success:
                logger.info(f"Zalo message sent to {zalo_id}")
            else:
                logger.warning(f"Zalo API error: {resp.text}")
            return success
        except Exception as e:
            logger.error(f"Failed to send Zalo message: {e}")
            return False

    def send_sms(self, phone: str, message: str) -> bool:
        """SMS – mock trong MVP."""
        logger.info(f"[SMS MOCK] To: {phone} | Message: {message[:80]}")
        return True

    # ------------------------------------------------------------------ #
    # Template messages cho cảnh báo giá
    # ------------------------------------------------------------------ #

    @staticmethod
    def build_price_alert_message(
        crop_name: str,
        region: str,
        current_price: float,
        target_price: float,
        condition: str,
    ) -> tuple:
        """
        Xây dựng subject và nội dung email cảnh báo giá.
        Returns: (subject, plain_text, html)
        """
        direction = "vượt ngưỡng" if condition.lower() in ("tren", "above", ">") else "xuống dưới ngưỡng"
        subject = f"[Cảnh báo giá] {crop_name} tại {region} đã {direction}"
        plain = (
            f"Thông báo: Giá {crop_name} tại {region} hiện tại là "
            f"{current_price:,.0f} VND/kg, đã {direction} mục tiêu "
            f"{target_price:,.0f} VND/kg.\n\n"
            "Hãy kiểm tra ứng dụng AgriAI để xem thêm thông tin thị trường."
        )
        html = f"""
        <html><body>
        <h2 style="color:#e65c00;">⚠ Cảnh báo giá nông sản</h2>
        <p>Giá <strong>{crop_name}</strong> tại <strong>{region}</strong>:</p>
        <ul>
          <li>Giá hiện tại: <strong style="color:#cc0000;">{current_price:,.0f} VND/kg</strong></li>
          <li>Ngưỡng mục tiêu: {target_price:,.0f} VND/kg</li>
          <li>Trạng thái: {direction}</li>
        </ul>
        <p>Kiểm tra <a href="#">AgriAI</a> để xem thêm thông tin thị trường.</p>
        </body></html>
        """
        return subject, plain, html


notification_service = NotificationService()
