import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api import alert, crops, harvest, market, price_forecast, pricing, quality, weather
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

app.include_router(crops.router)
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
            "health": "/health",
            "db_test": "/db-test",
            "crops_list": "/api/crops",
            "crop_detail": "/api/crops/{crop_id}",
            "crop_search": "/api/crops/search?keyword={keyword}",
            "harvest_forecast": "/api/harvest/forecast",
            "harvest_history": "/api/harvest/history/{user_id}",
            "harvest_schedules": "/api/harvest/schedules/{user_id}",
            "quality_check": "/api/quality/check",
            "quality_grades": "/api/quality/grades",
            "quality_history": "/api/quality/history/{user_id}",
            "quality_detail": "/api/quality/{record_id}",
            "pricing_current": "/api/pricing/current?crop_name={crop_name}&region={region}",
            "pricing_suggest": "/api/pricing/suggest",
            "pricing_forecast_legacy": "/api/pricing/forecast",
            "pricing_history": "/api/pricing/history/{crop_name}/{region}",
            "pricing_compare_regions": "/api/pricing/compare-regions/{crop_name}",
            "price_forecast": "/api/price-forecast/predict",
            "market_channels": "/api/market/channels",
            "market_suggest": "/api/market/suggest",
            "market_history": "/api/market/history/{user_id}",
            "alert_create": "/api/alert/create",
            "alert_list": "/api/alert/list",
            "alert_detail": "/api/alert/{alert_id}",
            "alert_deactivate": "/api/alert/{alert_id}",
            "weather_current": "/api/weather/current/{region}",
            "weather_create": "/api/weather/",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/db-test")
async def db_test():
    db = database.SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_url": database.active_database_url,
            "result": result,
        }
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {exc}") from exc
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
