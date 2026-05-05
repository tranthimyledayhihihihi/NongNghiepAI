"""
Pricing Service - merged Tien (repository + schema) + Quang (DB queries + mock data)
- API endpoints dùng: get_current_price, suggest_price, forecast_price, get_price_history
- Internal: analyze_price_trend (dùng bởi market_service, price_forecast_service)
"""
from datetime import datetime, timedelta
from unicodedata import category, normalize

from sqlalchemy import desc
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

GRADE_MULTIPLIERS = {
    "Loại 1": 1.0, "grade_1": 1.0,
    "Loại 2": 0.75, "grade_2": 0.75,
    "Loại 3": 0.45, "grade_3": 0.45,
}


def quantity_discount(qty: float) -> float:
    if qty >= 1000:
        return 0.92
    if qty >= 500:
        return 0.95
    if qty >= 100:
        return 0.97
    return 1.0


class PricingService:
    """Service xử lý định giá nông sản."""

    quality_multipliers = {
        "grade_1": 1.0, "loai_1": 1.0,
        "grade_2": 0.82, "loai_2": 0.82,
        "grade_3": 0.58, "loai_3": 0.58,
    }

    crop_base_prices = {
        "ca chua": 22000,
        "dua chuot": 18000,
        "rau muong": 9000,
        "cai xanh": 13000,
        "ot": 30000,
        "lua": 8500,
    }

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def get_current_price(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str = "grade_1",
    ) -> dict:
        """Lấy giá hiện tại, có cache Redis 1 giờ."""
        cache_key = f"price:{crop_name}:{region}:{quality_grade}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached

        latest_price = get_latest_price(db, crop_name, region, quality_grade)
        if latest_price:
            current_price = float(latest_price.price)
            last_updated = latest_price.collected_at
        else:
            # Fallback: thử lấy từ DB trực tiếp, rồi mock
            current_price = self._get_price_from_db(db, crop_name, region, quality_grade)
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
            {**result, "last_updated": result["last_updated"].isoformat() if hasattr(result["last_updated"], "isoformat") else result["last_updated"]},
            expire=3600,
        )
        return result

    def suggest_price(self, db: Session, request: PricingSuggestRequest) -> dict:
        """Đề xuất giá bán (min/suggested/max) dựa trên giá hiện tại và số lượng."""
        current = self.get_current_price(db, request.crop_name, request.region, request.quality_grade)
        base_price = float(current["current_price"])
        discount = quantity_discount(request.quantity)
        multiplier = GRADE_MULTIPLIERS.get(request.quality_grade, 0.75)
        suggested_price = round(base_price * multiplier * discount, 2)
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
            "message": "Gia de xuat dua tren du lieu thi truong hien tai.",
        }

    def forecast_price(self, crop_name: str, region: str, days: int = 7) -> dict:
        """Dự báo giá đơn giản (không cần DB). Dùng bởi /api/pricing/forecast."""
        base_price = self._mock_price(crop_name, region, "grade_1")
        forecast_data = []
        for offset in range(1, days + 1):
            predicted = round(base_price * (1 + offset * 0.006), 2)
            forecast_data.append({
                "date": (datetime.now() + timedelta(days=offset)).date().isoformat(),
                "predicted_price": predicted,
                "confidence_lower": round(predicted * 0.92, 2),
                "confidence_upper": round(predicted * 1.08, 2),
            })

        return {
            "crop_name": crop_name,
            "region": region,
            "forecast_data": forecast_data,
            "trend": "increasing" if days >= 3 else "stable",
            "recommendation": "Gia du bao tang nhe, co the can nhac giu hang neu bao quan duoc.",
        }

    def get_price_history(self, db: Session, crop_name: str, region: str, days: int = 30) -> list[dict]:
        """Lấy lịch sử giá, fallback về mock nếu không có dữ liệu."""
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

        # Fallback mock
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

    def analyze_price_trend(self, db: Session, crop_name: str, region: str) -> str:
        """Phân tích xu hướng giá: increasing / decreasing / stable."""
        # Thử qua repository trước
        recent_prices = get_recent_market_prices(db, crop_name, region)
        if len(recent_prices) >= 2:
            prices = [float(item.price) for item in reversed(recent_prices)]
        else:
            # Fallback: query trực tiếp DB
            prices = self._get_recent_prices_from_db(db, crop_name, region)

        if len(prices) < 2:
            return "stable"

        mid = max(len(prices) // 2, 1)
        first_avg = sum(prices[:mid]) / mid
        second_avg = sum(prices[mid:]) / max(len(prices) - mid, 1)
        change = ((second_avg - first_avg) / first_avg) * 100
        if change > 5:
            return "increasing"
        if change < -5:
            return "decreasing"
        return "stable"

    # ------------------------------------------------------------------ #
    # Helpers - kết hợp cả Tien và Quang
    # ------------------------------------------------------------------ #

    def _get_price_from_db(self, db: Session, crop_name: str, region: str, quality_grade: str) -> float:
        """Lấy giá từ DB trực tiếp (Quang) rồi fallback mock."""
        try:
            from app.models.crop import CropType
            from app.models.price import MarketPrice
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if crop:
                row = (
                    db.query(MarketPrice)
                    .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
                    .order_by(desc(MarketPrice.PriceDate))
                    .first()
                )
                if row:
                    base = float(row.PricePerKg)
                    multiplier = self.quality_multipliers.get(quality_grade, 1.0)
                    return round(base * multiplier, 2)
                if crop.TypicalPriceMin and crop.TypicalPriceMax:
                    base = (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
                    return round(base, 2)
        except Exception:
            pass
        return self._mock_price(crop_name, region, quality_grade)

    def _get_recent_prices_from_db(self, db: Session, crop_name: str, region: str) -> list[float]:
        """Query giá gần đây trực tiếp từ MarketPrice (Quang)."""
        try:
            from app.models.crop import CropType
            from app.models.price import MarketPrice
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return []
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
                .order_by(desc(MarketPrice.PriceDate))
                .limit(7)
                .all()
            )
            return [float(r.PricePerKg) for r in reversed(rows)]
        except Exception:
            return []

    def _nearby_region_prices(self, db: Session, crop_name: str, region: str) -> list[dict]:
        """Lấy giá các vùng lân cận."""
        latest_prices = get_latest_prices_by_crop(db, crop_name, limit=10)
        result = []
        seen = {region}
        for item in latest_prices:
            if item.region in seen:
                continue
            seen.add(item.region)
            result.append({
                "region": item.region,
                "price": float(item.price),
                "unit": getattr(item, "unit", "VND/kg"),
                "collected_at": item.collected_at.isoformat(),
            })
        if result:
            return result

        # Fallback mock
        fallback_regions = ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho"]
        return [
            {
                "region": r,
                "price": self._mock_price(crop_name, r, "grade_1"),
                "unit": "VND/kg",
                "collected_at": datetime.now().isoformat(),
            }
            for r in fallback_regions if r != region
        ][:3]

    def _mock_price(self, crop_name: str, region: str, quality_grade: str) -> float:
        key = self._normalize_key(crop_name)
        base = self.crop_base_prices.get(key, 20000)
        region_factor = 1 + ((sum(ord(c) for c in region) % 9) - 4) / 100
        multiplier = self.quality_multipliers.get(quality_grade, 1.0)
        return round(base * region_factor * multiplier, 2)

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = normalize("NFD", value.strip().lower())
        return "".join(char for char in normalized if category(char) != "Mn")


pricing_service = PricingService()
