from datetime import date, datetime

from pydantic import BaseModel, Field


class HarvestForecastRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    planting_date: date


class HarvestForecastResponse(BaseModel):
    crop_name: str
    region: str
    planting_date: date
    expected_harvest_date: date
    confidence: float = Field(..., ge=0, le=1)
    warning: str | None = None
    recommendation: str
    created_at: datetime | None = None


class HarvestScheduleCreateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    planting_date: date
    expected_harvest_date: date | None = None
    area_size: float | None = Field(default=None, ge=0)
    estimated_yield_kg: float | None = Field(default=None, ge=0)
    fertilizer_used: str | None = None
    pesticide_used: str | None = None
    notes: str | None = None
