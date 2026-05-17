from datetime import date, timedelta

from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.weather import WeatherData


def upsert_weather_cache(
    db: Session,
    *,
    region: str,
    record_date: date,
    temp_min: float | None = None,
    temp_max: float | None = None,
    rainfall: float | None = None,
    humidity: float | None = None,
    condition: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    wind_speed: float | None = None,
    uv_index: float | None = None,
    pressure: float | None = None,
    weather_code: int | None = None,
    source_name: str | None = "Open-Meteo",
    source_updated_at=None,
) -> WeatherData | None:
    try:
        row = (
            db.query(WeatherData)
            .filter(WeatherData.Region == region, WeatherData.RecordDate == record_date)
            .first()
        )
        if row is None:
            row = WeatherData(Region=region, RecordDate=record_date)
            db.add(row)
        row.TempMin = temp_min
        row.TempMax = temp_max
        row.Rainfall = rainfall
        row.Humidity = humidity
        row.WeatherDesc = condition
        row.Latitude = latitude
        row.Longitude = longitude
        row.WindSpeed = wind_speed
        row.UVIndex = uv_index
        row.Pressure = pressure
        row.WeatherCode = weather_code
        row.SourceName = source_name
        row.SourceUpdatedAt = source_updated_at
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError:
        db.rollback()
        return None


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
