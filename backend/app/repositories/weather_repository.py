from datetime import date, timedelta

from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.weather import WeatherData


def create_weather_data(db: Session, **data) -> WeatherData:
    temperature = data.pop("temperature", None)
    condition = data.pop("condition", None)
    weather = WeatherData(
        Region=data["region"],
        RecordDate=date.today(),
        TempMin=temperature,
        TempMax=temperature,
        Rainfall=data.get("rainfall"),
        Humidity=data.get("humidity"),
        WeatherDesc=condition,
    )
    try:
        db.add(weather)
        db.commit()
        db.refresh(weather)
    except SQLAlchemyError:
        db.rollback()
    return weather


def get_latest_weather(db: Session, region: str) -> WeatherData | None:
    try:
        today = date.today()
        return (
            db.query(WeatherData)
            .filter(
                WeatherData.Region == region,
                WeatherData.RecordDate <= today,
            )
            .order_by(desc(WeatherData.RecordDate), desc(WeatherData.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None


def get_weather_forecast(db: Session, region: str, days: int = 7) -> list[WeatherData]:
    """Lấy dữ liệu thời tiết từ hôm nay đến N ngày tới từ WeatherData (Open-Meteo)."""
    try:
        today = date.today()
        until = today + timedelta(days=days)
        return (
            db.query(WeatherData)
            .filter(
                WeatherData.Region == region,
                WeatherData.RecordDate >= today,
                WeatherData.RecordDate <= until,
            )
            .order_by(asc(WeatherData.RecordDate))
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []
