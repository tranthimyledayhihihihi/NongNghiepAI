from datetime import date, datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.weather import WeatherData


def create_weather_data(db: Session, **data) -> WeatherData:
    temperature = data.get("temperature")
    condition = data.get("condition")
    source_updated_at = data.get("source_updated_at")
    record_date = data.get("record_date")
    if record_date is None:
        record_date = source_updated_at.date() if isinstance(source_updated_at, datetime) else date.today()
    weather = WeatherData(
        Region=data["region"],
        RecordDate=record_date,
        TempMin=data.get("temp_min", temperature),
        TempMax=data.get("temp_max", temperature),
        Rainfall=data.get("rainfall"),
        Humidity=data.get("humidity"),
        WeatherDesc=condition,
        Latitude=data.get("latitude"),
        Longitude=data.get("longitude"),
        WindSpeed=data.get("wind_speed"),
        Pressure=data.get("pressure"),
        WeatherCode=data.get("weather_code"),
        SourceName=data.get("source_name"),
        SourceUpdatedAt=source_updated_at,
    )
    try:
        db.add(weather)
        db.commit()
        db.refresh(weather)
    except SQLAlchemyError:
        db.rollback()
    return weather


def upsert_current_weather(db: Session, **data) -> WeatherData | None:
    source_updated_at = data.get("source_updated_at")
    record_date = data.get("record_date")
    if record_date is None:
        record_date = source_updated_at.date() if isinstance(source_updated_at, datetime) else date.today()

    try:
        weather = (
            db.query(WeatherData)
            .filter(WeatherData.Region == data["region"], WeatherData.RecordDate == record_date)
            .first()
        )
        if weather is None:
            weather = WeatherData(Region=data["region"], RecordDate=record_date)
            db.add(weather)

        temperature = data.get("temperature")
        weather.TempMin = data.get("temp_min", temperature)
        weather.TempMax = data.get("temp_max", temperature)
        weather.Rainfall = data.get("rainfall")
        weather.Humidity = data.get("humidity")
        weather.WeatherDesc = data.get("condition")
        weather.Latitude = data.get("latitude")
        weather.Longitude = data.get("longitude")
        weather.WindSpeed = data.get("wind_speed")
        weather.Pressure = data.get("pressure")
        weather.WeatherCode = data.get("weather_code")
        weather.SourceName = data.get("source_name")
        weather.SourceUpdatedAt = source_updated_at
        db.commit()
        db.refresh(weather)
        return weather
    except SQLAlchemyError:
        db.rollback()
        return None


def get_latest_weather(db: Session, region: str) -> WeatherData | None:
    try:
        return (
            db.query(WeatherData)
            .filter(WeatherData.Region == region)
            .order_by(desc(WeatherData.RecordDate), desc(WeatherData.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None


def get_latest_by_region(db: Session, region: str) -> WeatherData | None:
    return get_latest_weather(db, region)


def list_forecast_by_region_date_range(
    db: Session,
    region: str,
    start_date: date,
    end_date: date,
) -> list[WeatherData]:
    try:
        return (
            db.query(WeatherData)
            .filter(
                WeatherData.Region == region,
                WeatherData.RecordDate >= start_date,
                WeatherData.RecordDate <= end_date,
            )
            .order_by(WeatherData.RecordDate)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []
