import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4

from app.core.config import settings


class EmailClient:
    def send(self, receiver: str, subject: str, message: str, html_message: str | None = None) -> dict:
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            return {
                "receiver": receiver,
                "status": "failed",
                "message_id": None,
                "error": "SMTP chưa được cấu hình",
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.FROM_EMAIL or settings.SMTP_USER
            msg["To"] = receiver
            msg.attach(MIMEText(message, "plain", "utf-8"))
            if html_message:
                msg.attach(MIMEText(html_message, "html", "utf-8"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], receiver, msg.as_string())
            return {"receiver": receiver, "status": "sent", "message_id": f"smtp-{uuid4()}", "error": None}
        except Exception as exc:
            return {"receiver": receiver, "status": "failed", "message_id": None, "error": str(exc)}


email_client = EmailClient()
