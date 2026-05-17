import unicodedata

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.services.claude_service import claude_service

router = APIRouter(prefix="/api/ai-chat", tags=["ai-chat"])


class AIChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    crop_name: str | None = None
    region: str | None = None
    session_id: str | None = None


def _detect_intent(message: str) -> str:
    text = unicodedata.normalize("NFD", message.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    if any(word in text for word in ["tuoi", "mua", "thoi tiet", "phun", "gio", "do am"]):
        return "weather_advice"
    if any(word in text for word in ["gia", "ban", "thi truong"]):
        return "price_query"
    if any(word in text for word in ["thu hoach", "mua vu"]):
        return "harvest_advice"
    if any(word in text for word in ["chat luong", "loai may", "anh", "nong san cua toi"]):
        return "quality_check"
    if "canh bao" in text or "alert" in text:
        return "alert_summary"
    return "general"


def _build_reasons(context: dict, result: dict) -> list[str]:
    reasons: list[str] = []
    weather = context.get("weather") or {}
    pricing = context.get("pricing") or {}
    market = context.get("market_trends") or {}
    if weather:
        reasons.append(
            f"Weather source {weather.get('source_name', 'backend')}: {weather.get('temperature')}C, rain {weather.get('rainfall')}mm."
        )
    if pricing:
        reasons.append(
            f"Price source {pricing.get('source_name', 'backend')}: market price {pricing.get('market_price') or pricing.get('current_price')} VND/kg."
        )
    if market:
        reasons.append(
            f"Market trend engine: trend {market.get('trend', 'stable')} with confidence {market.get('confidence', 0)}."
        )
    if context.get("quality_history"):
        reasons.append("Recent quality records from QualityRecords DB were included.")
    if context.get("harvest_status"):
        reasons.append("Active harvest schedules from HarvestSchedule DB were included.")
    if result.get("is_mock"):
        reasons.append("AI provider unavailable, so rule-based fallback generated the answer.")
    return reasons[:6]


def _build_recommendations(context: dict, result: dict) -> list[str]:
    recommendations: list[str] = []
    risk = context.get("weather_risk") or {}
    pricing = context.get("pricing") or {}
    market_risks = context.get("market_risks") or {}
    if risk.get("recommended_actions"):
        recommendations.extend(risk.get("recommended_actions")[:3])
    elif risk.get("reasons"):
        recommendations.extend(risk.get("reasons")[:3])
    if pricing.get("recommendation"):
        recommendations.append(pricing["recommendation"])
    for item in market_risks.get("risks", [])[:2]:
        if item.get("recommendation"):
            recommendations.append(item["recommendation"])
    if not recommendations:
        recommendations.append("Review weather, price, quality, and alerts before taking action today.")
    return recommendations[:6]


def _default_context(db: Session, user: User | None, request: AIChatMessageRequest) -> dict:
    region = request.region or (user.Region if user and user.Region else "Ha Noi")
    crop = request.crop_name or "lua"
    intent = _detect_intent(request.message)
    context: dict = {"intent": intent, "region": region, "crop_name": crop, "tools_used": []}
    try:
        from app.services.weather_service import weather_service
        context["weather"] = weather_service.get_current_weather(db, region)
        context["weather_risk"] = weather_service.analyze_agriculture_risk(db, region, crop)
        context["tools_used"].extend(["get_weather", "get_weather_risk"])
    except Exception as exc:
        context["weather_error"] = str(exc)
    if True:
        try:
            from app.services.pricing_service import pricing_service
            context["pricing"] = pricing_service.build_pricing_engine(db, crop_name=crop, region=region)
            context["tools_used"].append("get_price")
        except Exception as exc:
            context["pricing_error"] = str(exc)
    if True:
        try:
            from app.services.pricing_service import pricing_service
            trend = pricing_service.build_pricing_engine(db, crop_name=crop, region=region)
            context["market_trends"] = {
                "crop": crop,
                "region": region,
                "trend": trend.get("trend"),
                "confidence": trend.get("confidence", 0.0),
                "reasons": trend.get("reasons", []),
                "recommendation": trend.get("recommendation"),
                "source": trend.get("source"),
                "source_name": "Market trend engine",
                "is_mock": trend.get("is_mock", False),
            }
            context["market_risks"] = {
                "risks": [
                    {
                        "title": "Price volatility",
                        "severity": "high" if trend.get("trend") == "decreasing" else "medium" if trend.get("is_mock") else "low",
                        "recommendation": "Create price alert and avoid selling all stock at one time.",
                    }
                ],
                "source_name": "AI Market Risk Engine",
                "confidence": trend.get("confidence", 0.0),
            }
            context["tools_used"].extend(["get_market_trends", "get_market_risks"])
        except Exception as exc:
            context["market_error"] = str(exc)
    if user:
        try:
            from app.services.quality_service import quality_service
            context["quality_history"] = quality_service.get_history(db, user.UserID, 5)
            context["tools_used"].append("get_quality_history")
        except Exception:
            context["quality_history"] = []
        try:
            from app.services.harvest_service import harvest_service
            context["harvest_status"] = harvest_service.get_schedules(db, user.UserID, 5)
            context["tools_used"].append("get_harvest_status")
        except Exception:
            context["harvest_status"] = []
        try:
            from app.services.alert_service import alert_service
            context["alerts"] = alert_service.list_price_alerts(db, user)
            context["tools_used"].append("get_alerts")
        except Exception:
            context["alerts"] = []
    return context


@router.post("/message")
async def ai_chat_message(
    request: AIChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    context = _default_context(db, current_user, request)
    result = claude_service.answer_question(
        db,
        question=request.message,
        user_id=current_user.UserID if current_user else None,
        crop_name=context.get("crop_name"),
        region=context.get("region"),
        session_id=request.session_id,
        extra_context=context,
    )
    data = {
        **result,
        "message": request.message,
        "intent": context["intent"],
        "data_sources": context.get("tools_used", []),
        "tool_context": context,
        "reasons": _build_reasons(context, result),
        "recommendations": _build_recommendations(context, result),
        "source": "ai_generated" if not result.get("is_mock") else "mock",
        "source_name": result.get("provider") or "AI Farming Assistant",
        "confidence": 0.74 if not result.get("is_mock") else 0.45,
    }
    return api_response(
        data,
        source=data["source"],
        source_name=data["source_name"],
        is_mock=result.get("is_mock", False),
        last_updated=result.get("created_at"),
        confidence=data["confidence"],
    )


@router.post("/message-with-context")
async def ai_chat_message_with_context(
    request: AIChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return await ai_chat_message(request, db, current_user)


@router.get("/history")
async def ai_chat_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.conversation import AIConversation
    rows = (
        db.query(AIConversation)
        .filter(AIConversation.UserID == current_user.UserID)
        .order_by(AIConversation.CreatedAt.desc())
        .limit(limit)
        .all()
    )
    data = {
        "total": len(rows),
        "history": [
            {
                "id": row.ConvID,
                "user_message": row.UserMessage,
                "ai_response": row.AIResponse,
                "topic": row.Topic,
                "tools_used": row.ContextSnapshot,
                "created_at": row.CreatedAt,
            }
            for row in rows
        ],
    }
    return api_response(data, source="database", source_name="AIConversations DB", confidence=0.7)
