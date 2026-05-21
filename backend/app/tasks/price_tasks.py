from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.services.price_aggregator_service import price_aggregator_service
from app.tasks.celery_app import celery_app


def refresh_market_prices_task(source_name: str | None = None, crop_filter: str | None = None) -> dict:
    db = SessionLocal()
    log = start_ingestion_log(db, "refresh_market_prices", source_name or "WinMart")
    try:
        result = price_aggregator_service.refresh_prices(db, crop_name=crop_filter, source_name=source_name or "WinMart")
        records_fetched = int(result.get("records_fetched") or 0)
        for record in result.get("records", []) or []:
            redis_client.delete(
                f"price:{record.get('crop_name')}:{record.get('region')}:{record.get('quality_grade', 'grade_1')}"
            )
        status = "success" if not result.get("errors") else "partial_success"
        finish_ingestion_log(
            db,
            log,
            status=status,
            records_fetched=records_fetched,
            records_saved=int(result.get("records_saved") or 0) + int(result.get("records_updated") or 0),
            error_message="; ".join(result.get("errors") or []) if result.get("errors") else None,
        )
        return {
            "status": status,
            "source_name": result.get("source_name") or source_name or "WinMart",
            "records_fetched": records_fetched,
            **result,
        }
    except Exception as exc:
        finish_ingestion_log(db, log, status="failed", error_message=str(exc))
        return {"status": "failed", "source_name": source_name, "error": str(exc)}
    finally:
        db.close()


def refresh_market_prices() -> dict:
    return refresh_market_prices_task()


if celery_app:
    celery_refresh_market_prices_task = celery_app.task(name="refresh_market_prices_task")(refresh_market_prices_task)
