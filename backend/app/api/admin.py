from fastapi import APIRouter

from app.services.market_news_service import market_news_service
from app.tasks.alert_tasks import check_price_alerts_task
from app.tasks.crawler_tasks import crawl_sources_task
from app.tasks.forecast_tasks import refresh_harvest_forecasts_task

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingestion/run")
async def run_ingestion(job_name: str, source_name: str | None = None, crop_filter: str | None = None):
    if job_name == "price_crawler":
        return crawl_sources_task(source_name=source_name, crop_filter=crop_filter)
    if job_name == "market_news":
        return market_news_service.refresh_news()
    if job_name == "price_alerts":
        return check_price_alerts_task()
    if job_name == "harvest_forecasts":
        return refresh_harvest_forecasts_task()
    return {
        "status": "failed",
        "error": "Unsupported job_name",
        "supported_jobs": ["price_crawler", "market_news", "price_alerts", "harvest_forecasts"],
    }
