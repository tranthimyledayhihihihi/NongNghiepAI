from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.price import MarketPrice
# Giả định đường dẫn đến model CropType của bạn
from app.models.crop import CropType 

router = APIRouter(prefix="/api/prices", tags=["Market Prices"])

class PriceResponse(BaseModel):
    price_id: int
    crop_name: str
    region: str
    price_per_kg: float
    quality_grade: str
    market_type: str
    source_name: Optional[str]
    price_date: date
    updated_at: datetime

@router.get("", response_model=List[PriceResponse])
def get_latest_prices(limit: int = 20, db: Session = Depends(get_db)):
    """
    Lấy danh sách giá thị trường mới nhất (mặc định 20 dòng).
    """
    results = (
        db.query(MarketPrice, CropType.CropName)
        .join(CropType, MarketPrice.CropID == CropType.CropID)
        .order_by(MarketPrice.UpdatedAt.desc())
        .limit(limit)
        .all()
    )
    
    return [
        PriceResponse(
            price_id=price.PriceID,
            crop_name=crop_name,
            region=price.Region,
            price_per_kg=price.PricePerKg,
            quality_grade=price.QualityGrade,
            market_type=price.MarketType,
            source_name=price.SourceName,
            price_date=price.PriceDate,
            updated_at=price.UpdatedAt
        )
        for price, crop_name in results
    ]