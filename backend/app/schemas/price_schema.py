from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class PriceRequest(BaseModel):
    crop_name: str = Field(..., description="Tên nông sản")
    region: str = Field(..., description="Khu vực")
    quality_grade: Optional[str] = Field("grade_1", description="Phân loại chất lượng")

class PriceResponse(BaseModel):
    crop_name: str
    region: str
    current_price: float
    quality_grade: str
    price_trend: str  # increasing, decreasing, stable
    forecast_7days: Optional[List[dict]] = None
    last_updated: datetime

class PriceForecastRequest(BaseModel):
    crop_name: str
    region: str
    days: int = Field(7, ge=1, le=30, description="Số ngày dự báo (1-30)")

class PriceForecastResponse(BaseModel):
    crop_name: str
    region: str
    forecast_data: List[dict]
    trend: str
    recommendation: str
