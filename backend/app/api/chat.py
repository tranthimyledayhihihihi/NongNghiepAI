from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session
from app.integrations.gemini_client import GeminiClient
from app.core.database import get_db
from app.api.auth import get_optional_current_user, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])

gemini_client = GeminiClient()


def _save_conversation(db: Session, user_id: int | None, question: str, answer: str) -> None:
    try:
        from app.models.conversation import AIConversation
        db.add(AIConversation(
            UserID=user_id,
            UserMessage=question,
            AIResponse=answer,
            Provider="gemini",
        ))
        db.commit()
    except Exception:
        db.rollback()


class ChatRequest(BaseModel):
    question: str = ""
    message: str = ""   # alias cho question (backward compat)
    context_data: str = ""
    user_id: int | None = None

    @model_validator(mode="after")
    def resolve_question(self):
        if not self.question and self.message:
            self.question = self.message
        if not self.question:
            raise ValueError("Vui lòng cung cấp trường 'question' hoặc 'message'")
        return self


class ChatResponse(BaseModel):
    answer: str


class PriceQARequest(BaseModel):
    question: str     # Câu hỏi định giá, ví dụ: "Giá sầu riêng Đắk Lắk hôm nay?"


class PriceQAResponse(BaseModel):
    answer: str
    tavily_answer: str = ""
    sources: list = []
    db_prices: list = []

# Từ khoá kích hoạt RAG từng loại
_PRICE_KEYWORDS = ["giá", "bao nhiêu", "thị trường", "mua", "bán", "đồng", "tiền", "xu hướng giá"]
_CROP_KEYWORDS  = ["trồng", "chăm sóc", "thu hoạch", "sinh trưởng", "phát triển", "ra hoa", "đậu trái", "bón phân"]
_PEST_KEYWORDS  = ["sâu", "bệnh", "nấm", "vi khuẩn", "virus", "héo", "vàng lá", "thối", "rệp", "nhện"]

def _question_contains(question: str, keywords: list[str]) -> bool:
    q = question.lower()
    return any(k in q for k in keywords)

@router.post("", response_model=ChatResponse)
async def ask_farming_advice(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    context_parts = []
    if request.context_data:
        context_parts.append(request.context_data)

    q = request.question

    # RAG 1: Bổ sung giá thị trường từ DB nếu câu hỏi liên quan đến giá
    if _question_contains(q, _PRICE_KEYWORDS):
        try:
            from sqlalchemy import text
            query = text("""
                SELECT TOP 20 c.CropName, m.Region, m.PricePerKg, m.SourceName, m.PriceDate
                FROM MarketPrices m
                JOIN CropTypes c ON m.CropID = c.CropID
                ORDER BY m.PriceDate DESC
            """)
            rows = db.execute(query).fetchall()
            if rows:
                lines = ["## Giá thị trường từ hệ thống (cập nhật gần nhất):"]
                for r in rows:
                    lines.append(
                        f"- {r[0]} tại {r[1]}: **{float(r[2]):,.0f} VNĐ/kg** "
                        f"(nguồn: {r[3]}, ngày {r[4]})"
                    )
                context_parts.append("\n".join(lines))
        except Exception as e:
            print(f"[Chat RAG-price] Lỗi: {e}")

    # RAG 2: Bổ sung thông tin chu kỳ sinh trưởng từ DB nếu hỏi về cây trồng
    if _question_contains(q, _CROP_KEYWORDS + _PEST_KEYWORDS):
        try:
            from sqlalchemy import text
            crop_query = text("""
                SELECT TOP 10 CropName, GrowthDurationDays, HarvestSeason,
                       TypicalPriceMin, TypicalPriceMax
                FROM CropTypes
                ORDER BY CropName
            """)
            crops = db.execute(crop_query).fetchall()
            if crops:
                lines = ["## Thông tin cây trồng trong hệ thống:"]
                for c in crops:
                    price_range = ""
                    if c[3] and c[4]:
                        price_range = f", giá điển hình: {float(c[3]):,.0f}–{float(c[4]):,.0f} VNĐ/kg"
                    days = f", chu kỳ: {c[1]} ngày" if c[1] else ""
                    season = f", mùa vụ: {c[2]}" if c[2] else ""
                    lines.append(f"- {c[0]}{days}{season}{price_range}")
                context_parts.append("\n".join(lines))
        except Exception as e:
            print(f"[Chat RAG-crop] Lỗi: {e}")

    # RAG 3: Bổ sung lịch sử giá 7 ngày gần nhất để phân tích xu hướng
    if _question_contains(q, _PRICE_KEYWORDS):
        try:
            from sqlalchemy import text
            trend_query = text("""
                SELECT TOP 30 c.CropName, ph.Region, ph.AvgPrice, ph.MinPrice,
                       ph.MaxPrice, ph.RecordDate
                FROM PriceHistory ph
                JOIN CropTypes c ON ph.CropID = c.CropID
                WHERE ph.RecordDate >= DATEADD(day, -7, GETDATE())
                ORDER BY ph.RecordDate DESC
            """)
            hist = db.execute(trend_query).fetchall()
            if hist:
                lines = ["## Lịch sử giá 7 ngày gần nhất:"]
                for h in hist:
                    lines.append(
                        f"- {h[0]} tại {h[1]} ngày {h[5]}: "
                        f"TB {float(h[2]):,.0f} | Min {float(h[3]):,.0f} | Max {float(h[4]):,.0f} VNĐ/kg"
                    )
                context_parts.append("\n".join(lines))
        except Exception as e:
            print(f"[Chat RAG-trend] Lỗi: {e}")

    combined_context = "\n\n".join(context_parts)

    try:
        answer = await gemini_client.get_farming_advice(
            question=q,
            context_data=combined_context
        )
        _save_conversation(db, current_user.UserID if current_user else None, q, answer)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi kết nối AI: {str(e)}")


@router.post("/price-qa", response_model=PriceQAResponse)
async def price_qa(
    request: PriceQARequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    """
    Hỏi-đáp định giá nông sản với Tavily Search + dữ liệu DB thực tế.

    Quy trình:
    1. Truy vấn Tavily để lấy giá mới nhất từ web (real-time)
    2. Lấy giá từ DB hệ thống để đối chiếu
    3. Tổng hợp câu trả lời đầy đủ có nguồn trích dẫn
    """
    q = request.question

    # ── Bước 1: Lấy giá từ DB để làm context ──────────────────────────────
    db_context = ""
    db_prices = []
    try:
        from sqlalchemy import text
        rows = db.execute(text("""
            SELECT TOP 15 c.CropName, m.Region, m.PricePerKg, m.SourceName, m.PriceDate
            FROM MarketPrices m
            JOIN CropTypes c ON m.CropID = c.CropID
            ORDER BY m.PriceDate DESC
        """)).fetchall()
        if rows:
            lines = ["Giá trong hệ thống (cập nhật gần nhất):"]
            for r in rows:
                line = f"- {r[0]} tại {r[1]}: {float(r[2]):,.0f} VNĐ/kg (nguồn: {r[3]}, ngày {r[4]})"
                lines.append(line)
                db_prices.append({
                    "crop_name": r[0], "region": r[1],
                    "price": float(r[2]), "source": r[3],
                    "date": str(r[4]),
                })
            db_context = "\n".join(lines)
    except Exception:
        pass

    # ── Bước 2: Tavily Search Q&A ──────────────────────────────────────────
    try:
        from app.integrations.tavily_client import ask_price_qa
        import asyncio
        result = await asyncio.to_thread(ask_price_qa, q, db_context)
        tavily_answer = result.get("tavily_answer", "")
        sources = result.get("sources", [])
        full_answer = result.get("answer", "")
    except Exception as e:
        tavily_answer = ""
        sources = []
        full_answer = f"Không tìm được dữ liệu từ Tavily: {e}"

    # ── Bước 3: Nếu Tavily không trả lời được, dùng Gemini + context DB ───
    _AI_BUSY = "Xin lỗi, hệ thống AI đang bận. Vui lòng thử lại sau ít phút."
    if not tavily_answer and db_context:
        try:
            full_answer = await gemini_client.get_farming_advice(
                question=q,
                context_data=db_context,
            )
        except Exception:
            pass

    # ── Bước 4: Fallback từ DB khi tất cả AI đều fail ─────────────────────
    if not full_answer or full_answer == _AI_BUSY or full_answer.startswith("Không tìm được"):
        if db_prices:
            lines = ["**Dữ liệu giá nông sản mới nhất trong hệ thống:**\n"]
            for p in db_prices:
                lines.append(f"- **{p['crop_name']}** tại {p['region']}: **{p['price']:,.0f} VNĐ/kg** (nguồn: {p['source']}, ngày {p['date']})")
            lines.append("\n---")
            lines.append("*Lưu ý: Hệ thống AI tạm thời quá tải. Dữ liệu trên được lấy trực tiếp từ cơ sở dữ liệu của hệ thống.*")
            full_answer = "\n".join(lines)
        else:
            full_answer = "Hiện không có dữ liệu về nông sản này trong hệ thống. Vui lòng thử lại sau hoặc đặt câu hỏi về hồ tiêu, sầu riêng."

    _save_conversation(db, current_user.UserID if current_user else None, q, full_answer)

    return PriceQAResponse(
        answer=full_answer,
        tavily_answer=tavily_answer,
        sources=sources,
        db_prices=db_prices,
    )


@router.get("/history")
def get_chat_history(
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
    return {
        "total": len(rows),
        "history": [
            {
                "id": r.ConvID,
                "user_message": r.UserMessage,
                "ai_response": r.AIResponse,
                "topic": r.Topic,
                "created_at": r.CreatedAt.isoformat() if r.CreatedAt else None,
            }
            for r in rows
        ],
    }