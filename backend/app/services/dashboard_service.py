from datetime import date, datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.harvest import HarvestSchedule
from app.models.notification import Notification
from app.models.price import MarketPrice
from app.models.quality import QualityCheck
from app.repositories.common import ensure_crop
from app.services.pricing_service import pricing_service
from app.services.weather_service import weather_service


class DashboardService:
    def get_summary(self, db: Session, user_id: int | None = None, region: str | None = None) -> dict:
        region = region or "Ha Noi"
        featured = self.get_featured_crop(db, region=region)
        weather = self.get_weather_overview(db, region=region)

        schedules_query = db.query(HarvestSchedule)
        quality_query = db.query(QualityCheck)
        notification_query = db.query(Notification).filter(Notification.IsDeleted.is_(False))
        if user_id:
            schedules_query = schedules_query.filter(HarvestSchedule.UserID == user_id)
            quality_query = quality_query.filter(QualityCheck.UserID == user_id)
            notification_query = notification_query.filter(Notification.UserID == user_id)

        try:
            active_seasons = schedules_query.filter(HarvestSchedule.ActualHarvestDate.is_(None)).count()
            quality_checks = quality_query.count()
            unread_notifications = notification_query.filter(Notification.IsRead.is_(False)).count()
        except SQLAlchemyError:
            db.rollback()
            active_seasons = 0
            quality_checks = 0
            unread_notifications = 0

        return {
            "featured_crop": featured,
            "weather": weather,
            "active_seasons": active_seasons,
            "quality_checks": quality_checks,
            "unread_notifications": unread_notifications,
            "generated_at": datetime.now(),
        }

    def get_featured_crop(self, db: Session, region: str | None = None) -> dict:
        row = self._latest_market_price(db, region)
        if row:
            price, crop = row
            crop_name = crop.CropName
            crop_region = price.Region
            current_price = float(price.PricePerKg)
            last_updated = price.UpdatedAt
            is_mock = False
            source_name = price.SourceName or "database"
        else:
            crop_name = "lua"
            crop_region = region or "Ha Noi"
            current = pricing_service.get_current_price(db, crop_name, crop_region)
            current_price = float(current["current_price"])
            last_updated = current.get("last_updated") or datetime.now()
            is_mock = bool(current.get("is_mock"))
            source_name = current.get("source_name")

        trend = pricing_service.analyze_price_trend(db, crop_name, crop_region)
        change = self._estimate_change(db, crop_name, crop_region)
        return {
            "name": crop_name,
            "location": crop_region,
            "price": current_price,
            "unit": "VND/kg",
            "change": change,
            "trend": trend,
            "last_updated": last_updated,
            "source_name": source_name,
            "is_mock": is_mock,
            "cache_status": "mock" if is_mock else "from_db",
        }

    def get_price_trend(self, db: Session, crop_name: str = "lua", region: str = "Ha Noi", days: int = 7) -> dict:
        history = pricing_service.get_price_history(db, crop_name, region, max(days, 7))
        recent = history[-days:] if history else []
        forecast = []
        base_price = recent[-1]["avg_price"] if recent else pricing_service.get_current_price(db, crop_name, region)["current_price"]
        for offset in range(1, days + 1):
            predicted = round(float(base_price) * (1 + offset * 0.006), 2)
            forecast.append(
                {
                    "date": (date.today() + timedelta(days=offset)).isoformat(),
                    "predicted_price": predicted,
                    "confidence": "high" if offset <= 3 else "medium",
                    "trend": "up" if offset <= 3 else "stable",
                }
            )
        return {
            "crop_name": crop_name,
            "region": region,
            "history": recent,
            "forecast": forecast,
            "trend": pricing_service.analyze_price_trend(db, crop_name, region),
            "is_mock": any(item.get("is_mock") for item in recent) if recent else True,
        }

    def get_weather_overview(self, db: Session, region: str = "Ha Noi") -> dict:
        current = weather_service.get_current_weather(db, region)
        forecast = weather_service.get_forecast(db, region, 7)
        return {
            "current": current,
            "forecast": forecast,
            "alerts": weather_service.generate_alerts(current, forecast),
            "is_mock": bool(current.get("is_mock")) or any(item.get("is_mock") for item in forecast),
            "is_realtime": bool(current.get("is_realtime")),
            "cache_status": current.get("cache_status", "unknown"),
            "last_updated": current.get("last_updated"),
        }

    def get_ai_recommendation(self, db: Session, crop_name: str = "lua", region: str = "Ha Noi") -> dict:
        current_price = pricing_service.get_current_price(db, crop_name, region)
        weather = self.get_weather_overview(db, region)
        trend = current_price.get("price_trend", "stable")
        rainy_days = sum(1 for item in weather["forecast"] if float(item.get("rainfall") or 0) >= 5)

        if trend == "increasing" and rainy_days <= 2:
            action = "hold"
            title = "Hold inventory"
            confidence = 0.78
            description = "Price trend is improving and weather risk is acceptable."
        elif rainy_days >= 4:
            action = "sell_sooner"
            title = "Sell sooner"
            confidence = 0.72
            description = "Rain risk is elevated, so reducing storage exposure is safer."
        else:
            action = "sell_in_batches"
            title = "Sell in batches"
            confidence = 0.70
            description = "Market signal is mixed; split volume to reduce price and weather risk."

        return {
            "crop_name": crop_name,
            "region": region,
            "action": action,
            "title": title,
            "description": description,
            "confidence": confidence,
            "expected_price": round(float(current_price["current_price"]) * 1.02, 2),
            "period": "next 7 days",
            "source": "rule_based_ai",
            "is_mock": bool(current_price.get("is_mock")) or weather["is_mock"],
            "last_updated": datetime.now(),
        }

    @staticmethod
    def _latest_market_price(db: Session, region: str | None = None):
        try:
            query = db.query(MarketPrice, Crop).join(Crop, Crop.CropID == MarketPrice.CropID)
            if region:
                query = query.filter(MarketPrice.Region == region)
            row = query.order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt)).first()
            if row:
                return row
        except SQLAlchemyError:
            db.rollback()
        return None

    @staticmethod
    def _estimate_change(db: Session, crop_name: str, region: str) -> str:
        try:
            crop = ensure_crop(db, crop_name)
            prices = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.Region == region)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(2)
                .all()
            )
            if len(prices) >= 2 and prices[1].PricePerKg:
                change = ((float(prices[0].PricePerKg) - float(prices[1].PricePerKg)) / float(prices[1].PricePerKg)) * 100
                return f"{change:+.1f}%"
        except SQLAlchemyError:
            db.rollback()
        return "+0.0%"


dashboard_service = DashboardService()
