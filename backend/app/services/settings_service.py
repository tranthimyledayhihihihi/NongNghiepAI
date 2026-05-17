from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.core.security import get_password_hash, verify_password
from app.models.notification import Notification, NotificationDelivery
from app.models.settings import NotificationPreference, UserSettings
from app.models.user import User
from app.schemas.settings_schema import UserSettingsUpdate
from app.services.location_service import location_service
from app.services.notification_service import notification_service


TWO_FACTOR_CHALLENGES: dict[str, dict] = {}


class SettingsService:
    def get_settings(self, db: Session, user: User) -> dict:
        settings = self._get_or_create_settings(db, user)
        self._sync_preferences(db, user, settings)
        return self._to_dict(user, settings)

    def update_settings(self, db: Session, user: User, request: UserSettingsUpdate) -> dict:
        settings = self._get_or_create_settings(db, user)
        data = request.model_dump(exclude_unset=True)

        profile_map = {
            "full_name": "FullName",
            "email": "Email",
            "phone_number": "PhoneNumber",
            "zalo_user_id": "ZaloID",
            "region": "Region",
        }
        if data.get("region_key"):
            data["region"] = location_service.resolve_region(db, data["region_key"])
        for key, attr in profile_map.items():
            if key not in data:
                continue
            value = data[key]
            if key == "email" and value:
                if "@" not in value:
                    raise ValueError("email is invalid")
                existing = (
                    db.query(User)
                    .filter(func.lower(User.Email) == value.strip().lower(), User.UserID != user.UserID)
                    .first()
                )
                if existing:
                    raise ValueError("email already registered")
                value = value.strip().lower()
            if key == "phone_number" and value:
                digits = "".join(ch for ch in value if ch.isdigit())
                if len(digits) < 9:
                    raise ValueError("phone number is invalid")
            if isinstance(value, str):
                value = value.strip()
            setattr(user, attr, value)

        settings_map = {
            "language": "Language",
            "unit": "Unit",
            "theme": "Theme",
            "price_alerts": "PriceAlerts",
            "weather_alerts": "WeatherAlerts",
            "harvest_reminders": "HarvestReminders",
            "email_channel": "EmailChannel",
            "zalo_channel": "ZaloChannel",
            "sms_channel": "SmsChannel",
            "two_factor_enabled": "TwoFactorEnabled",
        }
        for key, attr in settings_map.items():
            if key not in data:
                continue
            value = data[key]
            if isinstance(value, str):
                value = value.strip()
            setattr(settings, attr, value)

        try:
            db.add(user)
            db.add(settings)
            db.commit()
            db.refresh(user)
            db.refresh(settings)
            self._sync_preferences(db, user, settings)
        except SQLAlchemyError:
            db.rollback()
            raise

        return self._to_dict(user, settings)

    def get_channel_status(self, db: Session, user: User) -> dict:
        settings = self._get_or_create_settings(db, user)

        def latest(channel: str):
            return (
                db.query(NotificationDelivery)
                .filter(NotificationDelivery.Channel == channel)
                .order_by(desc(NotificationDelivery.SentAt))
                .first()
            )

        email_latest = latest("email")
        zalo_latest = latest("zalo")
        sms_latest = latest("sms")
        return {
            "app": {
                "enabled": True,
                "configured": True,
                "status": "ready",
                "last_tested_at": None,
                "error": None,
            },
            "email": self._channel_status(
                enabled=bool(settings.EmailChannel),
                configured=bool(app_settings.SMTP_HOST and app_settings.SMTP_USER and app_settings.SMTP_PASSWORD),
                missing_status="not_configured",
                latest=email_latest,
                receiver=user.Email,
            ),
            "zalo": self._channel_status(
                enabled=bool(settings.ZaloChannel),
                configured=bool(app_settings.ZALO_OA_TOKEN),
                missing_status="missing_token",
                latest=zalo_latest,
                receiver=user.ZaloID,
            ),
            "sms": self._channel_status(
                enabled=bool(settings.SmsChannel),
                configured=bool(app_settings.ESMS_API_KEY and app_settings.ESMS_SECRET_KEY),
                missing_status="mock",
                latest=sms_latest,
                receiver=user.PhoneNumber,
            ),
            "data_sources": {
                "weather": {
                    "status": "ready" if app_settings.OPEN_METEO_BASE_URL else "not_configured",
                    "source": "Open-Meteo",
                    "cache_ttl_seconds": app_settings.WEATHER_CACHE_TTL_SECONDS,
                },
                "price": {
                    "status": "ready",
                    "source": "MarketPrices DB / crawler",
                    "cache_ttl_seconds": 3600,
                },
            },
        }

    def test_channel(self, db: Session, user: User, channel: str, receiver: str | None = None) -> dict:
        channel = channel.lower().strip()
        receiver = receiver or self._default_receiver(user, channel)
        if channel not in {"email", "zalo", "sms", "app"}:
            raise ValueError("unsupported channel")
        if channel != "app" and not receiver:
            raise ValueError("receiver is required")

        row = Notification(
            UserID=user.UserID,
            Type="system",
            Title=f"Kiểm tra kênh {channel.upper()}",
            Message="Đây là bản ghi kiểm tra kênh gửi từ trang cài đặt.",
            Priority="medium",
            Channel=channel,
            RelatedEntityType="channel_test",
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        if channel == "app":
            result = {"channel": "app", "receiver": receiver, "status": "stored", "message_id": None, "error": None}
        else:
            result = notification_service.send(
                channel,
                receiver,
                "[AgriAI] Kiểm tra kênh thông báo",
                "Tin nhắn kiểm tra từ trang cài đặt AgriAI.",
            )
        delivery = NotificationDelivery(
            NotificationID=row.NotificationID,
            Channel=channel,
            Receiver=receiver,
            Status=result.get("status") or "failed",
            ProviderMessageID=result.get("message_id"),
            ErrorMessage=result.get("error"),
        )
        db.add(delivery)
        db.commit()
        return {
            "notification_id": row.NotificationID,
            "delivery_id": delivery.DeliveryID,
            **result,
        }

    def start_2fa(self, db: Session, user: User, method: str = "email") -> dict:
        method = method.lower().strip()
        if method not in {"email", "sms"}:
            raise ValueError("unsupported 2FA method")
        receiver = self._default_receiver(user, method)
        if not receiver:
            raise ValueError(f"{method} receiver is missing")
        challenge_id = str(uuid4())
        code = str(uuid4().int)[0:6]
        expires_at = datetime.now() + timedelta(minutes=10)
        TWO_FACTOR_CHALLENGES[challenge_id] = {
            "user_id": user.UserID,
            "code": code,
            "expires_at": expires_at,
            "method": method,
        }
        notification_service.send(
            method,
            receiver,
            "[AgriAI] Mã xác thực 2 lớp",
            f"Mã xác thực AgriAI của bạn là {code}. Mã hết hạn sau 10 phút.",
        )
        return {
            "method": method,
            "challenge_id": challenge_id,
            "expires_at": expires_at,
            "receiver": receiver,
            "dev_code": code,
        }

    def verify_2fa(self, db: Session, user: User, challenge_id: str, code: str) -> dict:
        challenge = TWO_FACTOR_CHALLENGES.get(challenge_id)
        if not challenge or challenge["user_id"] != user.UserID:
            raise ValueError("invalid challenge")
        if challenge["expires_at"] < datetime.now():
            TWO_FACTOR_CHALLENGES.pop(challenge_id, None)
            raise ValueError("challenge expired")
        if challenge["code"] != code:
            raise ValueError("invalid verification code")
        settings = self._get_or_create_settings(db, user)
        settings.TwoFactorEnabled = True
        db.add(settings)
        db.commit()
        TWO_FACTOR_CHALLENGES.pop(challenge_id, None)
        return {"success": True, "two_factor_enabled": True}

    def disable_2fa(self, db: Session, user: User) -> dict:
        settings = self._get_or_create_settings(db, user)
        settings.TwoFactorEnabled = False
        db.add(settings)
        db.commit()
        return {"success": True, "two_factor_enabled": False}

    def change_password(self, db: Session, user: User, old_password: str, new_password: str) -> dict:
        if len(new_password) < 6:
            raise ValueError("new password must be at least 6 characters")
        if not verify_password(old_password, user.PasswordHash):
            raise ValueError("old password is incorrect")
        user.PasswordHash = get_password_hash(new_password)
        db.add(user)
        db.commit()
        return {"success": True, "message": "password changed"}

    def _get_or_create_settings(self, db: Session, user: User) -> UserSettings:
        settings = db.query(UserSettings).filter(UserSettings.UserID == user.UserID).first()
        if settings:
            return settings
        settings = UserSettings(UserID=user.UserID)
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings

    def _sync_preferences(self, db: Session, user: User, settings: UserSettings) -> None:
        event_flags = {
            "price": bool(settings.PriceAlerts),
            "weather": bool(settings.WeatherAlerts),
            "harvest": bool(settings.HarvestReminders),
        }
        channel_flags = {
            "email": (bool(settings.EmailChannel), user.Email),
            "zalo": (bool(settings.ZaloChannel), user.ZaloID),
            "sms": (bool(settings.SmsChannel), user.PhoneNumber),
        }
        try:
            for event_type, event_enabled in event_flags.items():
                for channel, (channel_enabled, receiver) in channel_flags.items():
                    preference = (
                        db.query(NotificationPreference)
                        .filter(
                            NotificationPreference.UserID == user.UserID,
                            NotificationPreference.EventType == event_type,
                            NotificationPreference.Channel == channel,
                        )
                        .first()
                    )
                    if preference is None:
                        preference = NotificationPreference(
                            UserID=user.UserID,
                            EventType=event_type,
                            Channel=channel,
                        )
                        db.add(preference)
                    preference.IsEnabled = event_enabled and channel_enabled
                    preference.Receiver = receiver
            db.commit()
        except SQLAlchemyError:
            db.rollback()

    @staticmethod
    def _to_dict(user: User, settings: UserSettings) -> dict:
        return {
            "user_setting_id": settings.UserSettingID,
            "user_id": user.UserID,
            "full_name": user.FullName,
            "email": user.Email,
            "phone_number": user.PhoneNumber,
            "zalo_user_id": user.ZaloID,
            "region": user.Region,
            "region_key": location_service.region_key(user.Region),
            "language": settings.Language,
            "unit": settings.Unit,
            "theme": settings.Theme,
            "price_alerts": bool(settings.PriceAlerts),
            "weather_alerts": bool(settings.WeatherAlerts),
            "harvest_reminders": bool(settings.HarvestReminders),
            "email_channel": bool(settings.EmailChannel),
            "zalo_channel": bool(settings.ZaloChannel),
            "sms_channel": bool(settings.SmsChannel),
            "two_factor_enabled": bool(settings.TwoFactorEnabled),
            "created_at": settings.CreatedAt,
            "updated_at": settings.UpdatedAt,
        }

    @staticmethod
    def _default_receiver(user: User, channel: str) -> str | None:
        if channel == "email":
            return user.Email
        if channel == "sms":
            return user.PhoneNumber
        if channel == "zalo":
            return user.ZaloID
        return None

    @staticmethod
    def _channel_status(
        *,
        enabled: bool,
        configured: bool,
        missing_status: str,
        latest: NotificationDelivery | None,
        receiver: str | None,
    ) -> dict:
        if not enabled:
            status = "disabled"
        elif not receiver:
            status = "pending_verification"
        elif configured:
            status = "ready"
        else:
            status = missing_status
        if latest and latest.Status in {"failed", "error"}:
            status = "failed_last_test"
        return {
            "enabled": enabled,
            "configured": configured,
            "status": status,
            "receiver": receiver,
            "last_tested_at": latest.SentAt if latest else None,
            "last_status": latest.Status if latest else None,
            "provider_message_id": latest.ProviderMessageID if latest else None,
            "error": latest.ErrorMessage if latest and latest.ErrorMessage else (None if configured else status),
        }


settings_service = SettingsService()
