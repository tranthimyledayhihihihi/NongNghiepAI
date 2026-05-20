from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.response import api_response, error_response
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


@router.get("/current/{region}")
async def get_current_weather(region: str, db: Session = Depends(get_db)):
    data = weather_service.get_current_weather(db, region)
    # Nếu realtime miss thì trả thẳng payload theo spec (không bị api_response wrap đổi fields)
    if data.get("_api_error"):
        return api_response(data)
    return api_response(
        data,
        source=data.get("source") or "weather",
        source_name=data.get("source_name") or "Open-Meteo",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "unknown"),
        last_updated=data.get("last_updated"),
        confidence=0.9 if data.get("is_realtime") else 0.72 if not data.get("is_mock") else 0.45,
    )



@router.post("/refresh/{region}")
async def refresh_current_weather(region: str, db: Session = Depends(get_db)):
    data = weather_service.get_current_weather(db, region, force_refresh=True)
    return api_response(
        data,
        source="realtime_api" if data.get("is_realtime") else data.get("source", "weather"),
        source_name=data.get("source_name") or "Open-Meteo",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "unknown"),
        last_updated=data.get("last_updated"),
        confidence=0.9 if data.get("is_realtime") else 0.72 if not data.get("is_mock") else 0.45,
    )


@router.get("/forecast/{region}")
async def get_weather_forecast(region: str, days: int = 7, db: Session = Depends(get_db)):
    forecast = weather_service.get_forecast(db, region, days)
    if not forecast:
        return error_response(
            "Không thể tải dữ liệu thời tiết realtime.",
            source_name="Open-Meteo",
            source_url="https://api.open-meteo.com/v1/forecast",
        )
    is_mock = bool(forecast) and all(item.get("is_mock") for item in forecast)
    is_realtime = any(item.get("is_realtime") for item in forecast)
    fallback_used = any(item.get("fallback_used") for item in forecast)
    timed_out = any(item.get("timeout") for item in forecast)
    data = {
        "region": region,
        "days": days,
        "forecast": forecast,
        "fallback_used": fallback_used,
        "timeout": timed_out,
    }
    return api_response(
        data,
        source="realtime_api" if is_realtime else "cached" if not is_mock else "mock",
        source_name=(forecast[0].get("source_name") if forecast else "Weather"),
        is_realtime=is_realtime,
        is_mock=is_mock,
        cache_status=(forecast[0].get("cache_status") if forecast else "empty"),
        last_updated=(forecast[0].get("last_updated") if forecast else None),
        confidence=0.84 if is_realtime else 0.68 if not is_mock else 0.42,
        fallback_used=fallback_used,
        timeout=timed_out,
    )


@router.get("/hourly/{region}")
async def get_hourly_weather_forecast(region: str, hours: int = 24, db: Session = Depends(get_db)):
    forecast = weather_service.get_hourly_forecast(db, region, hours)

    # realtime miss: forecast là payload error theo spec
    if isinstance(forecast, dict) and forecast.get("_api_error"):
        return api_response(forecast)

    # Nếu service trả về dict (theo implement mới) hoặc list: chuẩn hoá theo expectations API
    if isinstance(forecast, dict):
        payload = forecast
        data = {
            "region": payload.get("region") or region,
            "hours": hours,
            "forecast": payload.get("forecast") or [],
        }
        return api_response(
            data,
            source_name=payload.get("source_name") or "Open-Meteo",
            source=payload.get("source_url") or "Open-Meteo",
            is_realtime=payload.get("is_realtime", False),
            is_mock=payload.get("is_mock", False),
            cache_status=payload.get("cache_status", "unknown"),
            last_updated=payload.get("last_updated"),
            confidence=0.82,
        )

    if not forecast:
        return error_response(
            "Không thể tải dữ liệu thời tiết realtime.",
            source_name="Open-Meteo",
            source_url="https://api.open-meteo.com/v1/forecast",
        )

    data = {
        "region": region,
        "hours": hours,
        "forecast": forecast,
    }
    return api_response(
        data,
        source="realtime_api" if any(item.get("is_realtime") for item in forecast) else "cache",
        source_name=(forecast[0].get("source_name") if forecast else "Open-Meteo"),
        is_realtime=any(item.get("is_realtime") for item in forecast),
        is_mock=not any(not item.get("is_mock") for item in forecast),
        cache_status=(forecast[0].get("cache_status") if forecast else "empty"),
        last_updated=(forecast[0].get("last_updated") if forecast else None),
        confidence=0.82,
    )



@router.get("/agriculture/{region}")
async def get_agriculture_weather(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    include_hourly: bool = True,
    db: Session = Depends(get_db),
):
    data = weather_service.get_agriculture_weather(
        db,
        region,
        crop_name=crop_name,
        growth_stage=growth_stage,
        days=days,
        include_hourly=include_hourly,
    )

    # Nếu current/forecast/hourly trả error theo spec thì trả thẳng
    current = data.get("current", {})
    if current.get("_api_error"):
        return api_response(current)

    # Chuẩn hoá metadata nguồn: lấy từ current/forecast/hourly (ưu tiên current)
    meta_source_name = current.get("source_name") or data.get("source_name") or "Open-Meteo"
    meta_source_url = current.get("source_url") or data.get("source_url") or "https://api.open-meteo.com/v1/forecast"

    return api_response(
        data,
        source="cached_or_realtime",
        source_name=meta_source_name,
        is_realtime=current.get("is_realtime", False),
        is_mock=current.get("is_mock", False),
        cache_status=current.get("cache_status", "unknown"),
        last_updated=data.get("generated_at"),
        confidence=0.86 if current.get("is_realtime") else 0.72,
        fallback_used=bool(current.get("fallback_used")),
        timeout=bool(current.get("timeout")),
    )



@router.get("/risk-analysis/{region}/{crop}")
async def get_weather_risk_analysis(region: str, crop: str, db: Session = Depends(get_db)):
    data = weather_service.analyze_agriculture_risk(db, region, crop)
    return api_response(
        data,
        source="ai_generated",
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "computed"),
        last_updated=data.get("last_updated"),
        confidence=data.get("confidence", 0.0),
    )


@router.get("/farming-recommendation/{region}/{crop}")
async def get_weather_farming_recommendation(region: str, crop: str, db: Session = Depends(get_db)):
    data = weather_service.farming_recommendation(db, region, crop)
    return api_response(
        data,
        source="ai_generated",
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "computed"),
        last_updated=data.get("last_updated"),
        confidence=data.get("confidence", 0.0),
    )


@router.get("/alerts/{region}")
async def get_agriculture_weather_alerts(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=7),
    db: Session = Depends(get_db),
):
    current = weather_service.get_current_weather(db, region)
    forecast = weather_service.get_forecast(db, region, days)
    alerts = weather_service.generate_alerts(current, forecast, crop_name=crop_name, growth_stage=growth_stage)
    return api_response(
        {"alerts": alerts, "total": len(alerts), "region": region},
        source="ai_generated" if not current.get("is_mock") else "mock",
        source_name="Weather alert rules",
        is_mock=current.get("is_mock", False),
        cache_status=current.get("cache_status", "computed"),
        last_updated=current.get("last_updated"),
        confidence=0.72 if not current.get("is_mock") else 0.42,
    )


@router.get("/recommendations/{region}")
async def get_weather_activity_recommendations(
    region: str,
    crop_name: str | None = Query(default=None),
    growth_stage: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    current = weather_service.get_current_weather(db, region)
    forecast = weather_service.get_forecast(db, region, 7)
    hourly = weather_service.get_hourly_forecast(db, region, 168)
    recommendations = weather_service.build_activity_recommendations(
        current,
        forecast,
        hourly,
        crop_name=crop_name,
        growth_stage=growth_stage,
    )
    return api_response(
        {"recommendations": recommendations, "total": len(recommendations), "region": region},
        source="ai_generated" if not current.get("is_mock") else "mock",
        source_name="Weather recommendation rules",
        is_mock=current.get("is_mock", False),
        cache_status=current.get("cache_status", "computed"),
        last_updated=current.get("last_updated"),
        confidence=0.72 if not current.get("is_mock") else 0.42,
    )


@router.post("/", response_model=WeatherResponse)
async def create_weather(request: WeatherCreateRequest, db: Session = Depends(get_db)):
    return weather_service.create_weather(db, request)
