from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.market import MarketChannel, MarketSuggestion
from app.repositories.common import ensure_crop, ensure_user, to_db_channel, to_db_grade
from app.repositories.price_repository import get_latest_prices_by_crop


DEFAULT_MARKET_CHANNELS = [
    {"code": "xuat_khau", "name": "Xuất khẩu", "commission": 0.18, "min_qty": 1000, "quality_rank": 3, "price_factor": 1.35},
    {"code": "sieu_thi", "name": "Siêu thị / chuỗi cửa hàng", "commission": 0.12, "min_qty": 200, "quality_rank": 3, "price_factor": 1.20},
    {"code": "cho_dau_moi", "name": "Chợ đầu mối", "commission": 0.07, "min_qty": 100, "quality_rank": 2, "price_factor": 1.05},
    {"code": "thuong_lai", "name": "Thương lái địa phương", "commission": 0.05, "min_qty": 50, "quality_rank": 2, "price_factor": 0.95},
    {"code": "ban_le", "name": "Bán lẻ trực tiếp", "commission": 0.0, "min_qty": 0, "quality_rank": 1, "price_factor": 1.15},
    {"code": "che_bien", "name": "Nhà máy chế biến", "commission": 0.03, "min_qty": 500, "quality_rank": 1, "price_factor": 0.70},
]


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
    user_id: int | None = None,
) -> MarketSuggestion:
    crop = ensure_crop(db, crop_name)
    user = None
    if user_id is not None:
        try:
            from app.models.user import User

            user = db.query(User).filter(User.UserID == user_id).first()
        except SQLAlchemyError:
            db.rollback()
    user = user or ensure_user(db, region=region)
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


def get_market_suggestions_by_user(db: Session, user_id: int, limit: int = 50) -> list[tuple[MarketSuggestion, Crop]]:
    try:
        return (
            db.query(MarketSuggestion, Crop)
            .join(Crop, Crop.CropID == MarketSuggestion.CropID)
            .filter(MarketSuggestion.UserID == user_id)
            .order_by(desc(MarketSuggestion.CreatedAt))
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []


def get_active_channels(db: Session, region: str | None = None) -> list[MarketChannel]:
    try:
        query = db.query(MarketChannel).filter(MarketChannel.IsActive == 1)
        if region:
            query = query.filter((MarketChannel.Region == region) | (MarketChannel.Region.is_(None)))
        return query.order_by(MarketChannel.MinQuantityKg, MarketChannel.ChannelID).all()
    except SQLAlchemyError:
        db.rollback()
        return []


def seed_default_market_channels(db: Session) -> None:
    try:
        for channel in DEFAULT_MARKET_CHANNELS:
            row = db.query(MarketChannel).filter(MarketChannel.ChannelCode == channel["code"]).first()
            if row is None:
                row = MarketChannel(ChannelCode=channel["code"])
                db.add(row)
            row.ChannelName = channel["name"]
            row.CommissionRate = channel["commission"]
            row.MinQuantityKg = channel["min_qty"]
            row.RequiredQualityRank = channel["quality_rank"]
            row.PriceFactor = channel["price_factor"]
            row.Region = None
            row.IsActive = 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()


__all__ = [
    "DEFAULT_MARKET_CHANNELS",
    "create_market_suggestion",
    "get_active_channels",
    "get_latest_prices_by_crop",
    "get_market_suggestions_by_user",
    "seed_default_market_channels",
]
