"""
Weather Service - merged Tien (repository + schema API) + Quang (mock data + forecast + warnings)
- API endpoints dùng: get_current_weather(db, region), create_weather(db, request)
- Internal: get_forecast, get_harvest_weather_warning
"""
import logging
import unicodedata
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.real_data import (
    OPEN_METEO_FORECAST_URL,
    OPEN_METEO_SOURCE_NAME,
    age_minutes,
    cache_status_for,
    is_real_cache_record,
    realtime_error,
)
from app.core.resilience import ExternalServiceError
from app.integrations.weather_client import WeatherClient
from app.repositories.weather_repository import (
    create_weather_data,
    get_cached_hourly_forecasts,
    get_latest_weather,
    get_weather_forecast,
    upsert_weather_forecast_cache,
    upsert_weather_cache,
)
from app.schemas.weather_schema import WeatherCreateRequest

_weather_client = WeatherClient()
logger = logging.getLogger(__name__)

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

# Removed MOCK_WEATHER (no mock data allowed per spec)

ALERT_THRESHOLDS = {
    "temp_max_high": 35,
    "temp_min_cold": 12,
    "rainfall_heavy": 100,
    "humidity_high": 92,
    "humidity_low": 30,
}


class WeatherService:

    @staticmethod
    def _miss_weather_error(region: str, missing_part: str, *, detail: str | None = None) -> dict:
        return {
            "_api_error": True,
            "error_code": "REALTIME_WEATHER_FAILED",
            "error_message": f"Không thể tải dữ liệu thời tiết thực tế ({missing_part}).",
            "region": _normalize_region(region),
            "source_name": OPEN_METEO_SOURCE_NAME,
            "source_url": OPEN_METEO_FORECAST_URL,
            "is_realtime": False,
            "is_mock": False,
            "cache_status": "miss",
            "detail": detail,
        }

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def get_current_weather(self, db: Session, region: str, force_refresh: bool = False) -> dict:
        """Weather current request-time behavior (spec compliant).

        - Không mock.
        - Nếu DB cache còn fresh/stale => trả ngay.
        - Chỉ khi cache miss (hết hạn vượt staleTTL) hoặc force_refresh => thử realtime.
        - Nếu realtime lỗi => trả payload error với cache_status='miss', is_mock=False.
        """
        region = _normalize_region(region)

        cached_weather = get_latest_weather(db, region)
        if cached_weather and not cached_weather.IsMock:
            cached = self._weather_row_to_current(cached_weather, fallback_used=False)
            fetched_at = cached.get("fetched_at") or cached.get("last_updated")
            status = cache_status_for(fetched_at, "weather_current")
            if status in {"fresh_cache", "stale_cache"} and not force_refresh:
                cached["cache_status"] = status
                if status == "stale_cache":
                    cached["warning"] = "Dữ liệu thời tiết realtime chậm, đang hiển thị cache thật gần nhất."
                return cached
            # else: stale beyond TTL => miss => fallthrough to realtime attempt

        if not force_refresh:
            payload = realtime_error(
                code="WEATHER_CACHE_MISS",
                message="Weather cache miss. Background refresh has not fetched fresh real data yet.",
                source_name=OPEN_METEO_SOURCE_NAME,
                source_url=OPEN_METEO_FORECAST_URL,
            )
            payload["region"] = region
            return payload

        # Explicit refresh/background path => try realtime.
        try:
            live = _weather_client.get_current(region)
            now = datetime.now()

            temp = live.get("temperature")
            temp_min = live.get("temp_min")
            temp_max = live.get("temp_max")
            rain = live.get("rainfall") or 0.0
            hum = live.get("humidity") or 70.0

            upsert_weather_cache(
                db,
                region=region,
                record_date=date.today(),
                temp_min=temp_min,
                temp_max=temp_max,
                rainfall=rain,
                humidity=hum,
                condition=live.get("condition"),
                latitude=live.get("latitude"),
                longitude=live.get("longitude"),
                wind_speed=live.get("wind_speed"),
                uv_index=live.get("uv_index"),
                pressure=live.get("pressure"),
                weather_code=live.get("weather_code"),
                source_name=live.get("source_name") or OPEN_METEO_SOURCE_NAME,
                source_url=live.get("source_url") or OPEN_METEO_FORECAST_URL,
                source_updated_at=live.get("source_updated_at") or now,
                fetched_at=now,
                is_realtime=True,
                is_mock=False,
            )
            return {
                "region": region,
                "temperature": temp,
                "temp_min": temp_min,
                "temp_max": temp_max,
                "rainfall": rain,
                "humidity": hum,
                "condition": live.get("condition"),
                "wind_speed": live.get("wind_speed"),
                "uv_index": live.get("uv_index"),
                "pressure": live.get("pressure"),
                "weather_code": live.get("weather_code"),
                "latitude": live.get("latitude"),
                "longitude": live.get("longitude"),
                "recorded_at": live.get("source_updated_at") or now,
                "source": "realtime_api",
                "source_name": live.get("source_name") or OPEN_METEO_SOURCE_NAME,
                "source_url": live.get("source_url") or OPEN_METEO_FORECAST_URL,
                "is_realtime": True,
                "is_mock": False,
                "fetched_at": now,
                "last_updated": now,
                "data_age_minutes": 0,
                "cache_status": "live",
                "fallback_used": False,
                "timeout": False,
                "agriculture_insights": [],
                "warnings": self._analyze_warnings(temp_max or 30, temp_min or 20, rain, hum),
            }
        except Exception as exc:
            # realtime miss => ERROR (no mock fallback)
            payload = realtime_error(
                code="REALTIME_WEATHER_FAILED",
                message="Không thể tải dữ liệu thời tiết thực tế từ Open-Meteo.",
                source_name=OPEN_METEO_SOURCE_NAME,
                source_url=OPEN_METEO_FORECAST_URL,
                detail=str(exc),
            )
            payload["region"] = region
            payload["is_realtime"] = False
            payload["is_mock"] = False
            payload["cache_status"] = "miss"
            return payload

    @staticmethod
    def _realtime_only() -> bool:
        return bool(settings.USE_REALTIME_ONLY) and not bool(settings.ALLOW_MOCK_DATA or settings.ALLOW_SAMPLE_DATA)

    def _weather_row_to_current(self, weather, *, fallback_used: bool) -> dict:
        temp_min = float(weather.TempMin) if weather.TempMin is not None else None
        temp_max = float(weather.TempMax) if weather.TempMax is not None else None
        temp_avg = None
        if temp_min is not None and temp_max is not None:
            temp_avg = round((temp_min + temp_max) / 2, 1)
        elif temp_max is not None:
            temp_avg = temp_max
        elif temp_min is not None:
            temp_avg = temp_min

        recorded = weather.FetchedAt or weather.SourceUpdatedAt or weather.CreatedAt or (
            datetime.combine(weather.RecordDate, datetime.min.time()) if weather.RecordDate else datetime.now()
        )
        age_min = int((datetime.now() - recorded).total_seconds() / 60)
        rainfall = float(weather.Rainfall or 0)
        humidity = float(weather.Humidity or 70)
        return {
            "region": weather.Region,
            "temperature": temp_avg,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rainfall": float(weather.Rainfall) if weather.Rainfall is not None else None,
            "humidity": float(weather.Humidity) if weather.Humidity is not None else None,
            "condition": weather.WeatherDesc,
            "wind_speed": float(weather.WindSpeed) if weather.WindSpeed is not None else None,
            "uv_index": float(weather.UVIndex) if weather.UVIndex is not None else None,
            "pressure": float(weather.Pressure) if weather.Pressure is not None else None,
            "weather_code": weather.WeatherCode,
            "latitude": float(weather.Latitude) if weather.Latitude is not None else None,
            "longitude": float(weather.Longitude) if weather.Longitude is not None else None,
            "recorded_at": recorded,
            "source": "cached",
            "source_name": weather.SourceName or OPEN_METEO_SOURCE_NAME,
            "source_url": weather.SourceURL or OPEN_METEO_FORECAST_URL,
            "is_realtime": False,
            "is_mock": False,
            "fetched_at": recorded,
            "last_updated": recorded,
            "data_age_minutes": age_min,
            "cache_status": cache_status_for(recorded, "weather_current"),
            "fallback_used": fallback_used,
            "timeout": False,
            "agriculture_insights": [],
            "warnings": self._analyze_warnings(temp_max or 30, temp_min or 20, rainfall, humidity),
        }

    @staticmethod
    def _is_weather_fresh(updated_at) -> bool:
        if not updated_at:
            return False
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                return False
        try:
            return (datetime.now() - updated_at).total_seconds() <= settings.WEATHER_CACHE_TTL_SECONDS
        except TypeError:
            return False

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

    # NOTE: duplicate get_forecast removed: mock fallback no longer allowed

    def get_hourly_forecast(self, db: Session, region: str, hours: int = 24, force_refresh: bool = False) -> dict:
        """Hourly: Open-Meteo realtime → DB cache thật.

        Vì DB hiện tại chỉ có `WeatherData` (không có bảng hourly riêng), phần DB cache hourly
        được lấy từ record `WeatherData` gần nhất và map sang cấu trúc hourly tối giản.

        Rule:
        - Có cache (fresh/stale) => trả dữ liệu cache, is_realtime=false, is_mock=false.
        - Không có cache + Open-Meteo lỗi => trả payload error theo spec.
        - Không dùng mock.
        """
        norm = _normalize_region(region)

        # 1) DB cache (WeatherForecasts) thật — chỉ dùng nếu còn fresh/stale và không force_refresh
        if not force_refresh:
            hourly_rows = get_cached_hourly_forecasts(db, norm, hours)
            if hourly_rows:
                fetched_values = [row.FetchedAt for row in hourly_rows if row.FetchedAt]
                fetched = max(fetched_values) if fetched_values else datetime.now()
                cache_status = cache_status_for(fetched, "weather_hourly")
                if cache_status in {"fresh_cache", "stale_cache"}:
                    forecast_items = []
                    for row in hourly_rows[:hours]:
                        item_fetched = row.FetchedAt or fetched
                        forecast_items.append(
                            {
                                "time": (row.ForecastAt or row.ForecastDate).isoformat(),
                                "date": row.ForecastDate.isoformat(),
                                "forecast_at": row.ForecastAt,
                                "region": norm,
                                "temperature": float(row.Temperature) if row.Temperature is not None else None,
                                "apparent_temperature": float(row.ApparentTemperature) if row.ApparentTemperature is not None else None,
                                "rainfall": float(row.Rainfall) if row.Rainfall is not None else None,
                                "rain_probability": float(row.RainProbability) if row.RainProbability is not None else None,
                                "humidity": float(row.Humidity) if row.Humidity is not None else None,
                                "dew_point": float(row.DewPoint) if row.DewPoint is not None else None,
                                "wind_speed": float(row.WindSpeed) if row.WindSpeed is not None else None,
                                "wind_gusts": float(row.WindGusts) if row.WindGusts is not None else None,
                                "uv_index": float(row.UVIndex) if row.UVIndex is not None else None,
                                "visibility": float(row.Visibility) if row.Visibility is not None else None,
                                "cloud_cover": float(row.CloudCover) if row.CloudCover is not None else None,
                                "pressure": float(row.Pressure) if row.Pressure is not None else None,
                                "condition": row.WeatherDesc,
                                "weather_code": row.WeatherCode,
                                "recommendation": row.Recommendation,
                                "source_name": row.SourceName or OPEN_METEO_SOURCE_NAME,
                                "source_url": row.SourceURL or OPEN_METEO_FORECAST_URL,
                                "is_realtime": False,
                                "is_mock": False,
                                "cache_status": cache_status_for(item_fetched, "weather_hourly"),
                                "fetched_at": item_fetched,
                                "last_updated": item_fetched,
                                "data_age_minutes": age_minutes(item_fetched),
                            }
                        )
                    return {
                        "region": norm,
                        "hours": hours,
                        "forecast": forecast_items,
                        "source_name": hourly_rows[0].SourceName or OPEN_METEO_SOURCE_NAME,
                        "source_url": hourly_rows[0].SourceURL or OPEN_METEO_FORECAST_URL,
                        "is_realtime": False,
                        "is_mock": False,
                        "cache_status": cache_status,
                        "fetched_at": fetched,
                        "last_updated": fetched,
                        "data_age_minutes": age_minutes(fetched),
                    }

        # 2) Cache miss hoặc force_refresh — gọi Open-Meteo trực tiếp
        try:
            live_items = _weather_client.get_hourly_forecast(norm, hours)
            if not live_items:
                raise ExternalServiceError("Open-Meteo hourly empty payload")

            now = datetime.now()
            rep = live_items[0] if live_items else {}
            upsert_weather_cache(
                db,
                region=norm,
                record_date=date.today(),
                temp_min=rep.get("temp_min") or rep.get("temperature") or None,
                temp_max=rep.get("temp_max") or rep.get("temperature") or None,
                rainfall=rep.get("rainfall"),
                humidity=rep.get("humidity"),
                condition=rep.get("condition"),
                latitude=rep.get("latitude"),
                longitude=rep.get("longitude"),
                wind_speed=rep.get("wind_speed"),
                uv_index=rep.get("uv_index"),
                pressure=rep.get("pressure"),
                weather_code=rep.get("weather_code"),
                source_name=rep.get("source_name") or OPEN_METEO_SOURCE_NAME,
                source_url=rep.get("source_url") or OPEN_METEO_FORECAST_URL,
                source_updated_at=rep.get("last_updated") or now,
                fetched_at=now,
                is_realtime=True,
                is_mock=False,
            )
            for item in live_items[:hours]:
                forecast_at = item.get("forecast_at")
                if isinstance(forecast_at, str):
                    try:
                        forecast_at = datetime.fromisoformat(forecast_at.replace("Z", "+00:00")).replace(tzinfo=None)
                    except ValueError:
                        forecast_at = None
                forecast_at = forecast_at or now
                upsert_weather_forecast_cache(
                    db,
                    region=norm,
                    forecast_date=forecast_at.date(),
                    forecast_at=forecast_at,
                    forecast_type="hourly",
                    temperature=item.get("temperature"),
                    apparent_temperature=item.get("apparent_temperature"),
                    humidity=item.get("humidity"),
                    dew_point=item.get("dew_point"),
                    rainfall=item.get("rainfall"),
                    rain_probability=item.get("rain_probability"),
                    wind_speed=item.get("wind_speed"),
                    wind_gusts=item.get("wind_gusts"),
                    uv_index=item.get("uv_index"),
                    visibility=item.get("visibility"),
                    cloud_cover=item.get("cloud_cover"),
                    pressure=item.get("pressure"),
                    weather_code=item.get("weather_code"),
                    condition=item.get("condition"),
                    source_name=item.get("source_name") or OPEN_METEO_SOURCE_NAME,
                    source_url=item.get("source_url") or OPEN_METEO_FORECAST_URL,
                    source_updated_at=forecast_at,
                    fetched_at=now,
                    is_realtime=True,
                    is_mock=False,
                )

            return {
                "region": norm,
                "hours": hours,
                "forecast": [
                    {
                        **item,
                        "source_name": item.get("source_name") or OPEN_METEO_SOURCE_NAME,
                        "source_url": item.get("source_url") or OPEN_METEO_FORECAST_URL,
                        "is_realtime": True,
                        "is_mock": False,
                        "cache_status": "live",
                        "fetched_at": now,
                        "last_updated": now,
                        "data_age_minutes": 0,
                    }
                    for item in live_items[:hours]
                ],
                "source_name": OPEN_METEO_SOURCE_NAME,
                "source_url": OPEN_METEO_FORECAST_URL,
                "is_realtime": True,
                "is_mock": False,
                "cache_status": "live",
                "fetched_at": now,
                "last_updated": now,
                "data_age_minutes": 0,
            }
        except Exception as exc:
            payload = realtime_error(
                code="REALTIME_WEATHER_FAILED",
                message="Không thể tải dữ liệu thời tiết thực tế từ Open-Meteo.",
                source_name=OPEN_METEO_SOURCE_NAME,
                source_url=OPEN_METEO_FORECAST_URL,
                detail=str(exc),
            )
            payload.update({
                "is_mock": False,
                "cache_status": "miss",
                "data_age_minutes": None,
                "region": norm,
            })
            return payload


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
        hourly = _hourly.get("forecast", []) if isinstance(_hourly, dict) else (_hourly or [])
        return self._build_activity_recommendations(current, forecast, crop_name, growth_stage, hourly)

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
        if current.get("_api_error"):
            # Cache miss — try a live fetch before giving up
            current = self.get_current_weather(db, region, force_refresh=True)
        if current.get("_api_error"):
            return current

        # Forecast 7 ngày (DB cache thật)
        forecast = self.get_forecast(db, region, days)

        if not forecast:
            return self._miss_weather_error(region, "forecast_7_days")

        # Alerts từ forecast
        alerts = self._build_alerts(forecast, crop_name, growth_stage)

        hourly_bundle = self.get_hourly_forecast(db, region, 168) if include_hourly else {"forecast": []}
        hourly = hourly_bundle.get("forecast", []) if isinstance(hourly_bundle, dict) else hourly_bundle

        # Activity recommendations
        activity_recs = self._build_activity_recommendations(current, forecast, crop_name, growth_stage, hourly)

        # AI/rule recommendation summary
        ai_rec = self._build_ai_recommendation(current, forecast, alerts, crop_name, growth_stage, activity_recs)

        data_flow = [
            "Open-Meteo cung cấp thời tiết hiện tại, dự báo 7 ngày và dự báo từng giờ",
            "Backend chuẩn hóa nhiệt độ, mưa, xác suất mưa, gió, UV, độ ẩm và trạng thái cache",
            "AI thời tiết sinh cảnh báo và lịch canh tác theo cây trồng, giai đoạn sinh trưởng",
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
        "lua": {"spray_rain_limit": 10, "water_temp_limit": 36, "cold_limit": 15},
        "ca phe": {"spray_rain_limit": 8, "water_temp_limit": 35, "cold_limit": 10},
        "ho tieu": {"spray_rain_limit": 10, "water_temp_limit": 34, "cold_limit": 12},
        "rau mau": {"spray_rain_limit": 5, "water_temp_limit": 33, "cold_limit": 12},
        "cay an trai": {"spray_rain_limit": 10, "water_temp_limit": 36, "cold_limit": 10},
    }

    @staticmethod
    def _text_key(value: str | None) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFD", value.strip().lower())
        without_marks = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        return " ".join(without_marks.replace("đ", "d").split())

    def _crop_advice(self, crop_name: str | None) -> dict:
        if crop_name:
            return self._CROP_ADVICE.get(self._text_key(crop_name), self._CROP_ADVICE["lua"])
        return self._CROP_ADVICE["lua"]

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
                rain_prob = min(100, int(rain / 0.3)) if rain > 0 else 0

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

        # If DB has fewer days than requested, return only available real data (no mock padding).
        return result

    def _build_hourly(self, current: dict) -> list[dict]:
        """Tối ưu: không sinh dữ liệu giờ bằng random (không mock).
        Nếu cần hourly, hãy lấy từ DB Open-Meteo crawler hoặc gọi realtime hourly API.
        """
        return []

    @staticmethod
    def _num(value, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _dt(value) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def _day_label(self, forecast_date: str | date | None) -> str:
        if not forecast_date:
            return ""
        try:
            value = date.fromisoformat(str(forecast_date)[:10])
        except ValueError:
            return str(forecast_date)
        today = date.today()
        diff = (value - today).days
        if diff == 0:
            return "hôm nay"
        if diff == 1:
            return "ngày mai"
        if diff == 2:
            return "ngày kia"
        return value.strftime("%d/%m")

    def _format_window(self, start: datetime, end: datetime) -> str:
        if start.date() == end.date():
            return f"{start.strftime('%d/%m %H:%M')}–{end.strftime('%H:%M')}"
        return f"{start.strftime('%d/%m %H:%M')}–{end.strftime('%d/%m %H:%M')}"

    def _find_hour_window(
        self,
        hourly: list[dict] | None,
        *,
        hours_needed: int = 2,
        max_lookahead_hours: int = 72,
        max_rain_probability: float = 30,
        max_rainfall: float = 0.2,
        max_wind: float = 18,
        max_uv: float | None = None,
        min_temp: float | None = None,
        max_temp: float | None = None,
    ) -> str | None:
        if not hourly:
            return None

        ordered = sorted(
            hourly[:max_lookahead_hours],
            key=lambda item: self._dt(item.get("forecast_at") or item.get("time")) or datetime.max,
        )
        run: list[dict] = []
        for item in ordered:
            temp = self._num(item.get("temperature"), 28)
            rain_probability = self._num(item.get("rain_probability"), 0)
            rainfall = self._num(item.get("rainfall"), 0)
            wind = self._num(item.get("wind_speed"), 0)
            uv = self._num(item.get("uv_index"), 0)
            ok = (
                rain_probability <= max_rain_probability
                and rainfall <= max_rainfall
                and wind <= max_wind
                and (max_uv is None or uv <= max_uv)
                and (min_temp is None or temp >= min_temp)
                and (max_temp is None or temp <= max_temp)
            )
            if ok:
                run.append(item)
                if len(run) >= hours_needed:
                    start = self._dt(run[0].get("forecast_at") or run[0].get("time"))
                    last = self._dt(run[hours_needed - 1].get("forecast_at") or run[hours_needed - 1].get("time"))
                    if start and last:
                        return self._format_window(start, last + timedelta(hours=1))
            else:
                run = []
        return None

    @staticmethod
    def _is_thunderstorm(item: dict) -> bool:
        return item.get("weather_code") in {95, 96, 99} or item.get("condition") == "thunderstorm"

    def _build_alerts(self, forecast: list[dict], crop_name: str | None, growth_stage: str | None = None) -> list[dict]:
        alerts = []
        advice = self._crop_advice(crop_name)
        stage_key = self._text_key(growth_stage)
        cold_limit = advice["cold_limit"] + (2 if "con" in stage_key else 0)

        for item in forecast:
            temp_max = self._num(item.get("temp_max"), 30)
            temp_min = self._num(item.get("temp_min"), 20)
            rain = self._num(item.get("rainfall"), 0)
            rain_probability = self._num(item.get("rain_probability"), 0)
            humidity = self._num(item.get("humidity"), 70)
            wind = self._num(item.get("wind_speed"), 0)
            uv = self._num(item.get("uv_index"), 0)
            dt = item.get("date", "")
            day_label = self._day_label(dt)

            if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
                alerts.append({
                    "alert_type": "heat_stress",
                    "forecast_date": dt,
                    "title": f"Nắng nóng {temp_max:.0f}°C",
                    "message": f"Open-Meteo dự báo nhiệt độ tối đa {day_label} vượt ngưỡng chịu nóng của cây.",
                    "recommendation": "Tăng tưới vào sáng sớm/chiều mát, phủ gốc và che lưới cho cây non.",
                    "severity": "high" if temp_max > 38 else "medium",
                    "trigger_value": temp_max,
                    "trigger_unit": "°C",
                    "source": "open_meteo_rule",
                })
            if temp_min < cold_limit:
                alerts.append({
                    "alert_type": "cold_stress",
                    "forecast_date": dt,
                    "title": f"Lạnh {temp_min:.0f}°C",
                    "message": f"Nhiệt độ thấp {day_label} có thể làm chậm sinh trưởng, nhất là giai đoạn cây con.",
                    "recommendation": "Phủ nilon/rơm giữ ấm, tưới nhẹ buổi sáng và tránh bón đạm mạnh.",
                    "severity": "high" if temp_min < 10 else "medium",
                    "trigger_value": temp_min,
                    "trigger_unit": "°C",
                    "source": "open_meteo_rule",
                })
            if rain >= 50 or (rain_probability >= 80 and rain >= advice["spray_rain_limit"]):
                alerts.append({
                    "alert_type": "heavy_rain",
                    "forecast_date": dt,
                    "title": f"Mưa lớn {rain:.0f} mm",
                    "message": f"Dự báo mưa {rain:.0f} mm, xác suất {rain_probability:.0f}% trong {day_label}.",
                    "recommendation": "Khơi thông rãnh thoát nước, neo buộc cây, tạm hoãn bón phân và phun thuốc.",
                    "severity": "high" if rain >= 100 or rain_probability >= 90 else "medium",
                    "trigger_value": rain,
                    "trigger_unit": "mm",
                    "source": "open_meteo_rule",
                })
            if self._is_thunderstorm(item):
                alerts.append({
                    "alert_type": "thunderstorm",
                    "forecast_date": dt,
                    "title": "Nguy cơ giông sét",
                    "message": f"Open-Meteo ghi nhận mã thời tiết giông trong {day_label}.",
                    "recommendation": "Không làm việc ngoài đồng khi có giông, thu dọn dụng cụ và tránh trú dưới cây cao.",
                    "severity": "high",
                    "trigger_value": item.get("weather_code"),
                    "trigger_unit": "weather_code",
                    "source": "open_meteo_rule",
                })
            if wind >= 22:
                alerts.append({
                    "alert_type": "strong_wind",
                    "forecast_date": dt,
                    "title": f"Gió mạnh {wind:.0f} km/h",
                    "message": f"Gió mạnh làm tăng nguy cơ đổ ngã và thất thoát thuốc phun trong {day_label}.",
                    "recommendation": "Hoãn phun thuốc, kiểm tra giàn/neo buộc và che chắn cây dễ đổ.",
                    "severity": "high" if wind >= 30 else "medium",
                    "trigger_value": wind,
                    "trigger_unit": "km/h",
                    "source": "open_meteo_rule",
                })
            if humidity > ALERT_THRESHOLDS["humidity_high"]:
                alerts.append({
                    "alert_type": "high_humidity",
                    "forecast_date": dt,
                    "title": f"Độ ẩm cao {humidity:.0f}%",
                    "message": "Độ ẩm cao tạo điều kiện bùng phát nấm, vi khuẩn gây bệnh.",
                    "recommendation": "Tăng thông thoáng ruộng/vườn, kiểm tra bệnh lá và chỉ phun khi trời khô, gió nhẹ.",
                    "severity": "medium",
                    "trigger_value": humidity,
                    "trigger_unit": "%",
                    "source": "open_meteo_rule",
                })
            if uv >= 8:
                alerts.append({
                    "alert_type": "high_uv",
                    "forecast_date": dt,
                    "title": f"UV cao {uv:.1f}",
                    "message": f"UV cao trong {day_label} dễ gây héo lá, cháy mép lá ở cây non.",
                    "recommendation": "Che lưới, giữ ẩm gốc và tránh tưới/phun vào giữa trưa.",
                    "severity": "medium",
                    "trigger_value": uv,
                    "trigger_unit": "UV",
                    "source": "open_meteo_rule",
                })

        rain_3d = sum(self._num(item.get("rainfall"), 0) for item in forecast[:3])
        if rain_3d >= 80:
            alerts.append({
                "alert_type": "rain_accumulation",
                "forecast_date": forecast[0].get("date") if forecast else "",
                "title": f"Mưa cộng dồn 3 ngày {rain_3d:.0f} mm",
                "message": "Mưa cộng dồn cao làm tăng nguy cơ úng rễ, rửa trôi phân và bệnh nấm.",
                "recommendation": "Ưu tiên thoát nước, giảm tưới, chia nhỏ lần bón phân sau khi đất ráo.",
                "severity": "high" if rain_3d >= 120 else "medium",
                "trigger_value": rain_3d,
                "trigger_unit": "mm/3d",
                "source": "open_meteo_rule",
            })

        # Loại bỏ trùng lặp theo (alert_type, forecast_date)
        seen = set()
        unique = []
        severity_rank = {"high": 0, "medium": 1, "low": 2}
        for alert in sorted(alerts, key=lambda item: (severity_rank.get(item["severity"], 9), str(item.get("forecast_date") or ""))):
            key = (alert["alert_type"], alert["forecast_date"])
            if key not in seen:
                seen.add(key)
                unique.append(alert)
        return unique[:6]

    def _build_activity_recommendations(
        self,
        current: dict,
        forecast: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
        hourly: list[dict] | None = None,
    ) -> list[dict]:
        temp = self._num(current.get("temperature") or current.get("temp_max"), 28)
        current_rain = self._num(current.get("rainfall"), 0)
        humidity = self._num(current.get("humidity"), 70)
        wind = self._num(current.get("wind_speed"), 0)
        advice = self._crop_advice(crop_name)
        stage_key = self._text_key(growth_stage)
        today = forecast[0] if forecast else {}

        rain_today = self._num(today.get("rainfall"), current_rain)
        rain_probability_today = self._num(today.get("rain_probability"), 0)
        rain_24h = sum(self._num(item.get("rainfall"), 0) for item in (hourly or [])[:24])
        max_rain_probability_24h = max([self._num(item.get("rain_probability"), 0) for item in (hourly or [])[:24]] or [rain_probability_today])
        rain_3d = sum(self._num(item.get("rainfall"), 0) for item in forecast[:3])
        max_wind_24h = max([self._num(item.get("wind_speed"), 0) for item in (hourly or [])[:24]] or [wind])
        dry_window = self._find_hour_window(
            hourly,
            hours_needed=3,
            max_lookahead_hours=96,
            max_rain_probability=30,
            max_rainfall=0.2,
            max_wind=18,
            max_uv=7,
            min_temp=18,
            max_temp=34,
        )
        spray_window = self._find_hour_window(
            hourly,
            hours_needed=2,
            max_lookahead_hours=72,
            max_rain_probability=25,
            max_rainfall=0.1,
            max_wind=15,
            max_uv=6,
            min_temp=18,
            max_temp=32,
        )

        recs = []

        if rain_24h >= 8 or max_rain_probability_24h >= 70:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Tạm hoãn",
                "reason": f"Open-Meteo dự báo 24 giờ tới mưa khoảng {rain_24h:.1f} mm, xác suất cao nhất {max_rain_probability_24h:.0f}%.",
                "priority": "low",
                "timing": "Kiểm tra ẩm độ đất sau mưa rồi mới tưới bù.",
                "source": "open_meteo_rule",
            })
        elif temp >= advice["water_temp_limit"] or rain_3d < 5:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Nên tưới",
                "reason": f"Nhiệt độ {temp:.0f}°C, mưa 3 ngày tới chỉ {rain_3d:.1f} mm nên cây dễ thiếu nước.",
                "priority": "high" if temp >= advice["water_temp_limit"] else "medium",
                "timing": "Sáng sớm 5–7h hoặc chiều mát 17–19h.",
                "source": "open_meteo_rule",
            })
        else:
            recs.append({
                "action_type": "irrigation",
                "action": "Tưới nước",
                "decision": "Tưới duy trì",
                "reason": "Lượng mưa và nhiệt độ chưa vượt ngưỡng rủi ro, duy trì lịch tưới nhẹ theo ẩm độ đất.",
                "priority": "medium",
                "timing": "Ưu tiên sáng sớm, tránh tưới giữa trưa.",
                "source": "open_meteo_rule",
            })

        if max_wind_24h >= 22:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Không nên",
                "reason": f"Gió 24 giờ tới có thể đạt {max_wind_24h:.0f} km/h, dễ làm thuốc bay lệch và giảm hiệu quả.",
                "priority": "high",
                "timing": "Chờ gió dưới 15 km/h và trời khô.",
                "source": "open_meteo_rule",
            })
        elif rain_24h >= advice["spray_rain_limit"] or max_rain_probability_24h >= 60:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Hoãn",
                "reason": f"Mưa 24 giờ tới {rain_24h:.1f} mm/xác suất {max_rain_probability_24h:.0f}% có thể rửa trôi thuốc.",
                "priority": "high",
                "timing": dry_window or "Đợi sau mưa 12–24h, lá khô rồi phun.",
                "source": "open_meteo_rule",
            })
        else:
            recs.append({
                "action_type": "spraying",
                "action": "Phun thuốc",
                "decision": "Có thể phun",
                "reason": "Khung dự báo gần nhất ít mưa, gió không vượt ngưỡng nguy hiểm.",
                "priority": "medium",
                "timing": spray_window or "Sáng sớm 6–8h hoặc chiều mát khi gió nhẹ.",
                "source": "open_meteo_rule",
            })

        if rain_3d >= 50:
            recs.append({
                "action_type": "drainage",
                "action": "Thoát nước",
                "decision": "Ưu tiên kiểm tra",
                "reason": f"Mưa cộng dồn 3 ngày tới {rain_3d:.1f} mm, nguy cơ úng rễ và rửa trôi dinh dưỡng.",
                "priority": "high",
                "timing": "Làm trước đợt mưa, khơi rãnh và mở cửa thoát nước.",
                "source": "open_meteo_rule",
            })

        if rain_today >= 30 or rain_3d >= 60:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Hoãn bón",
                "reason": f"Mưa hôm nay {rain_today:.1f} mm, 3 ngày tới {rain_3d:.1f} mm có thể rửa trôi phân.",
                "priority": "high",
                "timing": dry_window or "Bón sau khi đất ráo, chia nhỏ lượng bón.",
                "source": "open_meteo_rule",
            })
        elif rain_3d < 5 and humidity < 55:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Bón kèm tưới",
                "reason": "Dự báo khô, độ ẩm thấp làm phân khó tan hoặc dễ thất thoát.",
                "priority": "medium",
                "timing": "Bón chiều mát, tưới nhẹ sau bón.",
                "source": "open_meteo_rule",
            })
        else:
            recs.append({
                "action_type": "fertilizing",
                "action": "Bón phân",
                "decision": "Có thể bón",
                "reason": "Độ ẩm và mưa dự báo ở mức phù hợp để cây hấp thu dinh dưỡng.",
                "priority": "medium",
                "timing": dry_window or "Chiều mát 16–18h.",
                "source": "open_meteo_rule",
            })

        if stage_key == "thu hoach":
            if rain_24h >= 3 or rain_probability_today >= 50:
                recs.append({
                    "action_type": "harvest",
                    "action": "Thu hoạch",
                    "decision": "Hoãn hoặc thu sớm trước mưa",
                    "reason": f"Dự báo mưa gần {rain_24h:.1f} mm trong 24h làm tăng nguy cơ ướt, dập và khó phơi sấy.",
                    "priority": "high",
                    "timing": dry_window or "Chọn khoảng khô ráo gần nhất, chuẩn bị che phủ/sấy.",
                    "source": "open_meteo_rule",
                })
            else:
                recs.append({
                    "action_type": "harvest",
                    "action": "Thu hoạch",
                    "decision": "Nên thực hiện",
                    "reason": "Dự báo gần ít mưa, thuận lợi thu hái, vận chuyển và phơi sấy.",
                    "priority": "high",
                    "timing": dry_window or "Sáng 7–11h.",
                    "source": "open_meteo_rule",
                })

        stage_notes = {
            "cay con": "Che nắng nhẹ, giữ ẩm đều và tránh phun/bón nồng độ cao khi nhiệt độ hoặc UV cao.",
            "ra hoa": "Hạn chế phun thuốc lúc hoa nở; ưu tiên sáng sớm, tránh mưa và gió mạnh để bảo vệ thụ phấn.",
            "lam dong": "Giữ nước ổn định, không để khô hạn kéo dài vì giai đoạn làm đòng rất nhạy với thiếu nước.",
            "dau trai": "Giữ ẩm đều, tránh sốc nước sau khô hạn và theo dõi nấm bệnh khi độ ẩm tăng.",
        }
        if stage_key in stage_notes:
            recs.append({
                "action_type": "crop_stage",
                "action": "Chăm sóc theo giai đoạn",
                "decision": "Điều chỉnh kỹ thuật",
                "reason": stage_notes[stage_key],
                "priority": "medium",
                "timing": "Áp dụng trong các khung giờ thời tiết ổn định.",
                "source": "open_meteo_rule",
            })

        return recs

    def _build_ai_recommendation(
        self,
        current: dict,
        forecast: list[dict],
        alerts: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
        activity_recs: list[dict] | None = None,
    ) -> dict:
        temp = self._num(current.get("temperature") or current.get("temp_max"), 28)
        humidity = self._num(current.get("humidity"), 70)
        rain = self._num(current.get("rainfall"), 0)
        crop_label = crop_name or "cây trồng"
        stage_label = growth_stage or "hiện tại"
        high_alerts = [a for a in alerts if a["severity"] == "high"]
        priority_actions = [item for item in (activity_recs or []) if item.get("priority") == "high"]

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

        avg_rain = sum(self._num(f.get("rainfall"), 0) for f in forecast) / max(len(forecast), 1)
        action_plan = [
            f"Nhiệt độ {temp:.0f}°C — {'tăng tưới, che mát' if temp > 35 else 'theo dõi bình thường'}",
            f"Độ ẩm {humidity:.0f}% — {'phòng nấm bệnh' if humidity > 85 else 'ổn định'}",
            f"Mưa TB 7 ngày {avg_rain:.1f} mm/ngày — {'hạn chế tưới' if avg_rain > 15 else 'duy trì tưới'}",
        ]
        if high_alerts:
            action_plan.append(f"Ưu tiên xử lý: {high_alerts[0]['recommendation']}")
        for item in priority_actions[:2]:
            timing = f" Thời điểm: {item['timing']}" if item.get("timing") else ""
            action_plan.append(f"{item['action']}: {item['decision']} — {item['reason']}{timing}")

        crop_note = None
        if crop_name:
            stage_notes = {
                "cây con": f"{crop_label} giai đoạn cây con rất nhạy cảm với nhiệt độ và độ ẩm.",
                "ra hoa": f"{crop_label} đang ra hoa — tránh phun thuốc và hạn chế tưới lá.",
                "làm đòng": f"{crop_label} đang làm đòng — đảm bảo đủ nước và dinh dưỡng.",
                "thu hoạch": f"{crop_label} sắp thu hoạch — chú ý thời tiết khô ráo để thu và phơi.",
                "cay con": f"{crop_label} giai đoạn cây con rất nhạy cảm với nhiệt độ và độ ẩm.",
                "ra hoa": f"{crop_label} đang ra hoa — tránh phun thuốc và hạn chế tưới lá.",
                "lam dong": f"{crop_label} đang làm đòng — đảm bảo đủ nước và dinh dưỡng.",
                "thu hoach": f"{crop_label} sắp thu hoạch — chú ý thời tiết khô ráo để thu và phơi.",
            }
            crop_note = stage_notes.get((growth_stage or "").lower()) or stage_notes.get(self._text_key(growth_stage))

        return {
            "provider": "weather_rule_ai",
            "provider_label": "AI thời tiết",
            "ai_generated": True,
            "summary": summary,
            "risk_explanation": risk,
            "action_plan": action_plan,
            "crop_note": crop_note,
            "data_note": "Dữ liệu đầu vào lấy từ Open-Meteo gồm hiện tại, dự báo ngày và dự báo từng giờ. Lớp AI thời tiết chuyển các ngưỡng khí tượng nông nghiệp thành cảnh báo và lịch thao tác phù hợp.",
        }


    def get_forecast(self, db: Session, region: str, days: int = 7, force_refresh: bool = False) -> list[dict]:
        """7-day forecast: Open-Meteo realtime → DB cache → miss(no mock).
        Không dùng mock data.
        """
        norm = _normalize_region(region)

        # Prefer DB cache first
        rows = get_weather_forecast(db, norm, days)
        cache_status = "miss"
        if rows:
            cached = self._forecast_rows_to_dict(rows, days, fallback_used=False, timeout=False)
            cache_status = cached[0].get("cache_status") if cached else "miss"
            if cached and cache_status in {"fresh_cache", "stale_cache"} and not force_refresh:
                return cached

        # Only bail out early if DB had rows (even stale) — empty cache always tries live fetch
        if not force_refresh and rows:
            return []

        # Live fetch
        try:
            live_items = _weather_client.get_forecast(norm, days)
            if not live_items:
                raise ExternalServiceError("Open-Meteo forecast empty payload")

            result = []
            now = datetime.now()
            for item in live_items[:days]:
                temp_max = item.get("temp_max")
                temp_min = item.get("temp_min")
                rain = float(item.get("rainfall") or 0)
                hum = item.get("humidity") if item.get("humidity") is not None else 70.0
                hum = float(hum if hum is not None else 70.0)

                record_date = date.fromisoformat(str(item["date"])[:10])
                upsert_weather_cache(
                    db,
                    region=norm,
                    record_date=record_date,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    rainfall=rain,
                    humidity=hum,
                    condition=item.get("condition"),
                    wind_speed=item.get("wind_speed"),
                    uv_index=item.get("uv_index"),
                    weather_code=item.get("weather_code"),
                    source_name=item.get("source_name") or "Open-Meteo",
                    source_url=item.get("source_url") or OPEN_METEO_FORECAST_URL,
                    source_updated_at=item.get("last_updated") or now,
                    fetched_at=now,
                    is_realtime=True,
                    is_mock=False,
                )

                result.append({
                    **item,
                    "humidity": round(hum, 1),
                    "warnings": self._analyze_warnings(
                        float(temp_max or item.get("temperature") or 30),
                        float(temp_min or item.get("temperature") or 20),
                        rain,
                        hum,
                    ),
                    "source": "realtime_api",
                    "source_name": item.get("source_name") or "Open-Meteo",
                    "source_url": item.get("source_url") or OPEN_METEO_FORECAST_URL,
                    "is_realtime": True,
                    "is_mock": False,
                    "cache_status": "live",
                    "fetched_at": now,
                    "last_updated": now,
                    "data_age_minutes": 0,
                    "fallback_used": False,
                    "timeout": False,
                })

            return result
        except Exception as exc:
            logger.warning("[weather] Open-Meteo forecast failed region=%s error=%s", region, exc)

        # Stale DB fallback if exists
        if rows and cache_status in {"fresh_cache", "stale_cache"}:
            return self._forecast_rows_to_dict(
                rows,
                days,
                fallback_used=True,
                timeout=True,
            )

        # miss => caller will map to miss/error; no mock
        return []

    def _forecast_rows_to_dict(
        self,
        rows,
        days: int,
        *,
        fallback_used: bool,
        timeout: bool,
    ) -> list[dict]:
        result = []
        for w in rows[:days]:
            temp_max = float(w.TempMax or 30)
            temp_min = float(w.TempMin or 20)
            rain = float(w.Rainfall or 0)
            hum = float(w.Humidity or 70)
            updated = w.FetchedAt or w.SourceUpdatedAt or w.CreatedAt or datetime.now()
            result.append({
                "date": str(w.RecordDate),
                "temperature": round((temp_max + temp_min) / 2, 1),
                "temp_min": temp_min,
                "temp_max": temp_max,
                "humidity": round(hum, 1),
                "rainfall": round(rain, 1),
                "rain_probability": min(100, int(rain / 0.3)) if rain > 0 else 0,
                "condition": w.WeatherDesc or "unknown",
                "wind_speed": float(w.WindSpeed) if w.WindSpeed is not None else None,
                "uv_index": float(w.UVIndex) if w.UVIndex is not None else None,
                "weather_code": w.WeatherCode,
                "source": "cached",
                "source_name": w.SourceName or OPEN_METEO_SOURCE_NAME,
                "source_url": w.SourceURL or OPEN_METEO_FORECAST_URL,
                "is_realtime": False,
                "is_mock": False,
                "cache_status": "stale_cache" if fallback_used else cache_status_for(updated, "weather_forecast"),
                "fetched_at": updated,
                "last_updated": updated,
                "data_age_minutes": age_minutes(updated),
                "fallback_used": fallback_used,
                "timeout": timeout,
                "message": "Dữ liệu realtime đang chậm. Đang hiển thị dữ liệu cache gần nhất." if fallback_used else None,
                "warnings": self._analyze_warnings(temp_max, temp_min, rain, hum),
            })
        return result

    def analyze_agriculture_risk(self, db: Session, region: str, crop_name: str) -> dict:
        current = self.get_current_weather(db, region)
        if current.get("_api_error"):
            return current
        forecast = self.get_forecast(db, region, 7)
        if not forecast:
            return self._miss_weather_error(region, "forecast_7_days")
        alerts = self.generate_alerts(current, forecast, crop_name=crop_name)
        temp = float(current.get("temperature") or current.get("temp_max") or 0)
        humidity = float(current.get("humidity") or 0)
        wind = float(current.get("wind_speed") or 0)
        rain_3d = sum(float(item.get("rainfall") or 0) for item in forecast[:3])
        risk_items = [
            {"type": "heavy_rain", "risk": "high" if rain_3d >= 60 else "medium" if rain_3d >= 25 else "low", "value": rain_3d, "unit": "mm/3d"},
            {"type": "heat", "risk": "high" if temp >= 37 else "medium" if temp >= 34 else "low", "value": temp, "unit": "C"},
            {"type": "strong_wind", "risk": "high" if wind >= 30 else "medium" if wind >= 20 else "low", "value": wind, "unit": "km/h"},
            {"type": "high_humidity", "risk": "high" if humidity >= 90 else "medium" if humidity >= 82 else "low", "value": humidity, "unit": "%"},
        ]
        disease_risk = "high" if humidity >= 88 and rain_3d >= 25 else "medium" if humidity >= 82 else "low"
        score = sum({"low": 10, "medium": 25, "high": 40}[item["risk"]] for item in risk_items)
        score = min(100, score + min(len(alerts) * 5, 20))
        risk_level = "high" if score >= 70 else "medium" if score >= 40 else "low"
        confidence = 0.88 if current.get("is_realtime") else 0.72 if not current.get("is_mock") else 0.45
        return {
            "region": _normalize_region(region),
            "crop": crop_name,
            "risk_level": risk_level,
            "risk_score": score,
            "disease_risk": disease_risk,
            "risks": risk_items,
            "alerts": alerts,
            "confidence": confidence,
            "reasons": [
                f"Rain next 3 days: {rain_3d:.1f} mm",
                f"Temperature: {temp:.1f} C",
                f"Humidity: {humidity:.1f}%",
                f"Wind: {wind:.1f} km/h",
            ],
            "source": "ai_generated",
            "source_name": "Rule-based weather risk engine",
            "is_mock": bool(current.get("is_mock")),
            "cache_status": current.get("cache_status", "unknown"),
            "last_updated": datetime.now(),
        }

    def farming_recommendation(self, db: Session, region: str, crop_name: str) -> dict:
        current = self.get_current_weather(db, region)
        if current.get("_api_error"):
            return current
        forecast = self.get_forecast(db, region, 7)
        if not forecast:
            return self._miss_weather_error(region, "forecast_7_days")
        hourly = self.get_hourly_forecast(db, region, 168)
        recommendations = self.build_activity_recommendations(current, forecast, hourly, crop_name=crop_name)
        risk = self.analyze_agriculture_risk(db, region, crop_name)
        should_irrigate = next((item for item in recommendations if item.get("action_type") == "irrigation"), None)
        should_spray = next((item for item in recommendations if item.get("action_type") == "spraying"), None)
        actions = [item.get("reason") for item in recommendations[:4] if item.get("reason")]
        if risk["risk_level"] == "high":
            actions.insert(0, "Prioritize field safety checks before spraying or fertilizing.")
        return {
            "region": _normalize_region(region),
            "crop": crop_name,
            "risk_level": risk["risk_level"],
            "confidence": risk["confidence"],
            "should_irrigate": should_irrigate,
            "should_spray": should_spray,
            "recommendations": recommendations,
            "recommended_actions": actions,
            "message": "Weather recommendation generated from realtime/cache weather plus rule-based agronomy thresholds.",
            "source": "ai_generated",
            "source_name": "AI Weather Advisor fallback engine",
            "is_mock": bool(current.get("is_mock")),
            "cache_status": current.get("cache_status", "unknown"),
            "last_updated": datetime.now(),
        }

    def generate_alerts(self, _current: dict, forecast: list[dict], crop_name: str | None = None, growth_stage: str | None = None) -> list[dict]:
        """Public wrapper để dashboard_service có thể gọi được."""
        return self._build_alerts(forecast, crop_name=crop_name, growth_stage=growth_stage)


    def get_weather_forecast(self, db: Session, region: str, days: int = 7) -> list[dict]:
        return self.get_forecast(db, region, days)

    def get_weather_risk(self, db: Session, region: str, crop: str | None = None) -> dict:
        return self.analyze_agriculture_risk(db, region, crop or "crop")

    def get_farming_recommendation(self, db: Session, region: str, crop: str | None = None) -> dict:
        return self.farming_recommendation(db, region, crop or "crop")


weather_service = WeatherService()
