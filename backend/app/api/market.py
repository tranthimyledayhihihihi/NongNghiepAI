from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.schemas.market_schema import MarketSuggestRequest, MarketSuggestResponse
from app.services.market_news_service import market_news_service
from app.services.market_service import market_service
from app.services.pricing_service import pricing_service

router = APIRouter(prefix="/api/market", tags=["market"])


class NewsAnalysisRequest(BaseModel):
    title: str = ""
    summary: str = ""
    crop: str | None = None
    region: str | None = None


def _analyze_news_payload(payload: NewsAnalysisRequest) -> dict:
    impact = market_news_service.analyze_news_impact(payload.model_dump())
    return {
        "news_title": payload.title,
        "affected_crops": [payload.crop] if payload.crop else [],
        "affected_regions": [payload.region] if payload.region else [],
        "summary": payload.summary or payload.title,
        "recommendation": "Theo doi them va tao canh bao gia neu tin nay lien quan den cay trong chinh.",
        **impact,
    }


@router.get("/channels")
async def get_market_channels(region: str | None = None, db: Session = Depends(get_db)):
    data = market_service.get_channels(db, region)
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name="MarketChannels DB" if not data.get("is_mock") else "Market channel fallback",
        is_mock=data.get("is_mock", False),
        cache_status="from_db" if not data.get("is_mock") else "mock",
        confidence=0.72 if not data.get("is_mock") else 0.45,
    )


@router.get("/news")
async def get_market_news(
    limit: int = Query(default=10, ge=1, le=50),
    crop: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
):
    data = market_news_service.get_market_news(db, limit=limit, crop=crop, region=region)
    return api_response(
        data,
        source=data.get("source", "cached"),
        source_name=data.get("source_name", "RSS market news cache"),
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        confidence=0.7,
    )


@router.get("/prices")
async def get_market_prices(
    crop: str = Query(default="lua"),
    region: str = Query(default="Ha Noi"),
    quality_grade: str = Query(default="grade_1"),
    db: Session = Depends(get_db),
):
    data = pricing_service.get_current_price(db, crop, region, quality_grade, include_weather=False)
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        last_updated=data.get("last_updated"),
        fetched_at=data.get("fetched_at"),
        confidence=data.get("confidence", 0.0),
    )


@router.post("/analyze-news")
async def analyze_market_news(request: NewsAnalysisRequest):
    data = _analyze_news_payload(request)
    return api_response(
        data,
        source=data.get("source", "mock"),
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", True),
        confidence=data.get("confidence", 0.0),
    )


@router.get("/trends")
async def get_market_trends(
    crop: str = Query(default="lua"),
    region: str = Query(default="Ha Noi"),
    db: Session = Depends(get_db),
):
    data = market_news_service.get_market_trends(db, crop=crop, region=region)
    return api_response(
        data,
        source="ai_generated" if not data["is_mock"] else "mock",
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        cache_status=data["cache_status"],
        confidence=data["confidence"],
    )


@router.get("/opportunities")
async def get_market_opportunities(
    crop: str = Query(default="lua"),
    region: str = Query(default="Ha Noi"),
    db: Session = Depends(get_db),
):
    data = market_news_service.get_market_opportunities(db, crop=crop, region=region)
    return api_response(
        data,
        source="ai_generated" if not data["is_mock"] else "mock",
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        confidence=data["confidence"],
    )


@router.get("/risks")
async def get_market_risks(
    crop: str = Query(default="lua"),
    region: str = Query(default="Ha Noi"),
    db: Session = Depends(get_db),
):
    data = market_news_service.get_market_risks(db, crop=crop, region=region)
    return api_response(
        data,
        source="ai_generated" if not data["is_mock"] else "mock",
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        confidence=data["confidence"],
    )


@router.post("/analyze")
async def analyze_market(
    request: MarketSuggestRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = pricing_service.analyze_market(
        db,
        crop_name=request.crop_name,
        region=request.region,
        quantity=request.quantity,
        quality_grade=request.quality_grade,
    )
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "computed"),
        last_updated=data.get("fetched_at") or data.get("last_updated"),
        confidence=data.get("confidence_score", data.get("confidence", 0.0)),
    )


@router.post("/suggest")
async def suggest_market_channel(
    request: MarketSuggestRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    data = market_service.suggest_market(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name="AI Market Channel Engine",
        is_mock=data.get("is_mock", False),
        cache_status="computed",
        confidence=0.7 if not data.get("is_mock") else 0.45,
    )


@router.get("/history/{user_id}")
async def get_market_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = market_service.get_history(db, user_id, limit)
    return api_response(
        {"user_id": user_id, "total": len(history), "history": history},
        source="database",
        source_name="MarketRecommendations DB",
        cache_status="from_db",
        confidence=0.7,
    )


@router.get("/demand/{crop_name}")
async def get_market_demand(crop_name: str):
    return api_response(
        {"crop_name": crop_name, "demand": "medium"},
        source="mock",
        source_name="Demand demo fallback",
        is_mock=True,
        confidence=0.4,
    )
