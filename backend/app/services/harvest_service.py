from datetime import date, datetime, timedelta
from unicodedata import category, normalize

from sqlalchemy.orm import Session

from app.repositories.harvest_repository import create_harvest_forecast
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

    def forecast_harvest(self, db: Session, request: HarvestForecastRequest) -> dict:
        growth_days = self._growth_days_for(request.crop_name)
        expected_date = request.planting_date + timedelta(days=growth_days)
        warning = self._warning_for(expected_date)
        recommendation = (
            f"Du kien thu hoach sau {growth_days} ngay. "
            "Nen kiem tra do chin va theo doi thoi tiet truoc thu hoach 5-7 ngay."
        )

        record = create_harvest_forecast(
            db,
            crop_name=request.crop_name,
            region=request.region,
            planting_date=request.planting_date,
            expected_harvest_date=expected_date,
            confidence=0.78,
            warning=warning,
            recommendation=recommendation,
        )

        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "planting_date": request.planting_date,
            "expected_harvest_date": expected_date,
            "confidence": 0.78,
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

    def _growth_days_for(self, crop_name: str) -> int:
        key = self._normalize_key(crop_name)
        return self.default_growth_days.get(key, 70)

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
