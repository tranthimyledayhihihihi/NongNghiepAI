from datetime import datetime

from pydantic import BaseModel, Field


class AlertCreateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    target_price: float = Field(..., gt=0)
    condition: str = Field("above", pattern="^(above|below)$")
    notification_channel: str = Field("email", pattern="^(email|zalo|sms)$")
    receiver: str = Field(..., min_length=1)


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
