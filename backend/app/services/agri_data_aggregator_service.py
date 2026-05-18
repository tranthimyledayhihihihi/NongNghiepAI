from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.alert_service import alert_service
from app.services.data_source_service import data_source_service
from app.services.harvest_service import harvest_service
from app.services.market_news_service import market_news_service
from app.services.notification_center_service import notification_center_service
from app.services.pricing_service import pricing_service
from app.services.quality_service import quality_service
from app.services.settings_service import settings_service
from app.services.weather_service import weather_service


class AgriDataAggregatorService:
    """Shared data facade for Dashboard, AI Chat, Alerts, Harvest and Pricing."""

    def get_pricing_bundle(
        self,
        db: Session,
        *,
        crop: str,
        region: str,
        quantity: float = 1,
        quality_grade: str = "grade_1",
    ) -> dict:
        current = pricing_service.get_current_price(db, crop, region, quality_grade)
        forecast = pricing_service.get_price_forecast(crop, region, days=7)
        history = pricing_service.get_price_history(db, crop, region, days=30)
        engine = pricing_service.get_ai_price_recommendation(
            db,
            crop,
            region,
            quality_grade=quality_grade,
            quantity=quantity,
        )
        return {
            "current": current,
            "history": history,
            "forecast": forecast,
            "recommendation": engine,
            "data_sources": data_source_service.collect_data_sources(
                {"current": current, "history": history, "forecast": forecast, "recommendation": engine}
            ),
            "source": data_source_service.normalize_source(current),
            "source_name": current.get("source_name") or "Pricing service",
            "updated_at": current.get("last_updated") or current.get("updated_at") or datetime.now(),
        }

    def get_weather_bundle(self, db: Session, *, region: str, crop: str | None = None) -> dict:
        current = weather_service.get_current_weather(db, region)
        forecast = weather_service.get_weather_forecast(db, region, days=7)
        risk = weather_service.get_weather_risk(db, region, crop)
        recommendation = weather_service.get_farming_recommendation(db, region, crop)
        agriculture = weather_service.get_agriculture_weather(db, region, crop_name=crop)
        return {
            "current": current,
            "forecast": forecast,
            "agriculture": agriculture,
            "risk": risk,
            "recommendation": recommendation,
            "data_sources": data_source_service.collect_data_sources(
                {"current": current, "forecast": forecast, "risk": risk, "recommendation": recommendation}
            ),
            "source": data_source_service.normalize_source(current),
            "source_name": current.get("source_name") or "Weather service",
            "updated_at": current.get("last_updated") or current.get("updated_at") or datetime.now(),
        }

    def get_market_bundle(self, db: Session, *, crop: str | None = None, region: str | None = None, limit: int = 10) -> dict:
        news = market_news_service.get_market_news(db, crop=crop, region=region, limit=limit)
        trends = market_news_service.get_market_trends(db, crop=crop, region=region)
        opportunities = market_news_service.get_market_opportunities(db, crop=crop, region=region)
        risks = market_news_service.get_market_risks(db, crop=crop, region=region)
        return {
            "news": news.get("news", []),
            "trends": trends,
            "opportunities": opportunities.get("opportunities", []),
            "risks": risks.get("risks", []),
            "data_sources": data_source_service.collect_data_sources(
                {"news": news, "trends": trends, "opportunities": opportunities, "risks": risks}
            ),
            "source": data_source_service.normalize_source(news),
            "source_name": news.get("source_name") or "Market news service",
            "updated_at": datetime.now(),
        }

    def get_alert_notification_bundle(
        self,
        db: Session,
        *,
        user_id: int | None = None,
        crop: str | None = None,
        region: str | None = None,
    ) -> dict:
        user = self._get_user(db, user_id)
        alerts = alert_service.get_active_alerts(db, user_id=user_id, crop=crop, region=region)
        notifications = {}
        if user:
            notifications = {
                "summary": notification_center_service.summary(db, user),
                "priority": notification_center_service.get_priority_notifications(db, user),
                "unread_count": notification_center_service.get_unread_notification_count(db, user),
            }
        return {
            "alerts": alerts,
            "notifications": notifications,
            "data_sources": data_source_service.collect_data_sources({"alerts": alerts, "notifications": notifications}),
            "source": "database",
            "source_name": "Alert and notification services",
            "updated_at": datetime.now(),
        }

    def get_user_settings(self, db: Session, user_id: int | None = None) -> dict:
        user = self._get_user(db, user_id)
        if not user:
            return {
                "profile": None,
                "farm": None,
                "preferences": {},
                "source": "database",
                "source_name": "Settings defaults",
                "updated_at": datetime.now(),
            }
        return settings_service.get_combined_settings(db, user)

    def get_quality_history(self, db: Session, user_id: int | None = None, limit: int = 5) -> list[dict]:
        if not user_id:
            return []
        try:
            return quality_service.get_history(db, user_id, limit)
        except Exception:
            return []

    def get_harvest_status(self, db: Session, user_id: int | None = None, limit: int = 5) -> dict:
        if not user_id:
            return {"schedules": [], "total": 0, "source": "database", "source_name": "Harvest service"}
        schedules = harvest_service.get_schedules(db, user_id, limit)
        return {
            "schedules": schedules,
            "total": len(schedules),
            "source": "database",
            "source_name": "HarvestSchedule DB",
            "updated_at": datetime.now(),
        }

    @staticmethod
    def _get_user(db: Session, user_id: int | None) -> User | None:
        if not user_id:
            return None
        try:
            return db.query(User).filter(User.UserID == user_id).first()
        except Exception:
            return None


agri_data_aggregator_service = AgriDataAggregatorService()
