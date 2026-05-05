from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.market import MarketSuggestion
from app.repositories.common import ensure_crop, ensure_user, to_db_channel, to_db_grade
from app.repositories.price_repository import get_latest_prices_by_crop


def create_market_suggestion(
    db: Session,
    *,
    crop_name: str,
    region: str,
    quantity: float,
    quality_grade: str,
    recommended_channel: str,
    estimated_profit: float,
    reason: str,
    warning: str | None,
) -> MarketSuggestion:
    crop = ensure_crop(db, crop_name)
    user = ensure_user(db, region=region)
    suggestion = MarketSuggestion(
        UserID=user.UserID,
        CropID=crop.CropID,
        Region=region,
        QuantityKg=quantity,
        QualityGrade=to_db_grade(quality_grade),
        RecommendedChannel=to_db_channel(recommended_channel),
        EstimatedProfit=estimated_profit,
        Reason=reason,
        Warning=warning,
    )
    try:
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
    except SQLAlchemyError:
        db.rollback()
    return suggestion


__all__ = ["create_market_suggestion", "get_latest_prices_by_crop"]
