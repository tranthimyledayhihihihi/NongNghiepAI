from datetime import datetime

from pydantic import BaseModel, Field


class QualityCheckResponse(BaseModel):
    crop_name: str
    region: str
    image_path: str | None = None
    quality_grade: str = Field(..., description="grade_1, grade_2, grade_3")
    disease_detected: bool = False
    damage_level: str = "low"
    suggested_price: float
    confidence: float = Field(..., ge=0, le=1)
    defects: list[str] = Field(default_factory=list)
    suggested_price_range: dict[str, float] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    checked_at: datetime | None = None


class QualityAnalysis(BaseModel):
    crop_type: str
    quality_grade: str
    defect_count: int
    defect_types: list[str]
    size_category: str | None = None
    color_score: float | None = None
    freshness_score: float | None = None
