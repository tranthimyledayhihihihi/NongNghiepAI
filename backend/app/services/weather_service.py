from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_client
from app.integrations.weather_client import WeatherClient, WeatherProviderError
from app.repositories.weather_repository import (
    create_weather_data,
    create_weather_observation,
    get_latest_by_region,
    list_weather_forecasts,
    upsert_current_weather,
    upsert_weather_alert,
    upsert_weather_forecast,
    upsert_weather_location,
    upsert_weather_recommendation,
)
from app.schemas.weather_schema import WeatherCreateRequest


MOCK_WEATHER = {
    "default": {
        "temperature": 28.0,
        "temp_min": 22.0,
        "temp_max": 32.0,
        "humidity": 75.0,
        "rainfall": 5.0,
        "rain_probability": 45.0,
        "wind_speed": 9.0,
        "uv_index": 7.0,
        "sunshine_hours": 7,
        "condition": "partly_cloudy",
    },
    "Ha Noi": {
        "temperature": 30.0,
        "temp_min": 24.0,
        "temp_max": 34.0,
        "humidity": 80.0,
        "rainfall": 3.0,
        "rain_probability": 40.0,
        "wind_speed": 11.0,
        "uv_index": 7.2,
        "sunshine_hours": 6,
        "condition": "cloudy",
    },
    "TP.HCM": {
        "temperature": 32.0,
        "temp_min": 25.0,
        "temp_max": 36.0,
        "humidity": 70.0,
        "rainfall": 0.0,
        "rain_probability": 20.0,
        "wind_speed": 12.0,
        "uv_index": 9.0,
        "sunshine_hours": 9,
        "condition": "sunny",
    },
    "Da Nang": {
        "temperature": 29.0,
        "temp_min": 23.0,
        "temp_max": 33.0,
        "humidity": 78.0,
        "rainfall": 8.0,
        "rain_probability": 55.0,
        "wind_speed": 14.0,
        "uv_index": 8.0,
        "sunshine_hours": 7,
        "condition": "rainy",
    },
    "Can Tho": {
        "temperature": 31.0,
        "temp_min": 24.0,
        "temp_max": 35.0,
        "humidity": 82.0,
        "rainfall": 10.0,
        "rain_probability": 60.0,
        "wind_speed": 10.0,
        "uv_index": 8.5,
        "sunshine_hours": 6,
        "condition": "rainy",
    },
    "Lam Dong": {
        "temperature": 20.0,
        "temp_min": 15.0,
        "temp_max": 24.0,
        "humidity": 85.0,
        "rainfall": 15.0,
        "rain_probability": 70.0,
        "wind_speed": 8.0,
        "uv_index": 5.0,
        "sunshine_hours": 5,
        "condition": "foggy",
    },
}

ALERT_THRESHOLDS = {
    "temp_max_high": 35.0,
    "temp_min_cold": 12.0,
    "rainfall_heavy": 30.0,
    "humidity_high": 85.0,
    "humidity_low": 30.0,
    "wind_strong": 25.0,
    "uv_high": 8.0,
    "dry_day_rain": 1.0,
}

ACTION_LABELS = {
    "watering": "Tưới nước",
    "spraying": "Phun thuốc",
    "fertilizing": "Bón phân",
    "harvesting": "Thu hoạch",
    "seedling_cover": "Che phủ cây non",
}

CROP_STAGE_NOTES = {
    ("cà phê", "ra hoa"): "Với cà phê giai đoạn ra hoa, tránh tưới quá mức và hạn chế thao tác mạnh khi có mưa hoặc gió lớn để giảm rụng hoa.",
    ("ca phe", "ra hoa"): "Với cà phê giai đoạn ra hoa, tránh tưới quá mức và hạn chế thao tác mạnh khi có mưa hoặc gió lớn để giảm rụng hoa.",
    ("lúa", "làm đòng"): "Với lúa giai đoạn làm đòng, duy trì nước ổn định và theo dõi nấm bệnh khi độ ẩm cao kéo dài.",
    ("lua", "lam dong"): "Với lúa giai đoạn làm đòng, duy trì nước ổn định và theo dõi nấm bệnh khi độ ẩm cao kéo dài.",
    ("rau màu", "cây con"): "Với rau màu giai đoạn cây con, cần che nắng khi UV cao và tránh để đất úng sau mưa lớn.",
    ("rau mau", "cay con"): "Với rau màu giai đoạn cây con, cần che nắng khi UV cao và tránh để đất úng sau mưa lớn.",
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
                return self._decorate_current(cached)

        latest = get_latest_by_region(db, region)
        if latest and not force_refresh and self._is_recent(latest):
            result = self._decorate_current(self._from_weather_row(latest, source="database", cache_status="db_fresh"))
            redis_client.set(cache_key, self._cache_payload(result), expire=settings.WEATHER_CACHE_TTL_SECONDS)
            return result

        if settings.WEATHER_PROVIDER.lower() != "mock":
            try:
                external = self.weather_client.get_current(region)
                saved = upsert_current_weather(db, **external)
                self._persist_location_and_observation(db, external)
                result = self._decorate_current(
                    self._from_payload(
                        external,
                        recorded_at=getattr(saved, "CreatedAt", None) if saved else datetime.now(),
                        source="api",
                        cache_status="miss",
                        is_realtime=True,
                        is_mock=False,
                    )
                )
                redis_client.set(cache_key, self._cache_payload(result), expire=settings.WEATHER_CACHE_TTL_SECONDS)
                return result
            except WeatherProviderError:
                pass

        if latest:
            return self._decorate_current(self._from_weather_row(latest, source="database", cache_status="db_stale"))

        result = self._mock_current_weather(region)
        self._persist_location_and_observation(db, result)
        return result

    def create_weather(self, db: Session, request: WeatherCreateRequest) -> dict:
        now = datetime.now()
        payload = {
            **request.model_dump(),
            "source_name": "manual",
            "source_updated_at": now,
        }
        weather = create_weather_data(db, **payload)
        self._persist_location_and_observation(db, payload)
        return self._decorate_current(
            {
                "region": request.region,
                "temperature": request.temperature,
                "temp_min": request.temperature,
                "temp_max": request.temperature,
                "rainfall": request.rainfall,
                "humidity": request.humidity,
                "condition": request.condition,
                "recorded_at": getattr(weather, "recorded_at", None) or now,
                "source": "manual",
                "source_name": "manual",
                "source_url": None,
                "is_realtime": False,
                "is_mock": False,
                "last_updated": now,
                "data_age_minutes": 0,
                "cache_status": "manual",
            }
        )

    def get_forecast(self, db: Session, region: str, days: int = 7) -> list[dict]:
        days = min(max(days, 1), 16)
        cache_key = f"weather:forecast:{region}:{days}"
        cached = redis_client.get(cache_key)
        if cached:
            return [{**item, "cache_status": "hit", "is_realtime": False} for item in cached]

        if settings.WEATHER_PROVIDER.lower() != "mock":
            try:
                forecast = [self._enrich_forecast_item(item) for item in self.weather_client.get_forecast(region, days)]
                self._persist_forecast_rows(db, forecast, "daily")
                redis_client.set(cache_key, self._cache_forecast(forecast), expire=settings.WEATHER_CACHE_TTL_SECONDS)
                return forecast
            except WeatherProviderError:
                pass

        db_forecast = self._get_saved_forecast(db, region, days, "daily")
        if db_forecast:
            redis_client.set(cache_key, self._cache_forecast(db_forecast), expire=settings.WEATHER_CACHE_TTL_SECONDS)
            return db_forecast

        forecast = self._mock_forecast(region, days)
        self._persist_forecast_rows(db, forecast, "daily")
        return forecast

    def get_hourly_forecast(self, db: Session, region: str, hours: int = 24) -> list[dict]:
        hours = min(max(hours, 1), 168)
        cache_key = f"weather:hourly:{region}:{hours}"
        cached = redis_client.get(cache_key)
        if cached:
            return [{**item, "cache_status": "hit", "is_realtime": False} for item in cached]

        if settings.WEATHER_PROVIDER.lower() != "mock":
            try:
                forecast = [self._enrich_hourly_item(item) for item in self.weather_client.get_hourly_forecast(region, hours)]
                self._persist_forecast_rows(db, forecast, "hourly")
                redis_client.set(cache_key, self._cache_forecast(forecast), expire=settings.WEATHER_CACHE_TTL_SECONDS)
                return forecast
            except WeatherProviderError:
                pass

        db_forecast = self._get_saved_forecast(db, region, min((hours + 23) // 24, 7), "hourly")
        if db_forecast:
            limited = db_forecast[:hours]
            redis_client.set(cache_key, self._cache_forecast(limited), expire=settings.WEATHER_CACHE_TTL_SECONDS)
            return limited

        forecast = self._mock_hourly_forecast(region, hours)
        self._persist_forecast_rows(db, forecast, "hourly")
        return forecast

    def get_agriculture_weather(
        self,
        db: Session,
        region: str,
        crop_name: str | None = None,
        growth_stage: str | None = None,
        days: int = 7,
        include_hourly: bool = True,
    ) -> dict:
        days = min(max(days, 1), 7)
        current = self.get_current_weather(db, region)
        forecast = self.get_forecast(db, region, days)
        hourly = self.get_hourly_forecast(db, region, 24) if include_hourly else []
        alerts = self.generate_alerts(current, forecast, crop_name=crop_name, growth_stage=growth_stage)
        activity_recommendations = self.build_activity_recommendations(
            current,
            forecast,
            hourly,
            crop_name=crop_name,
            growth_stage=growth_stage,
        )
        for alert in alerts:
            upsert_weather_alert(db, region=region, **alert)
        for recommendation in activity_recommendations:
            upsert_weather_recommendation(
                db,
                region=region,
                crop_name=crop_name,
                growth_stage=growth_stage,
                recommendation_date=date.today(),
                **recommendation,
            )

        return {
            "module_name": "Thời tiết nông vụ thông minh",
            "region": region,
            "crop_name": crop_name,
            "growth_stage": growth_stage,
            "location": {
                "region": region,
                "latitude": current.get("latitude"),
                "longitude": current.get("longitude"),
            },
            "current": current,
            "forecast": forecast,
            "hourly_forecast": hourly,
            "alerts": alerts,
            "activity_recommendations": activity_recommendations,
            "ai_recommendation": self._build_ai_summary(
                current,
                forecast,
                alerts,
                activity_recommendations,
                crop_name,
                growth_stage,
            ),
            "data_flow": [
                "Người dùng chọn khu vực/cây trồng",
                "Backend lấy tọa độ",
                "Gọi Weather API hoặc lấy cache Redis",
                "Lưu dữ liệu vào DB",
                "Rule engine kiểm tra cảnh báo",
                "AI/rule tạo giải thích và khuyến nghị",
                "Frontend hiển thị số liệu, cảnh báo và hành động đề xuất",
            ],
            "source_summary": self._source_summary(current, forecast),
            "generated_at": datetime.now(),
        }

    def generate_alerts(
        self,
        current: dict,
        forecast: list[dict],
        crop_name: str | None = None,
        growth_stage: str | None = None,
    ) -> list[dict]:
        alerts: list[dict] = []
        for item in forecast:
            forecast_date = self._date_from_value(item.get("date"))
            rainfall = self._safe_float(item.get("rainfall"))
            humidity = self._safe_float(item.get("humidity"))
            wind_speed = self._safe_float(item.get("wind_speed"))
            temp_max = self._safe_float(item.get("temp_max") or item.get("temperature"))

            if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
                alerts.append(
                    self._alert(
                        "heavy_rain",
                        "high",
                        "Mưa lớn trong ngày",
                        f"Dự báo mưa {rainfall:.0f} mm, có nguy cơ ngập úng và rửa trôi phân bón.",
                        "Kiểm tra rãnh thoát nước, hoãn bón phân và hạn chế thu hoạch khi ruộng còn ướt.",
                        rainfall,
                        "mm/ngày",
                        forecast_date,
                    )
                )
            if humidity > ALERT_THRESHOLDS["humidity_high"]:
                alerts.append(
                    self._alert(
                        "high_humidity",
                        "medium",
                        "Độ ẩm cao",
                        f"Độ ẩm khoảng {humidity:.0f}%, nguy cơ nấm lá và bệnh hại tăng.",
                        "Tăng kiểm tra vườn, giữ tán thông thoáng và chỉ phun thuốc khi trời khô ráo.",
                        humidity,
                        "%",
                        forecast_date,
                    )
                )
            if wind_speed > ALERT_THRESHOLDS["wind_strong"]:
                alerts.append(
                    self._alert(
                        "strong_wind",
                        "medium",
                        "Gió mạnh",
                        f"Gió có thể đạt {wind_speed:.0f} km/h, dễ làm thuốc bay lệch và ảnh hưởng cây non.",
                        "Không nên phun thuốc hoặc bón phân qua lá trong khung giờ gió mạnh.",
                        wind_speed,
                        "km/h",
                        forecast_date,
                    )
                )
            if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
                alerts.append(
                    self._alert(
                        "heat_stress",
                        "high",
                        "Nắng nóng",
                        f"Nhiệt độ cao nhất khoảng {temp_max:.0f}°C, cây dễ sốc nhiệt.",
                        "Tưới vào sáng sớm/chiều mát, che cây non và tránh làm việc ngoài đồng lúc trưa.",
                        temp_max,
                        "°C",
                        forecast_date,
                    )
                )

        if self._has_continuous_rain(forecast, min_days=3):
            total_rain = sum(self._safe_float(item.get("rainfall")) for item in forecast[:3])
            alerts.append(
                self._alert(
                    "continuous_rain",
                    "high",
                    "Mưa liên tục 3 ngày",
                    "Dự báo có mưa kéo dài, độ ẩm đất và tán lá duy trì ở mức cao.",
                    "Theo dõi nấm bệnh, thối rễ và chủ động thoát nước cho vùng trũng.",
                    total_rain,
                    "mm/3 ngày",
                    self._date_from_value(forecast[0].get("date")) if forecast else None,
                )
            )

        if len(forecast) >= 7 and all(self._safe_float(item.get("rainfall")) < ALERT_THRESHOLDS["dry_day_rain"] for item in forecast[:7]):
            alerts.append(
                self._alert(
                    "dry_spell",
                    "medium",
                    "7 ngày ít hoặc không mưa",
                    "Dự báo 7 ngày gần như không có mưa, nguy cơ khô hạn tăng.",
                    "Lên lịch tưới bổ sung, ưu tiên tưới tiết kiệm và phủ gốc để giữ ẩm.",
                    7,
                    "ngày",
                    self._date_from_value(forecast[0].get("date")) if forecast else None,
                )
            )

        alerts.extend(self._crop_specific_alerts(current, forecast, crop_name, growth_stage))
        return self._dedupe_alerts(current.get("region"), alerts)

    def build_activity_recommendations(
        self,
        current: dict,
        forecast: list[dict],
        hourly: list[dict] | None = None,
        crop_name: str | None = None,
        growth_stage: str | None = None,
    ) -> list[dict]:
        hourly = hourly or []
        today = forecast[0] if forecast else {}
        rainfall_24h = self._rainfall_next_hours(hourly, fallback=self._safe_float(today.get("rainfall")))
        rain_probability_24h = self._max_value(hourly, "rain_probability", fallback=self._safe_float(today.get("rain_probability")))
        wind_24h = self._max_value(hourly, "wind_speed", fallback=self._safe_float(today.get("wind_speed") or current.get("wind_speed")))
        uv_24h = self._max_value(hourly, "uv_index", fallback=self._safe_float(today.get("uv_index") or current.get("uv_index")))
        humidity = self._safe_float(today.get("humidity") or current.get("humidity"))
        temp_max = self._safe_float(today.get("temp_max") or current.get("temp_max") or current.get("temperature"))
        dry_week = len(forecast) >= 7 and all(self._safe_float(item.get("rainfall")) < 1 for item in forecast[:7])
        next_48h_rain = self._rainfall_next_hours(hourly[:48], fallback=sum(self._safe_float(item.get("rainfall")) for item in forecast[:2]))

        recommendations = []
        if rainfall_24h >= 2:
            recommendations.append(
                self._recommendation(
                    "watering",
                    "Không cần",
                    f"Có khoảng {rainfall_24h:.1f} mm mưa trong 24 giờ tới.",
                    "Theo dõi sau mưa",
                    "low",
                )
            )
        elif dry_week or temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            recommendations.append(
                self._recommendation(
                    "watering",
                    "Cần tưới bổ sung",
                    "Dự báo ít mưa và nhiệt độ cao làm tăng bốc hơi nước.",
                    "Sáng sớm hoặc chiều mát",
                    "high",
                )
            )
        else:
            recommendations.append(
                self._recommendation(
                    "watering",
                    "Theo dõi",
                    "Chưa có dấu hiệu thiếu nước rõ rệt từ dự báo hiện tại.",
                    "Kiểm tra ẩm độ đất trước khi tưới",
                    "medium",
                )
            )

        if rainfall_24h >= 1 or rain_probability_24h >= 50:
            recommendations.append(
                self._recommendation(
                    "spraying",
                    "Không nên",
                    f"Khả năng mưa {rain_probability_24h:.0f}% hoặc có mưa trong 24 giờ tới, thuốc dễ bị rửa trôi.",
                    "Chọn ngày ít mưa",
                    "high",
                )
            )
        elif wind_24h > ALERT_THRESHOLDS["wind_strong"]:
            recommendations.append(
                self._recommendation(
                    "spraying",
                    "Không nên",
                    f"Gió có thể vượt {wind_24h:.0f} km/h, thuốc dễ bay lệch.",
                    "Đợi khi gió dưới 20 km/h",
                    "high",
                )
            )
        elif humidity > ALERT_THRESHOLDS["humidity_high"]:
            recommendations.append(
                self._recommendation(
                    "spraying",
                    "Hạn chế",
                    "Độ ẩm cao làm tăng nguy cơ bệnh, nhưng cần chọn lúc lá khô để phun hiệu quả.",
                    "Cuối buổi sáng nếu không mưa",
                    "medium",
                )
            )
        else:
            recommendations.append(
                self._recommendation(
                    "spraying",
                    "Có thể",
                    "Mưa, gió và độ ẩm đang ở mức phù hợp cho thao tác phun.",
                    "Sáng sớm hoặc chiều mát",
                    "low",
                )
            )

        if next_48h_rain >= 10 or rain_probability_24h >= 60:
            recommendations.append(
                self._recommendation(
                    "fertilizing",
                    "Nên hoãn",
                    "Có mưa đáng kể trong 24-48 giờ tới, phân bón dễ bị rửa trôi.",
                    "Sau mưa 1-2 ngày khi đất ráo",
                    "high",
                )
            )
        elif rainfall_24h > 0:
            recommendations.append(
                self._recommendation(
                    "fertilizing",
                    "Có thể bón sau mưa",
                    "Đất đủ ẩm, thuận lợi cho cây hấp thu nếu không còn mưa lớn tiếp diễn.",
                    "Khi mặt đất ráo",
                    "medium",
                )
            )
        else:
            recommendations.append(
                self._recommendation(
                    "fertilizing",
                    "Có thể",
                    "Chưa có cảnh báo mưa lớn hoặc gió mạnh ảnh hưởng trực tiếp đến bón phân.",
                    "Theo lịch canh tác",
                    "low",
                )
            )

        if rainfall_24h >= 2 or rain_probability_24h >= 50:
            recommendations.append(
                self._recommendation(
                    "harvesting",
                    "Nên làm buổi sáng",
                    "Có khả năng mưa về sau, thu hoạch lúc khô ráo giúp giảm hao hụt và nấm mốc.",
                    "Ưu tiên trước mưa",
                    "high",
                )
            )
        elif humidity > ALERT_THRESHOLDS["humidity_high"]:
            recommendations.append(
                self._recommendation(
                    "harvesting",
                    "Chọn lúc nắng ráo",
                    "Độ ẩm cao làm nông sản lâu khô và dễ hư hỏng sau thu hoạch.",
                    "Giữa buổi sáng đến đầu chiều",
                    "medium",
                )
            )
        else:
            recommendations.append(
                self._recommendation(
                    "harvesting",
                    "Có thể",
                    "Điều kiện mưa và độ ẩm tương đối thuận lợi cho thu hoạch.",
                    "Theo độ chín của cây trồng",
                    "low",
                )
            )

        if uv_24h >= ALERT_THRESHOLDS["uv_high"] or temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            recommendations.append(
                self._recommendation(
                    "seedling_cover",
                    "Nên",
                    "UV hoặc nhiệt độ cao có thể làm cây non mất nước và cháy lá.",
                    "Che từ 10:00 đến 15:00",
                    "high",
                )
            )
        else:
            recommendations.append(
                self._recommendation(
                    "seedling_cover",
                    "Không cần",
                    "UV và nhiệt độ chưa vượt ngưỡng rủi ro cho cây non.",
                    "Theo dõi nếu trời nắng gắt",
                    "low",
                )
            )

        crop_note = self._crop_stage_note(crop_name, growth_stage)
        if crop_note:
            recommendations.append(
                {
                    "action_type": "crop_stage",
                    "action": "Theo cây trồng",
                    "decision": "Cá nhân hóa",
                    "reason": crop_note,
                    "timing": growth_stage,
                    "priority": "medium",
                    "source": "crop_weather_rule",
                }
            )
        return recommendations

    def get_harvest_weather_warning(self, db: Session, region: str) -> str | None:
        current = self.get_current_weather(db, region)
        forecast = self.get_forecast(db, region, 3)
        warnings = [alert["message"] for alert in self.generate_alerts(current, forecast)]
        return " | ".join(warnings) if warnings else None

    def _from_weather_row(self, weather: Any, source: str, cache_status: str) -> dict:
        last_updated = getattr(weather, "SourceUpdatedAt", None) or getattr(weather, "CreatedAt", None) or datetime.now()
        return {
            "region": getattr(weather, "Region", None),
            "temperature": getattr(weather, "temperature", None),
            "temp_min": getattr(weather, "TempMin", None),
            "temp_max": getattr(weather, "TempMax", None),
            "rainfall": getattr(weather, "Rainfall", None),
            "humidity": getattr(weather, "Humidity", None),
            "condition": getattr(weather, "WeatherDesc", None),
            "wind_speed": getattr(weather, "WindSpeed", None),
            "uv_index": getattr(weather, "UVIndex", None),
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
            "temp_min": payload.get("temp_min"),
            "temp_max": payload.get("temp_max"),
            "rainfall": payload.get("rainfall"),
            "humidity": payload.get("humidity"),
            "condition": payload.get("condition"),
            "wind_speed": payload.get("wind_speed"),
            "uv_index": payload.get("uv_index"),
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
        return self._decorate_current(
            {
                "region": region,
                "temperature": mock["temperature"],
                "temp_min": mock["temp_min"],
                "temp_max": mock["temp_max"],
                "rainfall": mock["rainfall"],
                "rain_probability": mock["rain_probability"],
                "humidity": mock["humidity"],
                "condition": mock["condition"],
                "wind_speed": mock["wind_speed"],
                "uv_index": mock["uv_index"],
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
        )

    def _mock_forecast(self, region: str, days: int) -> list[dict]:
        base = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        result = []
        for offset in range(days):
            variation = ((offset % 4) - 1.5) * 0.8
            rain = max(0.0, base["rainfall"] + ((offset % 5) - 2) * 2.5)
            humidity = min(100.0, max(35.0, base["humidity"] + ((offset % 3) - 1) * 4))
            temp_min = base["temp_min"] + variation
            temp_max = base["temp_max"] + variation
            item = {
                "date": date.today() + timedelta(days=offset),
                "region": region,
                "temperature": round((temp_min + temp_max) / 2, 1),
                "temp_min": round(temp_min, 1),
                "temp_max": round(temp_max, 1),
                "humidity": round(humidity, 1),
                "rainfall": round(rain, 1),
                "rain_probability": min(95.0, max(5.0, base["rain_probability"] + offset * 4)),
                "wind_speed": round(base["wind_speed"] + (offset % 4) * 2, 1),
                "uv_index": round(max(1.0, base["uv_index"] - (offset % 3) * 0.6), 1),
                "condition": base["condition"],
                "source": "mock",
                "source_name": "Mock Weather",
                "is_mock": True,
                "is_realtime": offset == 0,
                "cache_status": "mock",
                "last_updated": datetime.now(),
            }
            result.append(self._enrich_forecast_item(item))
        return result

    def _mock_hourly_forecast(self, region: str, hours: int) -> list[dict]:
        base = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        result = []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        for offset in range(hours):
            forecast_at = now + timedelta(hours=offset)
            day_part = 1 if 10 <= forecast_at.hour <= 15 else 0
            item = {
                "time": forecast_at.isoformat(timespec="minutes"),
                "date": forecast_at.date(),
                "forecast_at": forecast_at,
                "region": region,
                "temperature": round(base["temperature"] + day_part * 2 - (forecast_at.hour < 6) * 2, 1),
                "rainfall": round(max(0.0, base["rainfall"] / 8 if forecast_at.hour in {14, 15, 16, 17} else 0.0), 1),
                "rain_probability": min(95.0, base["rain_probability"] + (20 if forecast_at.hour in {14, 15, 16, 17} else 0)),
                "humidity": round(min(100.0, base["humidity"] + (8 if forecast_at.hour < 7 else 0)), 1),
                "wind_speed": round(base["wind_speed"] + (3 if 11 <= forecast_at.hour <= 16 else 0), 1),
                "uv_index": round(base["uv_index"] if day_part else 0.0, 1),
                "condition": base["condition"],
                "source_name": "Mock Weather",
                "is_mock": True,
                "is_realtime": offset == 0,
                "cache_status": "mock",
                "last_updated": datetime.now(),
            }
            result.append(self._enrich_hourly_item(item))
        return result

    def _decorate_current(self, weather: dict) -> dict:
        temp_max = self._safe_float(weather.get("temp_max") or weather.get("temperature"))
        temp_min = self._safe_float(weather.get("temp_min") or weather.get("temperature"))
        rainfall = self._safe_float(weather.get("rainfall"))
        humidity = self._safe_float(weather.get("humidity"))
        wind_speed = self._safe_float(weather.get("wind_speed"))
        uv_index = self._safe_float(weather.get("uv_index"))
        weather["agriculture_insights"] = [
            {
                "metric": "Nhiệt độ",
                "value": self._format_number(weather.get("temperature"), "°C"),
                "meaning": "Ảnh hưởng sinh trưởng, ra hoa, đậu trái và nguy cơ sốc nhiệt.",
            },
            {
                "metric": "Độ ẩm",
                "value": self._format_number(weather.get("humidity"), "%"),
                "meaning": "Liên quan mạnh đến nguy cơ nấm bệnh, sâu bệnh và tốc độ bốc hơi nước.",
            },
            {
                "metric": "Lượng mưa",
                "value": self._format_number(weather.get("rainfall"), "mm"),
                "meaning": "Quyết định tưới tiêu, thoát nước, phun thuốc và thu hoạch.",
            },
            {
                "metric": "Gió",
                "value": self._format_number(weather.get("wind_speed"), "km/h"),
                "meaning": "Ảnh hưởng đến việc phun thuốc, bón phân, che chắn cây non.",
            },
            {
                "metric": "UV/nắng",
                "value": self._format_number(weather.get("uv_index"), ""),
                "meaning": "Cảnh báo nắng nóng cho cây và người lao động.",
            },
            {
                "metric": "Thời gian cập nhật",
                "value": str(weather.get("last_updated") or weather.get("recorded_at") or ""),
                "meaning": "Cho biết dữ liệu còn mới hay đã cũ.",
            },
        ]
        weather["warnings"] = self._analyze_warnings(temp_max, temp_min, rainfall, humidity, wind_speed, uv_index)
        return weather

    def _enrich_forecast_item(self, item: dict) -> dict:
        enriched = item.copy()
        forecast_date = self._date_from_value(enriched.get("date"))
        enriched["date"] = forecast_date or enriched.get("date")
        enriched["day_label"] = self._day_label(forecast_date)
        enriched["warnings"] = self._analyze_warnings(
            self._safe_float(enriched.get("temp_max") or enriched.get("temperature")),
            self._safe_float(enriched.get("temp_min") or enriched.get("temperature")),
            self._safe_float(enriched.get("rainfall")),
            self._safe_float(enriched.get("humidity")),
            self._safe_float(enriched.get("wind_speed")),
            self._safe_float(enriched.get("uv_index")),
        )
        enriched["recommendation"] = self._daily_recommendation(enriched)
        return enriched

    def _enrich_hourly_item(self, item: dict) -> dict:
        enriched = item.copy()
        rainfall = self._safe_float(enriched.get("rainfall"))
        rain_probability = self._safe_float(enriched.get("rain_probability"))
        wind_speed = self._safe_float(enriched.get("wind_speed"))
        uv_index = self._safe_float(enriched.get("uv_index"))
        if rainfall >= 1 or rain_probability >= 60:
            recommendation = "Tránh phun thuốc, ưu tiên kiểm tra thoát nước."
        elif wind_speed > ALERT_THRESHOLDS["wind_strong"]:
            recommendation = "Không phun thuốc vì gió mạnh."
        elif uv_index >= ALERT_THRESHOLDS["uv_high"]:
            recommendation = "Che cây non và hạn chế lao động ngoài đồng."
        else:
            recommendation = "Có thể chăm sóc đồng ruộng nếu đất đủ ráo."
        enriched["recommendation"] = recommendation
        return enriched

    @staticmethod
    def _alert(
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        recommendation: str,
        trigger_value: float | int | None,
        trigger_unit: str | None,
        forecast_date: date | None,
    ) -> dict:
        return {
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "recommendation": recommendation,
            "trigger_value": float(trigger_value) if trigger_value is not None else None,
            "trigger_unit": trigger_unit,
            "forecast_date": forecast_date,
            "source": "rule",
        }

    @staticmethod
    def _recommendation(action_type: str, decision: str, reason: str, timing: str | None, priority: str) -> dict:
        return {
            "action_type": action_type,
            "action": ACTION_LABELS[action_type],
            "decision": decision,
            "reason": reason,
            "timing": timing,
            "priority": priority,
            "source": "rule",
        }

    def _daily_recommendation(self, item: dict) -> str:
        rainfall = self._safe_float(item.get("rainfall"))
        humidity = self._safe_float(item.get("humidity"))
        wind_speed = self._safe_float(item.get("wind_speed"))
        temp_max = self._safe_float(item.get("temp_max") or item.get("temperature"))
        if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
            return "Mưa lớn, cần kiểm tra thoát nước và hoãn bón phân."
        if rainfall >= 5 or humidity > ALERT_THRESHOLDS["humidity_high"]:
            return "Hạn chế phun thuốc, theo dõi nấm bệnh."
        if wind_speed > ALERT_THRESHOLDS["wind_strong"]:
            return "Không nên phun thuốc hoặc bón phân qua lá."
        if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            return "Tăng tưới nước, che cây non vào buổi trưa."
        return "Có thể phun thuốc hoặc bón phân nếu đất đủ ráo."

    def _crop_specific_alerts(
        self,
        current: dict,
        forecast: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
    ) -> list[dict]:
        if not crop_name:
            return []
        normalized_crop = self._normalize_text(crop_name)
        normalized_stage = self._normalize_text(growth_stage or "")
        max_humidity = max([self._safe_float(item.get("humidity")) for item in forecast] or [self._safe_float(current.get("humidity"))])
        max_wind = max([self._safe_float(item.get("wind_speed")) for item in forecast] or [self._safe_float(current.get("wind_speed"))])
        max_rain = max([self._safe_float(item.get("rainfall")) for item in forecast] or [self._safe_float(current.get("rainfall"))])

        alerts = []
        if "lua" in normalized_crop and max_humidity > ALERT_THRESHOLDS["humidity_high"]:
            alerts.append(
                self._alert(
                    "crop_disease_risk",
                    "medium",
                    "Rủi ro nấm bệnh trên lúa",
                    "Độ ẩm cao kéo dài làm tăng nguy cơ đạo ôn, lem lép hạt và bệnh lá.",
                    "Kiểm tra ruộng sau mưa, giữ mật độ tán thông thoáng và chỉ phun khi trời khô.",
                    max_humidity,
                    "%",
                    self._date_from_value(forecast[0].get("date")) if forecast else None,
                )
            )
        if "ca phe" in normalized_crop and ("ra hoa" in normalized_stage or "flower" in normalized_stage) and (max_rain >= 10 or max_wind > 20):
            alerts.append(
                self._alert(
                    "crop_flowering_risk",
                    "medium",
                    "Cà phê ra hoa gặp mưa/gió",
                    "Mưa hoặc gió mạnh trong giai đoạn ra hoa có thể làm rụng hoa, giảm tỷ lệ đậu trái.",
                    "Tránh tưới quá mức, kiểm tra vườn sau mưa và hạn chế thao tác mạnh.",
                    max(max_rain, max_wind),
                    "mm hoặc km/h",
                    self._date_from_value(forecast[0].get("date")) if forecast else None,
                )
            )
        if ("rau" in normalized_crop or "vegetable" in normalized_crop) and ("cay con" in normalized_stage or "seedling" in normalized_stage):
            max_uv = max([self._safe_float(item.get("uv_index")) for item in forecast] or [self._safe_float(current.get("uv_index"))])
            if max_uv >= ALERT_THRESHOLDS["uv_high"]:
                alerts.append(
                    self._alert(
                        "seedling_uv_risk",
                        "medium",
                        "Cây con gặp UV cao",
                        "UV cao làm cây con mất nước nhanh, dễ cháy lá.",
                        "Che lưới vào buổi trưa và tưới nhẹ sáng sớm.",
                        max_uv,
                        "UV index",
                        self._date_from_value(forecast[0].get("date")) if forecast else None,
                    )
                )
        return alerts

    def _build_ai_summary(
        self,
        current: dict,
        forecast: list[dict],
        alerts: list[dict],
        recommendations: list[dict],
        crop_name: str | None,
        growth_stage: str | None,
    ) -> dict:
        first_days = forecast[:3]
        total_rain = sum(self._safe_float(item.get("rainfall")) for item in first_days)
        max_humidity = max([self._safe_float(item.get("humidity")) for item in first_days] or [0])
        max_temp = max([self._safe_float(item.get("temp_max") or item.get("temperature")) for item in first_days] or [0])
        summary = (
            f"3 ngày tới dự kiến mưa khoảng {total_rain:.1f} mm, "
            f"độ ẩm cao nhất {max_humidity:.0f}% và nhiệt độ cao nhất {max_temp:.0f}°C."
        )
        if alerts:
            risk_explanation = "Rủi ro chính: " + "; ".join(alert["title"] for alert in alerts[:3]) + "."
        else:
            risk_explanation = "Chưa có cảnh báo lớn, nhưng vẫn nên theo dõi dữ liệu cập nhật trước khi thao tác ngoài đồng."

        action_plan = [
            f"{item['action']}: {item['decision']} - {item['reason']}"
            for item in recommendations
            if item.get("action_type") in {"watering", "spraying", "fertilizing", "harvesting", "seedling_cover"}
        ][:5]

        return {
            "provider": "rule_based_ai",
            "summary": summary,
            "risk_explanation": risk_explanation,
            "action_plan": action_plan,
            "crop_note": self._crop_stage_note(crop_name, growth_stage),
            "data_note": self._source_note(current, forecast),
        }

    def _persist_location_and_observation(self, db: Session, payload: dict) -> None:
        location = upsert_weather_location(
            db,
            region=payload.get("region"),
            province=payload.get("region"),
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude"),
            is_default=True,
        )
        create_weather_observation(
            db,
            **payload,
            location_id=getattr(location, "LocationID", None) if location else None,
        )

    def _persist_forecast_rows(self, db: Session, forecast: list[dict], forecast_type: str) -> None:
        for item in forecast:
            forecast_date = self._date_from_value(item.get("date"))
            forecast_at = item.get("forecast_at")
            if isinstance(forecast_at, str):
                forecast_at = self._datetime_from_value(forecast_at)
            payload = item.copy()
            payload.pop("forecast_date", None)
            payload.pop("forecast_at", None)
            payload.pop("forecast_type", None)
            payload.pop("source_updated_at", None)
            upsert_weather_forecast(
                db,
                **payload,
                forecast_date=forecast_date,
                forecast_at=forecast_at,
                forecast_type=forecast_type,
                source_updated_at=item.get("last_updated") or datetime.now(),
            )

    def _get_saved_forecast(self, db: Session, region: str, days: int, forecast_type: str) -> list[dict]:
        start_date = date.today()
        end_date = start_date + timedelta(days=days - 1)
        rows = list_weather_forecasts(db, region, start_date, end_date, forecast_type)
        result = []
        for row in rows:
            item = {
                "date": row.ForecastDate,
                "forecast_at": row.ForecastAt,
                "time": row.ForecastAt.isoformat(timespec="minutes") if row.ForecastAt else None,
                "region": row.Region,
                "temp_min": row.TempMin,
                "temp_max": row.TempMax,
                "temperature": row.Temperature,
                "rainfall": row.Rainfall,
                "rain_probability": row.RainProbability,
                "humidity": row.Humidity,
                "wind_speed": row.WindSpeed,
                "uv_index": row.UVIndex,
                "weather_code": row.WeatherCode,
                "condition": row.WeatherDesc,
                "recommendation": row.Recommendation,
                "source": "database",
                "source_name": row.SourceName or "database",
                "is_mock": False,
                "is_realtime": False,
                "cache_status": "db_fresh",
                "last_updated": row.SourceUpdatedAt or row.CreatedAt,
            }
            result.append(self._enrich_hourly_item(item) if forecast_type == "hourly" else self._enrich_forecast_item(item))
        return result

    @staticmethod
    def _has_continuous_rain(forecast: list[dict], min_days: int) -> bool:
        streak = 0
        for item in forecast:
            if WeatherService._safe_float(item.get("rainfall")) > 0:
                streak += 1
                if streak >= min_days:
                    return True
            else:
                streak = 0
        return False

    def _dedupe_alerts(self, region: str | None, alerts: list[dict]) -> list[dict]:
        seen = set()
        result = []
        for alert in alerts:
            forecast_date = self._date_from_value(alert.get("forecast_date"))
            alert["forecast_date"] = forecast_date
            key = f"{region}:{alert['alert_type']}:{forecast_date}:{alert['title']}"
            if key in seen:
                continue
            alert["dedup_key"] = key
            seen.add(key)
            result.append(alert)
        return result

    @staticmethod
    def _rainfall_next_hours(hourly: list[dict], fallback: float = 0.0) -> float:
        if not hourly:
            return fallback
        return sum(WeatherService._safe_float(item.get("rainfall")) for item in hourly)

    @staticmethod
    def _max_value(items: list[dict], key: str, fallback: float = 0.0) -> float:
        values = [WeatherService._safe_float(item.get(key)) for item in items if item.get(key) is not None]
        return max(values) if values else fallback

    @staticmethod
    def _age_minutes(value: datetime | str | None) -> int | None:
        value = WeatherService._datetime_from_value(value)
        if value is None:
            return None
        return max(int((datetime.now() - value.replace(tzinfo=None)).total_seconds() // 60), 0)

    def _is_recent(self, weather: Any) -> bool:
        updated_at = getattr(weather, "SourceUpdatedAt", None) or getattr(weather, "CreatedAt", None)
        age = self._age_minutes(updated_at)
        return age is not None and age * 60 <= settings.WEATHER_CACHE_TTL_SECONDS

    @staticmethod
    def _analyze_warnings(
        temp_max: float,
        temp_min: float,
        rainfall: float,
        humidity: float,
        wind_speed: float = 0.0,
        uv_index: float = 0.0,
    ) -> list[str]:
        warnings = []
        if temp_max > ALERT_THRESHOLDS["temp_max_high"]:
            warnings.append(f"Nắng nóng ({temp_max:.0f}°C) - tăng tưới nước và che cây non.")
        if temp_min < ALERT_THRESHOLDS["temp_min_cold"]:
            warnings.append(f"Lạnh ({temp_min:.0f}°C) - nguy cơ sương muối.")
        if rainfall > ALERT_THRESHOLDS["rainfall_heavy"]:
            warnings.append(f"Mưa lớn ({rainfall:.0f} mm) - kiểm tra thoát nước.")
        if humidity > ALERT_THRESHOLDS["humidity_high"]:
            warnings.append(f"Độ ẩm cao ({humidity:.0f}%) - nguy cơ nấm bệnh.")
        if humidity < ALERT_THRESHOLDS["humidity_low"] and humidity > 0:
            warnings.append(f"Độ ẩm thấp ({humidity:.0f}%) - tăng tưới.")
        if wind_speed > ALERT_THRESHOLDS["wind_strong"]:
            warnings.append(f"Gió mạnh ({wind_speed:.0f} km/h) - không nên phun thuốc.")
        if uv_index >= ALERT_THRESHOLDS["uv_high"]:
            warnings.append(f"UV cao ({uv_index:.1f}) - che cây non và bảo vệ người lao động.")
        return warnings

    @staticmethod
    def _cache_payload(result: dict) -> dict:
        payload = WeatherService._to_jsonable(result)
        payload["is_realtime"] = False
        payload["cache_status"] = "hit"
        return payload

    @staticmethod
    def _cache_forecast(forecast: list[dict]) -> list[dict]:
        cached = []
        for item in forecast:
            payload = WeatherService._to_jsonable(item)
            payload["cache_status"] = "hit"
            payload["is_realtime"] = False
            cached.append(payload)
        return cached

    @staticmethod
    def _to_jsonable(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, list):
            return [WeatherService._to_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {key: WeatherService._to_jsonable(item) for key, item in value.items()}
        return value

    @staticmethod
    def _date_from_value(value: Any) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value:
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return None
        return None

    @staticmethod
    def _datetime_from_value(value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                return None
        return None

    @staticmethod
    def _day_label(value: date | None) -> str | None:
        if value is None:
            return None
        labels = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        return labels[value.weekday()]

    @staticmethod
    def _safe_float(value: Any) -> float:
        try:
            if value is None:
                return 0.0
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _format_number(value: Any, suffix: str) -> str:
        if value is None:
            return "Chưa có dữ liệu"
        number = WeatherService._safe_float(value)
        if suffix:
            return f"{number:.1f}{suffix}"
        return f"{number:.1f}"

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        replacements = {
            "à": "a",
            "á": "a",
            "ạ": "a",
            "ả": "a",
            "ã": "a",
            "ă": "a",
            "ằ": "a",
            "ắ": "a",
            "ặ": "a",
            "ẳ": "a",
            "ẵ": "a",
            "â": "a",
            "ầ": "a",
            "ấ": "a",
            "ậ": "a",
            "ẩ": "a",
            "ẫ": "a",
            "è": "e",
            "é": "e",
            "ẹ": "e",
            "ẻ": "e",
            "ẽ": "e",
            "ê": "e",
            "ề": "e",
            "ế": "e",
            "ệ": "e",
            "ể": "e",
            "ễ": "e",
            "ì": "i",
            "í": "i",
            "ị": "i",
            "ỉ": "i",
            "ĩ": "i",
            "ò": "o",
            "ó": "o",
            "ọ": "o",
            "ỏ": "o",
            "õ": "o",
            "ô": "o",
            "ồ": "o",
            "ố": "o",
            "ộ": "o",
            "ổ": "o",
            "ỗ": "o",
            "ơ": "o",
            "ờ": "o",
            "ớ": "o",
            "ợ": "o",
            "ở": "o",
            "ỡ": "o",
            "ù": "u",
            "ú": "u",
            "ụ": "u",
            "ủ": "u",
            "ũ": "u",
            "ư": "u",
            "ừ": "u",
            "ứ": "u",
            "ự": "u",
            "ử": "u",
            "ữ": "u",
            "ỳ": "y",
            "ý": "y",
            "ỵ": "y",
            "ỷ": "y",
            "ỹ": "y",
            "đ": "d",
        }
        normalized = value.strip().lower()
        return "".join(replacements.get(char, char) for char in normalized)

    def _crop_stage_note(self, crop_name: str | None, growth_stage: str | None) -> str | None:
        if not crop_name and not growth_stage:
            return None
        normalized_crop = self._normalize_text(crop_name)
        normalized_stage = self._normalize_text(growth_stage)
        for (crop, stage), note in CROP_STAGE_NOTES.items():
            if self._normalize_text(crop) in normalized_crop and self._normalize_text(stage) in normalized_stage:
                return note
        if crop_name:
            return f"Khuyến nghị đã xét theo cây {crop_name}" + (f" ở giai đoạn {growth_stage}." if growth_stage else ".")
        return None

    @staticmethod
    def _source_summary(current: dict, forecast: list[dict]) -> dict:
        forecast_source = forecast[0].get("source_name") if forecast else None
        return {
            "current_source": current.get("source_name"),
            "forecast_source": forecast_source,
            "cache_status": current.get("cache_status"),
            "is_mock": bool(current.get("is_mock")) or any(item.get("is_mock") for item in forecast),
            "last_updated": current.get("last_updated"),
        }

    @staticmethod
    def _source_note(current: dict, forecast: list[dict]) -> str:
        if current.get("is_mock") or any(item.get("is_mock") for item in forecast):
            return "Một phần dữ liệu đang dùng mẫu mô phỏng vì chưa lấy được API realtime."
        source = current.get("source_name") or (forecast[0].get("source_name") if forecast else "nguồn thời tiết")
        return f"Số liệu lấy từ {source}, AI/rule chỉ diễn giải và khuyến nghị dựa trên dữ liệu này."


weather_service = WeatherService()
