import json
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings


class WeatherProviderError(RuntimeError):
    pass


WEATHER_CODE_CONDITIONS = {
    0: "clear",
    1: "mostly_clear",
    2: "partly_cloudy",
    3: "cloudy",
    45: "foggy",
    48: "foggy",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    61: "rainy",
    63: "rainy",
    65: "heavy_rain",
    80: "rain_showers",
    81: "rain_showers",
    82: "heavy_rain",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


class WeatherClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.OPEN_METEO_BASE_URL).rstrip("/")

    def get_current(self, region: str) -> dict:
        coordinates = self._coordinates_for_region(region)
        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "rain",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                    "pressure_msl",
                ]
            ),
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,weather_code,uv_index_max",
            "timezone": "auto",
        }
        url = f"{self.base_url}/v1/forecast"
        payload = self._get_json(url, params)
        current = payload.get("current") or {}
        daily = payload.get("daily") or {}
        weather_code = current.get("weather_code")
        source_updated_at = self._parse_datetime(current.get("time"))

        return {
            "region": region,
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "temperature": current.get("temperature_2m"),
            "temp_min": self._first(daily.get("temperature_2m_min"), current.get("temperature_2m")),
            "temp_max": self._first(daily.get("temperature_2m_max"), current.get("temperature_2m")),
            "rainfall": current.get("rain") if current.get("rain") is not None else current.get("precipitation"),
            "humidity": current.get("relative_humidity_2m"),
            "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
            "weather_code": weather_code,
            "wind_speed": current.get("wind_speed_10m"),
            "uv_index": self._first(daily.get("uv_index_max")),
            "pressure": current.get("pressure_msl"),
            "source_name": "Open-Meteo",
            "source_url": url,
            "source_updated_at": source_updated_at or datetime.now(),
        }

    def get_forecast(self, region: str, days: int = 7) -> list[dict]:
        coordinates = self._coordinates_for_region(region)
        forecast_days = min(max(days, 1), 16)
        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_max,relative_humidity_2m_mean,weather_code,wind_speed_10m_max,uv_index_max",
            "forecast_days": forecast_days,
            "timezone": "auto",
        }
        url = f"{self.base_url}/v1/forecast"
        payload = self._get_json(url, params)
        daily = payload.get("daily") or {}
        dates = daily.get("time") or []
        result = []
        for index, forecast_date in enumerate(dates[:forecast_days]):
            weather_code = self._at(daily.get("weather_code"), index)
            result.append(
                {
                    "date": forecast_date,
                    "region": region,
                    "temp_min": self._at(daily.get("temperature_2m_min"), index),
                    "temp_max": self._at(daily.get("temperature_2m_max"), index),
                    "temperature": self._average(
                        self._at(daily.get("temperature_2m_min"), index),
                        self._at(daily.get("temperature_2m_max"), index),
                    ),
                    "rainfall": self._at(daily.get("precipitation_sum"), index),
                    "rain_probability": self._at(daily.get("precipitation_probability_max"), index),
                    "humidity": self._at(daily.get("relative_humidity_2m_mean"), index),
                    "wind_speed": self._at(daily.get("wind_speed_10m_max"), index),
                    "uv_index": self._at(daily.get("uv_index_max"), index),
                    "weather_code": weather_code,
                    "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
                    "source_name": "Open-Meteo",
                    "source_url": url,
                    "is_realtime": index == 0,
                    "is_mock": False,
                    "cache_status": "miss",
                    "last_updated": datetime.now(),
                }
            )
        return result

    def get_hourly_forecast(self, region: str, hours: int = 24) -> list[dict]:
        coordinates = self._coordinates_for_region(region)
        forecast_hours = min(max(hours, 1), 168)
        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m,dew_point_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,uv_index,visibility,cloud_cover,surface_pressure",
            "forecast_days": max(2, min((forecast_hours + 47) // 24, 16)),
            "timezone": "auto",
        }
        url = f"{self.base_url}/v1/forecast"
        payload = self._get_json(url, params)
        hourly = payload.get("hourly") or {}
        times = hourly.get("time") or []
        start_at = datetime.now().replace(minute=0, second=0, microsecond=0)
        result = []
        for index, forecast_time in enumerate(times):
            if len(result) >= forecast_hours:
                break
            forecast_at = self._parse_datetime(forecast_time)
            if forecast_at and forecast_at < start_at:
                continue
            weather_code = self._at(hourly.get("weather_code"), index)
            result.append(
                {
                    "time": forecast_time,
                    "date": forecast_time[:10],
                    "forecast_at": forecast_at,
                    "region": region,
                    "temperature": self._at(hourly.get("temperature_2m"), index),
                    "apparent_temperature": self._at(hourly.get("apparent_temperature"), index),
                    "rainfall": self._at(hourly.get("precipitation"), index),
                    "rain_probability": self._at(hourly.get("precipitation_probability"), index),
                    "humidity": self._at(hourly.get("relative_humidity_2m"), index),
                    "dew_point": self._at(hourly.get("dew_point_2m"), index),
                    "wind_speed": self._at(hourly.get("wind_speed_10m"), index),
                    "wind_gusts": self._at(hourly.get("wind_gusts_10m"), index),
                    "uv_index": self._at(hourly.get("uv_index"), index),
                    "visibility": self._at(hourly.get("visibility"), index),
                    "cloud_cover": self._at(hourly.get("cloud_cover"), index),
                    "pressure": self._at(hourly.get("surface_pressure"), index),
                    "weather_code": weather_code,
                    "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
                    "source_name": "Open-Meteo",
                    "source_url": url,
                    "is_realtime": len(result) == 0,
                    "is_mock": False,
                    "cache_status": "miss",
                    "last_updated": datetime.now(),
                }
            )
        return result

    def _get_json(self, url: str, params: dict[str, Any]) -> dict:
        last_error: Exception | None = None
        attempts = max(settings.WEATHER_RETRY_COUNT + 1, 1)
        for _ in range(attempts):
            try:
                with httpx.Client(timeout=settings.WEATHER_TIMEOUT_SECONDS) as client:
                    response = client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
        raise WeatherProviderError(f"Weather provider request failed: {last_error}") from last_error

    @staticmethod
    def _first(values: Any, fallback: Any = None) -> Any:
        if isinstance(values, list) and values:
            return values[0]
        return fallback

    @staticmethod
    def _at(values: Any, index: int) -> Any:
        if isinstance(values, list) and len(values) > index:
            return values[index]
        return None

    @staticmethod
    def _average(first: Any, second: Any) -> float | None:
        if first is None and second is None:
            return None
        if first is None:
            return float(second)
        if second is None:
            return float(first)
        return round((float(first) + float(second)) / 2, 1)

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    @staticmethod
    def _coordinates_for_region(region: str) -> dict[str, float]:
        try:
            configured = json.loads(settings.REGION_COORDINATES_JSON or "{}")
        except json.JSONDecodeError:
            configured = {}

        normalized_region = region.strip().lower()
        for name, coordinates in configured.items():
            if name.strip().lower() == normalized_region:
                return {
                    "latitude": float(coordinates["latitude"]),
                    "longitude": float(coordinates["longitude"]),
                }

        default = configured.get("Ha Noi") or {"latitude": 21.0285, "longitude": 105.8542}
        return {"latitude": float(default["latitude"]), "longitude": float(default["longitude"])}
