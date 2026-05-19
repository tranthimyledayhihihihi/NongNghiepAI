from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.response import api_response
from app.core.database import get_db
from app.schemas.price_forecast_schema import PricePredictionRequest
from app.services.price_forecast_service import price_forecast_service

router = APIRouter(prefix="/api/price-forecast", tags=["price-forecast"])


@router.post("/predict")
async def predict_price(request: PricePredictionRequest, db: Session = Depends(get_db)):
    data = price_forecast_service.predict_price(db, request)
    return api_response(
        data,
        source=data.get("source", "cache"),
        source_name=data.get("source_name"),
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "fresh_cache"),
        fetched_at=data.get("fetched_at"),
        last_updated=data.get("last_updated"),
        confidence=data.get("confidence", 0.0),
        message=data.get("error_message") or "OK",
    )
