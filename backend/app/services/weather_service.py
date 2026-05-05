from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.weather_repository import create_weather_data, get_latest_weather
from app.schemas.weather_schema import WeatherCreateRequest


class WeatherService:
    def get_current_weather(self, db: Session, region: str) -> dict:
        weather = get_latest_weather(db, region)
        if weather:
            return {
                "region": weather.region,
                "temperature": weather.temperature,
                "rainfall": weather.rainfall,
                "humidity": weather.humidity,
                "condition": weather.condition,
                "recorded_at": weather.recorded_at,
            }

        return {
            "region": region,
            "temperature": 30.0,
            "rainfall": 2.5,
            "humidity": 78.0,
            "condition": "partly_cloudy",
            "recorded_at": datetime.now(),
        }

    def create_weather(self, db: Session, request: WeatherCreateRequest) -> dict:
        weather = create_weather_data(db, **request.model_dump())
        return {
            "region": request.region,
            "temperature": request.temperature,
            "rainfall": request.rainfall,
            "humidity": request.humidity,
            "condition": request.condition,
            "recorded_at": getattr(weather, "recorded_at", None) or datetime.now(),
        }


weather_service = WeatherService()
