"""
Weather Service - merged Tien (repository + schema API) + Quang (mock data + forecast + warnings)
- API endpoints dùng: get_current_weather(db, region), create_weather(db, request)
- Internal: get_forecast, get_harvest_weather_warning
"""
import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.weather_repository import create_weather_data, get_latest_weather
from app.schemas.weather_schema import WeatherCreateRequest

# Mock data theo vùng (Quang) - dùng khi không có dữ liệu DB
MOCK_WEATHER = {
    "default":  {"temperature": 28.0, "temp_min": 22, "temp_max": 32, "humidity": 75.0, "rainfall": 5.0, "sunshine_hours": 7, "condition": "partly_cloudy"},
    "Ha Noi":   {"temperature": 30.0, "temp_min": 24, "temp_max": 34, "humidity": 80.0, "rainfall": 3.0, "sunshine_hours": 6, "condition": "cloudy"},
    "TP.HCM":   {"temperature": 32.0, "temp_min": 25, "temp_max": 36, "humidity": 70.0, "rainfall": 0.0, "sunshine_hours": 9, "condition": "sunny"},
    "Da Nang":  {"temperature": 29.0, "temp_min": 23, "temp_max": 33, "humidity": 78.0, "rainfall": 8.0, "sunshine_hours": 7, "condition": "rainy"},
    "Can Tho":  {"temperature": 31.0, "temp_min": 24, "temp_max": 35, "humidity": 82.0, "rainfall": 10.0, "sunshine_hours": 6, "condition": "rainy"},
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

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def get_current_weather(self, db: Session, region: str) -> dict:
        """Lấy thời tiết hiện tại: DB qua repository → fallback mock."""
        weather = get_latest_weather(db, region)
        if weather:
            return {
                "region": getattr(weather, "region", region),
                "temperature": getattr(weather, "temperature", None),
                "rainfall": getattr(weather, "rainfall", None),
                "humidity": getattr(weather, "humidity", None),
                "condition": getattr(weather, "condition", None),
                "recorded_at": getattr(weather, "recorded_at", datetime.now()),
            }

        # Fallback mock
        mock = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        return {
            "region": region,
            "temperature": mock["temperature"],
            "rainfall": mock["rainfall"],
            "humidity": mock["humidity"],
            "condition": mock["condition"],
            "recorded_at": datetime.now(),
        }

    def create_weather(self, db: Session, request: WeatherCreateRequest) -> dict:
        """Tạo bản ghi thời tiết mới."""
        weather = create_weather_data(db, **request.model_dump())
        return {
            "region": request.region,
            "temperature": request.temperature,
            "rainfall": request.rainfall,
            "humidity": request.humidity,
            "condition": request.condition,
            "recorded_at": getattr(weather, "recorded_at", None) or datetime.now(),
        }

    # ------------------------------------------------------------------ #
    # Extra methods (Quang) - dùng bởi harvest_service, tasks, v.v.
    # ------------------------------------------------------------------ #

    def get_forecast(self, _db: Session, region: str, days: int = 7) -> list[dict]:
        """Dự báo thời tiết N ngày tới (mock với biến động nhỏ)."""
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
            })
        return result

    def get_harvest_weather_warning(self, db: Session, region: str) -> str | None:
        """Trả về chuỗi cảnh báo thời tiết ảnh hưởng đến thu hoạch."""
        w = self.get_current_weather(db, region)
        warnings = self._analyze_warnings(
            w.get("temperature") or 28,
            w.get("temperature") or 22,
            w.get("rainfall") or 0,
            w.get("humidity") or 70,
        )
        return " | ".join(warnings) if warnings else None

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

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
