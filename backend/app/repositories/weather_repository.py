from datetime import date, datetime, timedelta

from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.weather import WeatherData, WeatherObservation


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
    """Return the latest non-future daily weather row for a region."""
    try:
        today = date.today()
        return (
            db.query(WeatherData)
            .filter(WeatherData.Region == region, WeatherData.RecordDate <= today)
            .order_by(desc(WeatherData.RecordDate), desc(WeatherData.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None


def get_weather_for_date(db: Session, region: str, record_date: date) -> WeatherData | None:
    try:
        return (
            db.query(WeatherData)
            .filter(WeatherData.Region == region, WeatherData.RecordDate == record_date)
            .order_by(desc(WeatherData.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None


def get_weather_forecast(db: Session, region: str, days: int = 7) -> list[WeatherData]:
    """Read daily weather rows from today through the requested forecast window."""
    try:
        today = date.today()
        until = today + timedelta(days=max(days, 1) - 1)
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


def get_latest_observation(db: Session, region: str) -> WeatherObservation | None:
    try:
        return (
            db.query(WeatherObservation)
            .filter(WeatherObservation.Region == region)
            .order_by(desc(WeatherObservation.ObservedAt), desc(WeatherObservation.CreatedAt))
            .first()
        )
    except SQLAlchemyError:
        db.rollback()
        return None


def delete_weather_cache(
    db: Session,
    region: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """Delete cached daily and current weather rows for a region."""
    try:
        data_query = db.query(WeatherData).filter(WeatherData.Region == region)
        if start_date is not None:
            data_query = data_query.filter(WeatherData.RecordDate >= start_date)
        if end_date is not None:
            data_query = data_query.filter(WeatherData.RecordDate <= end_date)

        observation_query = db.query(WeatherObservation).filter(WeatherObservation.Region == region)
        if start_date is not None:
            observation_query = observation_query.filter(
                WeatherObservation.ObservedAt >= datetime.combine(start_date, datetime.min.time())
            )
        if end_date is not None:
            observation_query = observation_query.filter(
                WeatherObservation.ObservedAt <= datetime.combine(end_date, datetime.max.time())
            )

        deleted_data = data_query.delete(synchronize_session=False)
        deleted_observations = observation_query.delete(synchronize_session=False)
        db.commit()
        db.expunge_all()
        return {"weather_data": deleted_data, "observations": deleted_observations}
    except SQLAlchemyError:
        db.rollback()
        return {"weather_data": 0, "observations": 0}


def upsert_weather_data_rows(db: Session, rows: list[dict]) -> int:
    """Insert or update daily WeatherData rows fetched from Open-Meteo."""
    saved = 0
    try:
        for row in rows:
            region = row.get("region")
            record_date = row.get("record_date")
            if not region or not record_date:
                continue

            existing = (
                db.query(WeatherData)
                .filter(WeatherData.Region == region, WeatherData.RecordDate == record_date)
                .first()
            )
            if existing is None:
                existing = WeatherData(Region=region, RecordDate=record_date)
                db.add(existing)

            existing.TempMin = row.get("temp_min")
            existing.TempMax = row.get("temp_max")
            existing.Humidity = row.get("humidity")
            existing.Rainfall = row.get("rainfall")
            existing.SunshineHours = row.get("sunshine_hours")
            existing.WeatherDesc = row.get("weather_desc")
            existing.Latitude = row.get("latitude")
            existing.Longitude = row.get("longitude")
            existing.WindSpeed = row.get("wind_speed")
            existing.UVIndex = row.get("uv_index")
            existing.Pressure = row.get("pressure")
            existing.WeatherCode = row.get("weather_code")
            existing.SourceName = row.get("source_name")
            existing.SourceUpdatedAt = row.get("source_updated_at")
            saved += 1

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return 0
    return saved


def create_weather_observation(db: Session, row: dict) -> WeatherObservation | None:
    """Store the latest current-condition observation from Open-Meteo."""
    try:
        observation = WeatherObservation(
            Region=row["region"],
            ObservedAt=row["observed_at"],
            Temperature=row.get("temperature"),
            Humidity=row.get("humidity"),
            Rainfall=row.get("rainfall"),
            WindSpeed=row.get("wind_speed"),
            UVIndex=row.get("uv_index"),
            Pressure=row.get("pressure"),
            WeatherCode=row.get("weather_code"),
            WeatherDesc=row.get("weather_desc"),
            SourceName=row.get("source_name"),
            SourceUpdatedAt=row.get("source_updated_at"),
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)
        return observation
    except SQLAlchemyError:
        db.rollback()
        return None
