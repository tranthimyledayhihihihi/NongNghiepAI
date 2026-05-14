from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.ingestion import DataIngestionLog


def start_ingestion_log(db: Session, job_name: str, source_name: str | None = None) -> DataIngestionLog | None:
    log = DataIngestionLog(JobName=job_name, SourceName=source_name, StartedAt=datetime.now(), Status="running")
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except SQLAlchemyError:
        db.rollback()
        return None


def finish_ingestion_log(
    db: Session,
    log: DataIngestionLog | None,
    *,
    status: str,
    records_fetched: int = 0,
    records_saved: int = 0,
    error_message: str | None = None,
) -> None:
    if log is None:
        return
    try:
        log.FinishedAt = datetime.now()
        log.Status = status
        log.RecordsFetched = records_fetched
        log.RecordsSaved = records_saved
        log.ErrorMessage = error_message
        db.add(log)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
