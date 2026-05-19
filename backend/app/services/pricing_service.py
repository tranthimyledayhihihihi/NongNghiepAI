"""
Pricing Service
- Chuẩn hoá luồng giá hiện tại, lịch sử, dự báo, so sánh vùng miền và phân tích thị trường.
- Mọi điểm gọi nên đi qua service này thay vì tự mock rải rác ở controller/frontend.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from unicodedata import normalize as unicode_normalize
import unicodedata

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.common import ensure_crop, normalize_text, to_db_grade
from app.repositories.price_repository import (
    create_pricing_request,
    get_latest_price,
    get_latest_prices_by_crop,
    get_price_history,
    get_recent_market_prices,
)
from app.schemas.price_schema import PricingSuggestRequest
from app.services.price_aggregator_service import price_aggregator_service


GRADE_MULTIPLIERS = {
    "grade_1": 1.0,
    "grade_2": 0.88,
    "grade_3": 0.76,
    "Loai 1": 1.0,
    "Loai 2": 0.88,
    "Loai 3": 0.76,
    "loai_1": 1.0,
    "loai_2": 0.88,
    "loai_3": 0.76,
    "Loại 1": 1.0,
    "Loại 2": 0.88,
    "Loại 3": 0.76,
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
    """Service xử lý giá nông sản và phân tích thị trường."""

    quality_multipliers = GRADE_MULTIPLIERS

    crop_base_prices = {
        "ca chua": 22000,
        "dua chuot": 18000,
        "rau muong": 9000,
        "cai xanh": 13000,
        "ot": 30000,
        "khoai lang": 18000,
        "khoai tay": 20000,
        "lua": 8500,
        "gao": 12000,
        "ngo": 6500,
        "sau rieng": 75000,
        "xoai": 25000,
        "thanh long": 20000,
        "chuoi": 12000,
        "cam": 30000,
        "buoi": 22000,
        "mit": 15000,
        "dua hau": 8000,
        "ca phe": 110000,
        "ho tieu": 75000,
        "tieu": 75000,
        "dieu": 45000,
        "dau nanh": 18000,
        "cao su": 30000,
    }

    def get_current_price(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str = "grade_1",
        include_weather: bool = True,
        force_refresh: bool = False,
    ) -> dict:
        from app.core.redis_client import redis_client

        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        selected_grade = self._clean_grade(quality_grade)

        if not force_refresh:
            cache_key = f"price:{selected_crop}:{selected_region}:{selected_grade}"
            cached = redis_client.get(cache_key)
            if cached and isinstance(cached, dict):
                return cached

        if force_refresh:
            price_aggregator_service.refresh_prices(db, crop_name=selected_crop)

        latest_price = get_latest_price(db, selected_crop, selected_region, selected_grade)
        if latest_price is None and settings.ENABLE_STOOQ_PRICE_SOURCE:
            refresh_result = price_aggregator_service.refresh_prices(db, crop_name=selected_crop)
            if refresh_result.get("status") == "success":
                latest_price = get_latest_price(db, selected_crop, selected_region, selected_grade)

        if latest_price:
            current_price = float(latest_price.PricePerKg)
            source = "database"
            source_name = latest_price.SourceName or "MarketPrices DB"
            source_url = latest_price.SourceURL
            last_updated = latest_price.UpdatedAt
            price_date = latest_price.PriceDate
            is_mock = False
            cache_status = self._cache_status(latest_price.UpdatedAt)
        else:
            current_price = self._get_price_from_crop_profile(db, selected_crop, selected_region, selected_grade)
            source = "mock"
            source_name = "Dữ liệu mô phỏng"
            source_url = None
            last_updated = datetime.now()
            price_date = None
            is_mock = True
            cache_status = "mock"

        previous_price = self._previous_price(db, selected_crop, selected_region, selected_grade)
        price_change = round(current_price - previous_price, 2) if previous_price else 0.0
        price_change_percent = round((price_change / previous_price) * 100, 2) if previous_price else 0.0
        trend = self._trend_from_change(price_change_percent)

        result = {
            "crop_name": crop_name.strip(),
            "crop": crop_name.strip(),
            "region": selected_region,
            "current_price": round(float(current_price), 2),
            "market_price": round(float(current_price), 2),
            "price": round(float(current_price), 2),
            "unit": "VNĐ/kg",
            "quality_grade": selected_grade,
            "price_trend": self.analyze_price_trend(db, selected_crop, selected_region),
            "trend": trend,
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_percent, 2),
            "last_updated": last_updated,
            "fetched_at": last_updated,
            "price_date": price_date,
            "source": source,
            "source_type": source,
            "source_name": source_name,
            "source_url": source_url,
            "cache_status": cache_status,
            "is_mock": is_mock,
            "confidence": 0.84 if not is_mock else 0.42,
            "data_age_minutes": self._age_minutes(last_updated),
        }

        if include_weather:
            result.update(self._safe_weather_adjustment(db, selected_crop, selected_region, current_price))

        return result

    def refresh_current_price(self, db: Session, crop_name: str, region: str, quality_grade: str = "grade_1") -> dict:
        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        selected_grade = self._clean_grade(quality_grade)

        refresh_result = price_aggregator_service.refresh_prices(db, crop_name=selected_crop)
        current = self.get_current_price(
            db,
            selected_crop,
            selected_region,
            selected_grade,
            include_weather=False,
            force_refresh=False,
        )
        current["refresh_result"] = refresh_result
        current["source"] = current.get("source") or ("database" if not current.get("is_mock") else "mock")
        current["source_type"] = current["source"]
        current["message"] = (
            "Đã làm mới giá từ nguồn thực tế"
            if refresh_result.get("status") == "success" and not current.get("is_mock")
            else "Chưa lấy được giá thực tế, đang trả về dữ liệu dự phòng"
        )
        return current

    def suggest_price(self, db: Session, request: PricingSuggestRequest) -> dict:
        current = self.get_current_price(
            db,
            request.crop_name,
            request.region,
            request.quality_grade,
            include_weather=True,
        )
        base_price = float(current["current_price"])
        discount = quantity_discount(request.quantity)
        multiplier = GRADE_MULTIPLIERS.get(request.quality_grade, 0.88)

        suggested_price = round(base_price * multiplier * discount, 2)
        min_price = round(suggested_price * 0.92, 2)
        max_price = round(suggested_price * 1.08, 2)

        weather_factor = float(current.get("weather_factor", 1.0))
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
            "min_price": min_price,
            "suggested_price": suggested_price,
            "max_price": max_price,
            "weather_min_price": weather_min,
            "weather_suggested_price": weather_suggested,
            "weather_max_price": weather_max,
            "weather_factor": weather_factor,
            "weather_summary": current.get("weather_summary", ""),
            "weather_explanation": current.get("weather_explanation", ""),
            "price_change_pct": current.get("price_change_percent", 0.0),
            "unit": "VNĐ/kg",
            "nearby_region_prices": nearby_prices,
            "source": current.get("source", "database"),
            "source_name": current.get("source_name"),
            "source_url": current.get("source_url"),
            "last_updated": current.get("last_updated"),
            "is_mock": current.get("is_mock", False),
            "cache_status": current.get("cache_status", "from_db"),
            "confidence": current.get("confidence", 0.7),
            "message": "Giá đề xuất đã được điều chỉnh theo dữ liệu giá hiện tại và thời tiết.",
        }

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
            "region": self._clean_region(region),
            "forecast_data": forecast_data,
            "forecast_price_7d": forecast_data[min(days, 7) - 1]["predicted_price"] if forecast_data else base_price,
            "trend": "increasing" if days >= 3 else "stable",
            "recommendation": "Giá dự báo tăng nhẹ, có thể cân nhắc giữ hàng nếu bảo quản được.",
            "confidence": 0.6,
            "source": "mock",
            "source_name": "Rule-based moving average forecast",
            "cache_status": "mock",
            "is_mock": True,
            "last_updated": datetime.now(),
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
                    "source": "database",
                    "source_name": "PriceHistory DB",
                    "fetched_at": datetime.now().isoformat(),
                    "updated_at": item.record_date.isoformat(),
                    "confidence": 0.7,
                    "is_mock": False,
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
                "source": "mock",
                "source_name": "Pricing demo history",
                "fetched_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "confidence": 0.42,
                "is_mock": True,
            }
            for i in range(days, 0, -1)
        ]

    def analyze_price_trend(self, db: Session, crop_name: str, region: str) -> str:
        recent_prices = get_recent_market_prices(db, crop_name, region)
        if len(recent_prices) >= 2:
            prices = [float(item.price) for item in reversed(recent_prices)]
        else:
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
        source_label = current.get("source_name") or "hệ thống"
        trend_label = {"stable": "ổn định", "increasing": "tăng", "decreasing": "giảm"}.get(trend, trend)
        reasons = [
            f"Giá thị trường từ {source_label}: {market_price:,.0f} VNĐ/kg",
            f"Xu hướng {trend_label} dựa trên tín hiệu lịch sử giá gần đây.",
            f"Chất lượng {quality_grade} và sản lượng {quantity:g} kg được dùng để điều chỉnh giá bán.",
        ]
        if suggestion.get("weather_summary"):
            reasons.append(suggestion["weather_summary"])

        recommendation = (
            "Nên bán theo từng đợt nhỏ và bật cảnh báo giá."
            if trend == "stable"
            else "Có thể giữ lại một phần hàng trong 7 ngày nếu bảo quản được."
            if trend == "increasing"
            else "Nên ưu tiên bán sớm hoặc chốt cam kết với người mua."
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
            "last_updated": datetime.now().isoformat(),
        }

    def compare_regions(self, db: Session, crop_name: str, region: str = "Ha Noi") -> dict:
        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        base_current = self.get_current_price(db, selected_crop, selected_region, include_weather=False)
        base_price = float(base_current.get("current_price") or 0)

        regions = [
            selected_region,
            "Lâm Đồng",
            "Gia Lai",
            "Đắk Lắk",
            "Đồng Nai",
            "Cần Thơ",
        ]
        items = []
        for item_region in regions:
            current = self.get_current_price(db, selected_crop, item_region, include_weather=False)
            price = float(current.get("current_price") or 0)
            difference_percent = ((price - base_price) / base_price * 100) if base_price else 0
            items.append(
                {
                    "region": item_region,
                    "price": round(price, 2),
                    "difference_percent": round(difference_percent, 2),
                    "source": current.get("source", "database"),
                    "source_name": current.get("source_name"),
                    "last_updated": current.get("last_updated"),
                    "is_mock": current.get("is_mock", False),
                    "confidence": current.get("confidence", 0.7),
                }
            )

        has_real_data = any(not item.get("is_mock") for item in items)
        return {
            "crop_name": crop_name,
            "crop": crop_name,
            "base_region": selected_region,
            "regions": items,
            "best_region": max(items, key=lambda item: item.get("price", 0), default=None),
            "source": "database" if has_real_data else "mock",
            "source_name": "Pricing comparison service",
            "is_mock": not has_real_data,
            "cache_status": "computed",
            "confidence": 0.7 if has_real_data else 0.42,
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
                "confidence_note": "Độ tin cậy giảm khi dữ liệu nguồn thực tế chưa sẵn sàng và hệ thống phải dùng fallback.",
            },
        }

    def get_price_forecast(self, crop_name: str, region: str, days: int = 7) -> dict:
        return self.forecast_price(crop_name, region, days)

    def get_price_comparison(self, db: Session, crop_name: str, regions: list[str]) -> dict:
        regions = regions or ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho"]
        items = [self.get_current_price(db, crop_name, region, include_weather=False) for region in regions]
        has_real_data = any(not item.get("is_mock") for item in items)
        return {
            "crop_name": crop_name,
            "crop": crop_name,
            "regions": items,
            "best_region": max(items, key=lambda item: item.get("current_price", 0), default=None),
            "source": "database" if has_real_data else "mock",
            "source_name": "Pricing comparison service",
            "is_mock": not has_real_data,
            "cache_status": "computed",
            "confidence": 0.7 if has_real_data else 0.42,
            "last_updated": datetime.now(),
        }

    def get_ai_price_recommendation(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str | None = None,
        quantity: float | None = None,
    ) -> dict:
        return self.build_pricing_engine(
            db,
            crop_name=crop_name,
            region=region,
            quantity=quantity or 1,
            quality_grade=quality_grade or "grade_1",
            days=7,
        )

    def analyze_market(
        self,
        db: Session,
        *,
        crop_name: str,
        region: str,
        quantity: float | None = None,
        quality_grade: str | None = None,
    ) -> dict:
        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        selected_grade = self._clean_grade(quality_grade or "grade_2")
        current = self.get_current_price(db, selected_crop, selected_region, selected_grade, include_weather=False)
        history_30 = self.get_price_history(db, selected_crop, selected_region, 30)
        history_7 = self.get_price_history(db, selected_crop, selected_region, 7)
        comparison = self.compare_regions(db, selected_crop, selected_region)

        current_price = float(current.get("current_price") or 0)
        estimated_revenue = round(current_price * float(quantity or 0), 2) if quantity else None

        trend_7d = self._trend_summary(history_7, "7 ngày")
        trend_30d = self._trend_summary(history_30, "30 ngày")
        volatility = self._volatility_summary(history_30)
        recommendation = self._market_recommendation(
            current_price=current_price,
            trend_7d=trend_7d,
            trend_30d=trend_30d,
            quality_grade=selected_grade,
            quantity=quantity,
        )

        confidence_score = self._market_confidence(history_30, current)

        data_sources = [
            {
                "source_type": current.get("source", "database"),
                "source_name": current.get("source_name") or "MarketPrices DB",
                "source_url": current.get("source_url"),
                "fetched_at": self._serialize_dt(current.get("fetched_at") or current.get("last_updated")),
            }
        ]
        if history_30:
            data_sources.append(
                {
                    "source_type": "database",
                    "source_name": "PriceHistory DB",
                    "fetched_at": self._serialize_dt(datetime.now()),
                }
            )

        result = {
            "crop_name": crop_name.strip(),
            "region": selected_region,
            "current_price": current_price,
            "unit": "VNĐ/kg",
            "estimated_revenue": estimated_revenue,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "volatility": volatility,
            "regional_comparison": comparison.get("regions", [])[:2],
            "recommendation": recommendation,
            "risk_level": volatility["level"],
            "confidence_score": confidence_score,
            "data_sources": data_sources,
            "history_7d": history_7,
            "history_30d": history_30,
            "source": current.get("source", "database"),
            "source_name": current.get("source_name"),
            "source_url": current.get("source_url"),
            "fetched_at": current.get("fetched_at"),
            "is_mock": current.get("is_mock", False),
            "cache_status": current.get("cache_status", "from_db"),
        }

        if not history_30:
            result["history_notice"] = "Chưa đủ dữ liệu lịch sử để tính xu hướng 30 ngày"
        if not history_7:
            result["history_notice_7d"] = "Chưa đủ dữ liệu lịch sử để tính xu hướng 7 ngày"

        return result

    def get_market_analysis(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quantity: float | None = None,
        quality_grade: str | None = None,
    ) -> dict:
        return self.analyze_market(
            db,
            crop_name=crop_name,
            region=region,
            quantity=quantity,
            quality_grade=quality_grade,
        )

    def _safe_weather_adjustment(self, db: Session, crop_name: str, region: str, current_price: float) -> dict:
        try:
            from app.services.weather_pricing_service import get_weather_adjusted_pricing

            weather_info = get_weather_adjusted_pricing(db, crop_name, region, current_price)
            return {
                "weather_adjusted_price": weather_info["adjusted_price"],
                "weather_factor": weather_info["weather_factor"],
                "weather_summary": weather_info["weather_summary"],
                "weather_explanation": weather_info["weather_explanation"],
                "price_change_pct": weather_info["price_change_pct"],
            }
        except Exception:
            return {
                "weather_adjusted_price": current_price,
                "weather_factor": 1.0,
                "weather_summary": "",
                "weather_explanation": "",
                "price_change_pct": 0.0,
            }

    def _trend_summary(self, history: list[dict], label: str) -> dict:
        if len(history) < 2:
            return {
                "direction": "stable",
                "percent": 0.0,
                "summary": f"Chưa đủ dữ liệu lịch sử để tính xu hướng {label.lower()}",
            }
        first_price = float(history[0]["avg_price"])
        last_price = float(history[-1]["avg_price"])
        if not first_price:
            percent = 0.0
        else:
            percent = round(((last_price - first_price) / first_price) * 100, 2)
        direction = "up" if percent > 1 else "down" if percent < -1 else "stable"
        summary = (
            f"Giá tăng nhẹ trong {label.lower()}"
            if direction == "up"
            else f"Giá giảm trong {label.lower()}"
            if direction == "down"
            else f"Giá ổn định trong {label.lower()}"
        )
        return {"direction": direction, "percent": percent, "summary": summary}

    def _volatility_summary(self, history: list[dict]) -> dict:
        if len(history) < 3:
            return {
                "level": "low",
                "summary": "Chưa đủ dữ liệu để đánh giá độ biến động",
            }
        prices = [float(item["avg_price"]) for item in history if item.get("avg_price") is not None]
        if len(prices) < 3:
            return {"level": "low", "summary": "Chưa đủ dữ liệu để đánh giá độ biến động"}
        average = sum(prices) / len(prices)
        variance = sum((price - average) ** 2 for price in prices) / len(prices)
        stdev_pct = ((variance ** 0.5) / average) * 100 if average else 0
        if stdev_pct >= 12:
            level = "high"
            summary = "Giá biến động mạnh, nên chia nhỏ sản lượng trước khi bán"
        elif stdev_pct >= 6:
            level = "medium"
            summary = "Giá có dao động nhưng chưa quá rủi ro"
        else:
            level = "low"
            summary = "Giá khá ổn định, rủi ro biến động thấp"
        return {"level": level, "summary": summary, "stdev_percent": round(stdev_pct, 2)}

    def _market_recommendation(
        self,
        *,
        current_price: float,
        trend_7d: dict,
        trend_30d: dict,
        quality_grade: str,
        quantity: float | None,
    ) -> dict:
        grade = self._clean_grade(quality_grade)
        if grade in {"grade_1", "Loai 1", "Loại 1"}:
            action = "sell_partially"
            title = "Nên bán một phần sản lượng"
            reason = (
                "Chất lượng loại 1 có thể giữ giá cao. "
                "Giá đang cải thiện nên nên bán 60-70% để chốt lợi nhuận và giữ phần còn lại nếu kho chứa tốt."
            )
        elif grade in {"grade_3", "Loai 3", "Loại 3"}:
            action = "sell_soon"
            title = "Nên bán sớm"
            reason = (
                "Chất lượng thấp dễ bị ép giá. "
                "Nên ưu tiên chốt đơn sớm, hạn chế để hàng tồn lâu."
            )
        else:
            action = "hold_and_monitor"
            title = "Có thể theo dõi thêm"
            reason = (
                "Chất lượng ở mức trung bình, nên theo dõi thêm 3-5 ngày trước khi quyết định."
            )

        if trend_7d["direction"] == "down" and trend_30d["direction"] == "down":
            action = "sell_soon"
            title = "Nên bán sớm"
            reason = (
                "Giá đang giảm ở cả 7 ngày và 30 ngày gần đây. "
                "Nên ưu tiên chốt giá để giảm rủi ro."
            )
        elif trend_7d["direction"] == "up" and trend_30d["direction"] == "up":
            action = "hold_partially"
            title = "Có thể giữ lại một phần"
            reason = (
                "Giá đang tăng ở cả ngắn và dài hạn. "
                "Có thể giữ lại 30-40% nếu có điều kiện bảo quản tốt để chờ giá tốt hơn."
            )

        if quantity and float(quantity) >= 1000 and action == "sell_partially":
            reason += " Sản lượng lớn nên chia 2-3 đợt bán để tránh áp lực giá."

        return {
            "action": action,
            "title": title,
            "reason": reason,
            "current_price_context": current_price,
        }

    def _market_confidence(self, history: list[dict], current: dict) -> float:
        confidence = 0.55
        if history:
            confidence += 0.18
        if len(history) >= 7:
            confidence += 0.12
        if not current.get("is_mock"):
            confidence += 0.1
        return round(min(confidence, 0.95), 2)

    def _nearby_region_prices(self, db: Session, crop_name: str, region: str) -> list[dict]:
        latest_prices = get_latest_prices_by_crop(db, crop_name, limit=10)
        result = []
        seen = {normalize_text(region)}
        for item in latest_prices:
            normalized_region = normalize_text(item.Region)
            if normalized_region in seen:
                continue
            seen.add(normalized_region)
            result.append(
                {
                    "region": item.Region,
                    "price": float(item.price),
                    "unit": getattr(item, "unit", "VNĐ/kg"),
                    "collected_at": self._serialize_dt(item.collected_at),
                    "source": "database",
                    "source_name": getattr(item, "source_name", None) or "MarketPrices DB",
                    "updated_at": self._serialize_dt(item.collected_at),
                    "confidence": 0.7,
                    "is_mock": False,
                }
            )
        if result:
            return result

        fallback_regions = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ"]
        return [
            {
                "region": r,
                "price": self._mock_price(crop_name, r, "grade_1"),
                "unit": "VNĐ/kg",
                "collected_at": datetime.now().isoformat(),
                "source": "mock",
                "source_name": "Pricing regional fallback",
                "updated_at": datetime.now().isoformat(),
                "confidence": 0.42,
                "is_mock": True,
            }
            for r in fallback_regions
            if normalize_text(r) != normalize_text(region)
        ][:3]

    def _get_price_from_crop_profile(
        self,
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str,
    ) -> float:
        try:
            crop = ensure_crop(db, crop_name)
            if crop and crop.TypicalPriceMin and crop.TypicalPriceMax:
                base = (float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2
                return round(base * self.quality_multipliers.get(quality_grade, 1.0), 2)
        except Exception:
            pass
        return self._mock_price(crop_name, region, quality_grade)

    def _previous_price(self, db: Session, crop_name: str, region: str, quality_grade: str) -> float | None:
        history = self.get_price_history(db, crop_name, region, 7)
        if len(history) < 2:
            return None
        return float(history[-2]["avg_price"])

    def _get_recent_prices_from_db(self, db: Session, crop_name: str, region: str) -> list[float]:
        try:
            from app.models.crop import CropType
            from app.models.price import MarketPrice

            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return []
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID)
                .order_by(MarketPrice.PriceDate.desc(), MarketPrice.UpdatedAt.desc())
                .limit(7)
                .all()
            )
            target_region = normalize_text(region)
            rows = [row for row in rows if normalize_text(row.Region) == target_region]
            return [float(r.PricePerKg) for r in reversed(rows)]
        except Exception:
            return []

    def _mock_price(self, crop_name: str, region: str, quality_grade: str) -> float:
        key = self._normalize_key(crop_name)
        base = self.crop_base_prices.get(key, 20000)
        region_factor = 1 + ((sum(ord(c) for c in region) % 9) - 4) / 100
        multiplier = self.quality_multipliers.get(quality_grade, 1.0)
        return round(base * region_factor * multiplier, 2)

    @staticmethod
    def _clean_region(region: str | None) -> str:
        return " ".join((region or "Ha Noi").strip().split()) or "Ha Noi"

    @staticmethod
    def _clean_crop(crop_name: str | None) -> str:
        return normalize_text(crop_name) or "lua"

    @staticmethod
    def _clean_grade(quality_grade: str | None) -> str:
        if not quality_grade:
            return "grade_1"
        grade = quality_grade.strip()
        return to_db_grade(grade) if grade.lower().startswith("grade") or "loai" in normalize_text(grade) else grade

    @staticmethod
    def _display_crop(crop_name: str) -> str:
        labels = {"lua": "Lúa", "gao": "Gạo", "ca phe": "Cà phê", "ho tieu": "Hồ tiêu"}
        return labels.get(crop_name, crop_name.title())

    @staticmethod
    def _cache_status(updated_at: datetime | None) -> str:
        if not updated_at:
            return "unknown"
        age = datetime.now() - updated_at
        if age <= timedelta(hours=24):
            return "fresh"
        return "stale"

    @staticmethod
    def _age_minutes(updated_at: datetime | None) -> int | None:
        if not updated_at:
            return None
        delta = datetime.now() - updated_at
        return max(int(delta.total_seconds() // 60), 0)

    @staticmethod
    def _trend_from_change(change_percent: float) -> str:
        if change_percent > 1:
            return "up"
        if change_percent < -1:
            return "down"
        return "stable"

    @staticmethod
    def _serialize_dt(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _normalize_key(value: str) -> str:
        normalized = unicode_normalize("NFD", value.strip().lower())
        normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        return normalized.replace("đ", "d").replace("Đ", "d").strip()

    def _trend_summary_text(self, direction: str, days: int) -> str:
        if direction == "up":
            return f"Giá tăng nhẹ trong {days} ngày gần đây"
        if direction == "down":
            return f"Giá giảm trong {days} ngày gần đây"
        return f"Giá ổn định trong {days} ngày gần đây"


pricing_service = PricingService()
