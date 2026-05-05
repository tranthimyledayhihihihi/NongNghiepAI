from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.alert_schema import (
    AlertCreateRequest,
    AlertDeactivateResponse,
    AlertListResponse,
    AlertResponse,
)
from app.services.alert_service import alert_service

router = APIRouter(prefix="/api/alert", tags=["alert"])


@router.post("/create", response_model=AlertResponse)
async def create_price_alert(request: AlertCreateRequest, db: Session = Depends(get_db)):
    return alert_service.create_price_alert(db, request)


@router.get("/list", response_model=AlertListResponse)
async def list_price_alerts(db: Session = Depends(get_db)):
    return {"alerts": alert_service.list_price_alerts(db)}


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
