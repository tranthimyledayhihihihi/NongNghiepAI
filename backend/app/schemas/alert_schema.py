from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AlertCreateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    target_price: float = Field(0.0, ge=0)
    threshold_value: float = Field(0.0, ge=0)   # alias cho target_price (backward compat)
    condition: str = Field("above", pattern="^(above|below)$")
    alert_type: str = Field("price")             # backward compat field (ignored, kept for API compat)
    notification_channel: str = Field("email", pattern="^(email|zalo|sms)$")
    receiver: str = Field("", min_length=0)      # optional — default rỗng
    user_id: int | None = None                   # backward compat

    @model_validator(mode="after")
    def resolve_target_price(self):
        if self.target_price == 0.0 and self.threshold_value > 0:
            self.target_price = self.threshold_value
        if self.target_price <= 0:
            raise ValueError("Vui lòng cung cấp 'target_price' hoặc 'threshold_value' > 0")
        if not self.receiver:
            self.receiver = "admin@nongsan.vn"   # default khi không cung cấp
        return self


class AlertResponse(BaseModel):
    alert_id: int
    crop_name: str
    region: str
    target_price: float
    condition: str
    notification_channel: str
    receiver: str
    is_active: bool
    message: str
    created_at: datetime | None = None


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]


class AlertDeactivateResponse(BaseModel):
    alert_id: int
    message: str
