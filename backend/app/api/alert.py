from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.api.response import api_response
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
    alerts = alert_service.list_price_alerts(db, current_user)
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
    price_events = alert_service.check_and_trigger_alerts(db, current_user)
    weather_events = alert_service.check_and_trigger_weather_alerts(db, current_user)
    data = {
        "events": price_events + weather_events,
        "price_events": price_events,
        "weather_events": weather_events,
    }
    return api_response(data, source="ai_generated", source_name="Alert evaluator", confidence=0.72)


@alerts_router.post("/auto-generate")
async def smart_alert_auto_generate(
    request: SmartAlertRequest,
    db: Session = Depends(get_db),
):
    from app.services.weather_service import weather_service
    crop = request.crop_name or "lua"
    risk = weather_service.analyze_agriculture_risk(db, request.region, crop)
    data = {
        "alert_type": request.alert_type or "weather",
        "severity": "critical" if risk.get("risk_level") == "high" else risk.get("risk_level", "medium"),
        "title": request.title or f"AI alert for {crop} in {request.region}",
        "message": request.message or f"Risk level is {risk.get('risk_level')}; review recommended actions.",
        "affected_crop": crop,
        "recommended_action": request.recommended_action or risk.get("reasons", []),
        "send_channels": request.send_channels,
        "confidence": risk.get("confidence", 0.0),
        "source": "ai_generated" if not risk.get("is_mock") else "mock",
        "source_name": "AI Smart Alert generator",
        "is_mock": risk.get("is_mock", False),
    }
    return api_response(
        data,
        source=data["source"],
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        confidence=data["confidence"],
    )


@alerts_router.post("/send")
async def smart_alert_send(request: SmartAlertRequest):
    data = {
        "alert_type": request.alert_type,
        "send_channels": request.send_channels,
        "status": "stored" if "app" in request.send_channels else "mock_sent",
        "message": request.message or "Alert queued for delivery.",
        "source": "mock",
        "source_name": "Notification provider fallback",
        "is_mock": True,
        "confidence": 0.5,
    }
    return api_response(data, source="mock", source_name=data["source_name"], is_mock=True, confidence=0.5)


@alerts_router.post("/test-channel")
async def smart_alert_test_channel(request: TestChannelRequest):
    data = {
        "channel": request.channel,
        "receiver": request.receiver,
        "status": "stored" if request.channel == "app" else "mock_sent",
        "source": "mock",
        "source_name": "Notification channel test fallback",
        "is_mock": True,
        "confidence": 0.5,
    }
    return api_response(data, source="mock", source_name=data["source_name"], is_mock=True, confidence=0.5)


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
