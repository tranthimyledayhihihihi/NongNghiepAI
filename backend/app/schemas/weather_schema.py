from datetime import datetime

from pydantic import BaseModel, Field


class WeatherCreateRequest(BaseModel):
    region: str = Field(..., min_length=1)
    temperature: float | None = None
    rainfall: float | None = None
    humidity: float | None = None
    condition: str | None = None


class WeatherResponse(BaseModel):
    region: str
    temperature: float | None = None
    rainfall: float | None = None
    humidity: float | None = None
    condition: str | None = None
    recorded_at: datetime
