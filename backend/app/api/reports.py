from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.services.report_service import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
async def get_report_summary(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_user_summary(db, current_user.UserID, limit=limit)
    return api_response(data, last_updated=data["generated_at"])


@router.get("/me")
async def get_my_report(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_user_summary(db, current_user.UserID, limit=limit)
    return api_response(data, last_updated=data["generated_at"])
