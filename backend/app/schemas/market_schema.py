from pydantic import BaseModel, Field, model_validator


class MarketSuggestRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    quantity: float = Field(0.0, ge=0)
    quantity_kg: float = Field(0.0, ge=0)   # alias cho quantity (backward compat)
    quality_grade: str = "grade_1"

    @model_validator(mode="after")
    def resolve_quantity(self):
        if self.quantity == 0.0 and self.quantity_kg > 0:
            self.quantity = self.quantity_kg
        if self.quantity <= 0:
            raise ValueError("Vui lòng cung cấp 'quantity' hoặc 'quantity_kg' > 0")
        return self


class MarketSuggestResponse(BaseModel):
    crop_name: str
    region: str
    recommended_channel: str
    reason: str
    profit_comparison: list[dict] = Field(default_factory=list)
    warning: str | None = None
    source: str | None = None
    is_mock: bool = False
    pricing_source: str | None = None
