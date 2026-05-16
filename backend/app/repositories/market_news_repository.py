from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.market_news import MarketNews


def upsert_market_news(db: Session, records: list[dict]) -> dict:
    saved = 0
    updated = 0
    unique_records = {}
    for record in records:
        source_url = record.get("source_url")
        if source_url:
            unique_records[source_url] = record

    for record in unique_records.values():
        try:
            row = db.query(MarketNews).filter(MarketNews.SourceURL == record["source_url"]).first()
            if row is None:
                row = MarketNews(SourceURL=record["source_url"])
                db.add(row)
                saved += 1
            else:
                updated += 1
            row.Title = record["title"]
            row.Summary = record.get("summary")
            row.SourceName = record.get("source_name")
            row.PublishedAt = record.get("published_at")
            row.Region = record.get("region")
            row.Sentiment = record.get("sentiment")
        except Exception:
            continue
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    return {"records_saved": saved, "records_updated": updated}


def list_market_news(db: Session, limit: int = 20, crop_name: str | None = None, region: str | None = None) -> list[MarketNews]:
    try:
        query = db.query(MarketNews)
        if region:
            query = query.filter(MarketNews.Region == region)
        return query.order_by(desc(MarketNews.PublishedAt), desc(MarketNews.CreatedAt)).limit(limit).all()
    except SQLAlchemyError:
        db.rollback()
        return []
