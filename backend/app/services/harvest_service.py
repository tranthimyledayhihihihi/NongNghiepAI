"""
Harvest Service - merged Tien (repository + schema) + Quang (AI predictor + DB queries)
- API endpoints dùng: forecast_harvest(db, request), predict_harvest_date(db, crop_name, date, region)
- Scheduler/internal dùng: create_harvest_schedule, _get_latest_weather
"""
from datetime import date, datetime, timedelta
from typing import Dict, Optional
from unicodedata import category, normalize

from sqlalchemy.orm import Session

from app.repositories.harvest_repository import (
    create_harvest_forecast,
    get_harvest_forecast_history,
    get_harvest_schedules_by_user,
)
from app.schemas.harvest_schema import HarvestForecastRequest


class HarvestService:
    default_growth_days = {
        "ca chua": 75,
        "dua chuot": 60,
        "rau muong": 30,
        "cai xanh": 45,
        "ot": 90,
        "lua": 105,
    }

    @staticmethod
    def _get_predictor():
        """Lazy import AI predictor, tránh circular import."""
        try:
            from ai_models.harvest_forecast.predictor import harvest_predictor
            return harvest_predictor
        except ImportError:
            return None

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def forecast_harvest(self, db: Session, request: HarvestForecastRequest) -> dict:
        """
        Dự báo thu hoạch:
        - Thử gọi AI predictor (Quang's model)
        - Fallback về rule-based growth days nếu không có model
        - Lưu kết quả qua repository
        """
        crop_name = request.crop_name
        region = request.region
        planting_date = request.planting_date

        # Lấy thời tiết và thông tin cây trồng để truyền cho predictor
        weather_data = self._get_latest_weather(db, region)
        growth_duration = self._get_crop_growth_days(db, crop_name)

        # Thử AI predictor
        predictor = self._get_predictor()
        if predictor:
            try:
                ai_result = predictor.predict(
                    crop_name=crop_name,
                    planting_date=datetime.combine(planting_date, datetime.min.time()),
                    region=region,
                    growth_duration_days=growth_duration,
                    weather_data=weather_data,
                )
                growth_days = ai_result.get("growth_days", self._growth_days_for(crop_name))
                expected_date = planting_date + timedelta(days=growth_days)
                warning = ai_result.get("warning") or self._warning_for(expected_date)
                recommendation = ai_result.get(
                    "recommendation",
                    f"Du kien thu hoach sau {growth_days} ngay. Nen theo doi thoi tiet truoc thu hoach.",
                )
                confidence = ai_result.get("confidence", 0.78)
            except Exception:
                predictor = None

        if not predictor:
            # Rule-based fallback
            growth_days = self._growth_days_for(crop_name)
            expected_date = planting_date + timedelta(days=growth_days)
            warning = self._warning_for(expected_date)
            recommendation = (
                f"Du kien thu hoach sau {growth_days} ngay. "
                "Nen kiem tra do chin va theo doi thoi tiet truoc thu hoach 5-7 ngay."
            )
            confidence = 0.78

        record = create_harvest_forecast(
            db,
            crop_name=crop_name,
            region=region,
            planting_date=planting_date,
            expected_harvest_date=expected_date,
            confidence=confidence,
            warning=warning,
            recommendation=recommendation,
        )

        return {
            "crop_name": crop_name,
            "region": region,
            "planting_date": planting_date,
            "expected_harvest_date": expected_date,
            "confidence": confidence,
            "warning": warning,
            "recommendation": recommendation,
            "created_at": getattr(record, "created_at", None),
        }

    def predict_harvest_date(
        self,
        db: Session,
        crop_name: str,
        planting_date: datetime,
        region: str,
    ) -> dict:
        """Backward-compatible alias dùng bởi /api/harvest/predict."""
        request = HarvestForecastRequest(
            crop_name=crop_name,
            region=region,
            planting_date=planting_date.date(),
        )
        result = self.forecast_harvest(db, request)
        return {
            **result,
            "predicted_harvest_date": result["expected_harvest_date"],
            "growth_days": self._growth_days_for(crop_name),
            "recommendations": [result["recommendation"]],
        }

<<<<<<< HEAD
    # ------------------------------------------------------------------ #
    # Lưu kế hoạch thu hoạch (Quang)
    # ------------------------------------------------------------------ #

    def create_harvest_schedule(
        self,
        db: Session,
        user_id: int,
        crop_id: int,
        region: str,
        planting_date: date,
        expected_harvest_date: date,
        area_size: Optional[float] = None,
        estimated_yield_kg: Optional[float] = None,
        notes: Optional[str] = None,
    ):
        """Lưu kế hoạch thu hoạch vào bảng HarvestSchedule."""
        try:
            from app.models.crop import HarvestSchedule
            schedule = HarvestSchedule(
                UserID=user_id,
                CropID=crop_id,
                Region=region,
                PlantingDate=planting_date,
                ExpectedHarvestDate=expected_harvest_date,
                AreaSize=area_size,
                EstimatedYieldKg=estimated_yield_kg,
                Notes=notes,
                Status="Đang trồng",
            )
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            return schedule
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
=======
    def get_history(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        records = get_harvest_forecast_history(db, user_id, limit)
        return [
            {
                "forecast_id": forecast.id,
                "schedule_id": schedule.id,
                "user_id": schedule.user_id,
                "crop_id": crop.id,
                "crop_name": crop.name,
                "region": schedule.region,
                "planting_date": schedule.planting_date,
                "expected_harvest_date": forecast.expected_harvest_date,
                "confidence": forecast.confidence_score,
                "warning": forecast.weather_warning,
                "recommendation": forecast.labor_recommendation,
                "transport_recommendation": forecast.transport_recommendation,
                "model_version": forecast.model_version,
                "generated_at": forecast.generated_at,
            }
            for forecast, schedule, crop in records
        ]

    def get_schedules(self, db: Session, user_id: int, limit: int = 50) -> list[dict]:
        records = get_harvest_schedules_by_user(db, user_id, limit)
        return [
            {
                "schedule_id": schedule.id,
                "user_id": schedule.user_id,
                "crop_id": crop.id,
                "crop_name": crop.name,
                "planting_date": schedule.planting_date,
                "area_size": schedule.area_size,
                "region": schedule.region,
                "expected_harvest_date": schedule.expected_harvest_date,
                "actual_harvest_date": schedule.actual_harvest_date,
                "estimated_yield_kg": schedule.estimated_yield_kg,
                "actual_yield_kg": schedule.actual_yield_kg,
                "status": schedule.status,
                "notes": schedule.notes,
                "created_at": schedule.created_at,
                "updated_at": schedule.updated_at,
            }
            for schedule, crop in records
        ]
>>>>>>> 66f30715951267b33a40918eff337ea69faad67f

    def _growth_days_for(self, crop_name: str) -> int:
        key = self._normalize_key(crop_name)
        return self.default_growth_days.get(key, 70)

    def _get_crop_growth_days(self, db: Session, crop_name: str) -> Optional[int]:
        """Lấy GrowthDurationDays từ DB, fallback về rule-based."""
        try:
            from app.models.crop import CropType
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            return crop.GrowthDurationDays if crop and crop.GrowthDurationDays else None
        except Exception:
            return None

    @staticmethod
    def _get_latest_weather(db: Session, region: str) -> Optional[Dict]:
        """Lấy bản ghi thời tiết gần nhất cho region."""
        try:
            from app.models.weather import WeatherData
            weather = (
                db.query(WeatherData)
                .filter(WeatherData.Region == region)
                .order_by(WeatherData.RecordDate.desc())
                .first()
            )
            if not weather:
                return None
            return {
                "temperature": float(weather.TempMax) if weather.TempMax else None,
                "rainfall": float(weather.Rainfall) if weather.Rainfall else None,
                "humidity": float(weather.Humidity) if weather.Humidity else None,
            }
        except Exception:
            return None

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = normalize("NFD", value.strip().lower())
        return "".join(char for char in normalized if category(char) != "Mn")

    @staticmethod
    def _warning_for(expected_date: date) -> str | None:
        if expected_date.month in {9, 10, 11}:
            return "Mua mua bao, can theo doi thoi tiet va chuan bi thu hoach som neu can."
        return None


harvest_service = HarvestService()
