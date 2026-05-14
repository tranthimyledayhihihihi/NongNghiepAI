from app.core.database import SessionLocal
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.services.harvest_service import harvest_service
from app.tasks.celery_app import celery_app


def refresh_harvest_forecasts_task() -> dict:
    db = SessionLocal()
    log = start_ingestion_log(db, "refresh_harvest_forecasts", "database")
    updated = []
    try:
        from app.models.crop import Crop
        from app.models.harvest import HarvestSchedule

        schedules = db.query(HarvestSchedule).filter(HarvestSchedule.Status != "Da thu hoach").limit(200).all()
        for schedule in schedules:
            crop = db.query(Crop).filter(Crop.CropID == schedule.CropID).first()
            if not crop:
                continue
            result = harvest_service.predict_harvest_date(
                db,
                crop_name=crop.CropName,
                planting_date=schedule.PlantingDate,
                region=schedule.Region,
                user_id=schedule.UserID,
            )
            updated.append({"schedule_id": schedule.ScheduleID, "expected_harvest_date": result["expected_harvest_date"]})
        finish_ingestion_log(db, log, status="success", records_fetched=len(schedules), records_saved=len(updated))
        return {"status": "success", "updated_count": len(updated), "updated": updated}
    except Exception as exc:
        finish_ingestion_log(db, log, status="failed", error_message=str(exc))
        return {"status": "failed", "error": str(exc)}
    finally:
        db.close()


def refresh_forecasts() -> dict:
    return refresh_harvest_forecasts_task()


if celery_app:
    celery_refresh_harvest_forecasts_task = celery_app.task(name="refresh_harvest_forecasts_task")(refresh_harvest_forecasts_task)
