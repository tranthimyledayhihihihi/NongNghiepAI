from datetime import datetime, timedelta
from unicodedata import category, normalize

from sqlalchemy.orm import Session

from app.core.redis_client import redis_client
from app.repositories.price_repository import (
    create_pricing_request,
    get_latest_price,
    get_latest_prices_by_crop,
    get_price_history,
    get_recent_market_prices,
)
from app.schemas.price_schema import PricingSuggestRequest


class PricingService:
    quality_multipliers = {
        "grade_1": 1.0,
        "grade_2": 0.82,
        "grade_3": 0.58,
        "loai_1": 1.0,
        "loai_2": 0.82,
        "loai_3": 0.58,
    }

    crop_base_prices = {
        "ca chua": 22000,
        "dua chuot": 18000,
        "rau muong": 9000,
        "cai xanh": 13000,
        "ot": 30000,
        "lua": 8500,
    }

    def get_current_price(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str = "grade_1",
    ) -> dict:
        cache_key = f"price:{crop_name}:{region}:{quality_grade}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached

        latest_price = get_latest_price(db, crop_name, region, quality_grade)
        if latest_price:
            current_price = float(latest_price.price)
            last_updated = latest_price.collected_at
        else:
            current_price = self._mock_price(crop_name, region, quality_grade)
            last_updated = datetime.now()

        result = {
            "crop_name": crop_name,
            "region": region,
            "current_price": current_price,
            "quality_grade": quality_grade,
            "price_trend": self.analyze_price_trend(db, crop_name, region),
            "last_updated": last_updated,
        }
        redis_client.set(
            cache_key,
            {**result, "last_updated": result["last_updated"].isoformat()},
            expire=3600,
        )
        return result

    def suggest_price(self, db: Session, request: PricingSuggestRequest) -> dict:
        current = self.get_current_price(
            db,
            request.crop_name,
            request.region,
            request.quality_grade,
        )
        base_price = float(current["current_price"])
        quantity_adjustment = 0.95 if request.quantity >= 1000 else 1.0
        suggested_price = round(base_price * quantity_adjustment, 2)
        min_price = round(suggested_price * 0.92, 2)
        max_price = round(suggested_price * 1.08, 2)
        nearby_prices = self._nearby_region_prices(db, request.crop_name, request.region)

        create_pricing_request(
            db,
            crop_name=request.crop_name,
            region=request.region,
            quantity=request.quantity,
            quality_grade=request.quality_grade,
            suggested_price=suggested_price,
            min_price=min_price,
            max_price=max_price,
        )
        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "quantity": request.quantity,
            "quality_grade": request.quality_grade,
            "min_price": min_price,
            "suggested_price": suggested_price,
            "max_price": max_price,
            "unit": "VND/kg",
            "nearby_region_prices": nearby_prices,
            "message": "Gia de xuat dang dung mock/repository MVP, san sang de gan crawler/AI.",
        }

    def get_price_history(self, db: Session, crop_name: str, region: str, days: int = 30) -> list[dict]:
        history = get_price_history(db, crop_name, region, days)
        if history:
            return [
                {
                    "date": item.record_date.isoformat(),
                    "avg_price": float(item.avg_price),
                    "min_price": float(item.min_price or item.avg_price),
                    "max_price": float(item.max_price or item.avg_price),
                }
                for item in history
            ]

        base_price = self._mock_price(crop_name, region, "grade_1")
        return [
            {
                "date": (datetime.now() - timedelta(days=i)).date().isoformat(),
                "avg_price": round(base_price * (1 + ((days - i) % 5 - 2) * 0.01), 2),
                "min_price": round(base_price * 0.94, 2),
                "max_price": round(base_price * 1.06, 2),
            }
            for i in range(days, 0, -1)
        ]

    def forecast_price(self, crop_name: str, region: str, days: int = 7) -> dict:
        base_price = self._mock_price(crop_name, region, "grade_1")
        forecast_data = []
        for offset in range(1, days + 1):
            predicted = round(base_price * (1 + offset * 0.006), 2)
            forecast_data.append(
                {
                    "date": (datetime.now() + timedelta(days=offset)).date().isoformat(),
                    "predicted_price": predicted,
                    "confidence_lower": round(predicted * 0.92, 2),
                    "confidence_upper": round(predicted * 1.08, 2),
                }
            )

        return {
            "crop_name": crop_name,
            "region": region,
            "forecast_data": forecast_data,
            "trend": "increasing" if days >= 3 else "stable",
            "recommendation": "Gia du bao tang nhe, co the can nhac giu hang neu bao quan duoc.",
        }

    def analyze_price_trend(self, db: Session, crop_name: str, region: str) -> str:
        recent_prices = get_recent_market_prices(db, crop_name, region)
        if len(recent_prices) < 2:
            return "stable"
        prices = [float(item.price) for item in reversed(recent_prices)]
        midpoint = max(len(prices) // 2, 1)
        first_avg = sum(prices[:midpoint]) / midpoint
        second_avg = sum(prices[midpoint:]) / max(len(prices) - midpoint, 1)
        change = ((second_avg - first_avg) / first_avg) * 100
        if change > 5:
            return "increasing"
        if change < -5:
            return "decreasing"
        return "stable"

    def _mock_price(self, crop_name: str, region: str, quality_grade: str) -> float:
        key = self._normalize_key(crop_name)
        base = self.crop_base_prices.get(key, 20000)
        region_factor = 1 + ((sum(ord(char) for char in region) % 9) - 4) / 100
        multiplier = self.quality_multipliers.get(quality_grade, 1.0)
        return round(base * region_factor * multiplier, 2)

    def _nearby_region_prices(self, db: Session, crop_name: str, region: str) -> list[dict]:
        latest_prices = get_latest_prices_by_crop(db, crop_name, limit=10)
        result = []
        seen = {region}
        for item in latest_prices:
            if item.region in seen:
                continue
            seen.add(item.region)
            result.append(
                {
                    "region": item.region,
                    "price": float(item.price),
                    "unit": item.unit,
                    "collected_at": item.collected_at.isoformat(),
                }
            )
        if result:
            return result

        fallback_regions = ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho"]
        return [
            {
                "region": fallback_region,
                "price": self._mock_price(crop_name, fallback_region, "grade_1"),
                "unit": "VND/kg",
                "collected_at": datetime.now().isoformat(),
            }
            for fallback_region in fallback_regions
            if fallback_region != region
        ][:3]

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = normalize("NFD", value.strip().lower())
        return "".join(char for char in normalized if category(char) != "Mn")


pricing_service = PricingService()
