from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.market_price_client import market_price_client
from app.models.price import MarketPrice
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.repositories.price_repository import bulk_upsert_market_prices


class PriceAggregatorService:
    stale_after = timedelta(hours=24)

    def refresh_prices(
        self,
        db: Session,
        *,
        crop_name: str | None = None,
        source_name: str | None = None,
    ) -> dict:
        log_source = source_name or "price_aggregator"
        log = start_ingestion_log(db, "refresh_market_prices", log_source)
        try:
            records = market_price_client.fetch_all(source_name=source_name, crop_filter=crop_name)
            result = bulk_upsert_market_prices(db, records)
            finish_ingestion_log(
                db,
                log,
                status="success",
                records_fetched=len(records),
                records_saved=result["records_saved"] + result["records_updated"],
                error_message="; ".join(result.get("errors") or []) or None,
            )
            return {
                "status": "success",
                "records_fetched": len(records),
                **result,
            }
        except Exception as exc:
            finish_ingestion_log(db, log, status="failed", error_message=str(exc))
            return {"status": "failed", "error": str(exc), "records_fetched": 0, "records_saved": 0}

    def latest_global_references(self, db: Session, limit: int = 8) -> list[dict]:
        rows = (
            db.query(MarketPrice)
            .filter(MarketPrice.Region == "Global Futures")
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .limit(limit * 2)
            .all()
        )
        result = []
        seen = set()
        for row in rows:
            crop_name = getattr(getattr(row, "crop", None), "CropName", None)
            if not crop_name:
                try:
                    crop_name = row.Crop.CropName
                except Exception:
                    crop_name = None
            key = row.CropID
            if key in seen:
                continue
            seen.add(key)
            result.append(
                {
                    "crop_id": row.CropID,
                    "crop_name": crop_name,
                    "price": float(row.PricePerKg),
                    "unit": "VND/kg",
                    "market_type": row.MarketType,
                    "source_name": row.SourceName or "Stooq commodity futures",
                    "source_url": row.SourceURL,
                    "last_updated": row.UpdatedAt,
                    "cache_status": self.cache_status(row.UpdatedAt),
                    "is_realtime": False,
                    "is_mock": False,
                }
            )
            if len(result) >= limit:
                break
        return result

    def cache_status(self, updated_at: datetime | None) -> str:
        if not updated_at:
            return "unknown"
        age = datetime.now() - updated_at
        if age <= self.stale_after:
            return "fresh"
        return "stale"

    def is_stale(self, updated_at: datetime | None) -> bool:
        return self.cache_status(updated_at) in {"stale", "unknown"}

    def exchange_rate(self, live: bool = False) -> dict:
        rate = market_price_client._fetch_usd_vnd_rate() if live else float(settings.USD_VND_FALLBACK_RATE)
        return {
            "pair": "USD/VND",
            "rate": rate,
            "source_name": "open.er-api" if live else "USD/VND fallback config",
            "source_url": "https://open.er-api.com",
            "cache_status": "live" if live else "cached",
            "is_realtime": live,
            "is_mock": False,
            "last_updated": datetime.now(),
        }


price_aggregator_service = PriceAggregatorService()
