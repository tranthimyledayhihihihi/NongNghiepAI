from __future__ import annotations

from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.real_data import cache_status_for, is_real_cache_record
from app.integrations.retail_price_client import retail_price_client
from app.models.market import RetailPriceSnapshot
from app.repositories.common import normalize_text


class RetailPriceService:
    def refresh_retail_prices(self, db: Session, crop_name: str) -> dict:
        records = retail_price_client.fetch_retail_prices(crop_name)
        saved = 0
        for item in records:
            try:
                row = RetailPriceSnapshot(
                    CropName=item["crop_name"],
                    ProductName=item.get("product_name"),
                    Region=item.get("region"),
                    RetailerName=item["retailer_name"],
                    PricePerKg=float(item["price_per_kg"]),
                    Unit=item.get("unit") or "VND/kg",
                    SourceName=item["source_name"],
                    SourceURL=item["source_url"],
                    ObservedAt=item.get("observed_at") or datetime.now(),
                    FetchedAt=item.get("fetched_at") or datetime.now(),
                    IsRealtime=True,
                    IsMock=False,
                    Metadata=item.get("metadata"),
                )
                db.add(row)
                saved += 1
            except Exception:
                continue
        try:
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            return {"status": "failed", "error": str(exc), "records_fetched": len(records), "records_saved": 0}
        return {
            "status": "success" if saved else "empty",
            "records_fetched": len(records),
            "records_saved": saved,
            "source_name": "Vietnam retail websites",
            "fetched_at": datetime.now(),
        }

    def get_cached_retail_prices(self, db: Session, crop_name: str, *, limit: int = 10) -> dict:
        key = normalize_text(crop_name)
        rows = (
            db.query(RetailPriceSnapshot)
            .filter(RetailPriceSnapshot.IsMock == False)  # noqa: E712
            .order_by(desc(RetailPriceSnapshot.FetchedAt))
            .limit(limit * 4)
            .all()
        )
        items = []
        for row in rows:
            if key and key not in normalize_text(row.CropName):
                continue
            if not is_real_cache_record(
                source_url=row.SourceURL,
                source_name=row.SourceName,
                fetched_at=row.FetchedAt,
                is_mock=row.IsMock,
            ):
                continue
            status = cache_status_for(row.FetchedAt, "retail_price")
            if status == "miss":
                continue
            items.append(
                {
                    "crop_name": row.CropName,
                    "product_name": row.ProductName,
                    "region": row.Region,
                    "retailer_name": row.RetailerName,
                    "price": float(row.PricePerKg),
                    "unit": row.Unit or "VND/kg",
                    "source_name": row.SourceName,
                    "source_url": row.SourceURL,
                    "fetched_at": row.FetchedAt,
                    "last_updated": row.FetchedAt,
                    "is_realtime": False,
                    "is_mock": False,
                    "cache_status": status,
                }
            )
            if len(items) >= limit:
                break
        return {
            "retail_prices": items,
            "source_name": "Vietnam retail websites",
            "source_url": items[0]["source_url"] if items else None,
            "is_realtime": False,
            "is_mock": False,
            "cache_status": items[0]["cache_status"] if items else "miss",
            "fetched_at": items[0]["fetched_at"] if items else None,
            "last_updated": items[0]["last_updated"] if items else None,
        }


retail_price_service = RetailPriceService()
