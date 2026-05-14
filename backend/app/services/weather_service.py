from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.weather_client import WeatherClient, WeatherProviderError, normalize_location_key
from app.repositories.weather_repository import (
    create_weather_data,
    create_weather_observation,
    delete_weather_cache,
    get_latest_observation,
    get_latest_weather,
    get_weather_for_date,
    get_weather_forecast,
    upsert_weather_data_rows,
)
from app.schemas.weather_schema import WeatherCreateRequest


REGION_NORMALIZE = {
    "ha noi": "Hà Nội",
    "hanoi": "Hà Nội",
    "tp hcm": "TP.HCM",
    "tp.hcm": "TP.HCM",
    "tphcm": "TP.HCM",
    "hcm": "TP.HCM",
    "ho chi minh": "TP.HCM",
    "sai gon": "TP.HCM",
    "saigon": "TP.HCM",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
    "can tho": "Cần Thơ",
    "cantho": "Cần Thơ",
    "dak lak": "Đắk Lắk",
    "daklak": "Đắk Lắk",
    "lam dong": "Lâm Đồng",
    "lamdong": "Lâm Đồng",
    "hai phong": "Hải Phòng",
    "haiphong": "Hải Phòng",
    "gia lai": "Gia Lai",
    "tien giang": "Tiền Giang",
    "tiengiang": "Tiền Giang",
    "long an": "Long An",
    "longan": "Long An",
    "binh thuan": "Bình Thuận",
    "binhthuan": "Bình Thuận",
}


MOCK_WEATHER = {
    "default": {
        "temperature": 28.0,
        "temp_min": 23.0,
        "temp_max": 32.0,
        "humidity": 75.0,
        "rainfall": 4.0,
        "wind_speed": 8.0,
        "uv_index": 6.0,
        "condition": "partly_cloudy",
        "weather_desc": "Có mây",
    },
    "Hà Nội": {
        "temperature": 30.0,
        "temp_min": 25.0,
        "temp_max": 34.0,
        "humidity": 80.0,
        "rainfall": 3.0,
        "wind_speed": 9.0,
        "uv_index": 7.0,
        "condition": "cloudy",
        "weather_desc": "Nhiều mây",
    },
    "TP.HCM": {
        "temperature": 32.0,
        "temp_min": 26.0,
        "temp_max": 35.0,
        "humidity": 72.0,
        "rainfall": 1.0,
        "wind_speed": 10.0,
        "uv_index": 8.0,
        "condition": "mostly_clear",
        "weather_desc": "Ít mây",
    },
    "Đà Nẵng": {
        "temperature": 29.0,
        "temp_min": 24.0,
        "temp_max": 33.0,
        "humidity": 78.0,
        "rainfall": 7.0,
        "wind_speed": 12.0,
        "uv_index": 7.0,
        "condition": "rainy",
        "weather_desc": "Mưa vừa",
    },
    "Cần Thơ": {
        "temperature": 31.0,
        "temp_min": 25.0,
        "temp_max": 34.0,
        "humidity": 82.0,
        "rainfall": 9.0,
        "wind_speed": 8.0,
        "uv_index": 7.0,
        "condition": "rain_showers",
        "weather_desc": "Mưa rào",
    },
    "Lâm Đồng": {
        "temperature": 20.0,
        "temp_min": 16.0,
        "temp_max": 25.0,
        "humidity": 86.0,
        "rainfall": 12.0,
        "wind_speed": 7.0,
        "uv_index": 5.0,
        "condition": "foggy",
        "weather_desc": "Sương mù",
    },
}


ALERT_THRESHOLDS = {
    "temp_max_high": 35,
    "temp_min_cold": 12,
    "rainfall_heavy": 50,
    "humidity_high": 92,
    "humidity_low": 30,
    "wind_high": 25,
}


DAY_LABELS = ["Hôm nay", "Ngày mai", "Ngày kia"]


def _normalize_region(region: str) -> str:
    key = normalize_location_key(region)
    return REGION_NORMALIZE.get(key, region.strip())


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _avg_temp(temp_min: Any, temp_max: Any) -> float | None:
    min_value = _as_float(temp_min)
    max_value = _as_float(temp_max)
    if min_value is None and max_value is None:
        return None
    if min_value is None:
        return max_value
    if max_value is None:
        return min_value
    return round((min_value + max_value) / 2, 1)


class WeatherService:
    def __init__(self, client: WeatherClient | None = None):
        self.client = client or WeatherClient()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def get_current_weather(self, db: Session, region: str, force_refresh: bool = False) -> dict:
        requested_region = region.strip()
        normalized_region = _normalize_region(requested_region)
        meta = self.ensure_region_weather(db, requested_region, days=7, force_refresh=force_refresh)
        return self._read_current_weather_from_db(
            db,
            requested_region,
            normalized_region,
            cache_status=meta.get("cache_status", "hit"),
        )

    def _read_current_weather_from_db(
        self,
        db: Session,
        requested_region: str,
        normalized_region: str,
        cache_status: str,
    ) -> dict:
        observation = get_latest_observation(db, normalized_region)
        today_row = get_weather_for_date(db, normalized_region, date.today()) or get_latest_weather(db, normalized_region)

        if observation:
            return self._current_from_observation(
                observation,
                today_row,
                requested_region,
                cache_status=cache_status,
            )
        if today_row:
            return self._current_from_daily(
                today_row,
                requested_region,
                cache_status=cache_status,
            )
        return self._mock_current(requested_region, normalized_region)

    def refresh_region_weather(self, db: Session, region: str, days: int = 7) -> dict:
        return self.ensure_region_weather(db, region, days=days, force_refresh=True)

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

    def get_forecast_from_db(self, db: Session, region: str, days: int = 7) -> dict:
        normalized_region = _normalize_region(region)
        rows = get_weather_forecast(db, normalized_region, days)
        return {
            "region": region,
            "days_requested": days,
            "days_available": len(rows),
            "source": "open_meteo" if rows else "no_data",
            "forecast": [self._forecast_item(row, index, region, None) for index, row in enumerate(rows)],
        }

    def get_forecast(self, db: Session, region: str, days: int = 7) -> list[dict]:
        requested_region = region.strip()
        normalized_region = _normalize_region(requested_region)
        self.ensure_region_weather(db, requested_region, days=days, force_refresh=False)
        rows = get_weather_forecast(db, normalized_region, days)
        if rows:
            return [self._forecast_item(row, index, requested_region, None) for index, row in enumerate(rows[:days])]
        return self._mock_forecast(requested_region, normalized_region, days)

    def get_hourly_forecast(self, db: Session, region: str, hours: int = 24) -> list[dict]:
        requested_region = region.strip()
        normalized_region = _normalize_region(requested_region)
        forecast_hours = min(max(hours, 1), 168)
        try:
            hourly = self.client.get_hourly_forecast(normalized_region, forecast_hours)
            return [self._hourly_item(item, requested_region) for item in hourly]
        except WeatherProviderError:
            current = self.get_current_weather(db, requested_region)
            return self._build_hourly_fallback(current, forecast_hours)

    def get_harvest_weather_warning(self, db: Session, region: str) -> str | None:
        current = self.get_current_weather(db, region)
        warnings = self._analyze_warnings(
            current.get("temp_max") or current.get("temperature") or 28,
            current.get("temp_min") or current.get("temperature") or 22,
            current.get("rainfall") or 0,
            current.get("humidity") or 70,
            current.get("wind_speed") or 0,
        )
        return " | ".join(warnings) if warnings else None

    def build_activity_recommendations(
        self,
        current: dict,
        forecast: list[dict],
        _hourly: list[dict],
        crop_name: str | None = None,
        growth_stage: str | None = None,
    ) -> list[dict]:
        return self._build_activity_recommendations(current, forecast, crop_name, growth_stage)

    def get_agriculture_weather(
        self,
        db: Session,
        region: str,
        crop_name: str | None = None,
        growth_stage: str | None = None,
        days: int = 7,
        include_hourly: bool = True,
        force_refresh: bool = False,
    ) -> dict:
        requested_region = region.strip()
        normalized_region = _normalize_region(requested_region)
        meta = self.ensure_region_weather(db, requested_region, days=days, force_refresh=force_refresh)

        current = self._read_current_weather_from_db(
            db,
            requested_region,
            normalized_region,
            cache_status=meta.get("cache_status", "hit"),
        )
        forecast_rows = get_weather_forecast(db, normalized_region, days)
        forecast = [
            self._forecast_item(row, index, requested_region, crop_name)
            for index, row in enumerate(forecast_rows[:days])
        ] or self._mock_forecast(requested_region, normalized_region, days, crop_name=crop_name)

        hourly = self.get_hourly_forecast(db, requested_region, 24) if include_hourly else []
        alerts = self._build_alerts(forecast, crop_name, growth_stage)
        activity_recs = self._build_activity_recommendations(current, forecast, crop_name, growth_stage)
        ai_rec = self._build_ai_recommendation(current, forecast, alerts, crop_name, growth_stage)

        data_flow = [
            "Open-Meteo API -> lưu cache vào WeatherData/WeatherObservations",
            "Backend đọc DB theo khu vực và ngày hiện tại",
            "Rule engine tạo cảnh báo và gợi ý canh tác theo cây trồng",
        ]

        return {
            "module_name": "Thời tiết nông vụ thông minh",
            "region": requested_region,
            "crop_name": crop_name,
            "growth_stage": growth_stage,
            "location": {
                "latitude": current.get("latitude"),
                "longitude": current.get("longitude"),
            },
            "current": current,
            "forecast": forecast,
            "hourly_forecast": hourly,
            "alerts": alerts,
            "activity_recommendations": activity_recs,
            "ai_recommendation": ai_rec,
            "data_flow": data_flow,
            "source_summary": {
                "provider": "Open-Meteo",
                "source_url": "https://open-meteo.com",
                "cache_status": (
                    meta.get("cache_status")
                    if force_refresh
                    else current.get("cache_status", meta.get("cache_status", "unknown"))
                ),
                "is_mock": bool(current.get("is_mock")) or any(item.get("is_mock") for item in forecast),
                "daily_rows": len(forecast_rows),
                "force_refresh": force_refresh,
                "deleted": meta.get("deleted"),
                "saved_daily_rows": meta.get("saved_daily_rows", 0),
                "saved_observations": meta.get("saved_observations", 0),
            },
            "generated_at": datetime.now(),
        }

    def generate_alerts(
        self,
        _current: dict,
        forecast: list[dict],
        crop_name: str | None = None,
        growth_stage: str | None = None,
    ) -> list[dict]:
        return self._build_alerts(forecast, crop_name=crop_name, growth_stage=growth_stage)

    # ------------------------------------------------------------------ #
    # Open-Meteo cache
    # ------------------------------------------------------------------ #

    def ensure_region_weather(
        self,
        db: Session,
        region: str,
        days: int = 7,
        force_refresh: bool = False,
    ) -> dict:
        requested_region = region.strip()
        normalized_region = _normalize_region(requested_region)
        forecast_days = min(max(days, 1), 16)
        today = date.today()
        end_date = today + timedelta(days=forecast_days - 1)

        rows = get_weather_forecast(db, normalized_region, forecast_days)
        observation = get_latest_observation(db, normalized_region)
        daily_cache_ready = len(rows) >= forecast_days

        current = None
        current_error = None
        try:
            current = self.client.get_current(normalized_region)
        except WeatherProviderError as exc:
            current_error = str(exc)

        if daily_cache_ready and not force_refresh:
            saved_observation = self._store_current_observation(db, normalized_region, current) if current else None
            return {
                "cache_status": "live" if saved_observation else ("stale" if observation else "hit"),
                "error": current_error,
                "saved_daily_rows": 0,
                "saved_observations": 1 if saved_observation else 0,
                "deleted": {"weather_data": 0, "observations": 0},
            }

        try:
            if current is None:
                current = self.client.get_current(normalized_region)
            forecast = self.client.get_forecast(normalized_region, forecast_days)
        except WeatherProviderError as exc:
            saved_observation = self._store_current_observation(db, normalized_region, current) if current else None
            return {
                "cache_status": "stale" if rows or observation else "miss",
                "error": str(exc),
                "saved_daily_rows": 0,
                "saved_observations": 1 if saved_observation else 0,
                "deleted": {"weather_data": 0, "observations": 0},
            }

        deleted = {"weather_data": 0, "observations": 0}
        if force_refresh:
            deleted = delete_weather_cache(db, normalized_region, start_date=today, end_date=end_date)

        saved_daily = self._store_daily_forecast(db, normalized_region, current, forecast)
        saved_observation = self._store_current_observation(db, normalized_region, current)
        return {
            "cache_status": "refreshed" if force_refresh else "updated",
            "saved_daily_rows": saved_daily,
            "saved_observations": 1 if saved_observation else 0,
            "deleted": deleted,
        }

    def _store_daily_forecast(
        self,
        db: Session,
        region: str,
        current: dict,
        forecast: list[dict],
    ) -> int:
        source_updated_at = _as_datetime(current.get("source_updated_at")) or datetime.now()
        rows = []
        for item in forecast:
            record_date = _parse_date(item.get("date"))
            if not record_date:
                continue
            rows.append(
                {
                    "region": region,
                    "record_date": record_date,
                    "temp_min": item.get("temp_min"),
                    "temp_max": item.get("temp_max"),
                    "humidity": item.get("humidity"),
                    "rainfall": item.get("rainfall"),
                    "sunshine_hours": item.get("sunshine_hours"),
                    "weather_desc": item.get("weather_desc") or item.get("condition"),
                    "latitude": current.get("latitude"),
                    "longitude": current.get("longitude"),
                    "wind_speed": item.get("wind_speed"),
                    "uv_index": item.get("uv_index"),
                    "pressure": current.get("pressure"),
                    "weather_code": item.get("weather_code"),
                    "source_name": item.get("source_name") or "Open-Meteo",
                    "source_updated_at": source_updated_at,
                }
            )
        return upsert_weather_data_rows(db, rows)

    def _store_current_observation(self, db: Session, region: str, current: dict):
        observed_at = _as_datetime(current.get("source_updated_at")) or datetime.now()
        return create_weather_observation(
            db,
            {
                "region": region,
                "observed_at": observed_at,
                "temperature": current.get("temperature"),
                "humidity": current.get("humidity"),
                "rainfall": current.get("rainfall"),
                "wind_speed": current.get("wind_speed"),
                "uv_index": current.get("uv_index"),
                "pressure": current.get("pressure"),
                "weather_code": current.get("weather_code"),
                "weather_desc": current.get("weather_desc") or current.get("condition"),
                "source_name": current.get("source_name") or "Open-Meteo",
                "source_updated_at": observed_at,
            },
        )

    def _observation_is_fresh(self, observation) -> bool:
        if observation is None:
            return False
        updated_at = _as_datetime(observation.SourceUpdatedAt) or _as_datetime(observation.ObservedAt)
        if updated_at is None:
            return False
        age_seconds = (datetime.now() - updated_at).total_seconds()
        return 0 <= age_seconds <= max(settings.WEATHER_CACHE_TTL_SECONDS, 60)

    # ------------------------------------------------------------------ #
    # Response mapping
    # ------------------------------------------------------------------ #

    def _current_from_observation(self, observation, daily_row, requested_region: str, cache_status: str) -> dict:
        observed_at = _as_datetime(observation.ObservedAt) or datetime.now()
        last_updated = _as_datetime(observation.SourceUpdatedAt) or observed_at
        checked_at = datetime.now()
        temp_min = _as_float(getattr(daily_row, "TempMin", None))
        temp_max = _as_float(getattr(daily_row, "TempMax", None))
        temperature = _as_float(observation.Temperature, _avg_temp(temp_min, temp_max))
        response = {
            "region": requested_region,
            "temperature": temperature,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rainfall": _as_float(observation.Rainfall, _as_float(getattr(daily_row, "Rainfall", None))),
            "humidity": _as_float(observation.Humidity, _as_float(getattr(daily_row, "Humidity", None))),
            "condition": observation.WeatherDesc or getattr(daily_row, "WeatherDesc", None),
            "wind_speed": _as_float(observation.WindSpeed, _as_float(getattr(daily_row, "WindSpeed", None))),
            "uv_index": _as_float(observation.UVIndex, _as_float(getattr(daily_row, "UVIndex", None))),
            "pressure": _as_float(observation.Pressure, _as_float(getattr(daily_row, "Pressure", None))),
            "weather_code": observation.WeatherCode or getattr(daily_row, "WeatherCode", None),
            "latitude": _as_float(getattr(daily_row, "Latitude", None)),
            "longitude": _as_float(getattr(daily_row, "Longitude", None)),
            "recorded_at": observed_at,
            "source": "database",
            "source_name": observation.SourceName or getattr(daily_row, "SourceName", None) or "Open-Meteo",
            "source_url": "https://open-meteo.com",
            "is_realtime": True,
            "is_mock": False,
            "checked_at": checked_at,
            "source_updated_at": last_updated,
            "last_updated": last_updated,
            "data_age_minutes": self._age_minutes(last_updated),
            "cache_status": cache_status,
            "agriculture_insights": [],
            "warnings": [],
        }
        response["warnings"] = self._analyze_warnings(
            response.get("temp_max") or response.get("temperature") or 28,
            response.get("temp_min") or response.get("temperature") or 22,
            response.get("rainfall") or 0,
            response.get("humidity") or 70,
            response.get("wind_speed") or 0,
        )
        response["agriculture_insights"] = self._build_agriculture_insights(response)
        return response

    def _current_from_daily(self, row, requested_region: str, cache_status: str) -> dict:
        temp_min = _as_float(row.TempMin)
        temp_max = _as_float(row.TempMax)
        recorded_at = datetime.combine(row.RecordDate, datetime.min.time()) if row.RecordDate else datetime.now()
        last_updated = _as_datetime(row.SourceUpdatedAt) or _as_datetime(row.CreatedAt) or recorded_at
        checked_at = datetime.now()
        response = {
            "region": requested_region,
            "temperature": _avg_temp(temp_min, temp_max),
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rainfall": _as_float(row.Rainfall),
            "humidity": _as_float(row.Humidity),
            "condition": row.WeatherDesc,
            "wind_speed": _as_float(row.WindSpeed),
            "uv_index": _as_float(row.UVIndex),
            "pressure": _as_float(row.Pressure),
            "weather_code": row.WeatherCode,
            "latitude": _as_float(row.Latitude),
            "longitude": _as_float(row.Longitude),
            "recorded_at": recorded_at,
            "source": "database",
            "source_name": row.SourceName or "Open-Meteo",
            "source_url": "https://open-meteo.com",
            "is_realtime": False,
            "is_mock": False,
            "checked_at": checked_at,
            "source_updated_at": last_updated,
            "last_updated": last_updated,
            "data_age_minutes": self._age_minutes(last_updated),
            "cache_status": cache_status,
            "agriculture_insights": [],
            "warnings": [],
        }
        response["warnings"] = self._analyze_warnings(
            response.get("temp_max") or response.get("temperature") or 28,
            response.get("temp_min") or response.get("temperature") or 22,
            response.get("rainfall") or 0,
            response.get("humidity") or 70,
            response.get("wind_speed") or 0,
        )
        response["agriculture_insights"] = self._build_agriculture_insights(response)
        return response

    def _forecast_item(self, row, index: int, requested_region: str, crop_name: str | None) -> dict:
        temp_min = _as_float(row.TempMin)
        temp_max = _as_float(row.TempMax)
        rainfall = _as_float(row.Rainfall, 0.0) or 0.0
        humidity = _as_float(row.Humidity)
        wind_speed = _as_float(row.WindSpeed)
        source_updated_at = _as_datetime(row.SourceUpdatedAt) or _as_datetime(row.CreatedAt)
        item = {
            "date": row.RecordDate,
            "region": requested_region,
            "day_label": DAY_LABELS[index] if index < len(DAY_LABELS) else None,
            "temperature": _avg_temp(temp_min, temp_max),
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rainfall": round(rainfall, 1),
            "rain_probability": self._rain_probability(rainfall),
            "humidity": humidity,
            "wind_speed": wind_speed,
            "uv_index": _as_float(row.UVIndex),
            "condition": row.WeatherDesc,
            "weather_code": row.WeatherCode,
            "warnings": self._analyze_warnings(temp_max or 30, temp_min or 20, rainfall, humidity or 70, wind_speed or 0),
            "recommendation": None,
            "source_name": row.SourceName or "Open-Meteo",
            "source_url": "https://open-meteo.com",
            "is_realtime": index == 0,
            "is_mock": False,
            "cache_status": "hit",
            "last_updated": source_updated_at,
        }
        item["recommendation"] = self._daily_recommendation(item, crop_name)
        return item

    def _hourly_item(self, item: dict, requested_region: str) -> dict:
        result = dict(item)
        result["region"] = requested_region
        result["recommendation"] = self._hourly_recommendation(result)
        return result

    def _mock_current(self, requested_region: str, normalized_region: str) -> dict:
        base = MOCK_WEATHER.get(normalized_region, MOCK_WEATHER["default"])
        now = datetime.now()
        response = {
            "region": requested_region,
            "temperature": base["temperature"],
            "temp_min": base["temp_min"],
            "temp_max": base["temp_max"],
            "rainfall": base["rainfall"],
            "humidity": base["humidity"],
            "condition": base["weather_desc"],
            "wind_speed": base["wind_speed"],
            "uv_index": base["uv_index"],
            "pressure": None,
            "weather_code": None,
            "latitude": None,
            "longitude": None,
            "recorded_at": now,
            "source": "fallback",
            "source_name": "mock",
            "source_url": None,
            "is_realtime": False,
            "is_mock": True,
            "checked_at": now,
            "source_updated_at": now,
            "last_updated": now,
            "data_age_minutes": 0,
            "cache_status": "miss",
            "agriculture_insights": [],
            "warnings": [],
        }
        response["warnings"] = self._analyze_warnings(
            response["temp_max"],
            response["temp_min"],
            response["rainfall"],
            response["humidity"],
            response["wind_speed"],
        )
        response["agriculture_insights"] = self._build_agriculture_insights(response)
        return response

    def _mock_forecast(
        self,
        requested_region: str,
        normalized_region: str,
        days: int,
        crop_name: str | None = None,
    ) -> list[dict]:
        base = MOCK_WEATHER.get(normalized_region, MOCK_WEATHER["default"])
        result = []
        for index in range(days):
            temp_shift = [-1.0, 0.0, 1.0, 0.5, -0.5, 0.8, -0.2][index % 7]
            rainfall = max(0.0, base["rainfall"] + [0, 2, -1, 5, 0, -2, 3][index % 7])
            item = {
                "date": date.today() + timedelta(days=index),
                "region": requested_region,
                "day_label": DAY_LABELS[index] if index < len(DAY_LABELS) else None,
                "temperature": round(base["temperature"] + temp_shift, 1),
                "temp_min": round(base["temp_min"] + temp_shift, 1),
                "temp_max": round(base["temp_max"] + temp_shift, 1),
                "rainfall": round(rainfall, 1),
                "rain_probability": self._rain_probability(rainfall),
                "humidity": base["humidity"],
                "wind_speed": base["wind_speed"],
                "uv_index": base["uv_index"],
                "condition": base["weather_desc"],
                "weather_code": None,
                "warnings": [],
                "recommendation": None,
                "source_name": "mock",
                "source_url": None,
                "is_realtime": False,
                "is_mock": True,
                "cache_status": "miss",
                "last_updated": datetime.now(),
            }
            item["warnings"] = self._analyze_warnings(
                item["temp_max"],
                item["temp_min"],
                item["rainfall"],
                item["humidity"],
                item["wind_speed"],
            )
            item["recommendation"] = self._daily_recommendation(item, crop_name)
            result.append(item)
        return result

    def _build_hourly_fallback(self, current: dict, hours: int) -> list[dict]:
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        base_temp = current.get("temperature") or 28
        base_humidity = current.get("humidity") or 75
        result = []
        for offset in range(hours):
            forecast_at = now + timedelta(hours=offset)
            hour = forecast_at.hour
            temp_shift = -2 if 0 <= hour < 6 else (2 if 11 <= hour <= 15 else 0)
            rain_probability = 65 if 14 <= hour <= 18 and (current.get("rainfall") or 0) > 5 else 25
            item = {
                "time": forecast_at.isoformat(timespec="minutes"),
                "date": forecast_at.date(),
                "forecast_at": forecast_at,
                "region": current.get("region"),
                "temperature": round(base_temp + temp_shift, 1),
                "rainfall": 0.0,
                "rain_probability": rain_probability,
                "humidity": base_humidity,
                "wind_speed": current.get("wind_speed"),
                "uv_index": current.get("uv_index"),
                "condition": current.get("condition"),
                "weather_code": current.get("weather_code"),
                "recommendation": None,
                "source_name": current.get("source_name"),
                "is_realtime": offset == 0,
                "is_mock": bool(current.get("is_mock")),
                "cache_status": current.get("cache_status", "fallback"),
                "last_updated": current.get("last_updated"),
            }
            item["recommendation"] = self._hourly_recommendation(item)
            result.append(item)
        return result

    # ------------------------------------------------------------------ #
    # Agriculture rules
    # ------------------------------------------------------------------ #

    def _crop_advice(self, crop_name: str | None) -> dict:
        advice = {
            "lua": {"spray_rain_limit": 10, "water_temp_limit": 36, "cold_limit": 15},
            "ca phe": {"spray_rain_limit": 8, "water_temp_limit": 35, "cold_limit": 10},
            "ho tieu": {"spray_rain_limit": 10, "water_temp_limit": 34, "cold_limit": 12},
            "rau mau": {"spray_rain_limit": 5, "water_temp_limit": 33, "cold_limit": 12},
            "cay an trai": {"spray_rain_limit": 10, "water_temp_limit": 36, "cold_limit": 10},
        }
        key = normalize_location_key(crop_name or "lua")
        return advice.get(key, advice["lua"])

    def _daily_recommendation(self, item: dict, crop_name: str | None) -> str:
        advice = self._crop_advice(crop_name)
        parts = []
        if (item.get("rainfall") or 0) > advice["spray_rain_limit"]:
            parts.append("Không phun thuốc")
        if (item.get("temp_max") or 0) > advice["water_temp_limit"]:
            parts.append("Tăng tưới nước")
        if (item.get("humidity") or 0) > 88:
            parts.append("Theo dõi nấm bệnh")
        if (item.get("temp_min") or 99) < advice["cold_limit"]:
            parts.append("Giữ ấm cho cây")
        if (item.get("wind_speed") or 0) > ALERT_THRESHOLDS["wind_high"]:
            parts.append("Hạn chế phun thuốc khi gió mạnh")
        return " · ".join(parts) if parts else "Thời tiết thuận lợi cho canh tác"

    def _hourly_recommendation(self, item: dict) -> str:
        rain_probability = item.get("rain_probability") or 0
        wind_speed = item.get("wind_speed") or 0
        temperature = item.get("temperature") or 28
        forecast_at = _as_datetime(item.get("forecast_at") or item.get("time"))
        hour = forecast_at.hour if forecast_at else 8
        if rain_probability >= 60:
            return "Khả năng mưa cao, hạn chế phun thuốc"
        if wind_speed >= ALERT_THRESHOLDS["wind_high"]:
            return "Gió mạnh, không nên phun thuốc"
        if temperature >= 35 and 10 <= hour <= 15:
            return "Nắng nóng, tránh tưới giữa trưa"
        if 5 <= hour <= 8:
            return "Phù hợp phun thuốc hoặc kiểm tra ruộng"
        return "Có thể làm việc ngoài đồng"

    def _build_activity_recommendations(
        self,
        current: dict,
        forecast: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
    ) -> list[dict]:
        temp = current.get("temperature") or 28
        rain = current.get("rainfall") or 0
        humidity = current.get("humidity") or 70
        wind = current.get("wind_speed") or 0
        advice = self._crop_advice(crop_name)
        stage_key = normalize_location_key(growth_stage or "")

        recs = []
        if rain > advice["spray_rain_limit"]:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Hoãn",
                "reason": f"Mưa hiện tại {rain:.1f} mm, ưu tiên kiểm tra thoát nước.",
                "priority": "low",
                "timing": "",
            })
        elif temp > advice["water_temp_limit"]:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Tưới sớm",
                "reason": f"Nhiệt độ {temp:.0f}°C có thể làm cây mất nước nhanh.",
                "priority": "high",
                "timing": "5-7h hoặc 17-19h",
            })
        else:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Theo lịch",
                "reason": "Điều kiện hiện tại ổn định, duy trì lịch tưới bình thường.",
                "priority": "medium",
                "timing": "Sáng sớm",
            })

        if wind > ALERT_THRESHOLDS["wind_high"]:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Không nên",
                "reason": f"Gió {wind:.0f} km/h dễ làm thuốc bay lệch.",
                "priority": "low",
                "timing": "",
            })
        elif rain > advice["spray_rain_limit"]:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Hoãn",
                "reason": "Mưa có thể rửa trôi thuốc và giảm hiệu quả xử lý.",
                "priority": "low",
                "timing": "",
            })
        else:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Có thể",
                "reason": "Mưa và gió chưa vượt ngưỡng rủi ro.",
                "priority": "medium",
                "timing": "6-8h khi gió nhẹ",
            })

        avg_rain_3d = sum(day.get("rainfall") or 0 for day in forecast[:3]) / max(len(forecast[:3]), 1)
        if rain > 30 or avg_rain_3d > 20:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Hoãn",
                "reason": "Mưa lớn dễ rửa trôi phân bón.",
                "priority": "low",
                "timing": "",
            })
        elif humidity < 50 and avg_rain_3d < 2:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Kết hợp tưới",
                "reason": "Đất có xu hướng khô, cần đủ ẩm để phân tan đều.",
                "priority": "medium",
                "timing": "Chiều mát",
            })
        else:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Tốt",
                "reason": "Độ ẩm phù hợp cho hấp thu dinh dưỡng.",
                "priority": "medium",
                "timing": "16-18h",
            })

        if "thu hoach" in stage_key:
            dry_days = sum(1 for day in forecast[:3] if (day.get("rainfall") or 0) < 5)
            recs.append({
                "action_type": "harvest",
                "action": "Thu hoạch",
                "decision": "Nên làm sớm" if dry_days >= 2 else "Cân nhắc hoãn",
                "reason": "Ưu tiên khung ngày khô ráo để giảm hao hụt sau thu hoạch.",
                "priority": "high",
                "timing": "Sáng 7-11h",
            })

        return recs

    def _build_alerts(self, forecast: list[dict], crop_name: str | None, growth_stage: str | None = None) -> list[dict]:
        alerts = []
        advice = self._crop_advice(crop_name)
        stage_key = normalize_location_key(growth_stage or "")
        cold_limit = advice["cold_limit"] + (2 if "cay con" in stage_key else 0)

        for item in forecast:
            temp_max = item.get("temp_max") or 30
            temp_min = item.get("temp_min") or 20
            rainfall = item.get("rainfall") or 0
            humidity = item.get("humidity") or 70
            wind = item.get("wind_speed") or 0
            forecast_date = item.get("date")

            if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
                alerts.append({
                    "alert_type": "heat_stress",
                    "forecast_date": forecast_date,
                    "title": f"Nắng nóng {temp_max:.0f}°C",
                    "message": "Nhiệt độ cao có thể gây stress nhiệt cho cây trồng.",
                    "recommendation": "Tăng tưới, che phủ đất và tránh bón/phun giữa trưa.",
                    "severity": "high" if temp_max >= 38 else "medium",
                    "trigger_value": temp_max,
                    "trigger_unit": "°C",
                    "source": "rule",
                })
            if temp_min < cold_limit:
                alerts.append({
                    "alert_type": "cold_stress",
                    "forecast_date": forecast_date,
                    "title": f"Lạnh {temp_min:.0f}°C",
                    "message": "Nhiệt độ thấp có thể ảnh hưởng cây non hoặc giai đoạn ra hoa.",
                    "recommendation": "Giữ ấm gốc, hạn chế tưới muộn và theo dõi sương muối.",
                    "severity": "high" if temp_min < 10 else "medium",
                    "trigger_value": temp_min,
                    "trigger_unit": "°C",
                    "source": "rule",
                })
            if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
                alerts.append({
                    "alert_type": "heavy_rain",
                    "forecast_date": forecast_date,
                    "title": f"Mưa lớn {rainfall:.0f} mm",
                    "message": "Mưa lớn có thể gây úng rễ, rửa trôi phân bón và tăng bệnh nấm.",
                    "recommendation": "Kiểm tra mương thoát nước và tạm hoãn bón phân.",
                    "severity": "high",
                    "trigger_value": rainfall,
                    "trigger_unit": "mm",
                    "source": "rule",
                })
            if humidity > ALERT_THRESHOLDS["humidity_high"]:
                alerts.append({
                    "alert_type": "high_humidity",
                    "forecast_date": forecast_date,
                    "title": f"Độ ẩm cao {humidity:.0f}%",
                    "message": "Độ ẩm cao kéo dài tạo điều kiện cho nấm bệnh phát triển.",
                    "recommendation": "Tăng thông thoáng tán cây và kiểm tra dấu hiệu bệnh.",
                    "severity": "medium",
                    "trigger_value": humidity,
                    "trigger_unit": "%",
                    "source": "rule",
                })
            if wind > ALERT_THRESHOLDS["wind_high"]:
                alerts.append({
                    "alert_type": "strong_wind",
                    "forecast_date": forecast_date,
                    "title": f"Gió mạnh {wind:.0f} km/h",
                    "message": "Gió mạnh làm giảm hiệu quả phun thuốc và có thể gây đổ ngã.",
                    "recommendation": "Không phun thuốc; gia cố cây hoặc giàn leo nếu cần.",
                    "severity": "medium",
                    "trigger_value": wind,
                    "trigger_unit": "km/h",
                    "source": "rule",
                })

        seen = set()
        unique = []
        for alert in alerts:
            key = (alert["alert_type"], str(alert.get("forecast_date")))
            if key not in seen:
                seen.add(key)
                unique.append(alert)
        return unique

    def _build_ai_recommendation(
        self,
        current: dict,
        forecast: list[dict],
        alerts: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
    ) -> dict:
        crop_label = crop_name or "cây trồng"
        stage_label = growth_stage or "hiện tại"
        temp = current.get("temperature") or 28
        humidity = current.get("humidity") or 70
        rain = current.get("rainfall") or 0
        high_alerts = [alert for alert in alerts if alert.get("severity") == "high"]
        avg_rain = sum(day.get("rainfall") or 0 for day in forecast) / max(len(forecast), 1)
        hot_days = sum(1 for day in forecast if (day.get("temp_max") or 0) >= ALERT_THRESHOLDS["temp_max_high"])
        rainy_days = sum(1 for day in forecast if (day.get("rainfall") or 0) >= 10)

        if high_alerts:
            summary = f"Có {len(high_alerts)} cảnh báo nghiêm trọng trong {len(forecast)} ngày tới cho {crop_label}."
            risk = " | ".join(alert["title"] for alert in high_alerts[:3])
        elif hot_days >= 3:
            summary = f"Nắng nóng xuất hiện nhiều ngày, {crop_label} giai đoạn {stage_label} cần bổ sung nước chủ động."
            risk = "Rủi ro mất nước và stress nhiệt tăng trong khung giờ trưa."
        elif rainy_days >= 3:
            summary = f"Mưa xuất hiện nhiều ngày, ưu tiên thoát nước và quản lý nấm bệnh cho {crop_label}."
            risk = "Mưa liên tục có thể làm giảm hiệu quả phun thuốc và rửa trôi dinh dưỡng."
        else:
            summary = f"Thời tiết tương đối thuận lợi cho {crop_label} giai đoạn {stage_label}."
            risk = "Chưa có rủi ro lớn, tiếp tục theo dõi dự báo hằng ngày."

        action_plan = [
            f"Nhiệt độ hiện tại {temp:.0f}°C: {'tăng tưới và che phủ' if temp >= 35 else 'duy trì chăm sóc bình thường'}",
            f"Độ ẩm {humidity:.0f}%: {'theo dõi nấm bệnh' if humidity >= 85 else 'ổn định'}",
            f"Mưa trung bình 7 ngày {avg_rain:.1f} mm/ngày: {'ưu tiên thoát nước' if avg_rain >= 10 else 'duy trì lịch tưới'}",
        ]
        if rain >= 10:
            action_plan.append("Hoãn phun thuốc tới khi lá khô và xác suất mưa giảm.")

        crop_note = None
        stage_key = normalize_location_key(growth_stage or "")
        if "cay con" in stage_key:
            crop_note = f"{crop_label} giai đoạn cây con nhạy với nhiệt độ và úng nước."
        elif "ra hoa" in stage_key:
            crop_note = f"{crop_label} đang ra hoa, tránh phun thuốc khi mưa hoặc gió mạnh."
        elif "thu hoach" in stage_key:
            crop_note = f"{crop_label} gần thu hoạch, ưu tiên ngày khô để giảm hao hụt."

        return {
            "provider": "rule_based_ai",
            "summary": summary,
            "risk_explanation": risk,
            "action_plan": action_plan,
            "crop_note": crop_note,
            "data_note": "Dữ liệu lấy từ Open-Meteo, lưu cache trong DB và được làm mới khi bấm Cập nhật hoặc khi cache thiếu/stale.",
        }

    def _build_agriculture_insights(self, current: dict) -> list[dict]:
        insights = []
        temp = current.get("temperature")
        humidity = current.get("humidity")
        rainfall = current.get("rainfall")
        wind = current.get("wind_speed")
        if temp is not None:
            insights.append({
                "metric": "Nhiệt độ",
                "value": f"{temp:.1f}°C",
                "meaning": "Tăng tưới và che phủ nếu vượt 35°C.",
            })
        if humidity is not None:
            insights.append({
                "metric": "Độ ẩm",
                "value": f"{humidity:.0f}%",
                "meaning": "Độ ẩm cao làm tăng nguy cơ nấm bệnh.",
            })
        if rainfall is not None:
            insights.append({
                "metric": "Mưa",
                "value": f"{rainfall:.1f} mm",
                "meaning": "Mưa ảnh hưởng trực tiếp tới tưới, phun thuốc và bón phân.",
            })
        if wind is not None:
            insights.append({
                "metric": "Gió",
                "value": f"{wind:.1f} km/h",
                "meaning": "Không nên phun thuốc khi gió vượt 25 km/h.",
            })
        return insights

    @staticmethod
    def _analyze_warnings(temp_max: float, temp_min: float, rainfall: float, humidity: float, wind_speed: float = 0) -> list[str]:
        warnings = []
        if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            warnings.append(f"Nắng nóng {temp_max:.0f}°C, tăng tưới và che phủ.")
        if temp_min < ALERT_THRESHOLDS["temp_min_cold"]:
            warnings.append(f"Lạnh {temp_min:.0f}°C, chú ý giữ ấm cây.")
        if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
            warnings.append(f"Mưa lớn {rainfall:.0f} mm, kiểm tra thoát nước.")
        if humidity > ALERT_THRESHOLDS["humidity_high"]:
            warnings.append(f"Độ ẩm cao {humidity:.0f}%, tăng theo dõi nấm bệnh.")
        if humidity < ALERT_THRESHOLDS["humidity_low"]:
            warnings.append(f"Độ ẩm thấp {humidity:.0f}%, cần bổ sung nước.")
        if wind_speed > ALERT_THRESHOLDS["wind_high"]:
            warnings.append(f"Gió mạnh {wind_speed:.0f} km/h, hạn chế phun thuốc.")
        return warnings

    @staticmethod
    def _rain_probability(rainfall: float) -> int:
        if rainfall <= 0:
            return 10
        return max(20, min(95, int(rainfall * 6 + 20)))

    @staticmethod
    def _age_minutes(value: datetime | None) -> int | None:
        if value is None:
            return None
        return max(0, int((datetime.now() - value).total_seconds() / 60))


weather_service = WeatherService()
