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
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,weather_code",
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
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,relative_humidity_2m_mean,weather_code,wind_speed_10m_max",
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
                    "humidity": self._at(daily.get("relative_humidity_2m_mean"), index),
                    "wind_speed": self._at(daily.get("wind_speed_10m_max"), index),
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
