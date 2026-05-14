from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.market_news_service import market_news_service

router = APIRouter(prefix="/api/market-news", tags=["market-news"])


@router.get("/")
async def get_market_news(
    limit: int = 20,
    crop_name: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
):
    return market_news_service.get_latest(db, limit=limit, crop_name=crop_name, region=region)


@router.post("/refresh")
async def refresh_market_news():
    return market_news_service.refresh_news()
