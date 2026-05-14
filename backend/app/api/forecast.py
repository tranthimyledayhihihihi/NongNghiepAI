from fastapi import APIRouter

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

# Forecast endpoints - some features in Phase 2

@router.get("/weather/{region}")
async def get_weather_forecast(region: str):
    """Get weather forecast - Phase 2"""
    return {
        "message": "Weather forecast feature coming in Phase 2",
        "region": region,
        "forecast": []
    }

@router.get("/market-trends/{crop_name}")
async def get_market_trends(crop_name: str):
    """Get market trends - Phase 2"""
    return {
        "message": "Market trends feature coming in Phase 2",
        "crop_name": crop_name,
        "trends": []
    }
