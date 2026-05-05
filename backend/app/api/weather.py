from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.weather_schema import WeatherCreateRequest, WeatherResponse
from app.services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current/{region}", response_model=WeatherResponse)
async def get_current_weather(region: str, db: Session = Depends(get_db)):
    return weather_service.get_current_weather(db, region)


@router.post("/", response_model=WeatherResponse)
async def create_weather(request: WeatherCreateRequest, db: Session = Depends(get_db)):
    return weather_service.create_weather(db, request)
