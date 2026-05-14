from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.weather_schema import (
    WeatherActivityRecommendation,
    WeatherAgricultureResponse,
    WeatherAlertResponse,
    WeatherCreateRequest,
    WeatherForecastResponse,
    WeatherHourlyResponse,
    WeatherResponse,
)
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current/{region}", response_model=WeatherResponse)
async def get_current_weather(region: str, db: Session = Depends(get_db)):
    return weather_service.get_current_weather(db, region)


@router.post("/refresh/{region}", response_model=WeatherResponse)
async def refresh_current_weather(region: str, db: Session = Depends(get_db)):
    return weather_service.get_current_weather(db, region, force_refresh=True)


@router.get("/forecast/{region}", response_model=WeatherForecastResponse)
async def get_weather_forecast(region: str, days: int = 7, db: Session = Depends(get_db)):
    return {
        "region": region,
        "days": days,
        "forecast": weather_service.get_forecast(db, region, days),
    }


@router.get("/hourly/{region}", response_model=WeatherHourlyResponse)
async def get_hourly_weather_forecast(region: str, hours: int = 24, db: Session = Depends(get_db)):
    return {
        "region": region,
        "hours": hours,
        "forecast": weather_service.get_hourly_forecast(db, region, hours),
    }


@router.get("/agriculture/{region}", response_model=WeatherAgricultureResponse)
async def get_agriculture_weather(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    include_hourly: bool = True,
    force_refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return weather_service.get_agriculture_weather(
        db,
        region,
        crop_name=crop_name,
        growth_stage=growth_stage,
        days=days,
        include_hourly=include_hourly,
        force_refresh=force_refresh,
    )


@router.post("/agriculture/{region}/refresh", response_model=WeatherAgricultureResponse)
async def refresh_agriculture_weather(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    include_hourly: bool = True,
    db: Session = Depends(get_db),
):
    return weather_service.get_agriculture_weather(
        db,
        region,
        crop_name=crop_name,
        growth_stage=growth_stage,
        days=days,
        include_hourly=include_hourly,
        force_refresh=True,
    )


@router.get("/alerts/{region}", response_model=list[WeatherAlertResponse])
async def get_agriculture_weather_alerts(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    db: Session = Depends(get_db),
):
    current = weather_service.get_current_weather(db, region)
    forecast = weather_service.get_forecast(db, region, days)
    return weather_service.generate_alerts(current, forecast, crop_name=crop_name, growth_stage=growth_stage)


@router.get("/recommendations/{region}", response_model=list[WeatherActivityRecommendation])
async def get_weather_activity_recommendations(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    current = weather_service.get_current_weather(db, region)
    forecast = weather_service.get_forecast(db, region, 7)
    hourly = weather_service.get_hourly_forecast(db, region, 24)
    return weather_service.build_activity_recommendations(
        current,
        forecast,
        hourly,
        crop_name=crop_name,
        growth_stage=growth_stage,
    )


@router.post("/", response_model=WeatherResponse)
async def create_weather(request: WeatherCreateRequest, db: Session = Depends(get_db)):
    return weather_service.create_weather(db, request)
