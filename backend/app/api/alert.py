from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.alert_schema import (
    AlertCreateRequest,
    AlertDeactivateResponse,
    AlertListResponse,
    AlertResponse,
)
from app.services.alert_service import alert_service
from app.tasks.alert_tasks import check_price_alerts_task

router = APIRouter(prefix="/api/alert", tags=["alert"])
alerts_router = APIRouter(prefix="/api/alerts", tags=["alert"])
weather_alert_router = APIRouter(prefix="/api/weather-alert", tags=["alert"])


@router.get("/options")
async def get_alert_options(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return alert_service.get_options(db, current_user)


@router.get("/suggestions")
async def get_alert_suggestions(
    crop_name: str | None = None,
    crop_id: int | None = None,
    region: str | None = None,
    region_key: str | None = None,
    db: Session = Depends(get_db),
):
    return alert_service.get_suggestions(
        db,
        crop_name=crop_name,
        crop_id=crop_id,
        region=region,
        region_key=region_key,
    )


@alerts_router.get("/suggestions")
async def get_alert_suggestions_alias(
    crop_name: str | None = None,
    crop_id: int | None = None,
    region: str | None = None,
    region_key: str | None = None,
    db: Session = Depends(get_db),
):
    return alert_service.get_suggestions(
        db,
        crop_name=crop_name,
        crop_id=crop_id,
        region=region,
        region_key=region_key,
    )


@router.get("/triggers")
async def list_alert_triggers(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return alert_service.get_trigger_history(db, current_user, limit=limit)


@router.post("/create", response_model=AlertResponse)
async def create_price_alert(
    request: AlertCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return alert_service.create_price_alert(db, request, current_user)


@router.get("/list", response_model=AlertListResponse)
async def list_price_alerts(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return {"alerts": alert_service.list_price_alerts(db, current_user)}


@router.post("/check")
async def check_price_alerts(
    current_user: User | None = Depends(get_optional_current_user),
):
    return check_price_alerts_task(user_id=current_user.UserID if current_user else None)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_price_alert(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.get_price_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return result


@router.delete("/{alert_id}", response_model=AlertDeactivateResponse)
async def deactivate_price_alert(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.deactivate_price_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return result


class WeatherAlertCreateRequest(BaseModel):
    region: str
    region_key: str | None = None
    condition: str = "rainfall"
    threshold: float = 0
    unit: str | None = None
    severity: str = "medium"
    title: str | None = None
    message: str | None = None
    recommendation: str | None = None
    notification_channel: str = "email"
    receiver: str | None = None


@weather_alert_router.post("/create")
async def create_weather_alert(
    request: WeatherAlertCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return alert_service.create_weather_alert(db, request.model_dump(), current_user)


@weather_alert_router.delete("/{alert_id}", response_model=AlertDeactivateResponse)
async def deactivate_weather_alert(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.deactivate_weather_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="weather alert not found")
    return result
