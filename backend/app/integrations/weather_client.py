import json
import unicodedata
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


WEATHER_CODE_LABELS = {
    0: "Trời quang",
    1: "Ít mây",
    2: "Có mây",
    3: "Nhiều mây",
    45: "Sương mù",
    48: "Sương mù đóng băng",
    51: "Mưa phùn nhẹ",
    53: "Mưa phùn vừa",
    55: "Mưa phùn dày",
    61: "Mưa nhỏ",
    63: "Mưa vừa",
    65: "Mưa to",
    71: "Tuyết nhẹ",
    73: "Tuyết vừa",
    75: "Tuyết to",
    80: "Mưa rào nhẹ",
    81: "Mưa rào vừa",
    82: "Mưa rào to",
    95: "Giông bão",
    96: "Giông, có mưa đá nhỏ",
    99: "Giông, có mưa đá lớn",
}


DEFAULT_REGION_COORDINATES = {
    "Ha Noi": {"latitude": 21.0285, "longitude": 105.8542},
    "TP.HCM": {"latitude": 10.8231, "longitude": 106.6297},
    "Da Nang": {"latitude": 16.0544, "longitude": 108.2022},
    "Can Tho": {"latitude": 10.0452, "longitude": 105.7469},
    "Lam Dong": {"latitude": 11.9404, "longitude": 108.4583},
    "Hai Phong": {"latitude": 20.8449, "longitude": 106.6881},
    "Dak Lak": {"latitude": 12.6667, "longitude": 108.0500},
    "Gia Lai": {"latitude": 13.9833, "longitude": 108.0000},
    "Tien Giang": {"latitude": 10.3600, "longitude": 106.3600},
    "Long An": {"latitude": 10.5400, "longitude": 106.4100},
    "Binh Thuan": {"latitude": 10.9280, "longitude": 108.1000},
}


REGION_ALIASES = {
    "hanoi": "Ha Noi",
    "ha noi": "Ha Noi",
    "ha_noi": "Ha Noi",
    "ha-noi": "Ha Noi",
    "tp hcm": "TP.HCM",
    "tp.hcm": "TP.HCM",
    "tphcm": "TP.HCM",
    "hcm": "TP.HCM",
    "ho chi minh": "TP.HCM",
    "ho-chi-minh": "TP.HCM",
    "sai gon": "TP.HCM",
    "saigon": "TP.HCM",
    "da nang": "Da Nang",
    "danang": "Da Nang",
    "can tho": "Can Tho",
    "cantho": "Can Tho",
    "lam dong": "Lam Dong",
    "lamdong": "Lam Dong",
    "hai phong": "Hai Phong",
    "haiphong": "Hai Phong",
    "dak lak": "Dak Lak",
    "daklak": "Dak Lak",
    "gia lai": "Gia Lai",
    "tien giang": "Tien Giang",
    "tiengiang": "Tien Giang",
    "long an": "Long An",
    "longan": "Long An",
    "binh thuan": "Binh Thuan",
    "binhthuan": "Binh Thuan",
}


def normalize_location_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_value = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    for char in "._,-/":
        ascii_value = ascii_value.replace(char, " ")
    return " ".join(ascii_value.split())


def canonical_region_name(region: str) -> str:
    key = normalize_location_key(region)
    return REGION_ALIASES.get(key, region.strip())


class WeatherClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.OPEN_METEO_BASE_URL).rstrip("/")
        self.geocoding_base_url = "https://geocoding-api.open-meteo.com"

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
                    "uv_index",
                ]
            ),
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,weather_code,uv_index_max,sunshine_duration",
            "timezone": "Asia/Ho_Chi_Minh",
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
            "weather_desc": WEATHER_CODE_LABELS.get(weather_code, "Không xác định"),
            "weather_code": weather_code,
            "wind_speed": current.get("wind_speed_10m"),
            "uv_index": current.get("uv_index"),
            "uv_index_max": self._first(daily.get("uv_index_max")),
            "pressure": current.get("pressure_msl"),
            "sunshine_hours": self._sunshine_hours(self._first(daily.get("sunshine_duration"))),
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
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_max,relative_humidity_2m_mean,weather_code,wind_speed_10m_max,uv_index_max,sunshine_duration",
            "forecast_days": forecast_days,
            "timezone": "Asia/Ho_Chi_Minh",
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
                    "sunshine_hours": self._sunshine_hours(self._at(daily.get("sunshine_duration"), index)),
                    "weather_code": weather_code,
                    "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
                    "weather_desc": WEATHER_CODE_LABELS.get(weather_code, "Không xác định"),
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
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m,uv_index",
            "forecast_days": max(2, min((forecast_hours + 47) // 24, 16)),
            "timezone": "Asia/Ho_Chi_Minh",
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
                    "rainfall": self._at(hourly.get("precipitation"), index),
                    "rain_probability": self._at(hourly.get("precipitation_probability"), index),
                    "humidity": self._at(hourly.get("relative_humidity_2m"), index),
                    "wind_speed": self._at(hourly.get("wind_speed_10m"), index),
                    "uv_index": self._at(hourly.get("uv_index"), index),
                    "weather_code": weather_code,
                    "condition": WEATHER_CODE_CONDITIONS.get(weather_code, "unknown"),
                    "weather_desc": WEATHER_CODE_LABELS.get(weather_code, "Không xác định"),
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
                    response = client.get(
                        url,
                        params=params,
                        headers={
                            "Cache-Control": "no-cache",
                            "Pragma": "no-cache",
                        },
                    )
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
    def _sunshine_hours(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return round(float(value) / 3600, 1)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def _coordinates_for_region(self, region: str) -> dict[str, float]:
        try:
            configured = json.loads(settings.REGION_COORDINATES_JSON or "{}")
        except json.JSONDecodeError:
            configured = {}

        all_coordinates = {**DEFAULT_REGION_COORDINATES, **configured}
        canonical_region = canonical_region_name(region)
        accepted_keys = {
            normalize_location_key(region),
            normalize_location_key(canonical_region),
        }

        for name, coordinates in all_coordinates.items():
            if normalize_location_key(name) in accepted_keys:
                return {
                    "latitude": float(coordinates["latitude"]),
                    "longitude": float(coordinates["longitude"]),
                }

        geocoded = self._geocode_region(region)
        if geocoded:
            return geocoded

        raise WeatherProviderError(f"Không tìm thấy tọa độ cho khu vực: {region}")

    def _geocode_region(self, region: str) -> dict[str, float] | None:
        url = f"{self.geocoding_base_url}/v1/search"
        params = {
            "name": region,
            "count": 5,
            "language": "vi",
            "format": "json",
            "countryCode": "VN",
        }
        payload = self._get_json(url, params)
        results = payload.get("results") or []
        if not results:
            return None
        first = results[0]
        if first.get("latitude") is None or first.get("longitude") is None:
            return None
        return {
            "latitude": float(first["latitude"]),
            "longitude": float(first["longitude"]),
        }
