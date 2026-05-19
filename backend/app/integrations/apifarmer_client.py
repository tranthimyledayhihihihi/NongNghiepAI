from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urljoin
import re

from app.core.config import settings
from app.core.resilience import build_timeout, resilient_request
from app.integrations.base_market_client import BaseMarketClient, MarketPriceResult
from app.repositories.common import normalize_text


class APIFarmerClient(BaseMarketClient):
    source_name = "APIFarmer"

    def __init__(self) -> None:
        self.base_url = (settings.APIFARMER_API_BASE_URL or "").strip()
        self.api_key = (settings.APIFARMER_API_KEY or "").strip()
        self.price_endpoint = (settings.APIFARMER_PRICE_ENDPOINT or "").strip()
        self.history_endpoint = (settings.APIFARMER_HISTORY_ENDPOINT or "").strip()
        self.news_endpoint = (settings.APIFARMER_NEWS_ENDPOINT or "").strip()
        self.enabled = bool(settings.APIFARMER_ENABLED)

    def get_current_price(self, crop_name: str, region: str | None = None) -> MarketPriceResult | None:
        if not self._ready(self.price_endpoint):
            return None

        try:
            payload = self._get_json(
                self.price_endpoint,
                {
                    "crop_name": crop_name,
                    "crop": crop_name,
                    "region": region,
                },
            )
            item = self._pick_price_item(payload, crop_name, region)
            return self._map_price_result(item, crop_name, region) if item else None
        except Exception:
            return None

    def get_price_history(
        self,
        crop_name: str,
        region: str | None = None,
        days: int = 30,
    ) -> list[MarketPriceResult]:
        if not self._ready(self.history_endpoint):
            return []
        try:
            payload = self._get_json(
                self.history_endpoint,
                {
                    "crop_name": crop_name,
                    "crop": crop_name,
                    "region": region,
                    "days": days,
                },
            )
            return [
                result
                for item in self._records(payload)
                if (result := self._map_price_result(item, crop_name, region)) is not None
            ][:days]
        except Exception:
            return []

    def search_market_news(
        self,
        crop_name: str | None = None,
        region: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        if not self._ready(self.news_endpoint):
            return []
        try:
            payload = self._get_json(
                self.news_endpoint,
                {
                    "crop_name": crop_name,
                    "crop": crop_name,
                    "region": region,
                    "limit": limit,
                },
            )
            return [self._map_news_item(item, crop_name, region) for item in self._records(payload)][:limit]
        except Exception:
            return []

    def _ready(self, endpoint: str) -> bool:
        return bool(self.enabled and self.base_url and self.api_key and endpoint)

    def _get_json(self, endpoint: str, params: dict[str, Any]) -> Any:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }
        clean_params = {key: value for key, value in params.items() if value not in (None, "")}
        response = resilient_request(
            "GET",
            urljoin(self.base_url.rstrip("/") + "/", endpoint.lstrip("/")),
            params=clean_params,
            headers=headers,
            timeout=build_timeout(total=20, connect=5, read=12),
            retries=1,
            service_name=self.source_name,
        )
        return response.json()

    def _pick_price_item(self, payload: Any, crop_name: str, region: str | None) -> dict | None:
        records = self._records(payload)
        if not records:
            return None
        crop_key = normalize_text(crop_name)
        region_key = normalize_text(region)
        for item in records:
            item_crop = normalize_text(self._pick(item, ("crop_name", "crop", "CropName", "name", "commodity")))
            item_region = normalize_text(self._pick(item, ("region", "Region", "province", "market", "location")))
            crop_ok = not crop_key or crop_key in item_crop or item_crop in crop_key
            region_ok = not region_key or not item_region or region_key == item_region or region_key in item_region
            if crop_ok and region_ok:
                return item
        return records[0]

    def _map_price_result(
        self,
        item: dict,
        crop_name: str,
        region: str | None,
    ) -> MarketPriceResult | None:
        price = self._parse_price(
            self._pick(item, ("price", "current_price", "price_per_kg", "PricePerKg", "gia", "value"))
        )
        if price is None:
            return None
        observed_at = self._parse_datetime(
            self._pick(item, ("observed_at", "price_date", "date", "updated_at", "timestamp", "PublishedAt"))
        )
        fetched_at = datetime.now()
        return MarketPriceResult(
            crop_name=str(self._pick(item, ("crop_name", "crop", "CropName", "name", "commodity")) or crop_name).strip(),
            region=str(self._pick(item, ("region", "Region", "province", "market", "location")) or region or "Vietnam").strip(),
            price=price,
            unit=str(self._pick(item, ("unit", "Unit")) or "VND/kg"),
            currency=str(self._pick(item, ("currency", "Currency")) or "VND"),
            source_type="local_agriculture",
            source_name=str(self._pick(item, ("source_name", "SourceName")) or self.source_name),
            source_url=self._pick(item, ("source_url", "url", "SourceURL", "URL")),
            observed_at=observed_at,
            fetched_at=fetched_at,
            confidence_score=float(self._pick(item, ("confidence_score", "confidence")) or 0.86),
            is_realtime=True,
            metadata={"provider": self.source_name, "raw": self._compact_metadata(item)},
        )

    def _map_news_item(self, item: dict, crop_name: str | None, region: str | None) -> dict:
        now = datetime.now()
        url = self._pick(item, ("url", "source_url", "link", "SourceURL", "URL"))
        published_at = self._parse_datetime(self._pick(item, ("published_at", "date", "updated_at", "PublishedAt")))
        crop_tags = self._tags(self._pick(item, ("crop_tags", "crops", "affected_crops")), crop_name)
        region_tags = self._tags(self._pick(item, ("region_tags", "regions", "affected_regions")), region)
        sentiment = str(self._pick(item, ("sentiment", "Sentiment")) or "neutral")
        impact_score = float(self._pick(item, ("impact_score", "score")) or self._impact_score(sentiment))
        return {
            "title": str(self._pick(item, ("title", "Title", "name")) or "Tin thị trường nông nghiệp").strip(),
            "summary": str(self._pick(item, ("summary", "description", "Summary")) or "").strip(),
            "content": self._pick(item, ("content", "body", "Content")),
            "url": url,
            "source_url": url,
            "source_name": str(self._pick(item, ("source_name", "SourceName")) or self.source_name),
            "published_at": published_at,
            "fetched_at": now,
            "crop_tags": crop_tags,
            "region_tags": region_tags,
            "sentiment": sentiment,
            "impact_level": str(self._pick(item, ("impact_level", "level")) or self._impact_level(impact_score)),
            "impact_score": impact_score,
            "is_realtime": True,
            "is_mock": False,
            "metadata": {"provider": self.source_name, "raw": self._compact_metadata(item)},
        }

    @staticmethod
    def _records(payload: Any) -> list[dict]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("data", "records", "prices", "items", "news", "articles", "results"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
                if isinstance(value, dict):
                    return [value]
            return [payload]
        return []

    @staticmethod
    def _pick(item: dict, fields: tuple[str, ...]) -> Any:
        for field in fields:
            if item.get(field) not in (None, ""):
                return item.get(field)
        return None

    @staticmethod
    def _parse_price(value: Any) -> float | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value)
        if re.search(r"\d[.,]\d{3}", text):
            number = re.sub(r"[^\d]", "", text)
        else:
            number = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            price = float(number)
        except ValueError:
            return None
        return price if price > 0 else None

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if not value:
            return datetime.now()
        text = str(value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
            return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        return datetime.now()

    @staticmethod
    def _tags(value: Any, fallback: str | None) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in re.split(r"[,;|]", value) if part.strip()]
        return [fallback] if fallback else []

    @staticmethod
    def _impact_score(sentiment: str) -> float:
        if sentiment == "positive":
            return 0.75
        if sentiment == "negative":
            return 0.72
        return 0.5

    @staticmethod
    def _impact_level(score: float) -> str:
        if score >= 0.75:
            return "high"
        if score >= 0.55:
            return "medium"
        return "low"

    @staticmethod
    def _compact_metadata(item: dict) -> dict:
        return {key: item[key] for key in list(item.keys())[:20]}


apifarmer_client = APIFarmerClient()
