from datetime import date, datetime

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
    temp_min: float | None = None
    temp_max: float | None = None
    rainfall: float | None = None
    humidity: float | None = None
    condition: str | None = None
    wind_speed: float | None = None
    uv_index: float | None = None
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
    agriculture_insights: list[dict] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class WeatherForecastItem(BaseModel):
    date: date | str
    region: str | None = None
    day_label: str | None = None
    temperature: float | None = None
    temp_min: float | None = None
    temp_max: float | None = None
    rainfall: float | None = None
    rain_probability: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    uv_index: float | None = None
    condition: str | None = None
    weather_code: int | None = None
    warnings: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    is_realtime: bool = False
    is_mock: bool = False
    cache_status: str = "unknown"
    last_updated: datetime | None = None


class WeatherHourlyItem(BaseModel):
    time: str | None = None
    date: date | str | None = None
    forecast_at: datetime | None = None
    region: str | None = None
    temperature: float | None = None
    apparent_temperature: float | None = None
    rainfall: float | None = None
    rain_probability: float | None = None
    humidity: float | None = None
    dew_point: float | None = None
    wind_speed: float | None = None
    wind_gusts: float | None = None
    uv_index: float | None = None
    visibility: float | None = None
    cloud_cover: float | None = None
    pressure: float | None = None
    condition: str | None = None
    weather_code: int | None = None
    recommendation: str | None = None
    source_name: str | None = None
    is_realtime: bool = False
    is_mock: bool = False
    cache_status: str = "unknown"
    last_updated: datetime | None = None


class WeatherForecastResponse(BaseModel):
    region: str
    days: int
    forecast: list[WeatherForecastItem]


class WeatherHourlyResponse(BaseModel):
    region: str
    hours: int
    forecast: list[WeatherHourlyItem]


class WeatherAlertResponse(BaseModel):
    alert_type: str
    severity: str
    title: str
    message: str
    recommendation: str | None = None
    trigger_value: float | None = None
    trigger_unit: str | None = None
    forecast_date: date | str | None = None
    source: str = "rule"


class WeatherActivityRecommendation(BaseModel):
    action_type: str
    action: str
    decision: str
    reason: str
    timing: str | None = None
    priority: str = "medium"
    source: str = "rule"


class WeatherAISummary(BaseModel):
    provider: str = "rule_based_ai"
    summary: str
    risk_explanation: str
    action_plan: list[str] = Field(default_factory=list)
    crop_note: str | None = None
    data_note: str | None = None


class WeatherAgricultureResponse(BaseModel):
    module_name: str
    region: str
    crop_name: str | None = None
    growth_stage: str | None = None
    location: dict | None = None
    current: WeatherResponse
    forecast: list[WeatherForecastItem]
    hourly_forecast: list[WeatherHourlyItem] = Field(default_factory=list)
    alerts: list[WeatherAlertResponse] = Field(default_factory=list)
    activity_recommendations: list[WeatherActivityRecommendation] = Field(default_factory=list)
    ai_recommendation: WeatherAISummary
    data_flow: list[str] = Field(default_factory=list)
    source_summary: dict = Field(default_factory=dict)
    generated_at: datetime
