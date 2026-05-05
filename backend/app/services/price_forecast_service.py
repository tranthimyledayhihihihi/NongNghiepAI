from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.schemas.price_schema import PricePredictionRequest
from app.services.pricing_service import pricing_service


class PriceForecastService:
    def predict_price(self, db: Session, request: PricePredictionRequest) -> dict:
        current = pricing_service.get_current_price(db, request.crop_name, request.region)
        base_price = float(current["current_price"])
        predicted_prices = []

        for offset in range(1, request.forecast_days + 1):
            predicted = round(base_price * (1 + offset * 0.006), 2)
            predicted_prices.append(
                {
                    "date": date.today() + timedelta(days=offset),
                    "predicted_price": predicted,
                    "min_price": round(predicted * 0.92, 2),
                    "max_price": round(predicted * 1.08, 2),
                }
            )

        trend = self._trend(predicted_prices)
        return {
            "crop_name": request.crop_name,
            "region": request.region,
            "forecast_days": request.forecast_days,
            "trend": trend,
            "best_selling_time": self._best_selling_time(trend, request.forecast_days),
            "predicted_prices": predicted_prices,
            "warning": "Du bao MVP, can thay bang model cua nguoi 2 khi co du lieu lich su.",
        }

    @staticmethod
    def _trend(predicted_prices: list[dict]) -> str:
        if len(predicted_prices) < 2:
            return "stable"
        first = predicted_prices[0]["predicted_price"]
        last = predicted_prices[-1]["predicted_price"]
        change = ((last - first) / first) * 100
        if change > 3:
            return "increasing"
        if change < -3:
            return "decreasing"
        return "stable"

    @staticmethod
    def _best_selling_time(trend: str, forecast_days: int) -> str:
        if trend == "increasing":
            return f"Can nhac ban sau {min(forecast_days, 7)} ngay neu bao quan tot."
        if trend == "decreasing":
            return "Nen ban som trong 1-2 ngay toi."
        return "Co the ban bat ky thoi diem phu hop trong ky du bao."


price_forecast_service = PriceForecastService()
