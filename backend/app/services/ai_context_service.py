from datetime import datetime

from sqlalchemy.orm import Session

from app.services.agri_data_aggregator_service import agri_data_aggregator_service
from app.services.data_source_service import data_source_service


class AIContextService:
    def build_ai_context(
        self,
        db: Session,
        *,
        user_id: int | None = None,
        region: str | None = None,
        crop: str | None = None,
        intent: str | None = None,
    ) -> dict:
        selected_region = (region or "Ha Noi").strip() or "Ha Noi"
        selected_crop = (crop or "lua").strip().lower() or "lua"
        selected_intent = intent or "general"
        needs_all = selected_intent == "general"
        needs_weather = needs_all or selected_intent in {"weather_advice", "harvest_advice", "alert_summary"}
        needs_pricing = needs_all or selected_intent in {"price_query", "harvest_advice", "quality_check"}
        needs_market = needs_all or selected_intent == "price_query"
        needs_alerts = needs_all or selected_intent in {"weather_advice", "alert_summary", "harvest_advice"}

        weather_bundle = self._safe(
            lambda: agri_data_aggregator_service.get_weather_bundle(db, region=selected_region, crop=selected_crop),
            "weather",
        ) if needs_weather else {}
        pricing_bundle = self._safe(
            lambda: agri_data_aggregator_service.get_pricing_bundle(db, crop=selected_crop, region=selected_region),
            "pricing",
        ) if needs_pricing else {}
        market_bundle = self._safe(
            lambda: agri_data_aggregator_service.get_market_bundle(db, crop=selected_crop, region=selected_region),
            "market",
        ) if needs_market else {}
        alert_bundle = self._safe(
            lambda: agri_data_aggregator_service.get_alert_notification_bundle(
                db,
                user_id=user_id,
                crop=selected_crop,
                region=selected_region,
            ),
            "alerts",
        ) if needs_alerts else {}

        quality_history = agri_data_aggregator_service.get_quality_history(db, user_id) if needs_all or selected_intent == "quality_check" else []
        harvest_status = agri_data_aggregator_service.get_harvest_status(db, user_id) if needs_all or selected_intent == "harvest_advice" else {}
        settings = agri_data_aggregator_service.get_user_settings(db, user_id) if needs_all else {}

        context = {
            "intent": selected_intent,
            "region": selected_region,
            "crop_name": selected_crop,
            "crop": selected_crop,
            "weather": weather_bundle.get("current", {}),
            "weather_risk": weather_bundle.get("risk", {}),
            "weather_forecast": weather_bundle.get("forecast", []),
            "farming_recommendation": weather_bundle.get("recommendation", {}),
            "pricing": pricing_bundle.get("current", {}),
            "price_history": pricing_bundle.get("history", []),
            "price_forecast": pricing_bundle.get("forecast", {}),
            "price_recommendation": pricing_bundle.get("recommendation", {}),
            "market": {
                "news": market_bundle.get("news", []),
                "trends": market_bundle.get("trends", {}),
                "opportunities": market_bundle.get("opportunities", []),
                "risks": market_bundle.get("risks", []),
            },
            "quality_history": quality_history,
            "harvest_status": harvest_status,
            "alerts": alert_bundle.get("alerts", []),
            "notifications": alert_bundle.get("notifications", {}),
            "settings": settings,
            "generated_at": datetime.now(),
        }
        context["data_sources"] = data_source_service.collect_data_sources(context)
        context["tools_used"] = [
            "weather_service",
            "pricing_service",
            "market_news_service",
            "alert_service",
            "notification_center_service",
            "settings_service",
        ]
        return context

    @staticmethod
    def _safe(factory, key: str) -> dict:
        try:
            return factory()
        except Exception as exc:
            return {
                "error": str(exc),
                "source": "mock",
                "source_name": f"{key} context fallback",
                "is_mock": True,
                "fallback_used": True,
                "timeout": "timeout" in str(exc).lower(),
                "confidence": 0.0,
            }


ai_context_service = AIContextService()
