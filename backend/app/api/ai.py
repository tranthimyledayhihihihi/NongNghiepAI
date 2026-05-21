from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ai_schema import AIChatRequest, AIChatResponse
from app.services.claude_service import claude_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=AIChatResponse)
async def chat(request: AIChatRequest, db: Session = Depends(get_db)):
    return await claude_service.answer_question(
        db,
        question=request.question,
        user_id=request.user_id,
        crop_name=request.crop_name,
        region=request.region,
        session_id=request.session_id,
    )
