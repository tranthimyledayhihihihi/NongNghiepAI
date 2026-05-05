from datetime import date

from sqlalchemy import desc
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
        return (
            db.query(WeatherData)
            .filter(WeatherData.Region == region)
            .order_by(desc(WeatherData.RecordDate), desc(WeatherData.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None
