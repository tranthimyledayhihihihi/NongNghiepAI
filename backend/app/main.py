import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alert, harvest, market, price_forecast, pricing, quality, weather
from app.core.config import settings
from app.core import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.init_db()
        print(f"Database initialized: {database.active_database_url}")
    except Exception as exc:
        print(f"Database initialization warning: {exc}")
    yield

app = FastAPI(
    title="AgriAI Backend",
    description="API for harvest forecast, agricultural pricing, quality check, market suggestion and alerts.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(harvest.router)
app.include_router(quality.router)
app.include_router(pricing.router)
app.include_router(price_forecast.router)
app.include_router(market.router)
app.include_router(alert.router)
app.include_router(weather.router)

os.makedirs(os.path.join(settings.UPLOAD_DIR, "quality_check"), exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "AgriAI API Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "harvest_forecast": "/api/harvest/forecast",
            "quality_check": "/api/quality/check",
            "quality_grades": "/api/quality/grades",
            "pricing_current": "/api/pricing/current",
            "pricing_suggest": "/api/pricing/suggest",
            "pricing_forecast_legacy": "/api/pricing/forecast",
            "pricing_history": "/api/pricing/history/{crop_name}/{region}",
            "pricing_compare_regions": "/api/pricing/compare-regions/{crop_name}",
            "price_forecast": "/api/price-forecast/predict",
            "market_channels": "/api/market/channels",
            "market_suggest": "/api/market/suggest",
            "alert_create": "/api/alert/create",
            "alert_list": "/api/alert/list",
            "alert_deactivate": "/api/alert/{alert_id}",
            "weather_current": "/api/weather/current/{region}",
            "weather_create": "/api/weather/",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
