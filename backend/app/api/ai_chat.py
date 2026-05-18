import asyncio
import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_current_user
from app.api.response import api_response
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.ai_context_service import ai_context_service

router = APIRouter(prefix="/api/ai-chat", tags=["ai-chat"])

env_path = Path(__file__).resolve().parents[2] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=False)


class AIChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    crop: str | None = None
    crop_name: str | None = None
    region: str | None = None
    context: Any | None = None
    session_id: str | None = None

    @property
    def resolved_crop(self) -> str | None:
        return self.crop or self.crop_name


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
    crop = request.resolved_crop or "lua"
    intent = _detect_intent(request.message)
    return ai_context_service.build_ai_context(
        db,
        user_id=user.UserID if user else None,
        region=region,
        crop=crop,
        intent=intent,
    )


def _get_google_api_key() -> str | None:
    api_key = (os.getenv("GOOGLE_API_KEY") or "").strip()
    if api_key == "${GEMINI_API_KEY}":
        api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    return api_key or None


def _safe_json(data: Any) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data.strip()
    return json.dumps(data, ensure_ascii=False, default=str)


def _build_gemini_prompt(request: AIChatMessageRequest, context: dict) -> tuple[str, str]:
    crop = request.resolved_crop or context.get("crop_name") or "chua xac dinh"
    region = request.region or context.get("region") or "chua xac dinh"
    user_context = _safe_json(request.context)
    backend_context = json.dumps(context, ensure_ascii=False, default=str)

    system_instruction = (
        "You are AgriBot AI for a Vietnamese agriculture app. "
        "Answer in Vietnamese, be practical, concise, and specific. "
        "Use the provided crop, region, user context, and backend context when relevant. "
        "If data is missing, say what is missing and give safe next steps. "
        "Do not claim to inspect images unless image data was provided."
    )
    prompt = (
        f"Crop: {crop}\n"
        f"Region: {region}\n"
        f"User context: {user_context or 'None'}\n\n"
        f"Backend context JSON:\n{backend_context}\n\n"
        f"User message:\n{request.message}\n\n"
        "Reply with actionable agriculture advice."
    )
    return system_instruction, prompt


async def _call_gemini(request: AIChatMessageRequest, context: dict) -> tuple[str, str]:
    api_key = _get_google_api_key()
    if not api_key:
        raise RuntimeError("missing_google_api_key")

    configured_model = (os.getenv("GEMINI_MODEL") or "").strip()
    model_names = [configured_model] if configured_model else [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
    ]
    system_instruction, prompt = _build_gemini_prompt(request, context)
    client = genai.Client(api_key=api_key)

    last_error: Exception | None = None
    for model_name in model_names:
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.35,
                    ),
                ),
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
            reply = (getattr(response, "text", None) or "").strip()
            if not reply:
                raise RuntimeError("empty_gemini_response")
            return reply, model_name
        except asyncio.TimeoutError:
            raise
        except Exception as exc:
            last_error = exc
            error_text = str(exc)
            if any(token in error_text for token in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "404", "NOT_FOUND")):
                continue
            raise

    raise RuntimeError(
        f"all_gemini_models_failed: {last_error}" if last_error else "all_gemini_models_failed"
    )


def _save_gemini_conversation(
    db: Session,
    *,
    user_id: int | None,
    session_id: str | None,
    question: str,
    reply: str,
    topic: str,
    crop_name: str | None,
    context: dict,
    model_name: str,
) -> None:
    try:
        from app.models.conversation import AIConversation

        related_crop_id = None
        if crop_name:
            try:
                from app.models.crop import Crop

                crop = db.query(Crop).filter(Crop.CropName == crop_name).first()
                related_crop_id = crop.CropID if crop else None
            except Exception:
                related_crop_id = None

        db.add(AIConversation(
            UserID=user_id,
            SessionID=session_id,
            UserMessage=question,
            AIResponse=reply,
            Topic=topic,
            RelatedCropID=related_crop_id,
            ContextSnapshot=json.dumps(context, ensure_ascii=False, default=str),
            Provider="gemini",
            ModelName=model_name,
            TokenUsage=None,
        ))
        db.commit()
    except Exception:
        db.rollback()


@router.post("/message")
async def ai_chat_message(
    request: AIChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    intent = _detect_intent(request.message)
    region = request.region or (current_user.Region if current_user and current_user.Region else "Ha Noi")
    crop = request.resolved_crop or "lua"

    try:
        context = ai_context_service.build_ai_context(
            db,
            user_id=current_user.UserID if current_user else None,
            region=region,
            crop=crop,
            intent=intent,
        )
    except Exception as exc:
        context = {
            "intent": intent,
            "region": region,
            "crop_name": crop,
            "context_error": str(exc),
            "data_sources": [],
        }

    try:
        reply, model_name = await _call_gemini(request, context)
    except RuntimeError as exc:
        if str(exc) == "missing_google_api_key":
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "source": "gemini",
                    "error": "missing_google_api_key",
                    "message": "Backend chua cau hinh GOOGLE_API_KEY trong backend/.env.",
                },
            )
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "source": "gemini",
                "error": "gemini_error",
                "message": f"Gemini khong tra ve cau tra loi hop le: {exc}",
            },
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "source": "gemini",
                "error": "gemini_timeout",
                "message": f"Gemini API timeout sau {settings.AI_TIMEOUT_SECONDS:g} giay.",
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "source": "gemini",
                "error": "gemini_error",
                "message": f"Gemini API dang loi: {exc}",
            },
        )

    created_at = datetime.now()
    result = {"answer": reply, "is_mock": False}
    recommendations = _build_recommendations(context, result)
    reasons = _build_reasons(context, result)
    data = {
        "reply": reply,
        "response": reply,
        "message": reply,
        "answer": reply,
        "source": "gemini",
        "source_name": "Google Gemini",
        "provider": "gemini",
        "model": model_name,
        "created_at": created_at.isoformat(),
        "intent": context.get("intent", intent),
        "crop": crop,
        "crop_name": crop,
        "region": region,
        "data_sources": context.get("data_sources", []),
        "reasons": reasons,
        "recommendations": recommendations,
        "suggested_actions": recommendations,
        "confidence": 0.82,
    }
    _save_gemini_conversation(
        db,
        user_id=current_user.UserID if current_user else None,
        session_id=request.session_id,
        question=request.message,
        reply=reply,
        topic=context.get("intent", intent),
        crop_name=crop,
        context=context,
        model_name=model_name,
    )
    return {
        "success": True,
        "reply": reply,
        "source": "gemini",
        "data": data,
    }


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
