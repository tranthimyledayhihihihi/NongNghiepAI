from __future__ import annotations

from typing import Any

from app.integrations.winmart_price_client import WINMART_SOURCE_NAME, winmart_price_client
from app.repositories.common import normalize_text


class VietnamRetailPriceClient:
    """Fetch retail reference prices from WinMart only."""

    RETAILERS: list[tuple[str, str]] = [(WINMART_SOURCE_NAME, "https://winmart.vn/")]
    DEFAULT_UNIT = "VNĐ/kg"

    def fetch_retail_prices(self, crop_name: str, *, limit_per_retailer: int = 3) -> list[dict[str, Any]]:
        records = winmart_price_client.fetch_prices(crop_name)[:limit_per_retailer]
        return [self._to_retail_record(record, crop_name) for record in records]

    @staticmethod
    def _to_retail_record(record: dict[str, Any], crop_name: str) -> dict[str, Any]:
        metadata = record.get("metadata") or {}
        return {
            "product_name": metadata.get("product_name") or crop_name,
            "crop_name": normalize_text(crop_name) or record.get("crop_name") or crop_name,
            "retailer": WINMART_SOURCE_NAME,
            "retail_price": record.get("price"),
            "unit": record.get("unit") or VietnamRetailPriceClient.DEFAULT_UNIT,
            "source_url": record.get("source_url"),
            "fetched_at": record.get("fetched_at"),
            "is_realtime": True,
            "is_mock": False,
        }


vietnam_retail_price_client = VietnamRetailPriceClient()
