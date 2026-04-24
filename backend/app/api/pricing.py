from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.price import MarketPrice, PriceHistory
from app.schemas.price_schema import PriceRequest, PriceResponse, PriceForecastRequest, PriceForecastResponse
from ai_models.price_forecast.price_model import price_forecast_model

router = APIRouter(prefix="/api/pricing", tags=["pricing"])

@router.post("/current", response_model=PriceResponse)
async def get_current_price(request: PriceRequest, db: Session = Depends(get_db)):
    """
    Lấy giá hiện tại của nông sản
    
    - Kiểm tra cache Redis trước
    - Nếu không có, query từ database
    - Phân tích xu hướng giá
    """
    cache_key = f"price:{request.crop_name}:{request.region}:{request.quality_grade}"
    
    # Check cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return PriceResponse(**cached_data)
    
    # Query from database
    latest_price = db.query(MarketPrice).filter(
        MarketPrice.crop_name == request.crop_name,
        MarketPrice.region == request.region,
        MarketPrice.quality_grade == request.quality_grade
    ).order_by(desc(MarketPrice.date)).first()
    
    if not latest_price:
        # Return mock data if no data in database
        response_data = {
            "crop_name": request.crop_name,
            "region": request.region,
            "current_price": 20000.0,
            "quality_grade": request.quality_grade,
            "price_trend": "stable",
            "last_updated": datetime.now()
        }
    else:
        # Analyze trend
        trend = _analyze_price_trend(db, request.crop_name, request.region)
        
        response_data = {
            "crop_name": latest_price.crop_name,
            "region": latest_price.region,
            "current_price": latest_price.price_per_kg,
            "quality_grade": latest_price.quality_grade,
            "price_trend": trend,
            "last_updated": latest_price.created_at
        }
    
    # Cache for 1 hour
    redis_client.set(cache_key, response_data, expire=3600)
    
    return PriceResponse(**response_data)

@router.post("/forecast", response_model=PriceForecastResponse)
async def forecast_price(request: PriceForecastRequest):
    """
    Dự báo giá nông sản trong N ngày tới
    
    - Sử dụng AI model để dự báo
    - Phân tích xu hướng
    - Đưa ra khuyến nghị
    """
    try:
        forecast = price_forecast_model.predict(
            crop_name=request.crop_name,
            region=request.region,
            days=request.days
        )
        
        return PriceForecastResponse(**forecast)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự báo giá: {str(e)}")

@router.get("/history/{crop_name}/{region}")
async def get_price_history(
    crop_name: str,
    region: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Lấy lịch sử giá trong N ngày qua"""
    start_date = datetime.now() - timedelta(days=days)
    
    history = db.query(PriceHistory).filter(
        PriceHistory.crop_name == crop_name,
        PriceHistory.region == region,
        PriceHistory.date >= start_date.date()
    ).order_by(PriceHistory.date).all()
    
    if not history:
        # Return mock data
        return {
            "crop_name": crop_name,
            "region": region,
            "history": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    "avg_price": 20000 + (i * 100),
                    "min_price": 18000 + (i * 100),
                    "max_price": 22000 + (i * 100)
                }
                for i in range(days, 0, -1)
            ]
        }
    
    return {
        "crop_name": crop_name,
        "region": region,
        "history": [
            {
                "date": h.date.strftime('%Y-%m-%d'),
                "avg_price": h.avg_price,
                "min_price": h.min_price,
                "max_price": h.max_price
            }
            for h in history
        ]
    }

@router.get("/compare-regions/{crop_name}")
async def compare_regions(crop_name: str, db: Session = Depends(get_db)):
    """So sánh giá giữa các khu vực"""
    latest_prices = db.query(MarketPrice).filter(
        MarketPrice.crop_name == crop_name
    ).order_by(desc(MarketPrice.date)).limit(10).all()
    
    if not latest_prices:
        # Mock data
        regions = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Cần Thơ"]
        return {
            "crop_name": crop_name,
            "regions": [
                {
                    "region": region,
                    "price": 20000 + (i * 1000),
                    "date": datetime.now().strftime('%Y-%m-%d')
                }
                for i, region in enumerate(regions)
            ]
        }
    
    region_prices = {}
    for price in latest_prices:
        if price.region not in region_prices:
            region_prices[price.region] = {
                "region": price.region,
                "price": price.price_per_kg,
                "date": price.date.strftime('%Y-%m-%d')
            }
    
    return {
        "crop_name": crop_name,
        "regions": list(region_prices.values())
    }

def _analyze_price_trend(db: Session, crop_name: str, region: str) -> str:
    """Analyze price trend from recent history"""
    recent_prices = db.query(MarketPrice).filter(
        MarketPrice.crop_name == crop_name,
        MarketPrice.region == region
    ).order_by(desc(MarketPrice.date)).limit(7).all()
    
    if len(recent_prices) < 2:
        return "stable"
    
    prices = [p.price_per_kg for p in reversed(recent_prices)]
    first_half = sum(prices[:len(prices)//2]) / (len(prices)//2)
    second_half = sum(prices[len(prices)//2:]) / (len(prices) - len(prices)//2)
    
    change = ((second_half - first_half) / first_half) * 100
    
    if change > 5:
        return "increasing"
    elif change < -5:
        return "decreasing"
    else:
        return "stable"
