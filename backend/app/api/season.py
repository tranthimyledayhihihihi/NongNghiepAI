from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.schemas.season_schema import SeasonCreate, SeasonHarvestEstimateRequest, SeasonUpdate
from app.services.season_service import season_service

router = APIRouter(prefix="/api/seasons", tags=["seasons"])


def _user_id(current_user: User | None) -> int | None:
    return current_user.UserID if current_user else None


def _database_response(data: dict, message: str = "OK"):
    return api_response(
        data,
        source="database",
        source_name="Seasons DB",
        cache_status="from_db",
        confidence=0.95,
        message=message,
    )


@router.get("")
async def get_seasons(
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    seasons = season_service.get_seasons(
        db,
        user_id=_user_id(current_user),
        status=status_filter,
        search=search,
    )
    return _database_response({"total": len(seasons), "seasons": seasons})


@router.get("/active")
async def get_active_seasons(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    seasons = season_service.get_active_seasons(db, user_id=_user_id(current_user))
    return _database_response({"total": len(seasons), "seasons": seasons})


@router.get("/stats/summary")
async def get_season_summary(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return _database_response(season_service.get_summary(db, user_id=_user_id(current_user)))


@router.post("/predict-harvest-date")
async def predict_season_harvest_date(
    request: SeasonHarvestEstimateRequest,
    db: Session = Depends(get_db),
):
    try:
        estimate = season_service.estimate_harvest_date(
            db,
            crop_name=request.crop_name,
            region=request.region,
            start_date=request.start_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _database_response(estimate, message="harvest date estimated")


@router.get("/{season_id}")
async def get_season_by_id(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    season = season_service.get_season_by_id(db, season_id, user_id=_user_id(current_user))
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="season not found")
    return _database_response(season_service.serialize_season(season))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_season(
    request: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    try:
        season = season_service.create_season(db, request, user_id=_user_id(current_user))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not create season") from exc
    return _database_response(season, message="season created")


@router.put("/{season_id}")
async def update_season(
    season_id: int,
    request: SeasonUpdate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    try:
        season = season_service.update_season(db, season_id, request, user_id=_user_id(current_user))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not update season") from exc
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="season not found")
    return _database_response(season, message="season updated")


@router.delete("/{season_id}")
async def delete_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    try:
        deleted = season_service.delete_season(db, season_id, user_id=_user_id(current_user))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not delete season") from exc
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="season not found")
    return _database_response({"deleted": True, "season_id": season_id}, message="season deleted")


@router.patch("/{season_id}/complete")
async def complete_season(
    season_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    try:
        season = season_service.complete_season(db, season_id, user_id=_user_id(current_user))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="could not complete season") from exc
    if season is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="season not found")
    return _database_response(season, message="season completed")
