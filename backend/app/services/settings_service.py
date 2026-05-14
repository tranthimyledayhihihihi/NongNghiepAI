from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.settings import NotificationPreference, UserSettings
from app.models.user import User
from app.schemas.settings_schema import UserSettingsUpdate


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
            "region": "Region",
        }
        for key, attr in profile_map.items():
            if key not in data:
                continue
            value = data[key]
            if key == "email" and value:
                existing = (
                    db.query(User)
                    .filter(func.lower(User.Email) == value.strip().lower(), User.UserID != user.UserID)
                    .first()
                )
                if existing:
                    raise ValueError("email already registered")
                value = value.strip().lower()
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
            "region": user.Region,
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


settings_service = SettingsService()
