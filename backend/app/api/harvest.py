from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.harvest_schema import HarvestForecastRequest, HarvestForecastResponse
from app.services.harvest_service import harvest_service

router = APIRouter(prefix="/api/harvest", tags=["harvest"])


@router.post("/forecast", response_model=HarvestForecastResponse)
async def forecast_harvest(request: HarvestForecastRequest, db: Session = Depends(get_db)):
    return harvest_service.forecast_harvest(db, request)


@router.post("/predict")
async def predict_harvest(
    crop_name: str,
    planting_date: str,
    region: str,
    db: Session = Depends(get_db),
):
    try:
        planting_dt = datetime.fromisoformat(planting_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="planting_date must be ISO format") from exc
    return harvest_service.predict_harvest_date(db, crop_name, planting_dt, region)


@router.get("/schedule")
async def get_harvest_schedule():
    return {"schedules": []}


@router.get("/history/{user_id}")
async def get_harvest_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = harvest_service.get_history(db, user_id, limit)
    return {"user_id": user_id, "total": len(history), "history": history}


@router.get("/schedules/{user_id}")
async def get_harvest_schedules(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    schedules = harvest_service.get_schedules(db, user_id, limit)
    return {"user_id": user_id, "total": len(schedules), "schedules": schedules}
