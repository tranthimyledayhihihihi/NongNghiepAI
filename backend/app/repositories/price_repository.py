from datetime import date, datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.price import MarketPrice, PriceHistory, PricingRequest
from app.repositories.common import ensure_crop, ensure_user, to_db_grade


def create_market_price(
    db: Session,
    *,
    crop_name: str,
    region: str,
    price: float,
    unit: str = "VND/kg",
    quality_grade: str = "grade_1",
    source: str | None = None,
    collected_at: datetime | None = None,
) -> MarketPrice:
    crop = ensure_crop(db, crop_name)
    timestamp = collected_at or datetime.now()
    market_price = MarketPrice(
        CropID=crop.CropID,
        Region=region,
        PricePerKg=price,
        QualityGrade=to_db_grade(quality_grade),
        MarketType="Bán lẻ",
        SourceName=source,
        PriceDate=timestamp.date(),
        UpdatedAt=timestamp,
    )
    try:
        db.add(market_price)
        db.commit()
        db.refresh(market_price)
    except SQLAlchemyError:
        db.rollback()
    return market_price


def create_pricing_request(
    db: Session,
    *,
    crop_name: str,
    region: str,
    quantity: float,
    quality_grade: str,
    suggested_price: float,
    min_price: float,
    max_price: float,
) -> PricingRequest:
    crop = ensure_crop(db, crop_name)
    user = ensure_user(db, region=region)
    request = PricingRequest(
        UserID=user.UserID,
        CropID=crop.CropID,
        Region=region,
        QuantityKg=quantity,
        QualityGrade=to_db_grade(quality_grade),
        SuggestedPrice=suggested_price,
        MinPrice=min_price,
        MaxPrice=max_price,
    )
    try:
        db.add(request)
        db.commit()
        db.refresh(request)
    except SQLAlchemyError:
        db.rollback()
    return request


def get_latest_price(
    db: Session,
    crop_name: str,
    region: str,
    quality_grade: str | None = None,
) -> MarketPrice | None:
    try:
        crop = ensure_crop(db, crop_name)
        query = db.query(MarketPrice).filter(
            MarketPrice.CropID == crop.CropID,
            MarketPrice.Region == region,
        )
        if quality_grade:
            query = query.filter(MarketPrice.QualityGrade == to_db_grade(quality_grade))
        return query.order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt)).first()
    except SQLAlchemyError:
        db.rollback()
        return None


def get_price_history(db: Session, crop_name: str, region: str, days: int = 30) -> list[PriceHistory]:
    start_date = date.today() - timedelta(days=days)
    try:
        crop = ensure_crop(db, crop_name)
        return (
            db.query(PriceHistory)
            .filter(
                PriceHistory.CropID == crop.CropID,
                PriceHistory.Region == region,
                PriceHistory.RecordDate >= start_date,
            )
            .order_by(PriceHistory.RecordDate)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []


def get_recent_market_prices(db: Session, crop_name: str, region: str, limit: int = 7) -> list[MarketPrice]:
    try:
        crop = ensure_crop(db, crop_name)
        return (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []


def get_latest_prices_by_crop(db: Session, crop_name: str, limit: int = 10) -> list[MarketPrice]:
    try:
        crop = ensure_crop(db, crop_name)
        return (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop.CropID)
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []
