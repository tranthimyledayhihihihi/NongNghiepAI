from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.price import MarketPrice, PriceHistory
from ..core.redis_client import redis_client

class PricingService:
    """Service for pricing operations"""
    
    @staticmethod
    def get_current_price(
        db: Session,
        crop_name: str,
        region: str,
        quality_grade: str = "grade_1"
    ) -> Optional[Dict]:
        """Get current price for a crop in a region"""
        
        # Check cache first
        cache_key = f"price:{crop_name}:{region}:{quality_grade}"
        cached = redis_client.get(cache_key)
        if cached:
            return cached
        
        # Query database
        latest_price = db.query(MarketPrice).filter(
            MarketPrice.crop_name == crop_name,
            MarketPrice.region == region,
            MarketPrice.quality_grade == quality_grade
        ).order_by(desc(MarketPrice.date)).first()
        
        if not latest_price:
            return None
        
        result = {
            "crop_name": latest_price.crop_name,
            "region": latest_price.region,
            "current_price": latest_price.price_per_kg,
            "quality_grade": latest_price.quality_grade,
            "last_updated": latest_price.created_at.isoformat()
        }
        
        # Cache for 1 hour
        redis_client.set(cache_key, result, expire=3600)
        
        return result
    
    @staticmethod
    def get_price_history(
        db: Session,
        crop_name: str,
        region: str,
        days: int = 30
    ) -> List[Dict]:
        """Get price history for a crop"""
        start_date = datetime.now() - timedelta(days=days)
        
        history = db.query(PriceHistory).filter(
            PriceHistory.crop_name == crop_name,
            PriceHistory.region == region,
            PriceHistory.date >= start_date.date()
        ).order_by(PriceHistory.date).all()
        
        return [
            {
                "date": h.date.isoformat(),
                "avg_price": h.avg_price,
                "min_price": h.min_price,
                "max_price": h.max_price
            }
            for h in history
        ]
    
    @staticmethod
    def analyze_price_trend(
        db: Session,
        crop_name: str,
        region: str
    ) -> str:
        """Analyze price trend"""
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

pricing_service = PricingService()
