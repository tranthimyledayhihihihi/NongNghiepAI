"""
Weather Service - merged Tien (repository + schema API) + Quang (mock data + forecast + warnings)
- API endpoints dùng: get_current_weather(db, region), create_weather(db, request)
- Internal: get_forecast, get_harvest_weather_warning
"""
import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.integrations.weather_client import WeatherClient
from app.repositories.weather_repository import create_weather_data, get_latest_weather, get_weather_forecast
from app.schemas.weather_schema import WeatherCreateRequest

_weather_client = WeatherClient()

# Bảng chuyển đổi tên ASCII → tên tiếng Việt chuẩn lưu trong DB
_REGION_NORMALIZE = {
    "ha noi": "Hà Nội", "hanoi": "Hà Nội", "ha_noi": "Hà Nội",
    "tp.hcm": "TP.HCM", "hcm": "TP.HCM", "ho chi minh": "TP.HCM",
    "tphcm": "TP.HCM", "sai gon": "TP.HCM",
    "da nang": "Đà Nẵng", "danang": "Đà Nẵng",
    "can tho": "Cần Thơ", "cantho": "Cần Thơ",
    "dak lak": "Đắk Lắk", "daklak": "Đắk Lắk",
    "lam dong": "Lâm Đồng", "lamdong": "Lâm Đồng",
    "gia lai": "Gia Lai",
    "tien giang": "Tiền Giang",
    "long an": "Long An",
    "binh thuan": "Bình Thuận",
}


def _normalize_region(region: str) -> str:
    """Trả về tên tỉnh chuẩn (có dấu) để khớp với DB."""
    key = region.strip().lower()
    return _REGION_NORMALIZE.get(key, region.strip())

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

    def get_current_weather(self, db: Session, region: str, force_refresh: bool = False) -> dict:
        """Lấy thời tiết hiện tại: Live API (Open-Meteo) → fallback DB → fallback mock."""
        region = _normalize_region(region)

        # ── 1. Gọi live API để lấy nhiệt độ thực tế theo giờ ──────────────
        try:
            live = _weather_client.get_current(region)
            now = datetime.now()
            temp = live.get("temperature")
            temp_min = live.get("temp_min")
            temp_max = live.get("temp_max")
            rain = live.get("rainfall") or 0.0
            hum = live.get("humidity") or 70.0
            return {
                "region":           region,
                "temperature":      temp,
                "temp_min":         temp_min,
                "temp_max":         temp_max,
                "rainfall":         rain,
                "humidity":         hum,
                "condition":        live.get("condition"),
                "wind_speed":       live.get("wind_speed"),
                "uv_index":         live.get("uv_index"),
                "pressure":         live.get("pressure"),
                "weather_code":     live.get("weather_code"),
                "latitude":         live.get("latitude"),
                "longitude":        live.get("longitude"),
                "recorded_at":      live.get("source_updated_at") or now,
                "source":           "Open-Meteo",
                "source_name":      "Open-Meteo",
                "source_url":       "https://open-meteo.com",
                "is_realtime":      True,
                "is_mock":          False,
                "last_updated":     now,
                "data_age_minutes": 0,
                "cache_status":     "live",
                "agriculture_insights": [],
                "warnings":         self._analyze_warnings(
                    temp_max or 30, temp_min or 20, rain, hum
                ),
            }
        except Exception:
            pass  # API lỗi → thử DB

        # ── 2. Fallback: đọc từ DB (crawler đã cào) ────────────────────────
        weather = get_latest_weather(db, region)
        if weather:
            temp_min = float(weather.TempMin) if weather.TempMin is not None else None
            temp_max = float(weather.TempMax) if weather.TempMax is not None else None
            temp_avg = None
            if temp_min is not None and temp_max is not None:
                temp_avg = round((temp_min + temp_max) / 2, 1)
            elif temp_max is not None:
                temp_avg = temp_max
            elif temp_min is not None:
                temp_avg = temp_min

            recorded = weather.CreatedAt if weather.CreatedAt else (
                datetime.combine(weather.RecordDate, datetime.min.time()) if weather.RecordDate else datetime.now()
            )
            age_min = int((datetime.now() - recorded).total_seconds() / 60)
            return {
                "region":           weather.Region,
                "temperature":      temp_avg,
                "temp_min":         temp_min,
                "temp_max":         temp_max,
                "rainfall":         float(weather.Rainfall) if weather.Rainfall is not None else None,
                "humidity":         float(weather.Humidity) if weather.Humidity is not None else None,
                "condition":        weather.WeatherDesc,
                "wind_speed":       float(weather.WindSpeed) if weather.WindSpeed is not None else None,
                "uv_index":         float(weather.UVIndex) if weather.UVIndex is not None else None,
                "pressure":         float(weather.Pressure) if weather.Pressure is not None else None,
                "weather_code":     weather.WeatherCode,
                "latitude":         float(weather.Latitude) if weather.Latitude is not None else None,
                "longitude":        float(weather.Longitude) if weather.Longitude is not None else None,
                "recorded_at":      recorded,
                "source":           "Open-Meteo",
                "source_name":      weather.SourceName or "Open-Meteo",
                "source_url":       "https://open-meteo.com",
                "is_realtime":      False,
                "is_mock":          False,
                "last_updated":     recorded,
                "data_age_minutes": age_min,
                "cache_status":     "db",
                "agriculture_insights": [],
                "warnings":         self._analyze_warnings(
                    temp_max or 30, temp_min or 20,
                    float(weather.Rainfall or 0), float(weather.Humidity or 70)
                ),
            }

        # ── 3. Fallback mock khi không có gì ───────────────────────────────
        mock = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        return {
            "region":           region,
            "temperature":      mock["temperature"],
            "temp_min":         mock.get("temp_min"),
            "temp_max":         mock.get("temp_max"),
            "rainfall":         mock["rainfall"],
            "humidity":         mock["humidity"],
            "condition":        mock["condition"],
            "wind_speed":       None,
            "uv_index":         None,
            "pressure":         None,
            "weather_code":     None,
            "latitude":         None,
            "longitude":        None,
            "recorded_at":      datetime.now(),
            "source":           "mock",
            "source_name":      "mock",
            "source_url":       None,
            "is_realtime":      False,
            "is_mock":          True,
            "last_updated":     datetime.now(),
            "data_age_minutes": 0,
            "cache_status":     "miss",
            "agriculture_insights": [],
            "warnings":         [],
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

    def get_forecast_from_db(self, db: Session, region: str, days: int = 7) -> dict:
        """Dự báo thời tiết từ WeatherData (Open-Meteo đã cào vào DB)."""
        rows = get_weather_forecast(db, region, days)
        if not rows:
            return {
                "region": region,
                "days_requested": days,
                "source": "no_data",
                "message": "Chưa có dữ liệu thời tiết. Crawler sẽ cập nhật trong vài phút.",
                "forecast": [],
            }

        forecast = []
        for w in rows:
            temp_avg = None
            if w.TempMin is not None and w.TempMax is not None:
                temp_avg = round((float(w.TempMin) + float(w.TempMax)) / 2, 1)
            rainfall = float(w.Rainfall) if w.Rainfall is not None else 0.0
            warnings = self._analyze_warnings(
                w.TempMax or 30, w.TempMin or 20, rainfall, w.Humidity or 70
            )
            forecast.append({
                "date":           str(w.RecordDate),
                "temp_min":       float(w.TempMin) if w.TempMin is not None else None,
                "temp_max":       float(w.TempMax) if w.TempMax is not None else None,
                "temp_avg":       temp_avg,
                "humidity":       float(w.Humidity) if w.Humidity is not None else None,
                "rainfall_mm":    round(rainfall, 1),
                "sunshine_hours": float(w.SunshineHours) if w.SunshineHours is not None else None,
                "weather_desc":   w.WeatherDesc or "Không xác định",
                "warnings":       warnings,
            })

        return {
            "region":        region,
            "days_requested": days,
            "days_available": len(forecast),
            "source":        "open_meteo",
            "forecast":      forecast,
        }

    def get_forecast(self, db: Session, region: str, days: int = 7) -> list[dict]:
        """Dự báo thời tiết N ngày tới — DB trước, fallback mock."""
        norm = _normalize_region(region)
        rows = get_weather_forecast(db, norm, days)
        if rows:
            result = []
            for w in rows[:days]:
                temp_max = float(w.TempMax or 30)
                temp_min = float(w.TempMin or 20)
                rain = float(w.Rainfall or 0)
                hum = float(w.Humidity or 70)
                result.append({
                    "date": str(w.RecordDate),
                    "temperature": round((temp_max + temp_min) / 2, 1),
                    "temp_min": temp_min,
                    "temp_max": temp_max,
                    "humidity": round(hum, 1),
                    "rainfall": round(rain, 1),
                    "condition": w.WeatherDesc or "Không xác định",
                    "warnings": self._analyze_warnings(temp_max, temp_min, rain, hum),
                })
            return result

        # Fallback mock khi chưa có dữ liệu DB
        base = MOCK_WEATHER.get(norm, MOCK_WEATHER["default"])
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

    def get_hourly_forecast(self, db: Session, region: str, hours: int = 24) -> list[dict]:
        """Dự báo theo giờ: Live API → fallback mock."""
        norm = _normalize_region(region)
        try:
            return _weather_client.get_hourly_forecast(norm, hours)
        except Exception:
            current = self.get_current_weather(db, norm)
            return self._build_hourly(current)[:hours]

    def get_harvest_weather_warning(self, db: Session, region: str) -> str | None:
        """Trả về chuỗi cảnh báo thời tiết ảnh hưởng đến thu hoạch."""
        w = self.get_current_weather(db, region)
        warnings = self._analyze_warnings(
            w.get("temp_max") or w.get("temperature") or 28,
            w.get("temp_min") or w.get("temperature") or 22,
            w.get("rainfall") or 0,
            w.get("humidity") or 70,
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
        """Public wrapper cho _build_activity_recommendations (dùng bởi API endpoint)."""
        return self._build_activity_recommendations(current, forecast, crop_name, growth_stage)

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


    # ------------------------------------------------------------------ #
    # Agriculture endpoint
    # ------------------------------------------------------------------ #

    def get_agriculture_weather(
        self,
        db: Session,
        region: str,
        crop_name: str | None = None,
        growth_stage: str | None = None,
        days: int = 7,
        include_hourly: bool = True,
    ) -> dict:
        current = self.get_current_weather(db, region)

        # Forecast 7 ngày
        db_forecast = get_weather_forecast(db, _normalize_region(region), days)
        forecast = self._build_daily_forecast(db_forecast, region, days, crop_name)

        # Alerts từ forecast
        alerts = self._build_alerts(forecast, crop_name, growth_stage)

        # Hourly mock (24h)
        hourly = self._build_hourly(current) if include_hourly else []

        # Activity recommendations
        activity_recs = self._build_activity_recommendations(current, forecast, crop_name, growth_stage)

        # AI/rule recommendation summary
        ai_rec = self._build_ai_recommendation(current, forecast, alerts, crop_name, growth_stage)

        data_flow = [
            "Open-Meteo API → crawler cào mỗi giờ → lưu vào SQL Server",
            "Backend tổng hợp dữ liệu DB + rule-based engine",
            "Sinh khuyến nghị canh tác theo cây trồng và giai đoạn",
        ]

        return {
            "module_name": "Thời tiết nông vụ thông minh",
            "region": _normalize_region(region),
            "crop_name": crop_name,
            "growth_stage": growth_stage,
            "current": current,
            "forecast": forecast,
            "hourly_forecast": hourly,
            "alerts": alerts,
            "activity_recommendations": activity_recs,
            "ai_recommendation": ai_rec,
            "data_flow": data_flow,
            "source_summary": {"source": "Open-Meteo", "url": "https://open-meteo.com"},
            "generated_at": datetime.now(),
        }

    # ------------------------------------------------------------------ #
    # Agriculture helpers
    # ------------------------------------------------------------------ #

    _DAY_LABELS = ["Hôm nay", "Ngày mai", "Ngày kia"]

    _CROP_ADVICE = {
        "lúa":       {"spray_rain_limit": 10, "water_temp_limit": 36, "cold_limit": 15},
        "cà phê":    {"spray_rain_limit": 8,  "water_temp_limit": 35, "cold_limit": 10},
        "hồ tiêu":   {"spray_rain_limit": 10, "water_temp_limit": 34, "cold_limit": 12},
        "rau màu":   {"spray_rain_limit": 5,  "water_temp_limit": 33, "cold_limit": 12},
        "cây ăn trái":{"spray_rain_limit":10, "water_temp_limit": 36, "cold_limit": 10},
    }

    def _crop_advice(self, crop_name: str | None) -> dict:
        if crop_name:
            return self._CROP_ADVICE.get(crop_name.lower(), self._CROP_ADVICE["lúa"])
        return self._CROP_ADVICE["lúa"]

    def _build_daily_forecast(self, rows, region: str, days: int, crop_name: str | None) -> list[dict]:
        advice = self._crop_advice(crop_name)
        result = []

        if rows:
            for i, w in enumerate(rows[:days]):
                rain = float(w.Rainfall or 0)
                temp_max = float(w.TempMax or 30)
                temp_min = float(w.TempMin or 20)
                humidity = float(w.Humidity or 70)
                wind = float(w.WindSpeed) if w.WindSpeed is not None else None
                rain_prob = min(100, int(rain / 0.3)) if rain > 0 else random.randint(5, 30)

                rec_parts = []
                if rain > advice["spray_rain_limit"]:
                    rec_parts.append("Không phun thuốc")
                if temp_max > advice["water_temp_limit"]:
                    rec_parts.append("Tăng lượng tưới")
                if humidity > 88:
                    rec_parts.append("Theo dõi nấm bệnh")
                if temp_min < advice["cold_limit"]:
                    rec_parts.append("Giữ ấm cho cây")
                if not rec_parts:
                    rec_parts.append("Thời tiết thuận lợi canh tác")

                result.append({
                    "date": str(w.RecordDate),
                    "day_label": self._DAY_LABELS[i] if i < len(self._DAY_LABELS) else "",
                    "temp_min": temp_min,
                    "temp_max": temp_max,
                    "rainfall": round(rain, 1),
                    "rain_probability": rain_prob,
                    "humidity": round(humidity, 1),
                    "wind_speed": round(wind, 1) if wind is not None else None,
                    "recommendation": " · ".join(rec_parts),
                })

        # Pad với mock khi DB có ít hơn days ngày
        if len(result) < days:
            base = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
            last_date = date.fromisoformat(result[-1]["date"]) if result else date.today() - timedelta(days=1)
            for i in range(days - len(result)):
                dt = (last_date + timedelta(days=i + 1)).isoformat()
                rain = max(0.0, base["rainfall"] + random.uniform(-5, 10))
                temp_max = round(base["temp_max"] + random.uniform(-1, 2), 1)
                temp_min = round(base["temp_min"] + random.uniform(-1, 1), 1)
                hum = round(min(100.0, max(30.0, base["humidity"] + random.uniform(-5, 5))), 1)
                rain_prob = min(100, int(rain / 0.3))

                rec_parts = []
                if rain > advice["spray_rain_limit"]:
                    rec_parts.append("Không phun thuốc")
                if temp_max > advice["water_temp_limit"]:
                    rec_parts.append("Tăng lượng tưới")
                if not rec_parts:
                    rec_parts.append("Thời tiết thuận lợi canh tác")

                idx = len(result)
                result.append({
                    "date": dt,
                    "day_label": self._DAY_LABELS[idx] if idx < len(self._DAY_LABELS) else "",
                    "temp_min": temp_min,
                    "temp_max": temp_max,
                    "rainfall": round(rain, 1),
                    "rain_probability": rain_prob,
                    "humidity": hum,
                    "wind_speed": None,
                    "recommendation": " · ".join(rec_parts),
                })
        return result

    def _build_hourly(self, current: dict) -> list[dict]:
        now = datetime.now()
        base_temp = current.get("temperature") or 28
        base_rain_prob = 20

        result = []
        for h in range(24):
            t = now + timedelta(hours=h)
            hour = t.hour
            # Nhiệt độ thấp hơn ban đêm
            variation = -3 if 0 <= hour < 6 else (2 if 10 <= hour <= 14 else 0)
            rain_p = base_rain_prob + (30 if 13 <= hour <= 17 else 0)
            rain_p = min(95, rain_p + random.randint(-5, 5))
            temp = round(base_temp + variation + random.uniform(-0.5, 0.5), 1)

            rec = "Thích hợp làm việc ngoài đồng"
            if rain_p > 60:
                rec = "Khả năng mưa cao · hạn chế phun thuốc"
            elif 10 <= hour <= 14:
                rec = "Nắng mạnh · tránh tưới lúc giữa trưa"
            elif 5 <= hour < 8:
                rec = "Sáng sớm · tốt nhất để phun thuốc"

            result.append({
                "forecast_at": t.isoformat(),
                "temperature": temp,
                "rain_probability": rain_p,
                "recommendation": rec,
            })
        return result

    def _build_alerts(self, forecast: list[dict], crop_name: str | None, growth_stage: str | None = None) -> list[dict]:
        alerts = []
        advice = self._crop_advice(crop_name)
        cold_limit = advice["cold_limit"] + (2 if growth_stage and "con" in growth_stage.lower() else 0)

        for item in forecast:
            temp_max = item.get("temp_max") or 30
            temp_min = item.get("temp_min") or 20
            rain = item.get("rainfall") or 0
            humidity = item.get("humidity") or 70
            dt = item.get("date", "")

            if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
                alerts.append({
                    "alert_type": "heat_stress",
                    "forecast_date": dt,
                    "title": f"Nắng nóng {temp_max:.0f}°C",
                    "message": "Nhiệt độ cao gây stress nhiệt cho cây trồng.",
                    "recommendation": "Tăng tần suất tưới, che phủ đất, tưới vào sáng sớm hoặc chiều mát.",
                    "severity": "high" if temp_max > 38 else "medium",
                })
            if temp_min < cold_limit:
                alerts.append({
                    "alert_type": "cold_stress",
                    "forecast_date": dt,
                    "title": f"Lạnh {temp_min:.0f}°C",
                    "message": "Nhiệt độ thấp có thể gây hại cho cây non và mầm hoa.",
                    "recommendation": "Phủ nilon giữ ấm, tưới nhẹ vào buổi sáng.",
                    "severity": "high" if temp_min < 10 else "medium",
                })
            if rain > ALERT_THRESHOLDS["rainfall_heavy"]:
                alerts.append({
                    "alert_type": "heavy_rain",
                    "forecast_date": dt,
                    "title": f"Mưa lớn {rain:.0f} mm",
                    "message": "Mưa lớn nguy cơ ngập úng và rửa trôi phân bón.",
                    "recommendation": "Kiểm tra hệ thống thoát nước, tạm hoãn bón phân.",
                    "severity": "high",
                })
            if humidity > ALERT_THRESHOLDS["humidity_high"]:
                alerts.append({
                    "alert_type": "high_humidity",
                    "forecast_date": dt,
                    "title": f"Độ ẩm cao {humidity:.0f}%",
                    "message": "Độ ẩm cao tạo điều kiện bùng phát nấm, vi khuẩn gây bệnh.",
                    "recommendation": "Phun phòng trừ nấm bệnh, đảm bảo thông thoáng.",
                    "severity": "medium",
                })

        # Loại bỏ trùng lặp theo (alert_type, forecast_date)
        seen = set()
        unique = []
        for a in alerts:
            key = (a["alert_type"], a["forecast_date"])
            if key not in seen:
                seen.add(key)
                unique.append(a)
        return unique

    def _build_activity_recommendations(
        self, current: dict, forecast: list[dict], crop_name: str | None, growth_stage: str | None
    ) -> list[dict]:
        temp = current.get("temperature") or 28
        rain = current.get("rainfall") or 0
        humidity = current.get("humidity") or 70
        wind = current.get("wind_speed") or 0
        advice = self._crop_advice(crop_name)
        stage = (growth_stage or "").lower()

        recs = []

        # Tưới
        if rain > advice["spray_rain_limit"]:
            recs.append({"action_type": "irrigation", "action": "Tưới nước", "decision": "Hoãn — đủ mưa",
                         "reason": f"Mưa {rain:.0f} mm đã đủ, tiết kiệm nước.", "priority": "low", "timing": ""})
        elif temp > advice["water_temp_limit"]:
            recs.append({"action_type": "irrigation", "action": "Tưới nước", "decision": "Tưới ngay",
                         "reason": f"Nắng nóng {temp:.0f}°C, cây cần nước gấp.", "priority": "high",
                         "timing": "Sáng sớm 5–7h hoặc chiều mát 17–19h"})
        else:
            recs.append({"action_type": "irrigation", "action": "Tưới nước", "decision": "Tưới theo lịch",
                         "reason": "Thời tiết bình thường, duy trì lịch tưới định kỳ.", "priority": "medium",
                         "timing": "Sáng sớm 5–7h"})

        # Phun thuốc
        if wind and wind > 25:
            recs.append({"action_type": "spraying", "action": "Phun thuốc", "decision": "Không nên",
                         "reason": f"Gió {wind:.0f} km/h làm thuốc bay ngoài ý muốn.", "priority": "low", "timing": ""})
        elif rain > advice["spray_rain_limit"]:
            recs.append({"action_type": "spraying", "action": "Phun thuốc", "decision": "Hoãn",
                         "reason": "Mưa sẽ rửa trôi thuốc, giảm hiệu quả.", "priority": "low", "timing": ""})
        else:
            recs.append({"action_type": "spraying", "action": "Phun thuốc", "decision": "Được phép",
                         "reason": "Điều kiện thích hợp để phun.", "priority": "medium",
                         "timing": "Sáng sớm 6–8h khi gió nhẹ"})

        # Bón phân
        rain3d = sum(f.get("rainfall") or 0 for f in forecast[:3]) / max(len(forecast[:3]), 1)
        if rain > 50:
            recs.append({"action_type": "fertilizing", "action": "Bón phân", "decision": "Hoãn",
                         "reason": "Mưa lớn sẽ rửa trôi phân bón.", "priority": "low", "timing": ""})
        elif rain3d < 5 and humidity < 50:
            recs.append({"action_type": "fertilizing", "action": "Bón phân", "decision": "Cân nhắc",
                         "reason": "Đất khô, phân dễ bị bay hơi — cần kết hợp tưới.", "priority": "medium",
                         "timing": "Bón kèm tưới nhỏ giọt"})
        else:
            recs.append({"action_type": "fertilizing", "action": "Bón phân", "decision": "Tốt",
                         "reason": "Độ ẩm phù hợp, phân dễ hòa tan và hấp thu.", "priority": "medium",
                         "timing": "Chiều mát 16–18h"})

        # Thu hoạch
        if stage in ("thu hoạch", "thu hoach"):
            if rain > 20:
                recs.append({"action_type": "harvest", "action": "Thu hoạch", "decision": "Hoãn",
                             "reason": "Mưa làm ướt nông sản, tăng nguy cơ hư hỏng.", "priority": "high",
                             "timing": "Chờ thời tiết khô 2–3 ngày"})
            else:
                recs.append({"action_type": "harvest", "action": "Thu hoạch", "decision": "Nên làm ngay",
                             "reason": "Thời tiết khô ráo, thuận lợi thu hoạch và phơi sấy.", "priority": "high",
                             "timing": "Sáng 7–11h"})

        return recs

    def _build_ai_recommendation(
        self, current: dict, forecast: list[dict], alerts: list[dict], crop_name: str | None, growth_stage: str | None
    ) -> dict:
        temp = current.get("temperature") or 28
        humidity = current.get("humidity") or 70
        rain = current.get("rainfall") or 0
        crop_label = crop_name or "cây trồng"
        stage_label = growth_stage or "hiện tại"
        high_alerts = [a for a in alerts if a["severity"] == "high"]

        if high_alerts:
            summary = (
                f"Thời tiết có {len(high_alerts)} cảnh báo nghiêm trọng trong 7 ngày tới. "
                f"Cần theo dõi chặt và có biện pháp bảo vệ {crop_label} giai đoạn {stage_label}."
            )
            risk = " | ".join(a["title"] for a in high_alerts[:3])
        elif temp > 35:
            summary = f"Nắng nóng kéo dài, {crop_label} giai đoạn {stage_label} cần tưới đủ nước và che mát."
            risk = f"Nhiệt độ cao {temp:.0f}°C có thể gây stress nhiệt."
        elif rain > 50:
            summary = f"Mưa nhiều trong tuần, ưu tiên kiểm tra thoát nước cho {crop_label}."
            risk = "Nguy cơ ngập úng và bệnh nấm khi mưa kéo dài."
        else:
            summary = f"Thời tiết tương đối thuận lợi cho {crop_label} giai đoạn {stage_label}."
            risk = "Không có rủi ro lớn. Duy trì chăm sóc theo lịch thông thường."

        avg_rain = sum(f.get("rainfall") or 0 for f in forecast) / max(len(forecast), 1)
        action_plan = [
            f"Nhiệt độ {temp:.0f}°C — {'tăng tưới, che mát' if temp > 35 else 'theo dõi bình thường'}",
            f"Độ ẩm {humidity:.0f}% — {'phòng nấm bệnh' if humidity > 85 else 'ổn định'}",
            f"Mưa TB 7 ngày {avg_rain:.1f} mm/ngày — {'hạn chế tưới' if avg_rain > 15 else 'duy trì tưới'}",
        ]
        if high_alerts:
            action_plan.append(f"Ưu tiên xử lý: {high_alerts[0]['recommendation']}")

        crop_note = None
        if crop_name:
            stage_notes = {
                "cây con": f"{crop_label} giai đoạn cây con rất nhạy cảm với nhiệt độ và độ ẩm.",
                "ra hoa": f"{crop_label} đang ra hoa — tránh phun thuốc và hạn chế tưới lá.",
                "làm đòng": f"{crop_label} đang làm đòng — đảm bảo đủ nước và dinh dưỡng.",
                "thu hoạch": f"{crop_label} sắp thu hoạch — chú ý thời tiết khô ráo để thu và phơi.",
            }
            crop_note = stage_notes.get((growth_stage or "").lower())

        return {
            "summary": summary,
            "risk_explanation": risk,
            "action_plan": action_plan,
            "crop_note": crop_note,
            "data_note": "Dữ liệu thời tiết từ Open-Meteo (nguồn mở, cập nhật mỗi giờ). Khuyến nghị dựa trên rule-based engine.",
        }


    def generate_alerts(self, _current: dict, forecast: list[dict], crop_name: str | None = None, growth_stage: str | None = None) -> list[dict]:
        """Public wrapper để dashboard_service có thể gọi được."""
        return self._build_alerts(forecast, crop_name=crop_name, growth_stage=growth_stage)


weather_service = WeatherService()
