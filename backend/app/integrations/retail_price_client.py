from __future__ import annotations

from app.integrations.winmart_price_client import WINMART_SOURCE_NAME, winmart_price_client
from app.repositories.common import normalize_text


class RetailPriceClient:
    RETAILERS = [(WINMART_SOURCE_NAME, "https://winmart.vn/")]

    def fetch_retail_prices(self, crop_name: str, *, limit_per_site: int = 3) -> list[dict]:
        records = winmart_price_client.fetch_prices(crop_name)[:limit_per_site]
        return [self._to_retail_record(record, crop_name) for record in records]

    @staticmethod
    def _to_retail_record(record: dict, crop_name: str) -> dict:
        metadata = record.get("metadata") or {}
        return {
            "crop_name": normalize_text(crop_name) or record.get("crop_name") or crop_name,
            "product_name": metadata.get("product_name") or crop_name,
            "region": record.get("region") or "WinMart Online",
            "retailer_name": WINMART_SOURCE_NAME,
            "price_per_kg": record.get("price"),
            "unit": record.get("unit") or "VND/kg",
            "source_name": WINMART_SOURCE_NAME,
            "source_url": record.get("source_url"),
            "observed_at": record.get("observed_at"),
            "fetched_at": record.get("fetched_at"),
            "is_realtime": True,
            "is_mock": False,
            "metadata": metadata,
        }


retail_price_client = RetailPriceClient()
