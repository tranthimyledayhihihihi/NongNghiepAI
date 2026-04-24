from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import init_db
from .api import quality, pricing
import os

# Create FastAPI app
app = FastAPI(
    title="AgriAI - Hệ thống AI hỗ trợ nông dân",
    description="API cho dự báo thu hoạch, định giá nông sản, và kiểm tra chất lượng",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quality.router)
app.include_router(pricing.router)

# Import additional routers (Phase 2 features - basic endpoints)
from .api import alert, forecast, harvest, market

app.include_router(alert.router)
app.include_router(forecast.router)
app.include_router(harvest.router)
app.include_router(market.router)

# Create upload directories
os.makedirs("backend/uploads/quality_check", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting AgriAI Backend...")
    try:
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")
    print("✓ Server ready!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AgriAI API Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "quality_check": "/api/quality/check",
            "current_price": "/api/pricing/current",
            "price_forecast": "/api/pricing/forecast",
            "price_history": "/api/pricing/history/{crop_name}/{region}",
            "compare_regions": "/api/pricing/compare-regions/{crop_name}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
