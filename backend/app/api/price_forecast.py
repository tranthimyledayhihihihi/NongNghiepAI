from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.price_forecast_schema import PricePredictionRequest, PricePredictionResponse
from app.services.price_forecast_service import price_forecast_service

router = APIRouter(prefix="/api/price-forecast", tags=["price-forecast"])


@router.post("/predict", response_model=PricePredictionResponse)
async def predict_price(request: PricePredictionRequest, db: Session = Depends(get_db)):
    return price_forecast_service.predict_price(db, request)
