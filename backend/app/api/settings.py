from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.schemas.settings_schema import UserSettingsUpdate
from app.services.settings_service import settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/me")
async def get_my_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.get_settings(db, current_user)
    return api_response(data, last_updated=data.get("updated_at"))


@router.put("/me")
async def update_my_settings(
    request: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        data = settings_service.update_settings(db, current_user, request)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return api_response(data, last_updated=data.get("updated_at"), message="settings saved")
