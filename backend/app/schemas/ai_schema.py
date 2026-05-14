from datetime import datetime

from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    crop_name: str | None = None
    region: str | None = None
    user_id: int | None = None
    session_id: str | None = None


class AIChatResponse(BaseModel):
    answer: str
    provider: str
    model: str
    token_usage: dict | None = None
    context: dict
    is_mock: bool = False
    error: str | None = None
    created_at: datetime
