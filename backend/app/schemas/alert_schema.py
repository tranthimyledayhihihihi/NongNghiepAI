from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AlertCreateRequest(BaseModel):
    crop_name: str | None = Field(default=None, min_length=1)
    crop_id: int | None = None
    region: str = Field(..., min_length=1)
    region_key: str | None = None
    target_price: float = Field(0.0, ge=0)
    threshold_value: float = Field(0.0, ge=0)
    condition: str = Field("above", pattern="^(above|below)$")
    rule_type: str = Field("price_threshold")
    threshold_percent: float | None = None
    source: str | None = None
    alert_type: str = Field("price")
    notification_channel: str = Field("email", pattern="^(app|email|zalo|sms)$")
    receiver: str = Field("", min_length=0)
    user_id: int | None = None

    @model_validator(mode="after")
    def resolve_target_price(self):
        if not self.crop_name and not self.crop_id:
            raise ValueError("Vui lòng cung cấp crop_name hoặc crop_id")
        if self.target_price == 0.0 and self.threshold_value > 0:
            self.target_price = self.threshold_value
        if self.target_price <= 0:
            raise ValueError("Vui lòng cung cấp target_price hoặc threshold_value > 0")
        return self


class AlertResponse(BaseModel):
    alert_id: int
    alert_kind: str | None = "price"
    crop_name: str
    crop_id: int | None = None
    region: str
    region_key: str | None = None
    target_price: float
    condition: str
    weather_condition: str | None = None
    rule_type: str | None = None
    threshold_percent: float | None = None
    trigger_unit: str | None = None
    severity: str | None = None
    notification_channel: str
    receiver: str
    is_active: bool
    message: str
    created_at: datetime | None = None
    last_triggered_at: datetime | None = None


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]


class AlertDeactivateResponse(BaseModel):
    alert_id: int
    message: str
