"""
P2-03: Harvest Service
Lấy dữ liệu request → lấy thời tiết → gọi predictor → lưu qua repository.
POST /api/harvest/forecast trả kết quả thật hoặc rule-based ổn định.
"""
from datetime import datetime, date, timedelta
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..models.crop import CropType, HarvestSchedule
from ..models.weather import WeatherData


class HarvestService:
    """Service xử lý dự báo thu hoạch."""

    @staticmethod
    def _get_predictor():
        """Lazy import tránh circular import."""
        try:
            from ai_models.harvest_forecast.predictor import harvest_predictor
            return harvest_predictor
        except ImportError:
            return None

    # ------------------------------------------------------------------ #
    # Phương thức chính
    # ------------------------------------------------------------------ #

    def forecast_harvest(
        self,
        db: Session,
        crop_name: str,
        planting_date: datetime,
        region: str,
        area_size: Optional[float] = None,
    ) -> Dict:
        """
        Dự báo thu hoạch:
        1. Lấy thông tin cây trồng (GrowthDurationDays) từ DB
        2. Lấy thời tiết gần nhất cho region
        3. Gọi HarvestPredictor
        4. Trả về kết quả đầy đủ
        """
        # 1. Thông tin cây trồng
        crop = (
            db.query(CropType)
            .filter(CropType.CropName == crop_name)
            .first()
        )
        growth_duration = crop.GrowthDurationDays if crop else None

        # 2. Thời tiết gần nhất
        weather_data = HarvestService._get_latest_weather(db, region)

        # 3. Dự báo qua predictor
        predictor = self._get_predictor()
        if predictor:
            result = predictor.predict(
                crop_name=crop_name,
                planting_date=planting_date,
                region=region,
                growth_duration_days=growth_duration,
                weather_data=weather_data,
            )
        else:
            # Fallback đơn giản nếu không import được predictor
            days = growth_duration or 60
            result = {
                "expected_harvest_date": (planting_date + timedelta(days=days)).date().isoformat(),
                "confidence":            0.75,
                "growth_days":           days,
                "warning":               None,
                "recommendation":        f"Dự kiến thu hoạch {crop_name} sau {days} ngày tại {region}.",
            }

        # 4. Bổ sung metadata
        result["crop_name"]     = crop_name
        result["region"]        = region
        result["planting_date"] = planting_date.date().isoformat()
        if crop:
            result["crop_category"] = crop.Category

        return result

    # Backward-compat alias dùng bởi harvest.py API cũ
    def predict_harvest_date(
        self,
        db: Session,
        crop_name: str,
        planting_date: datetime,
        region: str,
    ) -> Optional[Dict]:
        """Alias backward-compatible."""
        return self.forecast_harvest(
            db=db,
            crop_name=crop_name,
            planting_date=planting_date,
            region=region,
        )

    # ------------------------------------------------------------------ #
    # Lưu kế hoạch thu hoạch
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
    ) -> HarvestSchedule:
        """Lưu kế hoạch thu hoạch mới."""
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

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_latest_weather(db: Session, region: str) -> Optional[Dict]:
        """Lấy bản ghi thời tiết gần nhất cho region."""
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
            "rainfall":    float(weather.Rainfall) if weather.Rainfall else None,
            "humidity":    float(weather.Humidity) if weather.Humidity else None,
        }


harvest_service = HarvestService()
