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
    # ASCII (DB constraint values)
    "Loai 1": 1.0,  "Loai 2": 0.75,  "Loai 3": 0.45,
    # Legacy Vietnamese keys (giữ để tương thích ngược)
    "Loại 1": 1.0,  "Loại 2": 0.75,  "Loại 3": 0.45,
    # English API keys
    "grade_1": 1.0, "grade_2": 0.75, "grade_3": 0.45,
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
        # English API keys
        "grade_1": 1.0,  "grade_2": 0.82,  "grade_3": 0.58,
        # ASCII DB keys
        "Loai 1": 1.0,   "Loai 2": 0.82,   "Loai 3": 0.58,
        # Legacy Vietnamese (tương thích ngược)
        "loai_1": 1.0,   "loai_2": 0.82,   "loai_3": 0.58,
        "Loại 1": 1.0,   "Loại 2": 0.82,   "Loại 3": 0.58,
    }

    crop_base_prices = {
        # Rau củ
        "ca chua": 22000,
        "dua chuot": 18000,
        "rau muong": 9000,
        "cai xanh": 13000,
        "ot": 30000,
        "khoai lang": 18000,
        "khoai tay": 20000,
        # Lúa gạo
        "lua": 8500,
        "ngo": 6500,
        # Trái cây
        "sau rieng": 75000,
        "xoai": 25000,
        "thanh long": 20000,
        "chuoi": 12000,
        "cam": 30000,
        "buoi": 22000,
        "mit": 15000,
        "dua hau": 8000,
        # Công nghiệp
        "ca phe": 110000,
        "ho tieu": 75000,
        "tieu": 75000,
        "dieu": 45000,
        "dau nanh": 18000,
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
        include_weather: bool = True,
    ) -> dict:
        """Lấy giá hiện tại + điều chỉnh theo thời tiết 7 ngày tới. Cache Redis 1 giờ."""
        cache_key = f"price:{crop_name}:{region}:{quality_grade}"
        cached = redis_client.get(cache_key)
        if cached:
            return {
                **cached,
                "source": "cached",
                "source_name": cached.get("source_name") or "Redis price cache",
                "cache_status": "cached",
                "is_mock": bool(cached.get("is_mock")),
                "confidence": cached.get("confidence", 0.72),
            }

        latest_price = get_latest_price(db, crop_name, region, quality_grade)
        if latest_price:
            current_price = float(latest_price.price)
            last_updated = latest_price.collected_at
            source_name = latest_price.SourceName or "MarketPrices DB"
            source_url = latest_price.SourceURL
            price_date = latest_price.PriceDate
            is_mock = False
            cache_status = "from_db"
        else:
            current_price = self._get_price_from_db(db, crop_name, region, quality_grade)
            last_updated = datetime.now()
            source_name = "Pricing fallback"
            source_url = None
            price_date = None
            is_mock = True
            cache_status = "mock"

        result = {
            "crop_name": crop_name,
            "crop": crop_name,
            "region": region,
            "current_price": current_price,
            "market_price": current_price,
            "quality_grade": quality_grade,
            "price_trend": self.analyze_price_trend(db, crop_name, region),
            "last_updated": last_updated,
            "source": "database" if not is_mock else "mock",
            "source_name": source_name,
            "source_url": source_url,
            "price_date": price_date,
            "cache_status": cache_status,
            "is_mock": is_mock,
            "confidence": 0.82 if not is_mock else 0.45,
        }

        # Bổ sung điều chỉnh thời tiết
        if include_weather:
            try:
                from app.services.weather_pricing_service import get_weather_adjusted_pricing
                weather_info = get_weather_adjusted_pricing(
                    db, crop_name, region, current_price
                )
                result["weather_adjusted_price"] = weather_info["adjusted_price"]
                result["weather_factor"]          = weather_info["weather_factor"]
                result["weather_summary"]         = weather_info["weather_summary"]
                result["weather_explanation"]     = weather_info["weather_explanation"]
                result["price_change_pct"]        = weather_info["price_change_pct"]
            except Exception:
                pass

        redis_client.set(
            cache_key,
            {**result, "last_updated": result["last_updated"].isoformat() if hasattr(result["last_updated"], "isoformat") else result["last_updated"]},
            expire=3600,
        )
        return result

    def suggest_price(self, db: Session, request: PricingSuggestRequest) -> dict:
        """Đề xuất giá bán (min/suggested/max) dựa trên giá thị trường + thời tiết 7 ngày tới."""
        current = self.get_current_price(
            db, request.crop_name, request.region, request.quality_grade,
            include_weather=True,
        )
        base_price = float(current["current_price"])
        discount = quantity_discount(request.quantity)
        multiplier = GRADE_MULTIPLIERS.get(request.quality_grade, 0.75)

        # Giá cơ sở (không thời tiết)
        suggested_price = round(base_price * multiplier * discount, 2)
        min_price = round(suggested_price * 0.92, 2)
        max_price = round(suggested_price * 1.08, 2)

        # Giá điều chỉnh theo thời tiết
        weather_factor = current.get("weather_factor", 1.0)
        weather_suggested = round(suggested_price * weather_factor, 2)
        weather_min = round(min_price * weather_factor, 2)
        weather_max = round(max_price * weather_factor, 2)

        nearby_prices = self._nearby_region_prices(db, request.crop_name, request.region)

        create_pricing_request(
            db,
            crop_name=request.crop_name,
            region=request.region,
            quantity=request.quantity,
            quality_grade=request.quality_grade,
            suggested_price=weather_suggested,
            min_price=weather_min,
            max_price=weather_max,
        )
        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "quantity": request.quantity,
            "quality_grade": request.quality_grade,
            # Giá gốc (không tính thời tiết)
            "min_price":       min_price,
            "suggested_price": suggested_price,
            "max_price":       max_price,
            # Giá điều chỉnh theo thời tiết (khuyến nghị dùng)
            "weather_min_price":       weather_min,
            "weather_suggested_price": weather_suggested,
            "weather_max_price":       weather_max,
            "weather_factor":          weather_factor,
            "weather_summary":         current.get("weather_summary", ""),
            "weather_explanation":     current.get("weather_explanation", ""),
            "price_change_pct":        current.get("price_change_pct", 0.0),
            "unit": "VND/kg",
            "nearby_region_prices": nearby_prices,
            "message": "Giá đề xuất đã được điều chỉnh theo dự báo thời tiết 7 ngày tới.",
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
            "recommendation": "Giá dự báo tăng nhẹ, có thể cân nhắc giữ hàng nếu bảo quản được.",
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
    def forecast_price(self, crop_name: str, region: str, days: int = 7) -> dict:
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
            "crop": crop_name,
            "region": region,
            "forecast_data": forecast_data,
            "forecast_price_7d": forecast_data[min(days, 7) - 1]["predicted_price"] if forecast_data else base_price,
            "trend": "increasing" if days >= 3 else "stable",
            "recommendation": "Gia du bao tang nhe, co the can nhac giu hang neu bao quan duoc.",
            "confidence": 0.62,
            "source": "mock",
            "source_name": "Rule-based moving average forecast",
            "cache_status": "mock",
            "is_mock": True,
            "last_updated": datetime.now(),
        }

    def build_pricing_engine(
        self,
        db: Session,
        *,
        crop_name: str,
        region: str,
        quantity: float = 1,
        quality_grade: str = "grade_1",
        days: int = 7,
    ) -> dict:
        current = self.get_current_price(db, crop_name, region, quality_grade)
        forecast = self.forecast_price(crop_name, region, days)
        suggestion = self.suggest_price(
            db,
            PricingSuggestRequest(
                crop_name=crop_name,
                region=region,
                quantity=max(float(quantity or 1), 1),
                quality_grade=quality_grade,
            ),
        )
        history = self.get_price_history(db, crop_name, region, 30)
        trend = current.get("price_trend") or forecast.get("trend") or "stable"
        market_price = float(current["current_price"])
        forecast_price_7d = float(forecast.get("forecast_price_7d") or market_price)
        suggested_price = float(suggestion.get("weather_suggested_price") or suggestion.get("suggested_price") or market_price)
        reasons = [
            f"Market price from {current.get('source_name', 'backend')}: {market_price:,.0f} VND/kg",
            f"Trend is {trend} from recent DB/history signals",
            f"Quality grade {quality_grade} and quantity {quantity:g} kg adjusted selling price",
        ]
        if suggestion.get("weather_summary"):
            reasons.append(suggestion["weather_summary"])
        recommendation = (
            "Sell in small batches and enable a price alert."
            if trend == "stable"
            else "Consider holding part of the stock for 7 days."
            if trend == "increasing"
            else "Prioritize selling soon or locking buyer commitments."
        )
        is_mock = bool(current.get("is_mock")) or bool(forecast.get("is_mock"))
        confidence = 0.76 if not is_mock else 0.48
        return {
            "crop": crop_name,
            "crop_name": crop_name,
            "region": region,
            "market_price": market_price,
            "current_price": market_price,
            "forecast_price_7d": forecast_price_7d,
            "suggested_price": suggested_price,
            "trend": trend,
            "confidence": confidence,
            "reasons": reasons,
            "recommendation": recommendation,
            "history": history,
            "forecast": forecast.get("forecast_data", []),
            "nearby_region_prices": suggestion.get("nearby_region_prices", []),
            "source": "ai_generated" if not is_mock else "mock",
            "source_name": "AI Pricing Engine rule fallback",
            "is_mock": is_mock,
            "cache_status": current.get("cache_status", "computed"),
            "last_updated": datetime.now(),
        }

    def compare_regions(self, db: Session, crop_name: str, region: str = "Ha Noi") -> dict:
        suggestion = self.suggest_price(
            db,
            PricingSuggestRequest(
                crop_name=crop_name,
                region=region,
                quantity=1,
                quality_grade="grade_1",
            ),
        )
        regions = suggestion.get("nearby_region_prices", [])
        return {
            "crop_name": crop_name,
            "crop": crop_name,
            "base_region": region,
            "regions": regions,
            "best_region": max(regions, key=lambda item: item.get("price", 0), default=None),
            "source": "database" if regions else "mock",
            "source_name": "MarketPrices DB / pricing fallback",
            "is_mock": not bool(regions),
            "cache_status": "from_db" if regions else "mock",
            "confidence": 0.72 if regions else 0.42,
            "last_updated": datetime.now(),
        }

    def explain_pricing(self, db: Session, crop_name: str, region: str, quality_grade: str = "grade_1") -> dict:
        engine = self.build_pricing_engine(
            db,
            crop_name=crop_name,
            region=region,
            quality_grade=quality_grade,
            quantity=1,
            days=7,
        )
        return {
            **engine,
            "explanation": {
                "summary": engine["recommendation"],
                "factors": engine["reasons"],
                "confidence_note": "Confidence drops when market API/DB is missing and demo fallback is used.",
            },
        }

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
