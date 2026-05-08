from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    user_id: int
    type: str = Field(default="system", max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    priority: str = Field(default="medium", max_length=30)
    channel: str = Field(default="app", max_length=30)
    related_entity_type: str | None = Field(default=None, max_length=50)
    related_entity_id: int | None = None


class NotificationRead(BaseModel):
    notification_id: int
    user_id: int
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    is_deleted: bool
    related_entity_type: str | None = None
    related_entity_id: int | None = None
    channel: str
    created_at: datetime | None = None
    read_at: datetime | None = None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationRead]
    total: int
    unread_count: int


class NotificationUpdateResponse(BaseModel):
    notification_id: int
    message: str
