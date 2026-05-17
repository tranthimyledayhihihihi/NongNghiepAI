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


class FarmSettingsRequest(BaseModel):
    region: str | None = None
    farm_area: float | None = None
    main_crops: list[str] | None = None
    planting_date: str | None = None
    farming_type: str | None = None


class AlertPreferencesRequest(BaseModel):
    price_alerts: bool | None = None
    weather_alerts: bool | None = None
    harvest_reminders: bool | None = None
    email_channel: bool | None = None
    zalo_channel: bool | None = None
    sms_channel: bool | None = None
    price_threshold: float | None = None
    weather_thresholds: dict | None = None


class AIPreferencesRequest(BaseModel):
    language: str | None = None
    explanation_level: str | None = "balanced"
    preferred_model: str | None = "auto"
    tone: str | None = "practical"


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


@router.get("/profile")
async def get_profile_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.get_settings(db, current_user)
    profile = {
        "full_name": data.get("full_name"),
        "email": data.get("email"),
        "phone_number": data.get("phone_number"),
        "zalo_user_id": data.get("zalo_user_id"),
        "region": data.get("region"),
        "region_key": data.get("region_key"),
        "source": "database",
        "source_name": "Users/UserSettings DB",
        "updated_at": data.get("updated_at"),
    }
    return api_response(profile, source="database", source_name=profile["source_name"], last_updated=data.get("updated_at"), confidence=0.72)


@router.post("/profile")
async def save_profile_settings(
    request: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.update_settings(db, current_user, request)
    return api_response(data, source="database", source_name="Users/UserSettings DB", last_updated=data.get("updated_at"), message="profile saved", confidence=0.72)


@router.get("/farm")
async def get_farm_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.get_settings(db, current_user)
    farm = {
        "region": data.get("region") or "Ha Noi",
        "farm_area": None,
        "main_crops": ["lua"],
        "planting_date": None,
        "farming_type": "mixed",
        "source": "mock",
        "source_name": "UserSettings DB + demo farm defaults",
        "is_mock": True,
        "updated_at": data.get("updated_at"),
    }
    return api_response(farm, source="mock", source_name=farm["source_name"], is_mock=True, last_updated=data.get("updated_at"), confidence=0.45)


@router.post("/farm")
async def save_farm_settings(
    request: FarmSettingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.region:
        settings_service.update_settings(db, current_user, UserSettingsUpdate(region=request.region))
    data = {
        **request.model_dump(),
        "stored": True,
        "note": "Farm profile accepted; non-core fields are demo until a dedicated farm profile table is enabled.",
        "source": "mock",
        "source_name": "Farm settings fallback",
        "is_mock": True,
    }
    return api_response(data, source="mock", source_name=data["source_name"], is_mock=True, message="farm settings saved", confidence=0.45)


@router.get("/alert-preferences")
async def get_alert_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.get_settings(db, current_user)
    prefs = {
        "price_alerts": data.get("price_alerts"),
        "weather_alerts": data.get("weather_alerts"),
        "harvest_reminders": data.get("harvest_reminders"),
        "channels": {
            "email": data.get("email_channel"),
            "zalo": data.get("zalo_channel"),
            "sms": data.get("sms_channel"),
            "app": True,
        },
        "thresholds": {"price_change_pct": 5, "rainfall_mm": 30, "temperature_c": 35},
        "source": "database",
        "source_name": "UserSettings DB",
    }
    return api_response(prefs, source="database", source_name=prefs["source_name"], confidence=0.72)


@router.post("/alert-preferences")
async def save_alert_preferences(
    request: AlertPreferencesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.update_settings(
        db,
        current_user,
        UserSettingsUpdate(
            price_alerts=request.price_alerts,
            weather_alerts=request.weather_alerts,
            harvest_reminders=request.harvest_reminders,
            email_channel=request.email_channel,
            zalo_channel=request.zalo_channel,
            sms_channel=request.sms_channel,
        ),
    )
    data["thresholds"] = {
        "price_threshold": request.price_threshold,
        "weather_thresholds": request.weather_thresholds,
    }
    return api_response(data, source="database", source_name="UserSettings DB", message="alert preferences saved", confidence=0.72)


@router.get("/ai-preferences")
async def get_ai_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = settings_service.get_settings(db, current_user)
    prefs = {
        "language": data.get("language") or "vi",
        "explanation_level": "balanced",
        "preferred_model": "auto",
        "tone": "practical",
        "source": "mock",
        "source_name": "UserSettings DB + AI defaults",
        "is_mock": True,
    }
    return api_response(prefs, source="mock", source_name=prefs["source_name"], is_mock=True, confidence=0.5)


@router.post("/ai-preferences")
async def save_ai_preferences(
    request: AIPreferencesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.language:
        settings_service.update_settings(db, current_user, UserSettingsUpdate(language=request.language))
    data = {
        **request.model_dump(),
        "stored": True,
        "note": "AI preferences accepted; model/tone/explanation use demo persistence until a dedicated AI preference table is enabled.",
        "source": "mock",
        "source_name": "AI preferences fallback",
        "is_mock": True,
    }
    return api_response(data, source="mock", source_name=data["source_name"], is_mock=True, message="ai preferences saved", confidence=0.5)


@router.post("/test-notification-channel")
async def test_notification_channel_alias(
    request: ChannelTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = settings_service.test_channel(db, current_user, request.channel, request.receiver)
    return api_response(result, source="mock" if result.get("status") == "mock_sent" else "database", source_name="Notification channel test", confidence=0.6)


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
