from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.response import api_response
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
    data = market_news_service.get_market_news(db, limit=limit, crop=crop_name, region=region)
    return api_response(
        data,
        source=data.get("source", "cached"),
        source_name=data.get("source_name") or "RSS market news cache",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        confidence=0.7,
    )


@router.post("/refresh")
async def refresh_market_news():
    data = market_news_service.refresh_news()
    return api_response(
        data,
        source="realtime_api",
        source_name="RSS market news refresh",
        is_mock=False,
        confidence=0.7 if data.get("status") == "success" else 0.0,
    )
