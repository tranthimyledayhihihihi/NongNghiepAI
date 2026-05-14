from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _region_from(user: User | None, region: str | None) -> str:
    return region or (user.Region if user and user.Region else "Ha Noi")


@router.get("/summary")
async def get_dashboard_summary(
    region: str | None = None,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_summary(
        db,
        user_id=current_user.UserID if current_user else None,
        region=_region_from(current_user, region),
        force_refresh_weather=force_refresh,
    )
    return api_response(data, is_mock=data["featured_crop"].get("is_mock", False))


@router.get("/featured-crop")
async def get_featured_crop(
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_featured_crop(db, region=_region_from(current_user, region))
    return api_response(data, is_mock=data.get("is_mock", False), cache_status=data.get("cache_status", "from_db"))


@router.get("/price-trend")
async def get_price_trend(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_price_trend(db, crop_name=crop_name, region=_region_from(current_user, region), days=days)
    return api_response(data, is_mock=data.get("is_mock", False))


@router.get("/weather-overview")
async def get_weather_overview(
    region: str | None = None,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_weather_overview(
        db,
        region=_region_from(current_user, region),
        force_refresh=force_refresh,
    )
    return api_response(
        data,
        source="weather",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "unknown"),
        last_updated=data.get("last_updated"),
    )


@router.get("/ai-recommendation")
async def get_ai_recommendation(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_ai_recommendation(db, crop_name=crop_name, region=_region_from(current_user, region))
    return api_response(data, source="rule_based_ai", is_mock=data.get("is_mock", False), last_updated=data.get("last_updated"))
