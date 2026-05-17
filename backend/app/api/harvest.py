from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.schemas.harvest_schema import HarvestForecastRequest, HarvestForecastResponse, HarvestScheduleCreateRequest
from app.services.harvest_service import harvest_service

router = APIRouter(prefix="/api/harvest", tags=["harvest"])


def _harvest_response(data: dict):
    return api_response(
        data,
        source=data.get("source", "ai_generated"),
        source_name=data.get("source_name", "AI Harvest Optimizer"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "computed"),
        last_updated=data.get("created_at"),
        confidence=data.get("confidence", 0.0),
    )


@router.post("/forecast")
async def forecast_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = harvest_service.forecast_harvest(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )
    return _harvest_response(data)


@router.post("/optimize")
async def optimize_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = harvest_service.optimize(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )
    return _harvest_response(data)


@router.get("/calendar")
async def get_harvest_calendar(
    user_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = harvest_service.calendar(
        db,
        user_id=user_id or (current_user.UserID if current_user else None),
        limit=limit,
    )
    return api_response(
        data,
        source="database",
        source_name=data.get("source_name", "HarvestSchedule DB"),
        cache_status=data.get("cache_status", "from_db"),
        confidence=data.get("confidence", 0.0),
    )


@router.get("/risk/{season_id}")
async def get_harvest_risk(season_id: int, db: Session = Depends(get_db)):
    data = harvest_service.risk_for_season(db, season_id)
    return api_response(
        data,
        source=data.get("source", "ai_generated"),
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "computed"),
        confidence=data.get("confidence", 0.0),
    )


@router.post("/recalculate")
async def recalculate_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = harvest_service.optimize(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )
    data["recalculated"] = True
    return _harvest_response(data)


@router.post("/predict")
async def predict_harvest(
    request: HarvestForecastRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = harvest_service.predict_harvest_date(
        db,
        request.crop_name,
        datetime.combine(request.planting_date, datetime.min.time()),
        request.region,
        user_id=current_user.UserID if current_user else None,
    )
    return _harvest_response(data)


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
