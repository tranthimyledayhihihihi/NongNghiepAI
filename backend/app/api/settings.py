from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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


@router.get("/channels/status")
async def get_channel_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(settings_service.get_channel_status(db, current_user))


class ChannelTestRequest(BaseModel):
    channel: str
    receiver: str | None = None


@router.post("/channels/test")
async def test_channel(
    request: ChannelTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = settings_service.test_channel(db, current_user, request.channel, request.receiver)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_response(result)


class TwoFactorStartRequest(BaseModel):
    method: str = "email"


@router.post("/2fa/start")
async def start_two_factor(
    request: TwoFactorStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = settings_service.start_2fa(db, current_user, request.method)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_response(result)


class TwoFactorVerifyRequest(BaseModel):
    challenge_id: str
    code: str


@router.post("/2fa/verify")
async def verify_two_factor(
    request: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = settings_service.verify_2fa(db, current_user, request.challenge_id, request.code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_response(result)


@router.post("/2fa/disable")
async def disable_two_factor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return api_response(settings_service.disable_2fa(db, current_user))


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/password")
async def change_password(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = settings_service.change_password(db, current_user, request.old_password, request.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_response(result)
