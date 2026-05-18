from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SeasonStatus = Literal["planned", "active", "harvesting", "completed", "cancelled"]
SeasonHealthStatus = Literal["good", "warning", "risk"]
AreaUnit = Literal["ha", "m2", "sao"]


class SeasonBase(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=100)
    region: str = Field(..., min_length=1, max_length=100)
    farm_name: str | None = Field(default=None, max_length=150)
    area: float | None = Field(default=None, gt=0)
    area_unit: AreaUnit = "ha"
    start_date: date
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    status: SeasonStatus = "active"
    health_status: SeasonHealthStatus = "good"
    note: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expected_harvest_date and self.expected_harvest_date <= self.start_date:
            raise ValueError("expected_harvest_date must be after start_date")
        if self.actual_harvest_date and self.actual_harvest_date < self.start_date:
            raise ValueError("actual_harvest_date must be on or after start_date")
        return self


class SeasonCreate(SeasonBase):
    pass


class SeasonUpdate(BaseModel):
    crop_name: str | None = Field(default=None, min_length=1, max_length=100)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    farm_name: str | None = Field(default=None, max_length=150)
    area: float | None = Field(default=None, gt=0)
    area_unit: AreaUnit | None = None
    start_date: date | None = None
    expected_harvest_date: date | None = None
    actual_harvest_date: date | None = None
    status: SeasonStatus | None = None
    health_status: SeasonHealthStatus | None = None
    note: str | None = None


class SeasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    crop_name: str
    region: str
    farm_name: str | None = None
    area: float | None = None
    area_unit: str
    start_date: date
    expected_harvest_date: date
    actual_harvest_date: date | None = None
    status: str
    health_status: str
    note: str | None = None
    days_until_harvest: int | None = None
    is_upcoming_harvest: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SeasonListResponse(BaseModel):
    total: int
    seasons: list[SeasonResponse]


class SeasonSummaryResponse(BaseModel):
    total_seasons: int
    active_seasons: int
    completed_seasons: int
    risk_seasons: int
    upcoming_harvest_count: int


class SeasonHarvestEstimateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1, max_length=100)
    region: str = Field(..., min_length=1, max_length=100)
    start_date: date


class SeasonHarvestEstimateResponse(BaseModel):
    expected_harvest_date: date
    growth_days: int
    confidence: float
    warning: str | None = None
    recommendation: str | None = None
    weather_risk: str | None = None
    weather_source_name: str | None = None
