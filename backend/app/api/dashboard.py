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
    crop_name: str = Query(default="lua"),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_summary(
        db,
        user_id=current_user.UserID if current_user else None,
        region=_region_from(current_user, region),
        crop_name=crop_name,
        force_refresh_weather=force_refresh,
        force_refresh_market=force_refresh,
        force_refresh_news=force_refresh,
    )
    return api_response(
        data,
        source="dashboard_cache" if data.get("cache_status") == "hit" else "dashboard",
        is_mock=data["featured_crop"].get("is_mock", False),
        cache_status=data.get("cache_status", "fresh"),
        last_updated=data.get("generated_at"),
    )


@router.get("/featured-crop")
async def get_featured_crop(
    region: str | None = None,
    crop_name: str = Query(default="lua"),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_featured_crop(
        db,
        crop_name=crop_name,
        region=_region_from(current_user, region),
        force_refresh=force_refresh,
    )
    return api_response(data, is_mock=data.get("is_mock", False), cache_status=data.get("cache_status", "from_db"))


@router.get("/price-trend")
async def get_price_trend(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_price_trend(
        db,
        crop_name=crop_name,
        region=_region_from(current_user, region),
        days=days,
    )
    return api_response(data, source="forecast", is_mock=data.get("is_mock", False), cache_status="computed")


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


@router.get("/weather-risk")
async def get_weather_risk(
    region: str | None = None,
    crop_name: str = Query(default="lua"),
    growth_stage: str | None = None,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_weather_risk(
        db,
        region=_region_from(current_user, region),
        crop_name=crop_name,
        growth_stage=growth_stage,
        force_refresh=force_refresh,
    )
    return api_response(
        data,
        source="weather_risk",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "unknown"),
        last_updated=data.get("last_updated"),
    )


@router.get("/regional-prices")
async def get_regional_prices(
    crop_name: str = Query(default="lua"),
    regions: list[str] | None = Query(default=None),
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    data = dashboard_service.get_regional_prices(
        db,
        crop_name=crop_name,
        regions=regions,
        force_refresh=force_refresh,
    )
    return api_response(data, source="regional_prices", is_mock=all(item.get("is_mock") for item in data["regions"]), cache_status=data.get("cache_status", "from_db"))


@router.get("/realtime-market")
async def get_realtime_market(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_realtime_market(
        db,
        crop_name=crop_name,
        region=_region_from(current_user, region),
        force_refresh=force_refresh,
    )
    return api_response(
        data,
        source="price_aggregator",
        is_mock=data["featured_crop"].get("is_mock", False),
        cache_status=data.get("cache_status", "unknown"),
        last_updated=data.get("last_updated"),
    )


@router.get("/news")
async def get_dashboard_news(
    limit: int = Query(default=6, ge=1, le=30),
    crop_name: str | None = None,
    region: str | None = None,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_news(
        db,
        limit=limit,
        crop_name=crop_name,
        region=_region_from(current_user, region) if region else None,
        force_refresh=force_refresh,
    )
    return api_response(data, source="rss", is_realtime=True, is_mock=False, cache_status=data.get("cache_status", "from_db"))


@router.get("/data-health")
async def get_dashboard_data_health(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_data_health(
        db,
        region=_region_from(current_user, region),
        crop_name=crop_name,
    )
    return api_response(data, source="data_health", cache_status="computed")


@router.post("/refresh")
async def refresh_dashboard(
    source: str = Query(default="all", pattern="^(weather|prices|price|news|all)$"),
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.refresh_dashboard(
        db,
        source=source,
        region=_region_from(current_user, region),
        crop_name=crop_name,
    )
    return api_response(data, source="refresh", cache_status="refreshed", last_updated=data.get("refreshed_at"))


@router.post("/reset")
async def reset_dashboard(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.reset_and_load_dashboard(
        db,
        user_id=current_user.UserID if current_user else None,
        region=_region_from(current_user, region),
        crop_name=crop_name,
    )
    return api_response(
        data,
        source="dashboard_reset",
        is_mock=data["featured_crop"].get("is_mock", False),
        cache_status=data.get("cache_status", "reset_refreshed"),
        last_updated=data.get("generated_at"),
    )


@router.get("/ai-recommendation")
async def get_ai_recommendation(
    crop_name: str = Query(default="lua"),
    region: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = dashboard_service.get_ai_recommendation(
        db,
        crop_name=crop_name,
        region=_region_from(current_user, region),
    )
    return api_response(
        data,
        source="explainable_rule_ai",
        is_mock=data.get("is_mock", False),
        last_updated=data.get("last_updated"),
    )
