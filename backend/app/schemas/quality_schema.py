from pydantic import BaseModel, Field
from typing import Optional, List

class QualityCheckResponse(BaseModel):
    quality_grade: str = Field(..., description="Phân loại: grade_1, grade_2, grade_3")
    confidence: float = Field(..., description="Độ tin cậy (0-1)")
    defects: List[str] = Field(default_factory=list, description="Các khuyết tật phát hiện")
    suggested_price_range: dict = Field(..., description="Khoảng giá đề xuất")
    recommendations: List[str] = Field(default_factory=list, description="Khuyến nghị")

class QualityAnalysis(BaseModel):
    crop_type: str
    quality_grade: str
    defect_count: int
    defect_types: List[str]
    size_category: Optional[str] = None
    color_score: Optional[float] = None
    freshness_score: Optional[float] = None
