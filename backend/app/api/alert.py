from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.api.response import api_response, error_response
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


@alerts_router.get("/options")
async def get_alert_options_alias(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = alert_service.get_options(db, current_user)
    return api_response(
        data,
        source="database",
        source_name="Alert rules DB",
        cache_status="from_db",
        confidence=0.7,
    )


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


@alerts_router.get("/triggers")
async def list_alert_triggers_alias(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = alert_service.get_trigger_history(db, current_user, limit=limit)
    return api_response(
        data,
        source="database",
        source_name="Alert trigger history DB",
        cache_status="from_db",
        confidence=0.7,
    )


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


@alerts_router.delete("/{alert_id}")
async def deactivate_price_alert_alias(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.deactivate_price_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="alert not found")
    return api_response(
        result,
        source="database",
        source_name="Alert rules DB",
        cache_status="from_db",
        confidence=0.7,
    )


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


class SmartAlertRequest(BaseModel):
    alert_type: str = "price"
    crop_name: str | None = None
    region: str = "Ha Noi"
    severity: str = "medium"
    title: str | None = None
    message: str | None = None
    recommended_action: list[str] | None = None
    target_price: float | None = None
    condition: str = "above"
    send_channels: list[str] = ["app"]
    receiver: str | None = None


class TestChannelRequest(BaseModel):
    channel: str = "app"
    receiver: str | None = None


@alerts_router.post("/create")
async def smart_alert_create(
    request: SmartAlertRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if request.alert_type == "weather":
        payload = {
            "region": request.region,
            "condition": request.condition if request.condition in {"rainfall", "temperature", "wind", "humidity", "air_quality"} else "rainfall",
            "threshold": request.target_price or 20,
            "severity": request.severity,
            "title": request.title,
            "message": request.message,
            "recommendation": "; ".join(request.recommended_action or []),
            "notification_channel": (request.send_channels or ["app"])[0],
            "receiver": request.receiver,
        }
        data = alert_service.create_weather_alert(db, payload, current_user)
    else:
        data = alert_service.create_price_alert(
            db,
            AlertCreateRequest(
                crop_name=request.crop_name or "lua",
                region=request.region,
                target_price=request.target_price or 1,
                condition=request.condition if request.condition in {"above", "below"} else "above",
                notification_channel=(request.send_channels or ["app"])[0],
                receiver=request.receiver or "",
            ),
            current_user,
        )
    return api_response(
        data,
        source="database",
        source_name="Alert rules DB",
        cache_status="from_db",
        last_updated=data.get("created_at"),
        confidence=0.7,
    )


@alerts_router.get("/list")
async def smart_alert_list(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    alerts = alert_service.get_active_alerts(db, user_id=current_user.UserID if current_user else None)
    return api_response(
        {"alerts": alerts, "total": len(alerts)},
        source="database",
        source_name="Alert rules DB",
        cache_status="from_db",
        confidence=0.7,
    )


@alerts_router.post("/evaluate")
async def smart_alert_evaluate(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    events = alert_service.evaluate_alert_rules(db, {}, current_user)
    price_events = [item for item in events if item.get("alert_kind") != "weather"]
    weather_events = [item for item in events if item.get("alert_kind") == "weather"]
    data = {
        "events": events,
        "price_events": price_events,
        "weather_events": weather_events,
    }
    return api_response(data, source="ai_generated", source_name="Alert evaluator", confidence=0.72)


@alerts_router.post("/auto-generate")
async def smart_alert_auto_generate(
    request: SmartAlertRequest,
    db: Session = Depends(get_db),
):
    crop = request.crop_name or "lua"
    data = alert_service.auto_generate_alerts(db, {"crop_name": crop, "region": request.region})
    first_alert = (data.get("alerts") or [{}])[0]
    first_alert.update({
        "alert_type": request.alert_type or first_alert.get("alert_type"),
        "title": request.title or first_alert.get("title"),
        "message": request.message or first_alert.get("message"),
        "recommended_action": request.recommended_action or [first_alert.get("suggested_action")],
        "send_channels": request.send_channels,
    })
    return api_response(
        data,
        source=data["source"],
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        confidence=data["confidence"],
    )


@alerts_router.post("/send")
async def smart_alert_send(request: SmartAlertRequest):
    return error_response(
        "Không thể gửi cảnh báo realtime vì kênh gửi chưa được cấu hình.",
        code="REALTIME_API_FAILED",
        source="realtime_api",
    )


@alerts_router.post("/test-channel")
async def smart_alert_test_channel(request: TestChannelRequest):
    return error_response(
        "Không thể kiểm tra kênh thông báo realtime vì kênh gửi chưa được cấu hình.",
        code="REALTIME_API_FAILED",
        source="realtime_api",
    )


@weather_alert_router.post("/create")
async def create_weather_alert(
    request: WeatherAlertCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = alert_service.create_weather_alert(db, request.model_dump(), current_user)
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name=data.get("source_name", "WeatherAlert DB"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        last_updated=data.get("created_at"),
        confidence=data.get("confidence", 0.7),
    )


@weather_alert_router.delete("/{alert_id}", response_model=AlertDeactivateResponse)
async def deactivate_weather_alert(alert_id: int, db: Session = Depends(get_db)):
    result = alert_service.deactivate_weather_alert(db, alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="weather alert not found")
    return result
