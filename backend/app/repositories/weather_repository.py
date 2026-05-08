from datetime import date, datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.weather import (
    WeatherAlert,
    WeatherData,
    WeatherForecast,
    WeatherLocation,
    WeatherObservation,
    WeatherRecommendation,
)


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
        UVIndex=data.get("uv_index"),
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
        weather.UVIndex = data.get("uv_index")
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


def upsert_weather_location(db: Session, **data) -> WeatherLocation | None:
    try:
        region = data["region"]
        location = db.query(WeatherLocation).filter(WeatherLocation.Region == region).first()
        if location is None:
            location = WeatherLocation(Region=region)
            db.add(location)

        location.Province = data.get("province") or location.Province or region
        location.District = data.get("district")
        location.Ward = data.get("ward")
        location.Latitude = data.get("latitude", location.Latitude)
        location.Longitude = data.get("longitude", location.Longitude)
        location.IsDefault = bool(data.get("is_default", location.IsDefault))
        db.commit()
        db.refresh(location)
        return location
    except SQLAlchemyError:
        db.rollback()
        return None


def create_weather_observation(db: Session, **data) -> WeatherObservation | None:
    try:
        observed_at = data.get("source_updated_at") or data.get("observed_at") or datetime.now()
        row = WeatherObservation(
            LocationID=data.get("location_id"),
            Region=data["region"],
            ObservedAt=observed_at,
            Temperature=data.get("temperature"),
            Humidity=data.get("humidity"),
            Rainfall=data.get("rainfall"),
            WindSpeed=data.get("wind_speed"),
            UVIndex=data.get("uv_index"),
            Pressure=data.get("pressure"),
            WeatherCode=data.get("weather_code"),
            WeatherDesc=data.get("condition"),
            SourceName=data.get("source_name"),
            SourceUpdatedAt=data.get("source_updated_at"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError:
        db.rollback()
        return None


def upsert_weather_forecast(db: Session, **data) -> WeatherForecast | None:
    try:
        forecast_date = data.get("forecast_date")
        if forecast_date is None:
            raw_date = data.get("date")
            forecast_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date
        forecast_at = data.get("forecast_at")
        forecast_type = data.get("forecast_type", "daily")

        query = db.query(WeatherForecast).filter(
            WeatherForecast.Region == data["region"],
            WeatherForecast.ForecastDate == forecast_date,
            WeatherForecast.ForecastType == forecast_type,
        )
        if forecast_at is None:
            query = query.filter(WeatherForecast.ForecastAt.is_(None))
        else:
            query = query.filter(WeatherForecast.ForecastAt == forecast_at)

        row = query.first()
        if row is None:
            row = WeatherForecast(
                Region=data["region"],
                ForecastDate=forecast_date,
                ForecastAt=forecast_at,
                ForecastType=forecast_type,
            )
            db.add(row)

        row.TempMin = data.get("temp_min")
        row.TempMax = data.get("temp_max")
        row.Temperature = data.get("temperature")
        row.Humidity = data.get("humidity")
        row.Rainfall = data.get("rainfall")
        row.RainProbability = data.get("rain_probability")
        row.WindSpeed = data.get("wind_speed")
        row.UVIndex = data.get("uv_index")
        row.WeatherCode = data.get("weather_code")
        row.WeatherDesc = data.get("condition")
        row.Recommendation = data.get("recommendation")
        row.SourceName = data.get("source_name")
        row.SourceUpdatedAt = data.get("source_updated_at") or datetime.now()
        db.commit()
        db.refresh(row)
        return row
    except (SQLAlchemyError, ValueError):
        db.rollback()
        return None


def list_weather_forecasts(
    db: Session,
    region: str,
    start_date: date,
    end_date: date,
    forecast_type: str = "daily",
) -> list[WeatherForecast]:
    try:
        return (
            db.query(WeatherForecast)
            .filter(
                WeatherForecast.Region == region,
                WeatherForecast.ForecastDate >= start_date,
                WeatherForecast.ForecastDate <= end_date,
                WeatherForecast.ForecastType == forecast_type,
            )
            .order_by(WeatherForecast.ForecastDate, WeatherForecast.ForecastAt)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        return []


def upsert_weather_alert(db: Session, **data) -> WeatherAlert | None:
    try:
        dedup_key = data.get("dedup_key")
        row = None
        if dedup_key:
            row = db.query(WeatherAlert).filter(WeatherAlert.DedupKey == dedup_key).first()
        if row is None:
            row = WeatherAlert(
                Region=data["region"],
                AlertType=data["alert_type"],
                DedupKey=dedup_key,
            )
            db.add(row)

        row.Severity = data.get("severity", "medium")
        row.Title = data.get("title", "")
        row.Message = data.get("message", "")
        row.Recommendation = data.get("recommendation")
        row.TriggerValue = data.get("trigger_value")
        row.TriggerUnit = data.get("trigger_unit")
        row.ForecastDate = data.get("forecast_date")
        row.Source = data.get("source", "rule")
        row.IsActive = bool(data.get("is_active", True))
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError:
        db.rollback()
        return None


def upsert_weather_recommendation(db: Session, **data) -> WeatherRecommendation | None:
    try:
        recommendation_date = data.get("recommendation_date") or date.today()
        row = (
            db.query(WeatherRecommendation)
            .filter(
                WeatherRecommendation.Region == data["region"],
                WeatherRecommendation.RecommendationDate == recommendation_date,
                WeatherRecommendation.ActionType == data["action_type"],
                WeatherRecommendation.CropName == data.get("crop_name"),
                WeatherRecommendation.GrowthStage == data.get("growth_stage"),
            )
            .first()
        )
        if row is None:
            row = WeatherRecommendation(
                Region=data["region"],
                RecommendationDate=recommendation_date,
                ActionType=data["action_type"],
            )
            db.add(row)

        row.CropName = data.get("crop_name")
        row.GrowthStage = data.get("growth_stage")
        row.Decision = data.get("decision", "")
        row.Reason = data.get("reason", "")
        row.Timing = data.get("timing")
        row.Priority = data.get("priority", "medium")
        row.Source = data.get("source", "rule")
        db.commit()
        db.refresh(row)
        return row
    except SQLAlchemyError:
        db.rollback()
        return None
