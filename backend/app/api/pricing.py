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
