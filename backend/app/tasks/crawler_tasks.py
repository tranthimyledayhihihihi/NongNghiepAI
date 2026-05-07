from datetime import date

from app.tasks.price_tasks import refresh_market_prices_task
from app.tasks.celery_app import celery_app


def crawl_sources_task(
    source_name: str | None = None,
    run_date: date | None = None,
    crop_filter: str | None = None,
) -> dict:
    result = refresh_market_prices_task(source_name=source_name, crop_filter=crop_filter)
    return {
        **result,
        "run_date": (run_date or date.today()).isoformat(),
        "job_name": "crawl_sources",
    }


def run_price_crawler() -> dict:
    return crawl_sources_task()


if celery_app:
    celery_crawl_sources_task = celery_app.task(name="crawl_sources_task")(crawl_sources_task)
