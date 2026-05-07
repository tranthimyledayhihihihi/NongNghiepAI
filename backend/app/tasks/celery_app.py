try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional for MVP
    Celery = None

from app.core.config import settings


celery_app = (
    Celery(
        "agri_ai",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=[
            "app.tasks.alert_tasks",
            "app.tasks.crawler_tasks",
            "app.tasks.forecast_tasks",
            "app.tasks.price_tasks",
        ],
    )
    if Celery
    else None
)
