from datetime import date, datetime, timedelta

from sqlalchemy import desc, func
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
    source_url: str | None = None,
    collected_at: datetime | None = None,
    price_date: date | None = None,
    market_type: str = "BĂ¡n láº»",
) -> MarketPrice:
    crop = ensure_crop(db, crop_name)
    timestamp = collected_at or datetime.now()
    market_price = MarketPrice(
        CropID=crop.CropID,
        Region=region,
        PricePerKg=price,
        QualityGrade=to_db_grade(quality_grade),
        MarketType=market_type,
        SourceName=source,
        SourceURL=source_url,
        PriceDate=timestamp.date(),
        CollectedAt=timestamp,
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


def get_latest_market_price(
    db: Session,
    crop_name: str,
    region: str,
    quality_grade: str | None = None,
) -> MarketPrice | None:
    return get_latest_price(db, crop_name, region, quality_grade)


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


def get_price_history_range(
    db: Session,
    crop_name: str,
    region: str,
    start_date: date,
    end_date: date,
) -> list[PriceHistory]:
    try:
        crop = ensure_crop(db, crop_name)
        return (
            db.query(PriceHistory)
            .filter(
                PriceHistory.CropID == crop.CropID,
                PriceHistory.Region == region,
                PriceHistory.RecordDate >= start_date,
                PriceHistory.RecordDate <= end_date,
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


def bulk_upsert_market_prices(db: Session, records: list[dict]) -> dict:
    saved = 0
    updated = 0
    errors: list[str] = []
    touched_history: set[tuple[int, str, date]] = set()

    for index, record in enumerate(records, start=1):
        try:
            crop = ensure_crop(db, record["crop_name"])
            record_date = record.get("price_date") or date.today()
            if isinstance(record_date, datetime):
                record_date = record_date.date()
            quality_grade = to_db_grade(record.get("quality_grade"))
            source_name = record.get("source_name") or record.get("source") or "manual"
            source_url = record.get("source_url")
            market_type = record.get("market_type") or "BĂ¡n láº»"
            timestamp = record.get("collected_at") or datetime.now()

            query = db.query(MarketPrice).filter(
                MarketPrice.CropID == crop.CropID,
                MarketPrice.Region == record["region"],
                MarketPrice.QualityGrade == quality_grade,
                MarketPrice.MarketType == market_type,
                MarketPrice.PriceDate == record_date,
            )
            if source_name:
                query = query.filter(MarketPrice.SourceName == source_name)
            else:
                query = query.filter(MarketPrice.SourceName.is_(None))

            market_price = query.first()
            if market_price is None:
                market_price = MarketPrice(
                    CropID=crop.CropID,
                    Region=record["region"],
                    QualityGrade=quality_grade,
                    MarketType=market_type,
                    PriceDate=record_date,
                )
                db.add(market_price)
                saved += 1
            else:
                updated += 1

            market_price.PricePerKg = float(record["price"])
            market_price.SourceName = source_name
            market_price.SourceURL = source_url
            market_price.CollectedAt = timestamp
            market_price.ConfidenceScore = record.get("confidence_score")
            market_price.IsRealtime = bool(record.get("is_realtime", False))
            market_price.IsScraped = bool(record.get("is_scraped", bool(source_url)))
            market_price.RawPayloadHash = record.get("raw_payload_hash")
            market_price.RawPayload = record.get("raw_payload")
            market_price.UpdatedAt = timestamp
            touched_history.add((crop.CropID, record["region"], record_date))
        except Exception as exc:
            errors.append(f"record {index}: {exc}")

    try:
        db.commit()
        for crop_id, region, record_date in touched_history:
            _upsert_price_history(db, crop_id, region, record_date)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        errors.append(str(exc))

    return {
        "records_saved": saved,
        "records_updated": updated,
        "errors": errors,
    }


def _upsert_price_history(db: Session, crop_id: int, region: str, record_date: date) -> None:
    stats = (
        db.query(
            func.avg(MarketPrice.PricePerKg),
            func.min(MarketPrice.PricePerKg),
            func.max(MarketPrice.PricePerKg),
            func.count(MarketPrice.PriceID),
        )
        .filter(
            MarketPrice.CropID == crop_id,
            MarketPrice.Region == region,
            MarketPrice.PriceDate == record_date,
        )
        .one()
    )
    if stats[0] is None:
        return

    history = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.CropID == crop_id,
            PriceHistory.Region == region,
            PriceHistory.RecordDate == record_date,
        )
        .first()
    )
    if history is None:
        history = PriceHistory(CropID=crop_id, Region=region, RecordDate=record_date)
        db.add(history)

    history.AvgPrice = float(stats[0])
    history.MinPrice = float(stats[1])
    history.MaxPrice = float(stats[2])
    history.Volume = float(stats[3] or 0)
