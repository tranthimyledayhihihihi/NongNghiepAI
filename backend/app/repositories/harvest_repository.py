from datetime import date

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.harvest import HarvestForecast, HarvestSchedule
from app.repositories.common import ensure_crop, ensure_user


def create_harvest_forecast(
    db: Session,
    *,
    crop_name: str,
    region: str,
    planting_date: date,
    expected_harvest_date: date,
    confidence: float,
    warning: str | None,
    recommendation: str,
) -> HarvestForecast:
    crop = ensure_crop(db, crop_name)
    user = ensure_user(db, region=region)
    schedule = HarvestSchedule(
        UserID=user.UserID,
        CropID=crop.CropID,
        PlantingDate=planting_date,
        Region=region,
        ExpectedHarvestDate=expected_harvest_date,
        Status="Đang trồng",
        Notes=recommendation,
    )
    forecast = HarvestForecast(
        ScheduleID=1,
        ExpectedHarvestDate=expected_harvest_date,
        ConfidenceScore=confidence,
        WeatherWarning=warning,
        LaborRecommendation=recommendation,
        TransportRecommendation="Chuẩn bị phương tiện vận chuyển trước ngày thu hoạch.",
        ModelVersion="mock-v1",
    )
    try:
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        forecast.ScheduleID = schedule.ScheduleID
        db.add(forecast)
        db.commit()
        db.refresh(forecast)
    except SQLAlchemyError:
        db.rollback()
    return forecast


def get_harvest_forecasts(
    db: Session,
    crop_name: str | None = None,
    region: str | None = None,
    limit: int = 20,
) -> list[HarvestForecast]:
    try:
        query = db.query(HarvestForecast).join(
            HarvestSchedule,
            HarvestSchedule.ScheduleID == HarvestForecast.ScheduleID,
        )
        if region:
            query = query.filter(HarvestSchedule.Region == region)
        if crop_name:
            crop = ensure_crop(db, crop_name)
            query = query.filter(HarvestSchedule.CropID == crop.CropID)
        return query.order_by(desc(HarvestForecast.GeneratedAt)).limit(limit).all()
    except SQLAlchemyError:
        db.rollback()
        return []


def get_harvest_schedules_by_user(db: Session, user_id: int, limit: int = 50) -> list[tuple[HarvestSchedule, Crop]]:
    try:
        return (
            db.query(HarvestSchedule, Crop)
            .join(Crop, Crop.CropID == HarvestSchedule.CropID)
            .filter(HarvestSchedule.UserID == user_id)
            .order_by(desc(HarvestSchedule.CreatedAt))
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []


def get_harvest_forecast_history(
    db: Session,
    user_id: int,
    limit: int = 50,
) -> list[tuple[HarvestForecast, HarvestSchedule, Crop]]:
    try:
        return (
            db.query(HarvestForecast, HarvestSchedule, Crop)
            .join(HarvestSchedule, HarvestSchedule.ScheduleID == HarvestForecast.ScheduleID)
            .join(Crop, Crop.CropID == HarvestSchedule.CropID)
            .filter(HarvestSchedule.UserID == user_id)
            .order_by(desc(HarvestForecast.GeneratedAt))
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []
