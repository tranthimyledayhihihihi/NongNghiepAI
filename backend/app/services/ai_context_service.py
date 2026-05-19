from sqlalchemy.orm import Session

from app.services.agri_data_aggregator_service import agri_data_aggregator_service
from app.services.data_source_service import data_source_service
from app.services.ai_intent_service import normalize_intent
from app.services.pricing_service import pricing_service


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
        selected_intent = normalize_intent(intent)

        needs_all = selected_intent == "full_farm_analysis"
        needs_weather = selected_intent in {"weather_analysis", "alert_analysis"} or needs_all
        needs_pricing = selected_intent == "price_analysis" or needs_all
        needs_market = selected_intent == "price_analysis" or needs_all
        needs_alerts = selected_intent == "alert_analysis" or needs_all
        needs_quality = selected_intent == "quality_analysis" or needs_all
        needs_harvest = selected_intent == "harvest_analysis" or needs_all
        needs_settings = needs_all

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
        market_analysis = self._safe(
            lambda: pricing_service.analyze_market(
                db,
                crop_name=selected_crop,
                region=selected_region,
                quantity=1000,
                quality_grade="grade_2",
            ),
            "market_analysis",
        ) if needs_pricing else {}
        alert_bundle = self._safe(
            lambda: agri_data_aggregator_service.get_alert_notification_bundle(
                db,
                user_id=user_id,
                crop=selected_crop,
                region=selected_region,
            ),
            "alerts",
        ) if needs_alerts else {}

        quality_history = agri_data_aggregator_service.get_quality_history(db, user_id) if needs_quality else []
        harvest_status = agri_data_aggregator_service.get_harvest_status(db, user_id) if needs_harvest else {}
        settings = agri_data_aggregator_service.get_user_settings(db, user_id) if needs_settings else {}
        include_weather_details = selected_intent == "weather_analysis" or needs_all

        context = {
            "intent": selected_intent,
            "region": selected_region,
            "crop_name": selected_crop,
            "crop": selected_crop,
            "weather": weather_bundle.get("current", {}) if include_weather_details else {},
            "weather_risk": weather_bundle.get("risk", {}),
            "weather_forecast": weather_bundle.get("forecast", []) if include_weather_details else [],
            "farming_recommendation": weather_bundle.get("recommendation", {}) if include_weather_details else {},
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
            "market_analysis": market_analysis,
            "pricing_analysis": market_analysis,
            "quality_history": quality_history,
            "harvest_status": harvest_status,
            "alerts": alert_bundle.get("alerts", []),
            "notifications": alert_bundle.get("notifications", {}),
            "settings": settings,
        }
        context["data_sources"] = data_source_service.collect_data_sources(context)
        tools_used = []
        if needs_weather:
            tools_used.append("weather_service")
        if needs_pricing:
            tools_used.append("pricing_service")
        if needs_market:
            tools_used.append("market_news_service")
        if needs_alerts:
            tools_used.extend(["alert_service", "notification_center_service"])
        if needs_quality:
            tools_used.append("quality_service")
        if needs_harvest:
            tools_used.append("harvest_service")
        if needs_settings:
            tools_used.append("settings_service")
        context["tools_used"] = tools_used
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
