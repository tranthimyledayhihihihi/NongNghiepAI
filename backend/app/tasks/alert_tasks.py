from app.core.database import SessionLocal
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.services.alert_service import alert_service
from app.tasks.celery_app import celery_app


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
