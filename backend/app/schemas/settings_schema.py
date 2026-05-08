from datetime import datetime

from pydantic import BaseModel, Field


class SettingsProfile(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)
    region: str | None = Field(default=None, max_length=100)


class UserSettingsUpdate(SettingsProfile):
    language: str | None = Field(default=None, max_length=10)
    unit: str | None = Field(default=None, max_length=30)
    theme: str | None = Field(default=None, max_length=30)
    price_alerts: bool | None = None
    weather_alerts: bool | None = None
    harvest_reminders: bool | None = None
    email_channel: bool | None = None
    zalo_channel: bool | None = None
    sms_channel: bool | None = None
    two_factor_enabled: bool | None = None


class UserSettingsRead(BaseModel):
    user_setting_id: int
    user_id: int
    full_name: str
    email: str | None = None
    phone_number: str | None = None
    region: str | None = None
    language: str
    unit: str
    theme: str
    price_alerts: bool
    weather_alerts: bool
    harvest_reminders: bool
    email_channel: bool
    zalo_channel: bool
    sms_channel: bool
    two_factor_enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
