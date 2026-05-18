import unicodedata

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.services.ai_context_service import ai_context_service
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
    market = (context.get("market") or {}).get("trends") or context.get("market_trends") or {}
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
    market_risks = (context.get("market") or {}).get("risks") or context.get("market_risks") or {}
    if risk.get("recommended_actions"):
        recommendations.extend(risk.get("recommended_actions")[:3])
    elif risk.get("reasons"):
        recommendations.extend(risk.get("reasons")[:3])
    if pricing.get("recommendation"):
        recommendations.append(pricing["recommendation"])
    risks = market_risks if isinstance(market_risks, list) else market_risks.get("risks", [])
    for item in risks[:2]:
        if item.get("recommendation"):
            recommendations.append(item["recommendation"])
    if not recommendations:
        recommendations.append("Review weather, price, quality, and alerts before taking action today.")
    return recommendations[:6]


def _default_context(db: Session, user: User | None, request: AIChatMessageRequest) -> dict:
    region = request.region or (user.Region if user and user.Region else "Ha Noi")
    crop = request.crop_name or "lua"
    intent = _detect_intent(request.message)
    return ai_context_service.build_ai_context(
        db,
        user_id=user.UserID if user else None,
        region=region,
        crop=crop,
        intent=intent,
    )


@router.post("/message")
async def ai_chat_message(
    request: AIChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    intent = _detect_intent(request.message)
    region = request.region or (current_user.Region if current_user and current_user.Region else "Ha Noi")
    crop = request.crop_name or "lua"
    context = ai_context_service.build_ai_context(
        db,
        user_id=current_user.UserID if current_user else None,
        region=region,
        crop=crop,
        intent=intent,
    )
    result = claude_service.answer_question(
        db,
        question=request.message,
        user_id=current_user.UserID if current_user else None,
        crop_name=context.get("crop_name"),
        region=context.get("region"),
        session_id=request.session_id,
        extra_context=context,
    )
    recommendations = _build_recommendations(context, result)
    data = {
        "answer": result.get("answer"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "token_usage": result.get("token_usage"),
        "is_mock": result.get("is_mock", False),
        "error": result.get("error"),
        "timeout": result.get("timeout", False),
        "fallback_used": result.get("is_mock", False) or bool(result.get("error")),
        "created_at": result.get("created_at"),
        "message": request.message,
        "intent": context["intent"],
        "data_sources": context.get("data_sources", []),
        "context_used": context,
        "tool_context": context,
        "reasons": _build_reasons(context, result),
        "recommendations": recommendations,
        "suggested_actions": recommendations,
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
        fallback_used=data["fallback_used"],
        timeout=data["timeout"],
        error=data.get("error"),
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
