import random
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.integrations.weather_client import WeatherClient, WeatherProviderError
from app.repositories.weather_repository import (
    create_weather_data,
    get_latest_by_region,
    upsert_current_weather,
)
from app.schemas.weather_schema import WeatherCreateRequest


MOCK_WEATHER = {
    "default": {"temperature": 28.0, "temp_min": 22, "temp_max": 32, "humidity": 75.0, "rainfall": 5.0, "sunshine_hours": 7, "condition": "partly_cloudy"},
    "Ha Noi": {"temperature": 30.0, "temp_min": 24, "temp_max": 34, "humidity": 80.0, "rainfall": 3.0, "sunshine_hours": 6, "condition": "cloudy"},
    "TP.HCM": {"temperature": 32.0, "temp_min": 25, "temp_max": 36, "humidity": 70.0, "rainfall": 0.0, "sunshine_hours": 9, "condition": "sunny"},
    "Da Nang": {"temperature": 29.0, "temp_min": 23, "temp_max": 33, "humidity": 78.0, "rainfall": 8.0, "sunshine_hours": 7, "condition": "rainy"},
    "Can Tho": {"temperature": 31.0, "temp_min": 24, "temp_max": 35, "humidity": 82.0, "rainfall": 10.0, "sunshine_hours": 6, "condition": "rainy"},
    "Lam Dong": {"temperature": 20.0, "temp_min": 15, "temp_max": 24, "humidity": 85.0, "rainfall": 15.0, "sunshine_hours": 5, "condition": "foggy"},
}

ALERT_THRESHOLDS = {
    "temp_max_high": 35,
    "temp_min_cold": 12,
    "rainfall_heavy": 100,
    "humidity_high": 92,
    "humidity_low": 30,
}


class WeatherService:
    def __init__(self, weather_client: WeatherClient | None = None):
        self.weather_client = weather_client or WeatherClient()

    def get_current_weather(self, db: Session, region: str, force_refresh: bool = False) -> dict:
        cache_key = f"weather:current:{region}"
        if not force_refresh:
            cached = redis_client.get(cache_key)
            if cached:
                cached["cache_status"] = "hit"
                cached["is_realtime"] = False
                return cached

        latest = get_latest_by_region(db, region)
        if latest and not force_refresh and self._is_recent(latest):
            result = self._from_weather_row(latest, source="database", cache_status="db_fresh")
            redis_client.set(cache_key, self._cache_payload(result), expire=settings.WEATHER_CACHE_TTL_SECONDS)
            return result

        if settings.WEATHER_PROVIDER.lower() != "mock":
            try:
                external = self.weather_client.get_current(region)
                saved = upsert_current_weather(db, **external)
                result = self._from_payload(
                    external,
                    recorded_at=getattr(saved, "CreatedAt", None) if saved else datetime.now(),
                    source="api",
                    cache_status="miss",
                    is_realtime=True,
                    is_mock=False,
                )
                redis_client.set(cache_key, self._cache_payload(result), expire=settings.WEATHER_CACHE_TTL_SECONDS)
                return result
            except WeatherProviderError:
                pass

        if latest:
            return self._from_weather_row(latest, source="database", cache_status="db_stale")

        return self._mock_current_weather(region)

    def create_weather(self, db: Session, request: WeatherCreateRequest) -> dict:
        now = datetime.now()
        weather = create_weather_data(
            db,
            **request.model_dump(),
            source_name="manual",
            source_updated_at=now,
        )
        return {
            "region": request.region,
            "temperature": request.temperature,
            "rainfall": request.rainfall,
            "humidity": request.humidity,
            "condition": request.condition,
            "recorded_at": getattr(weather, "recorded_at", None) or now,
            "source": "manual",
            "source_name": "manual",
            "is_realtime": False,
            "is_mock": False,
            "last_updated": now,
            "data_age_minutes": 0,
            "cache_status": "manual",
        }

    def get_forecast(self, _db: Session, region: str, days: int = 7) -> list[dict]:
        cache_key = f"weather:forecast:{region}:{days}"
        cached = redis_client.get(cache_key)
        if cached:
            return [{**item, "cache_status": "hit", "is_realtime": False} for item in cached]

        if settings.WEATHER_PROVIDER.lower() != "mock":
            try:
                forecast = self.weather_client.get_forecast(region, days)
                redis_client.set(cache_key, self._cache_forecast(forecast), expire=settings.WEATHER_CACHE_TTL_SECONDS)
                return forecast
            except WeatherProviderError:
                pass

        base = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        result = []
        for i in range(1, days + 1):
            dt = (date.today() + timedelta(days=i)).isoformat()
            variation = random.uniform(-2, 2)
            rain = max(0.0, base["rainfall"] + random.uniform(-5, 10))
            hum = min(100.0, max(30.0, base["humidity"] + random.uniform(-5, 5)))
            temp = base["temperature"] + variation
            result.append({
                "date": dt,
                "temperature": round(temp, 1),
                "temp_min": round(base["temp_min"] + variation, 1),
                "temp_max": round(base["temp_max"] + variation, 1),
                "humidity": round(hum, 1),
                "rainfall": round(rain, 1),
                "condition": base["condition"],
                "warnings": self._analyze_warnings(temp, base["temp_min"] + variation, rain, hum),
                "source": "mock",
                "source_name": "Mock Weather",
                "is_mock": True,
                "is_realtime": False,
                "cache_status": "mock",
                "last_updated": datetime.now(),
            })
        return result

    def get_harvest_weather_warning(self, db: Session, region: str) -> str | None:
        w = self.get_current_weather(db, region)
        warnings = self._analyze_warnings(
            w.get("temperature") or 28,
            w.get("temperature") or 22,
            w.get("rainfall") or 0,
            w.get("humidity") or 70,
        )
        return " | ".join(warnings) if warnings else None

    def _from_weather_row(self, weather: Any, source: str, cache_status: str) -> dict:
        last_updated = getattr(weather, "SourceUpdatedAt", None) or getattr(weather, "CreatedAt", None) or datetime.now()
        return {
            "region": getattr(weather, "Region", None),
            "temperature": getattr(weather, "temperature", None),
            "rainfall": getattr(weather, "Rainfall", None),
            "humidity": getattr(weather, "Humidity", None),
            "condition": getattr(weather, "WeatherDesc", None),
            "wind_speed": getattr(weather, "WindSpeed", None),
            "pressure": getattr(weather, "Pressure", None),
            "weather_code": getattr(weather, "WeatherCode", None),
            "latitude": getattr(weather, "Latitude", None),
            "longitude": getattr(weather, "Longitude", None),
            "recorded_at": getattr(weather, "CreatedAt", None) or last_updated,
            "source": source,
            "source_name": getattr(weather, "SourceName", None) or source,
            "source_url": None,
            "is_realtime": False,
            "is_mock": False,
            "last_updated": last_updated,
            "data_age_minutes": self._age_minutes(last_updated),
            "cache_status": cache_status,
        }

    def _from_payload(
        self,
        payload: dict,
        recorded_at: datetime,
        source: str,
        cache_status: str,
        is_realtime: bool,
        is_mock: bool,
    ) -> dict:
        last_updated = payload.get("source_updated_at") or recorded_at
        return {
            "region": payload.get("region"),
            "temperature": payload.get("temperature"),
            "rainfall": payload.get("rainfall"),
            "humidity": payload.get("humidity"),
            "condition": payload.get("condition"),
            "wind_speed": payload.get("wind_speed"),
            "pressure": payload.get("pressure"),
            "weather_code": payload.get("weather_code"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "recorded_at": recorded_at,
            "source": source,
            "source_name": payload.get("source_name") or source,
            "source_url": payload.get("source_url"),
            "is_realtime": is_realtime,
            "is_mock": is_mock,
            "last_updated": last_updated,
            "data_age_minutes": self._age_minutes(last_updated),
            "cache_status": cache_status,
        }

    def _mock_current_weather(self, region: str) -> dict:
        now = datetime.now()
        mock = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        return {
            "region": region,
            "temperature": mock["temperature"],
            "rainfall": mock["rainfall"],
            "humidity": mock["humidity"],
            "condition": mock["condition"],
            "recorded_at": now,
            "source": "mock",
            "source_name": "Mock Weather",
            "source_url": None,
            "is_realtime": False,
            "is_mock": True,
            "last_updated": now,
            "data_age_minutes": 0,
            "cache_status": "mock",
        }

    @staticmethod
    def _cache_payload(result: dict) -> dict:
        payload = result.copy()
        payload["is_realtime"] = False
        payload["cache_status"] = "hit"
        for key in ("recorded_at", "last_updated"):
            value = payload.get(key)
            if hasattr(value, "isoformat"):
                payload[key] = value.isoformat()
        return payload

    @staticmethod
    def _cache_forecast(forecast: list[dict]) -> list[dict]:
        cached = []
        for item in forecast:
            payload = item.copy()
            payload["cache_status"] = "hit"
            payload["is_realtime"] = False
            value = payload.get("last_updated")
            if hasattr(value, "isoformat"):
                payload["last_updated"] = value.isoformat()
            cached.append(payload)
        return cached

    @staticmethod
    def _age_minutes(value: datetime | None) -> int | None:
        if value is None:
            return None
        return max(int((datetime.now() - value.replace(tzinfo=None)).total_seconds() // 60), 0)

    def _is_recent(self, weather: Any) -> bool:
        updated_at = getattr(weather, "SourceUpdatedAt", None) or getattr(weather, "CreatedAt", None)
        age = self._age_minutes(updated_at)
        return age is not None and age * 60 <= settings.WEATHER_CACHE_TTL_SECONDS

    @staticmethod
    def _analyze_warnings(temp_max: float, temp_min: float, rainfall: float, humidity: float) -> list[str]:
        warnings = []
        if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            warnings.append(f"Nang nong ({temp_max:.0f}C) - tang tuoi nuoc.")
        if temp_min < ALERT_THRESHOLDS["temp_min_cold"]:
            warnings.append(f"Lanh ({temp_min:.0f}C) - nguy co suong muoi.")
        if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
            warnings.append(f"Mua lon ({rainfall:.0f}mm) - kiem tra thoat nuoc.")
        if humidity > ALERT_THRESHOLDS["humidity_high"]:
            warnings.append(f"Do am cao ({humidity:.0f}%) - nguy co nam benh.")
        if humidity < ALERT_THRESHOLDS["humidity_low"]:
            warnings.append(f"Do am thap ({humidity:.0f}%) - tang tuoi.")
        return warnings


weather_service = WeatherService()
