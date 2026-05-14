from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.integrations.rss_client import rss_client
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.repositories.market_news_repository import list_market_news, upsert_market_news


class MarketNewsService:
    def refresh_news(self) -> dict:
        db = SessionLocal()
        log = start_ingestion_log(db, "refresh_market_news", "rss")
        try:
            records = rss_client.fetch_market_news()
            result = upsert_market_news(db, records)
            redis_client.delete("market_news:latest")
            finish_ingestion_log(
                db,
                log,
                status="success",
                records_fetched=len(records),
                records_saved=result["records_saved"] + result["records_updated"],
            )
            return {"status": "success", "records_fetched": len(records), **result}
        except Exception as exc:
            finish_ingestion_log(db, log, status="failed", error_message=str(exc))
            return {"status": "failed", "error": str(exc)}
        finally:
            db.close()

    def get_latest(self, db, limit: int = 20, crop_name: str | None = None, region: str | None = None) -> dict:
        cache_key = "market_news:latest" if not crop_name and not region else None
        cached = redis_client.get(cache_key) if cache_key else None
        if cached:
            return {**cached, "cache_status": "hit"}

        rows = list_market_news(db, limit=limit, crop_name=crop_name, region=region)
        if not rows:
            self.refresh_news()
            rows = list_market_news(db, limit=limit, crop_name=crop_name, region=region)

        response = {
            "news": [self._to_dict(row) for row in rows],
            "source": "rss",
            "is_realtime": True,
            "is_mock": False,
            "cache_status": "from_db",
        }
        if cache_key:
            redis_client.set(cache_key, response, expire=1800)
        return response

    @staticmethod
    def _to_dict(row) -> dict:
        return {
            "news_id": row.NewsID,
            "title": row.Title,
            "summary": row.Summary,
            "source_name": row.SourceName,
            "source_url": row.SourceURL,
            "published_at": row.PublishedAt.isoformat() if row.PublishedAt else None,
            "region": row.Region,
            "sentiment": row.Sentiment,
        }


market_news_service = MarketNewsService()
