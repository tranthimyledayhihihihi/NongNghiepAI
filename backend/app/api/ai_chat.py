import asyncio
import json
import os
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
from app.services.ai_intent_service import (
    ANALYSIS_INTENTS,
    GENERAL_CAPABILITY_REPLY,
    GREETING_REPLY,
    classify_user_intent,
    db_topic_for_intent,
    extract_crop_from_message,
    extract_region_from_message,
    is_capability_question,
    normalize_user_text,
    normalize_intent,
)

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
    return classify_user_intent(message)


def _build_reasons(context: dict, result: dict) -> list[str]:
    reasons: list[str] = []
    weather = context.get("weather") or {}
    pricing = context.get("pricing") or {}
    market = (context.get("market") or {}).get("trends") or context.get("market_trends") or {}
    if weather:
        reasons.append(
            f"Thời tiết hiện có: {weather.get('temperature')}C, lượng mưa {weather.get('rainfall')}mm."
        )
    if pricing:
        reasons.append(
            f"Giá hiện tại: {pricing.get('market_price') or pricing.get('current_price')} VND/kg."
        )
    if market:
        reasons.append(
            f"Xu hướng thị trường: {market.get('trend', 'ổn định')}."
        )
    if context.get("quality_history"):
        reasons.append("Có lịch sử kiểm tra chất lượng gần đây.")
    if context.get("harvest_status"):
        reasons.append("Có lịch mùa vụ/thu hoạch đang theo dõi.")
    if result.get("is_mock"):
        reasons.append("Câu trả lời được tạo bằng fallback nội bộ.")
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
        recommendations.append("Cung cấp thêm cây trồng, khu vực hoặc mùa vụ để phân tích chính xác hơn.")
    return recommendations[:6]


def _default_context(db: Session, user: User | None, request: AIChatMessageRequest) -> dict:
    intent = _detect_intent(request.message)
    region = request.region or extract_region_from_message(request.message) or (user.Region if user and user.Region else "Ha Noi")
    crop = request.resolved_crop or extract_crop_from_message(request.message) or "lua"
    return ai_context_service.build_ai_context(
        db,
        user_id=user.UserID if user else None,
        region=region,
        crop=crop,
        intent=intent,
    )


def _should_answer_market_locally(message: str, intent: str) -> bool:
    text = normalize_user_text(message)
    market_words = (
        "gia",
        "thi truong",
        "co nen ban",
        "nen ban",
        "giu hang",
        "tin tuc",
        "tin thi truong",
        "phan tich thi truong",
    )
    return intent == "price_analysis" and any(word in text for word in market_words)


def _format_vnd(value: Any) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", ".")
    except Exception:
        return "N/A"


def _local_market_reply(context: dict, message: str) -> str:
    crop = context.get("crop_name") or "nông sản"
    region = context.get("region") or "khu vực này"
    pricing = context.get("pricing") or {}
    analysis = context.get("market_analysis") or context.get("pricing_analysis") or {}
    market = context.get("market") or {}
    news_items = market.get("news") or analysis.get("related_news") or []
    wants_news = "tin" in normalize_user_text(message)

    has_real_price = bool(pricing) and not pricing.get("is_mock") and pricing.get("source_type") != "mock"
    if not has_real_price:
        return (
            f"Hiện chưa có dữ liệu thị trường thực tế cho {crop} tại {region}. "
            "Mình sẽ không tự bịa giá. Bạn có thể cập nhật dữ liệu thị trường thực tế hoặc thử lại sau khi hệ thống đồng bộ xong."
        )

    lines = [
        f"Giá {crop} tại {region}: {_format_vnd(pricing.get('current_price') or pricing.get('market_price'))} {pricing.get('unit') or 'VNĐ/kg'}.",
        f"Nguồn: {pricing.get('source_name') or 'MarketPrices DB'}; độ tin cậy khoảng {round(float(pricing.get('confidence_score') or pricing.get('confidence') or 0) * 100)}%.",
    ]
    global_reference = pricing.get("global_reference") or analysis.get("global_reference")
    if global_reference:
        lines.append(
            f"Tham chiếu quốc tế: {global_reference.get('price')} {global_reference.get('unit') or 'USD/ton'} từ {global_reference.get('source_name') or 'Nguồn tham chiếu quốc tế'}."
        )
    recommendation = analysis.get("recommendation") or pricing.get("recommendation")
    if isinstance(recommendation, dict):
        lines.append(f"Khuyến nghị: {recommendation.get('title') or recommendation.get('action')}. {recommendation.get('reason') or ''}".strip())
    elif recommendation:
        lines.append(f"Khuyến nghị: {recommendation}")
    if wants_news:
        if news_items:
            lines.append("Tin thị trường liên quan:")
            for item in news_items[:3]:
                lines.append(f"- {item.get('title')} ({item.get('source_name') or 'nguồn tin thị trường'})")
        else:
            lines.append("Chưa có tin tức thị trường thực tế phù hợp trong cache cho nông sản/khu vực này.")
    return "\n".join(lines)


def _get_google_api_key() -> str | None:
    api_key = (os.getenv("GOOGLE_API_KEY") or settings.GOOGLE_API_KEY or "").strip()
    if not api_key or api_key == "${GEMINI_API_KEY}":
        api_key = (os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()
    return api_key or None


def _safe_json(data: Any) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data.strip()
    return json.dumps(data, ensure_ascii=False, default=str)


_INTERNAL_CONTEXT_KEYS = {
    "source",
    "source_name",
    "source_url",
    "meta",
    "cache_status",
    "is_mock",
    "fallback_used",
    "timeout",
    "data_sources",
    "tools_used",
    "provider",
    "model",
    "engine",
    "error",
    "context_error",
    "generated_at",
    "updated_at",
    "fetched_at",
    "last_updated",
}


def _is_unreliable_context(value: dict) -> bool:
    source = str(value.get("source") or "").lower()
    cache_status = str(value.get("cache_status") or "").lower()
    return bool(
        value.get("is_mock")
        or value.get("fallback_used")
        or source in {"mock", "fallback", "demo"}
        or cache_status in {"mock", "miss"}
    )


def _sanitize_context_for_prompt(value: Any) -> Any:
    if isinstance(value, dict):
        if _is_unreliable_context(value):
            return {
                "data_available": False,
                "message": "Hiện chưa có đủ dữ liệu để phân tích chính xác",
            }
        cleaned: dict[str, Any] = {}
        for key, child in value.items():
            if key in _INTERNAL_CONTEXT_KEYS:
                continue
            sanitized = _sanitize_context_for_prompt(child)
            if sanitized in ({}, [], None, ""):
                continue
            cleaned[key] = sanitized
        return cleaned
    if isinstance(value, list):
        cleaned_items = []
        for child in value:
            sanitized = _sanitize_context_for_prompt(child)
            if sanitized not in ({}, [], None, ""):
                cleaned_items.append(sanitized)
        return cleaned_items
    return value


def _current_season_context() -> str:
    month = datetime.now().month
    year = datetime.now().year
    if month in (12, 1, 2):
        north = "vụ Đông Xuân giai đoạn mạ/cây con. Chú ý rét đậm, rét hại, ốc bươu vàng"
        central = "vụ Đông Xuân mới gieo sạ. Thời tiết lạnh-khô. Chú ý chuột, ốc bươu vàng, bệnh lùn sọc đen"
        south = "mùa khô - vụ Đông Xuân sinh trưởng hoặc sắp thu hoạch. Thiếu nước tưới cuối vụ"
    elif month in (3, 4):
        north = "vụ Đông Xuân giai đoạn làm đòng-trổ bông. Cần bón thúc đòng, phòng đạo ôn cổ bông, sâu cuốn lá"
        central = "vụ Đông Xuân giai đoạn làm đòng-trổ bông. Nắng nóng sớm, nguy cơ hạn, bọ trĩ, sâu đục thân"
        south = "vụ Đông Xuân thu hoạch. Chuẩn bị làm đất vụ Hè Thu. Nguy cơ cháy đồng"
    elif month in (5, 6):
        north = "vụ Đông Xuân thu hoạch. Đang làm đất chuẩn bị vụ Mùa. Nắng nóng, dễ cháy đồng"
        central = "vụ Đông Xuân thu hoạch; đang gieo sạ vụ Hè Thu. Nắng nóng đỉnh điểm, hạn Bắc Trung Bộ, nguy cơ sâu cuốn lá vụ Hè Thu"
        south = "đầu mùa mưa, vụ Hè Thu bắt đầu gieo sạ. Chú ý ốc bươu vàng, bệnh lùn sọc đen, rầy nâu"
    elif month in (7, 8):
        north = "vụ Mùa giai đoạn đẻ nhánh-làm đòng. Mưa nhiều, nguy cơ sâu cuốn lá, bạc lá, đạo ôn"
        central = "vụ Hè Thu sinh trưởng. Mưa lũ, nguy cơ đổ ngã, sâu cuốn lá, đạo ôn cổ bông"
        south = "vụ Hè Thu sinh trưởng. Mùa mưa, nguy cơ rầy nâu, bệnh đạo ôn, vàng lùn"
    elif month in (9, 10):
        north = "vụ Mùa giai đoạn trổ-chín. Đầu mùa lạnh, chú ý đạo ôn, chuẩn bị thu hoạch"
        central = "vụ Hè Thu thu hoạch. Mùa bão lũ - cần thu hoạch sớm trước lũ"
        south = "vụ Hè Thu thu hoạch. Vụ Thu Đông bắt đầu ở ĐBSCL. Chú ý nhện gié, rầy nâu cuối vụ"
    else:
        north = "thu hoạch vụ Mùa xong. Chuẩn bị đất vụ Đông Xuân. Trồng rau màu vụ Đông"
        central = "chuẩn bị vụ Đông Xuân. Mưa muộn, lũ lụt còn xảy ra ở Trung Bộ"
        south = "mùa khô bắt đầu. Vụ Thu Đông ĐBSCL đang sinh trưởng"
    return (
        f"Thời điểm: tháng {month}/{year}\n"
        f"Miền Bắc: {north}\n"
        f"Miền Trung (Quảng Bình, Quảng Nam, Nghệ An...): {central}\n"
        f"Miền Nam (ĐBSCL, Đông Nam Bộ): {south}"
    )


def _classify_region_zone(region: str) -> str:
    r = region.lower()
    north = [
        "hà nội", "ha noi", "hải phòng", "hai phong", "hà giang", "lào cai", "yên bái",
        "phú thọ", "thái nguyên", "bắc giang", "bắc ninh", "nam định", "thái bình",
        "hà nam", "ninh bình", "thanh hóa", "thanh hoa", "nghệ an", "nghe an",
        "hà tĩnh", "ha tinh", "bắc kạn", "cao bằng", "lạng sơn", "quảng ninh",
        "hòa bình", "sơn la", "điện biên", "lai châu", "tuyên quang", "vĩnh phúc", "hưng yên",
    ]
    central = [
        "quảng bình", "quang binh", "lệ thủy", "le thuy", "đồng hới", "quảng trị", "quang tri",
        "thừa thiên", "thua thien", "huế", "hue", "đà nẵng", "da nang",
        "quảng nam", "quang nam", "hội an", "hoi an", "quảng ngãi", "quang ngai",
        "bình định", "binh dinh", "quy nhon", "quy nhơn", "phú yên", "phu yen",
        "khánh hòa", "khanh hoa", "nha trang", "ninh thuận", "ninh thuan",
        "bình thuận", "binh thuan", "lâm đồng", "lam dong", "đà lạt", "da lat",
        "kon tum", "gia lai", "pleiku", "đắk lắk", "dak lak", "buon ma thuot",
        "đắk nông", "dak nong",
    ]
    south = [
        "tp.hcm", "tp hcm", "hồ chí minh", "ho chi minh", "sài gòn", "sai gon",
        "bình dương", "binh duong", "đồng nai", "dong nai", "vũng tàu", "vung tau",
        "long an", "tiền giang", "tien giang", "bến tre", "ben tre", "trà vinh", "tra vinh",
        "vĩnh long", "vinh long", "đồng tháp", "dong thap", "an giang", "kiên giang",
        "kien giang", "cần thơ", "can tho", "hậu giang", "hau giang", "sóc trăng",
        "soc trang", "bạc liêu", "bac lieu", "cà mau", "ca mau",
    ]
    for kw in north:
        if kw in r:
            return "miền Bắc"
    for kw in central:
        if kw in r:
            return "miền Trung"
    for kw in south:
        if kw in r:
            return "miền Nam"
    return "Việt Nam"


def _intent_format_instruction(intent: str) -> str:
    formats = {
        "price_analysis": (
            "- Giá hiện tại\n"
            "- Xu hướng\n"
            "- So sánh nếu có\n"
            "- Khuyến nghị bán/giữ hàng\n"
            "- Mức độ tin cậy nếu backend có dữ liệu"
        ),
        "weather_analysis": (
            "- Thời tiết hiện tại/dự báo\n"
            "- Ảnh hưởng đến cây trồng\n"
            "- Rủi ro\n"
            "- Khuyến nghị tưới/phun/thu hoạch"
        ),
        "harvest_analysis": (
            "- Giai đoạn vụ mùa hiện tại tại khu vực người dùng hỏi (dựa vào context mùa vụ)\n"
            "- Tình hình cụ thể: cây đang ở giai đoạn nào, cần làm gì\n"
            "- Rủi ro thời tiết/sâu bệnh phổ biến trong giai đoạn này tại khu vực đó\n"
            "- Khuyến nghị cụ thể cho nông dân tại khu vực và thời điểm hiện tại\n"
            "(Nếu backend không có số liệu cụ thể, dùng kiến thức nông nghiệp cho vùng và tháng này)"
        ),
        "quality_analysis": (
            "- Sâu bệnh/vấn đề chất lượng phổ biến với cây trồng đó tại khu vực và thời điểm hỏi\n"
            "- Triệu chứng nhận biết\n"
            "- Cách xử lý cụ thể: thuốc/biện pháp sinh học/canh tác\n"
            "- Phòng ngừa cho giai đoạn tiếp theo\n"
            "(Dùng kiến thức nông nghiệp thực tế, không cần dữ liệu backend cho câu hỏi kỹ thuật)"
        ),
        "alert_analysis": (
            "- Cảnh báo hiện có\n"
            "- Mức độ rủi ro\n"
            "- Nguyên nhân chính nếu có dữ liệu\n"
            "- Việc cần chú ý ngay"
        ),
        "full_farm_analysis": (
            "# Tổng quan hôm nay\n"
            "# Điểm đáng chú ý\n"
            "# Rủi ro\n"
            "# Việc nên làm ngay"
        ),
    }
    return formats.get(
        intent,
        "Trả lời trực tiếp câu hỏi. Không tự phân tích giá, thời tiết, mùa vụ, chất lượng hoặc cảnh báo nếu người dùng chưa yêu cầu.",
    )


def _build_gemini_prompt(request: AIChatMessageRequest, context: dict) -> tuple[str, str]:
    intent = normalize_intent(context.get("intent") or classify_user_intent(request.message))
    crop = request.resolved_crop or context.get("crop_name") or "chưa xác định"
    region = request.region or context.get("region") or "chưa xác định"
    region_zone = _classify_region_zone(region)
    user_context = _safe_json(request.context)
    sanitized_context = _sanitize_context_for_prompt(context)
    backend_context = json.dumps(sanitized_context, ensure_ascii=False, default=str)
    season_ctx = _current_season_context()

    system_instruction = f"""Bạn là Trợ lý AI nông nghiệp của hệ thống NongNghiepAI.
Nhiệm vụ: hỗ trợ nông dân Việt Nam về giá nông sản, thời tiết, mùa vụ, sâu bệnh, kỹ thuật canh tác.

Nguyên tắc:
1. Trả lời đúng câu hỏi. Không phân tích dữ liệu khi người dùng chỉ chào hỏi.
2. Câu trả lời phải CỤ THỂ cho: khu vực "{region}" ({region_zone}), cây "{crop}", thời điểm tháng hiện tại.
3. KHÔNG được trả lời chung chung kiểu "ở các vùng khác nhau" hay "tùy điều kiện". Phải nói rõ cho {region_zone}.
4. Với DỮ LIỆU SỐ LIỆU (giá, nhiệt độ, lượng mưa, ngày tháng cụ thể): chỉ dùng từ backend context. Nếu không có, nói rõ "hệ thống chưa có số liệu thị trường cho khu vực này".
5. Với KIẾN THỨC KỸ THUẬT (sâu bệnh, mùa vụ, kỹ thuật canh tác): BẮT BUỘC trả lời dựa trên kiến thức nông nghiệp Việt Nam cho {region_zone}, tháng hiện tại. Không được từ chối với lý do "thiếu dữ liệu".
6. Không bịa giá, nhiệt độ, sản lượng cụ thể khi không có trong context.
7. Ngắn gọn, thực tế, dễ hiểu cho nông dân. Dùng gạch đầu dòng.
8. Không hiển thị metadata: Database, API, timestamp, engine."""

    prompt = (
        f"Intent: {intent}\n"
        f"Cây trồng: {crop}\n"
        f"Khu vực: {region} ({region_zone})\n\n"
        f"=== LỊCH MÙA VỤ HIỆN TẠI ===\n{season_ctx}\n\n"
        f"=== DỮ LIỆU BACKEND (nếu có) ===\n{backend_context or '{}'}\n\n"
        f"Ngữ cảnh người dùng thêm: {user_context or 'Không có'}\n\n"
        f"=== ĐỊNH DẠNG TRẢ LỜI ===\n{_intent_format_instruction(intent)}\n\n"
        f"Câu hỏi: {request.message}\n\n"
        f"Hãy trả lời CỤ THỂ cho {region} ({region_zone}), tháng này. "
        "Dùng kiến thức nông nghiệp Việt Nam khi backend không có dữ liệu."
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
    provider: str = "gemini",
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
            Topic=db_topic_for_intent(topic),
            RelatedCropID=related_crop_id,
            ContextSnapshot=json.dumps(context, ensure_ascii=False, default=str),
            Provider=provider,
            ModelName=model_name,
            TokenUsage=None,
        ))
        db.commit()
    except Exception:
        db.rollback()


def _success_payload(
    *,
    reply: str,
    intent: str,
    crop: str | None,
    region: str | None,
    model_name: str,
    provider: str,
    context: dict | None = None,
    confidence: float = 0.82,
) -> dict:
    created_at = datetime.now()
    context = context or {}
    data = {
        "reply": reply,
        "response": reply,
        "message": reply,
        "answer": reply,
        "provider": provider,
        "model": model_name,
        "created_at": created_at.isoformat(),
        "intent": intent,
        "crop": crop,
        "crop_name": crop,
        "region": region,
        "data_sources": context.get("data_sources", []),
        "reasons": [],
        "recommendations": [],
        "suggested_actions": [],
        "confidence": confidence,
    }
    if provider == "gemini":
        data["source"] = "gemini"
        data["source_name"] = "Google Gemini"
    return {
        "success": True,
        "reply": reply,
        "source": data.get("source"),
        "data": data,
    }


@router.post("/message")
async def ai_chat_message(
    request: AIChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    intent = classify_user_intent(request.message)
    region = request.region or extract_region_from_message(request.message) or (
        current_user.Region if current_user and current_user.Region else None
    )
    crop = request.resolved_crop or extract_crop_from_message(request.message)

    if intent == "greeting":
        context = {"intent": intent, "data_sources": []}
        _save_gemini_conversation(
            db,
            user_id=current_user.UserID if current_user else None,
            session_id=request.session_id,
            question=request.message,
            reply=GREETING_REPLY,
            topic=intent,
            crop_name=crop,
            context=context,
            model_name="intent-router-v1",
            provider="local",
        )
        return _success_payload(
            reply=GREETING_REPLY,
            intent=intent,
            crop=crop,
            region=region,
            model_name="intent-router-v1",
            provider="local",
            context=context,
            confidence=1.0,
        )

    if intent == "general_question" and is_capability_question(request.message):
        context = {"intent": intent, "data_sources": []}
        _save_gemini_conversation(
            db,
            user_id=current_user.UserID if current_user else None,
            session_id=request.session_id,
            question=request.message,
            reply=GENERAL_CAPABILITY_REPLY,
            topic=intent,
            crop_name=crop,
            context=context,
            model_name="intent-router-v1",
            provider="local",
        )
        return _success_payload(
            reply=GENERAL_CAPABILITY_REPLY,
            intent=intent,
            crop=crop,
            region=region,
            model_name="intent-router-v1",
            provider="local",
            context=context,
            confidence=1.0,
        )

    if intent in ANALYSIS_INTENTS:
        try:
            context = ai_context_service.build_ai_context(
                db,
                user_id=current_user.UserID if current_user else None,
                region=region or "Ha Noi",
                crop=crop or "lua",
                intent=intent,
            )
        except Exception as exc:
            context = {
                "intent": intent,
                "region": region or "Ha Noi",
                "crop_name": crop or "lua",
                "context_error": str(exc),
                "data_sources": [],
            }
    else:
        context = {
            "intent": intent,
            "region": region,
            "crop_name": crop,
            "data_sources": [],
        }

    if _should_answer_market_locally(request.message, intent):
        reply = _local_market_reply(context, request.message)
        _save_gemini_conversation(
            db,
            user_id=current_user.UserID if current_user else None,
            session_id=request.session_id,
            question=request.message,
            reply=reply,
            topic=context.get("intent", intent),
            crop_name=crop or context.get("crop_name"),
            context=context,
            model_name="market-data-router-v1",
            provider="local",
        )
        response_payload = _success_payload(
            reply=reply,
            intent=context.get("intent", intent),
            crop=crop or context.get("crop_name"),
            region=region or context.get("region"),
            model_name="market-data-router-v1",
            provider="local",
            context=context,
            confidence=0.86,
        )
        response_payload["data"]["reasons"] = _build_reasons(context, {"is_mock": False})
        response_payload["data"]["recommendations"] = _build_recommendations(context, {"is_mock": False})
        response_payload["data"]["suggested_actions"] = response_payload["data"]["recommendations"]
        return response_payload

    try:
        reply, model_name = await _call_gemini(request, context)
    except RuntimeError as exc:
        if str(exc) == "missing_google_api_key":
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "data": None,
                    "source": "realtime_api",
                    "is_realtime": False,
                    "is_cache": False,
                    "is_mock": False,
                    "warning": None,
                    "error": {
                        "code": "AI_API_KEY_MISSING",
                        "message": "Không thể kết nối trợ lý AI. Vui lòng cấu hình GOOGLE_API_KEY trong backend/.env.",
                    },
                },
            )
        return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "data": None,
                    "source": "realtime_api",
                    "is_realtime": False,
                    "is_cache": False,
                    "is_mock": False,
                    "warning": None,
                    "error": {
                        "code": "AI_API_FAILED",
                        "message": f"Gemini không trả về câu trả lời hợp lệ: {exc}",
                    },
                },
            )
    except asyncio.TimeoutError:
        return JSONResponse(
                status_code=504,
                content={
                    "success": False,
                    "data": None,
                    "source": "realtime_api",
                    "is_realtime": False,
                    "is_cache": False,
                    "is_mock": False,
                    "warning": None,
                    "error": {
                        "code": "AI_API_TIMEOUT",
                        "message": f"Gemini API timeout sau {settings.AI_TIMEOUT_SECONDS:g} giây.",
                    },
                },
            )
    except Exception as exc:
        return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "data": None,
                    "source": "realtime_api",
                    "is_realtime": False,
                    "is_cache": False,
                    "is_mock": False,
                    "warning": None,
                    "error": {
                        "code": "AI_API_FAILED",
                        "message": f"Gemini API đang lỗi: {exc}",
                    },
                },
            )

    result = {"answer": reply, "is_mock": False}
    recommendations = _build_recommendations(context, result) if intent in ANALYSIS_INTENTS else []
    reasons = _build_reasons(context, result) if intent in ANALYSIS_INTENTS else []
    response_payload = _success_payload(
        reply=reply,
        intent=context.get("intent", intent),
        crop=crop or context.get("crop_name"),
        region=region or context.get("region"),
        model_name=model_name,
        provider="gemini",
        context=context,
        confidence=0.82,
    )
    response_payload["data"]["reasons"] = reasons
    response_payload["data"]["recommendations"] = recommendations
    response_payload["data"]["suggested_actions"] = recommendations
    _save_gemini_conversation(
        db,
        user_id=current_user.UserID if current_user else None,
        session_id=request.session_id,
        question=request.message,
        reply=reply,
        topic=context.get("intent", intent),
        crop_name=crop or context.get("crop_name"),
        context=context,
        model_name=model_name,
    )
    return response_payload


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
