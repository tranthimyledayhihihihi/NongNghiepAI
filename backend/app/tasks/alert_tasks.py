import asyncio
import logging
import os

from app.core.database import SessionLocal
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.services.alert_service import alert_service
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def check_price_alerts_task(user_id: int | None = None) -> dict:
    db = SessionLocal()
    log = start_ingestion_log(db, "check_price_alerts", "database")
    try:
        user = None
        if user_id:
            from app.models.user import User

            user = db.query(User).filter(User.UserID == user_id).first()
        price_triggered = alert_service.check_and_trigger_alerts(db, user)
        weather_triggered = alert_service.check_and_trigger_weather_alerts(db, user)
        triggered = price_triggered + weather_triggered
        finish_ingestion_log(
            db,
            log,
            status="success",
            records_fetched=len(alert_service.list_price_alerts(db, user)),
            records_saved=len(triggered),
        )
        return {"status": "success", "triggered_count": len(triggered), "triggered": triggered}
    except Exception as exc:
        finish_ingestion_log(db, log, status="failed", error_message=str(exc))
        return {"status": "failed", "error": str(exc)}
    finally:
        db.close()


def check_price_alerts() -> dict:
    return check_price_alerts_task()


if celery_app:
    celery_check_price_alerts_task = celery_app.task(name="check_price_alerts_task")(check_price_alerts_task)
    celery_check_active_alerts_task = celery_app.task(name="app.tasks.alert_tasks.check_active_alerts")(check_price_alerts_task)


async def auto_alert_loop() -> None:
    """FastAPI fallback scheduler for deployments that do not run Celery Beat."""
    interval = int(os.getenv("ALERT_CHECK_INTERVAL_SECONDS", "3600"))
    run_on_start = os.getenv("ALERT_CHECK_ON_STARTUP", "false").lower() == "true"
    logger.info("[Alerts] Auto-alert loop enabled, interval=%ss", interval)
    if run_on_start:
        await asyncio.to_thread(check_price_alerts_task)
    while True:
        await asyncio.sleep(interval)
        result = await asyncio.to_thread(check_price_alerts_task)
        logger.info("[Alerts] Scheduled evaluation result: %s", result)
