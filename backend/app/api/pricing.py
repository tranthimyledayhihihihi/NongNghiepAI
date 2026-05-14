from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.price_schema import (
    PriceForecastRequest,
    PriceForecastResponse,
    PriceRequest,
    PriceResponse,
    PricingSuggestRequest,
    PricingSuggestResponse,
)
from app.services.pricing_service import pricing_service

router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.post("/current", response_model=PriceResponse)
async def get_current_price(request: PriceRequest, db: Session = Depends(get_db)):
    return pricing_service.get_current_price(
        db,
        request.crop_name,
        request.region,
        request.quality_grade,
    )


@router.get("/current", response_model=PriceResponse)
async def get_current_price_query(
    crop_name: str,
    region: str,
    quality_grade: str = "grade_1",
    db: Session = Depends(get_db),
):
    return pricing_service.get_current_price(db, crop_name, region, quality_grade)


@router.post("/suggest", response_model=PricingSuggestResponse)
async def suggest_price(request: PricingSuggestRequest, db: Session = Depends(get_db)):
    return pricing_service.suggest_price(db, request)


@router.post("/forecast", response_model=PriceForecastResponse)
async def forecast_price(request: PriceForecastRequest):
    return pricing_service.forecast_price(request.crop_name, request.region, request.days)


@router.get("/history/{crop_name}/{region}")
async def get_price_history(crop_name: str, region: str, days: int = 30, db: Session = Depends(get_db)):
    return {
        "crop_name": crop_name,
        "region": region,
        "history": pricing_service.get_price_history(db, crop_name, region, days),
    }


@router.get("/weather-forecast")
async def weather_price_forecast(
    crop_name: str,
    region: str,
    quality_grade: str = "grade_1",
    db: Session = Depends(get_db),
):
    """
    Dự báo giá điều chỉnh theo thời tiết 7 ngày tới.
    Trả về giá gốc, hệ số thời tiết, giá đề xuất sau điều chỉnh, và chi tiết từng ngày.
    """
    from app.services.weather_pricing_service import get_weather_adjusted_pricing

    current = pricing_service.get_current_price(
        db, crop_name, region, quality_grade, include_weather=False
    )
    base_price = float(current["current_price"])

    weather_info = get_weather_adjusted_pricing(db, crop_name, region, base_price)
    multiplier = pricing_service.quality_multipliers.get(quality_grade, 1.0)

    return {
        "crop_name":   crop_name,
        "region":      region,
        "quality_grade": quality_grade,
        "base_price":  round(base_price * multiplier, 2),
        "weather_adjusted_price": round(weather_info["adjusted_price"] * multiplier, 2),
        "weather_factor":         weather_info["weather_factor"],
        "price_change_pct":       weather_info["price_change_pct"],
        "weather_summary":        weather_info["weather_summary"],
        "weather_explanation":    weather_info["weather_explanation"],
        "crop_category":          weather_info["crop_category"],
        "forecast_days":          weather_info["forecast_days"],
        "forecast":               weather_info["forecast"],
        "unit": "VND/kg",
    }


@router.get("/compare-regions/{crop_name}")
async def compare_regions(crop_name: str, region: str = "Ha Noi", db: Session = Depends(get_db)):
    suggestion = pricing_service.suggest_price(
        db,
        PricingSuggestRequest(
            crop_name=crop_name,
            region=region,
            quantity=1,
            quality_grade="grade_1",
        ),
    )
    return {"crop_name": crop_name, "regions": suggestion["nearby_region_prices"]}
