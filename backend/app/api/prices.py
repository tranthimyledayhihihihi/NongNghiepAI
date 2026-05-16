from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.price import MarketPrice
# Giả định đường dẫn đến model CropType của bạn
from app.models.crop import CropType
from app.services.location_service import location_service
from app.services.pricing_service import pricing_service

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


def _serialize_dt(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _cache_status(updated_at: datetime | None) -> tuple[str, int | None]:
    if not updated_at:
        return "from_db", None
    age_seconds = max(int((datetime.now() - updated_at).total_seconds()), 0)
    if age_seconds <= int(timedelta(minutes=60).total_seconds()):
        return "cached", age_seconds
    return "from_db", age_seconds


@router.get("/current")
def get_current_price(
    crop_name: str | None = Query(default=None),
    crop_id: int | None = Query(default=None),
    region: str | None = Query(default=None),
    region_key: str | None = Query(default=None),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    resolved_region = location_service.resolve_region(db, region_key or region)

    crop = None
    if crop_id:
        crop = db.query(CropType).filter(CropType.CropID == crop_id).first()
    if crop is None and crop_name:
        crop = (
            db.query(CropType)
            .filter(func.lower(CropType.CropName) == crop_name.strip().lower())
            .first()
        )
    if crop is None and not crop_name:
        crop = db.query(CropType).order_by(CropType.CropName).first()
    if crop is None and not crop_name:
        raise HTTPException(status_code=404, detail="crop not found")

    display_crop_name = crop.CropName if crop else crop_name.strip()
    base_query = db.query(MarketPrice)
    if crop:
        base_query = base_query.filter(MarketPrice.CropID == crop.CropID)

    latest = None
    if resolved_region:
        lookup_key = location_service.region_key(resolved_region)
        latest = (
            base_query.filter(func.lower(MarketPrice.Region) == resolved_region.lower())
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .first()
        )
        if latest is None:
            latest = (
                base_query.filter(MarketPrice.Region.ilike(f"%{resolved_region}%"))
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .first()
            )
        if latest is None:
            candidates = base_query.order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt)).limit(100).all()
            latest = next(
                (row for row in candidates if location_service.region_key(row.Region) == lookup_key),
                None,
            )
    if latest is None and not resolved_region:
        latest = base_query.order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt)).first()

    if latest:
        cache_status, age_seconds = _cache_status(latest.UpdatedAt)
        return {
            "crop_id": latest.CropID,
            "crop_name": display_crop_name,
            "region": latest.Region,
            "region_key": location_service.region_key(latest.Region),
            "price": float(latest.PricePerKg),
            "current_price": float(latest.PricePerKg),
            "unit": "VND/kg",
            "source": "database",
            "source_name": latest.SourceName or "MarketPrices DB",
            "source_url": latest.SourceURL,
            "observed_at": _serialize_dt(latest.PriceDate),
            "last_updated": _serialize_dt(latest.UpdatedAt),
            "cache_status": cache_status,
            "cache_age_seconds": age_seconds,
            "confidence": 0.86 if cache_status == "cached" else 0.7,
            "is_realtime": force_refresh and cache_status == "cached",
            "is_mock": False,
        }

    fallback = pricing_service.get_current_price(
        db,
        display_crop_name,
        resolved_region,
        include_weather=False,
    )
    return {
        "crop_id": crop.CropID if crop else None,
        "crop_name": display_crop_name,
        "region": resolved_region,
        "region_key": location_service.region_key(resolved_region),
        "price": float(fallback["current_price"]),
        "current_price": float(fallback["current_price"]),
        "unit": "VND/kg",
        "source": "fallback",
        "source_name": "Pricing fallback",
        "source_url": None,
        "observed_at": _serialize_dt(fallback.get("last_updated")),
        "last_updated": _serialize_dt(fallback.get("last_updated") or datetime.now()),
        "cache_status": "mock",
        "cache_age_seconds": 0,
        "confidence": 0.45,
        "is_realtime": False,
        "is_mock": True,
    }


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
