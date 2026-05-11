from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.harvest_schema import HarvestForecastRequest, HarvestForecastResponse, HarvestScheduleCreateRequest
from app.services.harvest_service import harvest_service

router = APIRouter(prefix="/api/harvest", tags=["harvest"])


@router.post("/forecast", response_model=HarvestForecastResponse)
async def forecast_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return harvest_service.forecast_harvest(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )


@router.post("/predict")
async def predict_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return harvest_service.predict_harvest_date(
        db,
        request.crop_name,
        datetime.combine(request.planting_date, datetime.min.time()),
        request.region,
        user_id=current_user.UserID if current_user else None,
    )


@router.get("/schedule")
async def get_harvest_schedule():
    return {"schedules": []}


@router.get("/history/me")
async def get_my_harvest_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = harvest_service.get_history(db, current_user.UserID, limit)
    return {"user_id": current_user.UserID, "total": len(history), "history": history}


@router.get("/history/{user_id}")
async def get_harvest_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = harvest_service.get_history(db, user_id, limit)
    return {"user_id": user_id, "total": len(history), "history": history}


@router.get("/schedules/me")
async def get_my_harvest_schedules(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedules = harvest_service.get_schedules(db, current_user.UserID, limit)
    return {"user_id": current_user.UserID, "total": len(schedules), "schedules": schedules}


@router.post("/schedules")
async def create_my_harvest_schedule(
    request: HarvestScheduleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule = harvest_service.create_schedule_from_request(db, current_user.UserID, request)
    if schedule is None:
        raise HTTPException(status_code=400, detail="could not create harvest schedule")
    return schedule


@router.get("/schedules/{user_id}")
async def get_harvest_schedules(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    schedules = harvest_service.get_schedules(db, user_id, limit)
    return {"user_id": user_id, "total": len(schedules), "schedules": schedules}
