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
    wind_speed: float | None = None
    pressure: float | None = None
    weather_code: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    recorded_at: datetime
    source: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    is_realtime: bool = False
    is_mock: bool = False
    last_updated: datetime | None = None
    data_age_minutes: int | None = None
    cache_status: str = "unknown"
