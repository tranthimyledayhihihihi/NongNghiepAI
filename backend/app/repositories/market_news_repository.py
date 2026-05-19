from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.market_news import MarketNews
from app.repositories.common import normalize_text


def upsert_market_news(db: Session, records: list[dict]) -> dict:
    saved = 0
    updated = 0
    unique_records = {}
    for index, record in enumerate(records):
        source_url = record.get("source_url") or record.get("url")
        if not source_url:
            continue
        record["source_url"] = source_url
        record.setdefault("url", source_url)
        if source_url:
            unique_records[source_url] = record

    for record in unique_records.values():
        try:
            source_url = record.get("source_url") or record.get("url")
            row = db.query(MarketNews).filter(MarketNews.SourceURL == source_url).first() if source_url else None
            if row is None:
                row = MarketNews(SourceURL=source_url)
                db.add(row)
                saved += 1
            else:
                updated += 1
            row.Title = record["title"]
            row.Summary = record.get("summary")
            row.Content = record.get("content")
            row.URL = record.get("url") or source_url
            row.SourceName = record.get("source_name")
            row.PublishedAt = record.get("published_at")
            row.FetchedAt = record.get("fetched_at") or datetime.utcnow()
            row.Region = record.get("region")
            row.CropTags = record.get("crop_tags") or []
            row.RegionTags = record.get("region_tags") or ([record.get("region")] if record.get("region") else [])
            row.Sentiment = record.get("sentiment")
            row.ImpactLevel = record.get("impact_level")
            row.ImpactScore = record.get("impact_score")
            row.IsRealtime = bool(record.get("is_realtime", False))
            row.IsMock = bool(record.get("is_mock", False))
            row.Metadata = record.get("metadata")
        except Exception:
            continue
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    return {"records_saved": saved, "records_updated": updated}


def list_market_news(
    db: Session,
    limit: int = 20,
    crop_name: str | None = None,
    region: str | None = None,
    since: datetime | None = None,
) -> list[MarketNews]:
    try:
        query = db.query(MarketNews)
        if since:
            query = query.filter(MarketNews.PublishedAt.isnot(None), MarketNews.PublishedAt >= since)
        rows = query.order_by(desc(MarketNews.PublishedAt), desc(MarketNews.CreatedAt)).limit(limit * 4).all()
        if crop_name or region:
            crop_key = normalize_text(crop_name)
            region_key = normalize_text(region)
            filtered = []
            for row in rows:
                crop_tags = _as_list(row.CropTags)
                region_tags = _as_list(row.RegionTags)
                crop_text = normalize_text(" ".join(str(item) for item in crop_tags) + " " + (row.Title or "") + " " + (row.Summary or ""))
                region_text = normalize_text(
                    " ".join(str(item) for item in region_tags) + " " + (row.Region or "") + " " + (row.Title or "") + " " + (row.Summary or "")
                )
                crop_ok = not crop_key or crop_key in crop_text
                region_ok = not region_key or region_key in region_text
                if crop_ok and region_ok:
                    filtered.append(row)
            rows = filtered
        return rows[:limit]
    except SQLAlchemyError:
        db.rollback()
        return []


def _as_list(value) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.strip("[]").replace('"', "").split(",") if part.strip()]
    return []
