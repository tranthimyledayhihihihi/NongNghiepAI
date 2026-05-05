from pydantic import BaseModel, Field


class MarketSuggestRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    quality_grade: str = "grade_1"


class MarketSuggestResponse(BaseModel):
    crop_name: str
    region: str
    recommended_channel: str
    reason: str
    profit_comparison: list[dict] = Field(default_factory=list)
    warning: str | None = None
