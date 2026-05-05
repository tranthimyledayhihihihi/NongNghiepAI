"""
Price Forecast Service - merged Tien (schema/API) + Quang (AI model + rich analysis)
- API endpoint dùng: predict_price(db, request: PricePredictionRequest)
- Thử AI model trước, fallback về moving average, rồi về mock
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.schemas.price_schema import PricePredictionRequest
from app.services.pricing_service import pricing_service


class PriceForecastService:
    """Service dự báo giá nông sản 7-30 ngày."""

    @staticmethod
    def _get_model():
        """Lazy import AI price forecast model (Quang)."""
        try:
            from ai_models.price_forecast.price_model import price_forecast_model
            return price_forecast_model
        except ImportError:
            return None

    # ------------------------------------------------------------------ #
    # API interface
    # ------------------------------------------------------------------ #

    def predict_price(self, db: Session, request: PricePredictionRequest) -> dict:
        """
        Dự báo giá:
        1. Thử AI model (Quang's price_forecast model)
        2. Fallback về moving average từ DB history
        3. Fallback cuối: mock dựa trên giá hiện tại
        """
        crop_name = request.crop_name
        region = request.region
        forecast_days = request.forecast_days

        # 1. Thử AI model
        model = self._get_model()
        if model:
            try:
                raw = model.predict(crop_name=crop_name, region=region, days=forecast_days)
                predicted_prices = raw.get("forecast_data", [])
                trend = raw.get("trend", self._calc_trend([p["predicted_price"] for p in predicted_prices]))
                return {
                    "crop_name": crop_name,
                    "region": region,
                    "forecast_days": forecast_days,
                    "predicted_prices": predicted_prices,
                    "trend": trend,
                    "best_selling_time": self._find_best_selling_time(predicted_prices),
                    "warning": self._build_warning(trend, [p["predicted_price"] for p in predicted_prices]),
                    "recommendation": raw.get("recommendation", self._get_recommendation(trend)),
                }
            except Exception:
                pass

        # 2. Fallback: lịch sử giá từ DB + moving average
        price_history = self._load_price_history(db, crop_name, region, days=60)
        if price_history:
            raw = self._fallback_forecast(price_history, forecast_days)
            predicted_prices = raw.get("forecast_data", [])
            trend = raw.get("trend", "stable")
            return {
                "crop_name": crop_name,
                "region": region,
                "forecast_days": forecast_days,
                "predicted_prices": predicted_prices,
                "trend": trend,
                "best_selling_time": self._find_best_selling_time(predicted_prices),
                "warning": self._build_warning(trend, [p["predicted_price"] for p in predicted_prices]),
                "recommendation": raw.get("recommendation", self._get_recommendation(trend)),
            }

        # 3. Fallback cuối: mock từ giá hiện tại
        current = pricing_service.get_current_price(db, crop_name, region)
        base_price = float(current["current_price"])
        predicted_prices = []
        for offset in range(1, forecast_days + 1):
            predicted = round(base_price * (1 + offset * 0.006), 2)
            predicted_prices.append({
                "date": (date.today() + timedelta(days=offset)).isoformat(),
                "predicted_price": predicted,
                "confidence_lower": round(predicted * 0.92, 2),
                "confidence_upper": round(predicted * 1.08, 2),
            })

        trend = self._calc_trend([p["predicted_price"] for p in predicted_prices])
        return {
            "crop_name": crop_name,
            "region": region,
            "forecast_days": forecast_days,
            "predicted_prices": predicted_prices,
            "trend": trend,
            "best_selling_time": self._best_selling_time(trend, forecast_days),
            "warning": self._build_warning(trend, [p["predicted_price"] for p in predicted_prices]),
            "recommendation": self._get_recommendation(trend),
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _load_price_history(self, db: Session, crop_name: str, region: str, days: int = 60) -> List[Dict]:
        """Lấy lịch sử giá từ DB (Quang)."""
        try:
            from app.models.crop import CropType
            from app.models.price import PriceHistory
            crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                return []
            start = (datetime.now() - timedelta(days=days)).date()
            rows = (
                db.query(PriceHistory)
                .filter(
                    PriceHistory.CropID == crop.CropID,
                    PriceHistory.Region == region,
                    PriceHistory.RecordDate >= start,
                )
                .order_by(PriceHistory.RecordDate)
                .all()
            )
            return [{"date": r.RecordDate.isoformat(), "price": float(r.AvgPrice)} for r in rows]
        except Exception:
            return []

    @staticmethod
    def _fallback_forecast(history: List[Dict], days: int) -> Dict:
        """Moving average đơn giản khi không có AI model."""
        try:
            import numpy as np
            prices = [h["price"] for h in history]
            base = float(np.mean(prices[-7:])) if len(prices) >= 7 else float(np.mean(prices))
        except ImportError:
            base = sum(h["price"] for h in history[-7:]) / min(7, len(history))

        forecast_data = []
        current = base
        for i in range(1, days + 1):
            # Simple random walk (deterministic seed cho reproducibility)
            noise = 0.01 * ((i * 7) % 5 - 2) / 5
            current = current * (1 + noise)
            forecast_data.append({
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "predicted_price": round(current),
                "confidence_lower": round(current * 0.92),
                "confidence_upper": round(current * 1.08),
            })

        trend = PriceForecastService._calc_trend([f["predicted_price"] for f in forecast_data])
        return {
            "forecast_data": forecast_data,
            "trend": trend,
            "recommendation": PriceForecastService._get_recommendation(trend),
        }

    @staticmethod
    def _calc_trend(prices: List[float]) -> str:
        if len(prices) < 2:
            return "stable"
        mid = max(len(prices) // 2, 1)
        first = sum(prices[:mid]) / mid
        second = sum(prices[mid:]) / max(len(prices) - mid, 1)
        change = ((second - first) / first) * 100
        if change > 5:
            return "increasing"
        if change < -5:
            return "decreasing"
        return "stable"

    @staticmethod
    def _find_best_selling_time(forecast_data: List[Dict]) -> Optional[str]:
        """Tìm ngày có giá dự báo cao nhất."""
        if not forecast_data:
            return None
        best = max(forecast_data, key=lambda x: x.get("predicted_price", 0))
        return best.get("date")

    @staticmethod
    def _best_selling_time(trend: str, forecast_days: int) -> str:
        if trend == "increasing":
            return f"Can nhac ban sau {min(forecast_days, 7)} ngay neu bao quan tot."
        if trend == "decreasing":
            return "Nen ban som trong 1-2 ngay toi."
        return "Co the ban bat ky thoi diem phu hop trong ky du bao."

    @staticmethod
    def _build_warning(trend: str, prices: List[float]) -> Optional[str]:
        if trend == "decreasing":
            return "Giá có xu hướng giảm trong thời gian tới. Cân nhắc bán sớm."
        if trend == "increasing":
            return "Giá có xu hướng tăng. Có thể chờ thêm để bán giá tốt hơn."
        if prices and min(prices) > 0 and max(prices) / min(prices) > 1.2:
            return "Giá biến động lớn. Theo dõi thị trường trước khi quyết định."
        return None

    @staticmethod
    def _get_recommendation(trend: str) -> str:
        recs = {
            "increasing": "Giá đang tăng – nên giữ hàng thêm vài ngày để bán được giá tốt hơn.",
            "decreasing": "Giá đang giảm – nên bán sớm để tránh mất giá.",
            "stable": "Giá ổn định – có thể bán bất kỳ lúc nào phù hợp với kế hoạch.",
        }
        return recs.get(trend, "Theo dõi thị trường để chọn thời điểm bán phù hợp.")


price_forecast_service = PriceForecastService()
