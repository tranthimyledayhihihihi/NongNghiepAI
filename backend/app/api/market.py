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
    text = f"{payload.title} {payload.summary}".lower()
    crops = [crop for crop in ["lua", "gao", "ca phe", "ho tieu", "sau rieng", "thanh long", "rau", "ca chua"] if crop in text]
    if payload.crop:
        crops.append(payload.crop)
    regions = [region for region in ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho", "Lam Dong", "Dak Lak"] if region.lower() in text]
    if payload.region:
        regions.append(payload.region)
    negative_words = ["giam", "thua", "dich", "bao", "han", "rut", "cam", "khung hoang"]
    positive_words = ["tang", "xuat khau", "don hang", "duoc gia", "co hoi", "ky ket"]
    score = sum(word in text for word in positive_words) - sum(word in text for word in negative_words)
    impact = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {
        "news_title": payload.title,
        "affected_crops": sorted(set(crops)),
        "affected_regions": sorted(set(regions)),
        "impact": impact,
        "impact_score": 0.68 if impact != "neutral" else 0.5,
        "price_effect": "likely_increase" if impact == "positive" else "likely_decrease" if impact == "negative" else "stable",
        "summary": payload.summary or payload.title,
        "recommendation": "Theo doi them va tao canh bao gia neu tin nay lien quan den cay trong chinh.",
        "source": "mock",
        "source_name": "Rule-based market news analyzer",
        "is_mock": True,
        "confidence": 0.58,
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
    data = market_news_service.get_latest(db, limit=limit, crop_name=crop, region=region)
    return api_response(
        data,
        source="realtime_api" if data.get("is_realtime") else "database",
        source_name="RSS market news cache",
        is_realtime=data.get("is_realtime", False),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        confidence=0.7,
    )


@router.get("/prices")
async def get_market_prices(
    crop: str = Query(default="lua"),
    region: str = Query(default="Ha Noi"),
    db: Session = Depends(get_db),
):
    data = pricing_service.get_current_price(db, crop, region)
    return api_response(
        data,
        source=data.get("source", "database"),
        source_name=data.get("source_name"),
        is_mock=data.get("is_mock", False),
        cache_status=data.get("cache_status", "from_db"),
        last_updated=data.get("last_updated"),
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
    price = pricing_service.build_pricing_engine(db, crop_name=crop, region=region)
    data = {
        "crop": crop,
        "crop_name": crop,
        "region": region,
        "trend": price.get("trend"),
        "confidence": price.get("confidence", 0.0),
        "evidence": price.get("reasons", []),
        "forecast": price.get("forecast", []),
        "source": price.get("source"),
        "source_name": "Market trend engine",
        "is_mock": price.get("is_mock", False),
        "cache_status": price.get("cache_status", "computed"),
    }
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
    trend = pricing_service.build_pricing_engine(db, crop_name=crop, region=region)
    data = {
        "opportunities": [
            {
                "title": "Batch selling opportunity",
                "crop": crop,
                "region": region,
                "reason": trend.get("recommendation"),
                "expected_price": trend.get("suggested_price"),
                "confidence": trend.get("confidence", 0.0),
            }
        ],
        "source": trend.get("source"),
        "source_name": "AI Market Intelligence",
        "is_mock": trend.get("is_mock", False),
        "confidence": trend.get("confidence", 0.0),
    }
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
    trend = pricing_service.build_pricing_engine(db, crop_name=crop, region=region)
    risk = "high" if trend.get("trend") == "decreasing" else "medium" if trend.get("is_mock") else "low"
    data = {
        "risks": [
            {
                "title": "Price volatility",
                "severity": risk,
                "crop": crop,
                "region": region,
                "recommendation": "Create price alert and avoid selling all stock at one time.",
            }
        ],
        "source": trend.get("source"),
        "source_name": "AI Market Risk Engine",
        "is_mock": trend.get("is_mock", False),
        "confidence": trend.get("confidence", 0.0),
    }
    return api_response(
        data,
        source="ai_generated" if not data["is_mock"] else "mock",
        source_name=data["source_name"],
        is_mock=data["is_mock"],
        confidence=data["confidence"],
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
