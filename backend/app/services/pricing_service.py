"""
P2-09: Pricing Service
Dựa vào giá mới nhất, chất lượng, số lượng, khu vực để đề xuất min/suggested/max price.
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.price import MarketPrice, PriceHistory
from ..models.crop import CropType
from ..core.redis_client import redis_client

GRADE_MULTIPLIERS = {
    "Loại 1": 1.0, "grade_1": 1.0,
    "Loại 2": 0.75, "grade_2": 0.75,
    "Loại 3": 0.45, "grade_3": 0.45,
}

def quantity_discount(qty):
    if qty >= 1000: return 0.92
    elif qty >= 500: return 0.95
    elif qty >= 100: return 0.97
    return 1.0


class PricingService:
    """Service xử lý định giá nông sản."""

    def suggest_price(self, db, crop_name, region, quantity=0, quality_grade="Loại 1"):
        crop = self._get_crop(db, crop_name)
        market_price = self._get_latest_market_price(db, crop.CropID if crop else None, region)
        if market_price:
            base = float(market_price)
        elif crop and crop.TypicalPriceMin and crop.TypicalPriceMax:
            base = (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
        else:
            base = 20000.0
        multiplier = GRADE_MULTIPLIERS.get(quality_grade, 0.75)
        discount = quantity_discount(quantity)
        suggested = base * multiplier * discount
        min_price = suggested * 0.90
        max_price = suggested * 1.10
        nearby = self._get_nearby_region_prices(db, crop.CropID if crop else None, region)
        return {
            "crop_name": crop_name,
            "region": region,
            "quality_grade": quality_grade,
            "quantity_kg": quantity,
            "suggested_price": round(suggested),
            "min_price": round(min_price),
            "max_price": round(max_price),
            "nearby_region_prices": nearby,
            "price_basis": "market_data" if market_price else "typical_range",
        }

    def get_current_price(self, db, crop_name, region, quality_grade="Loại 1"):
        cache_key = f"price:{crop_name}:{region}:{quality_grade}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached
        crop = self._get_crop(db, crop_name)
        if not crop:
            return None
        price = self._get_latest_market_price(db, crop.CropID, region)
        if not price:
            return None
        result = {
            "crop_name": crop_name,
            "region": region,
            "current_price": float(price),
            "quality_grade": quality_grade,
            "last_updated": datetime.now().isoformat(),
        }
        redis_client.set(cache_key, result, expire=3600)
        return result

    def get_price_history(self, db, crop_name, region, days=30):
        crop = self._get_crop(db, crop_name)
        if not crop:
            return []
        start_date = (datetime.now() - timedelta(days=days)).date()
        history = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.CropID == crop.CropID,
                PriceHistory.Region == region,
                PriceHistory.RecordDate >= start_date,
            )
            .order_by(PriceHistory.RecordDate)
            .all()
        )
        return [
            {
                "date": h.RecordDate.isoformat(),
                "avg_price": float(h.AvgPrice),
                "min_price": float(h.MinPrice) if h.MinPrice else None,
                "max_price": float(h.MaxPrice) if h.MaxPrice else None,
            }
            for h in history
        ]

    def analyze_price_trend(self, db, crop_name, region):
        crop = self._get_crop(db, crop_name)
        if not crop:
            return "stable"
        recent = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
            .order_by(desc(MarketPrice.PriceDate))
            .limit(7)
            .all()
        )
        if len(recent) < 2:
            return "stable"
        prices = [float(p.PricePerKg) for p in reversed(recent)]
        mid = len(prices) // 2
        first = sum(prices[:mid]) / mid
        second = sum(prices[mid:]) / (len(prices) - mid)
        change = ((second - first) / first) * 100
        if change > 5: return "increasing"
        elif change < -5: return "decreasing"
        return "stable"

    @staticmethod
    def _get_crop(db, crop_name):
        return db.query(CropType).filter(CropType.CropName == crop_name).first()

    @staticmethod
    def _get_latest_market_price(db, crop_id, region):
        if not crop_id:
            return None
        row = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop_id, MarketPrice.Region == region)
            .order_by(desc(MarketPrice.PriceDate))
            .first()
        )
        return float(row.PricePerKg) if row else None

    @staticmethod
    def _get_nearby_region_prices(db, crop_id, region):
        if not crop_id:
            return []
        rows = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop_id, MarketPrice.Region != region)
            .order_by(desc(MarketPrice.PriceDate))
            .limit(20)
            .all()
        )
        seen = {}
        for r in rows:
            if r.Region not in seen:
                seen[r.Region] = float(r.PricePerKg)
        return [{"region": k, "price": v} for k, v in seen.items()]


pricing_service = PricingService()
