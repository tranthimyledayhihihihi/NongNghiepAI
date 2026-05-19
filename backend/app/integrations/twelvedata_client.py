from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from app.core.config import settings
from app.core.resilience import build_timeout, resilient_request
from app.integrations.base_market_client import BaseMarketClient, MarketPriceResult
from app.repositories.common import normalize_text


COMMODITY_SYMBOL_MAP: dict[str, list[str]] = {
    "ca phe": ["coffee", "COFFEE"],
    "cà phê": ["coffee", "COFFEE"],
    "ngo": ["corn", "CORN"],
    "ngô": ["corn", "CORN"],
    "bap": ["corn", "CORN"],
    "bắp": ["corn", "CORN"],
    "lua mi": ["wheat", "WHEAT"],
    "lúa mì": ["wheat", "WHEAT"],
    "dau tuong": ["soybean", "SOYBEAN"],
    "đậu tương": ["soybean", "SOYBEAN"],
    "dau nanh": ["soybean", "SOYBEAN"],
    "đậu nành": ["soybean", "SOYBEAN"],
    "duong": ["sugar", "SUGAR"],
    "đường": ["sugar", "SUGAR"],
    "ca cao": ["cocoa", "COCOA"],
    "bong": ["cotton", "COTTON"],
    "bông": ["cotton", "COTTON"],
}


class TwelveDataClient(BaseMarketClient):
    source_name = "Twelve Data"

    def __init__(self) -> None:
        self.base_url = (settings.TWELVEDATA_API_BASE_URL or "https://api.twelvedata.com").strip()
        self.api_key = (settings.TWELVEDATA_API_KEY or "").strip()
        self.price_endpoint = (settings.TWELVEDATA_PRICE_ENDPOINT or "/price").strip()
        self.time_series_endpoint = (settings.TWELVEDATA_TIME_SERIES_ENDPOINT or "/time_series").strip()
        self.news_endpoint = (settings.TWELVEDATA_NEWS_ENDPOINT or "").strip()
        self.enabled = bool(settings.TWELVEDATA_ENABLED)

    def get_current_price(self, crop_name: str, region: str | None = None) -> MarketPriceResult | None:
        symbols = self.symbols_for_crop(crop_name)
        if not self._ready(self.price_endpoint) or not symbols:
            return None

        for symbol in symbols:
            try:
                payload = self._get_json(self.price_endpoint, {"symbol": symbol})
                if self._is_error(payload):
                    continue
                price = self._parse_float(payload.get("price") if isinstance(payload, dict) else None)
                if price is None:
                    continue
                now = datetime.now()
                return MarketPriceResult(
                    crop_name=crop_name,
                    region=region or "Global Futures",
                    price=price,
                    unit="USD/ton",
                    currency="USD",
                    source_type="global_commodity",
                    source_name=self.source_name,
                    source_url=f"https://twelvedata.com/commodities/{symbol}",
                    observed_at=now,
                    fetched_at=now,
                    confidence_score=0.72,
                    is_realtime=True,
                    metadata={"symbol": symbol, "provider": self.source_name, "role": "global_reference"},
                )
            except Exception:
                continue
        return None

    def get_price_history(
        self,
        crop_name: str,
        region: str | None = None,
        days: int = 30,
    ) -> list[MarketPriceResult]:
        symbols = self.symbols_for_crop(crop_name)
        if not self._ready(self.time_series_endpoint) or not symbols:
            return []
        for symbol in symbols:
            try:
                payload = self._get_json(
                    self.time_series_endpoint,
                    {
                        "symbol": symbol,
                        "interval": "1day",
                        "outputsize": max(min(days, 365), 1),
                    },
                )
                if self._is_error(payload):
                    continue
                values = payload.get("values", []) if isinstance(payload, dict) else []
                results: list[MarketPriceResult] = []
                fetched_at = datetime.now()
                for item in values:
                    close = self._parse_float(item.get("close") if isinstance(item, dict) else None)
                    if close is None:
                        continue
                    observed_at = self._parse_datetime(item.get("datetime"))
                    results.append(
                        MarketPriceResult(
                            crop_name=crop_name,
                            region=region or "Global Futures",
                            price=close,
                            unit="USD/ton",
                            currency="USD",
                            source_type="global_commodity",
                            source_name=self.source_name,
                            source_url=f"https://twelvedata.com/commodities/{symbol}",
                            observed_at=observed_at,
                            fetched_at=fetched_at,
                            confidence_score=0.68,
                            is_realtime=True,
                            metadata={"symbol": symbol, "provider": self.source_name, "role": "global_reference"},
                        )
                    )
                return list(reversed(results))[:days]
            except Exception:
                continue
        return []

    def search_market_news(
        self,
        crop_name: str | None = None,
        region: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        if not self._ready(self.news_endpoint):
            return []
        symbol = (self.symbols_for_crop(crop_name or "") or [None])[0]
        try:
            payload = self._get_json(
                self.news_endpoint,
                {
                    "symbol": symbol,
                    "query": crop_name,
                    "limit": limit,
                },
            )
            if self._is_error(payload):
                return []
            records = self._records(payload)
            return [self._map_news(item, crop_name, region) for item in records][:limit]
        except Exception:
            return []

    @classmethod
    def symbols_for_crop(cls, crop_name: str | None) -> list[str]:
        normalized = normalize_text(crop_name)
        if not normalized:
            return []
        return COMMODITY_SYMBOL_MAP.get(normalized, [])

    def _ready(self, endpoint: str) -> bool:
        return bool(self.enabled and self.base_url and self.api_key and endpoint)

    def _get_json(self, endpoint: str, params: dict[str, Any]) -> Any:
        clean_params = {
            key: value
            for key, value in {
                **params,
                "apikey": self.api_key,
            }.items()
            if value not in (None, "")
        }
        response = resilient_request(
            "GET",
            urljoin(self.base_url.rstrip("/") + "/", endpoint.lstrip("/")),
            params=clean_params,
            timeout=build_timeout(total=20, connect=5, read=12),
            retries=1,
            service_name=self.source_name,
        )
        return response.json()

    @staticmethod
    def _is_error(payload: Any) -> bool:
        if not isinstance(payload, dict):
            return True
        return str(payload.get("status") or "").lower() == "error" or payload.get("code") in (400, 401, 403, 429)

    @staticmethod
    def _parse_float(value: Any) -> float | None:
        if value in (None, "", "NaN"):
            return None
        try:
            number = float(str(value).replace(",", ""))
        except ValueError:
            return None
        return number if number > 0 else None

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if not value:
            return datetime.now()
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return datetime.now()

    @staticmethod
    def _records(payload: Any) -> list[dict]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("data", "news", "articles", "results", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def _pick(item: dict, fields: tuple[str, ...]) -> Any:
        for field in fields:
            if item.get(field) not in (None, ""):
                return item.get(field)
        return None

    def _map_news(self, item: dict, crop_name: str | None, region: str | None) -> dict:
        now = datetime.now()
        url = self._pick(item, ("url", "source_url", "link"))
        published_at = self._parse_datetime(self._pick(item, ("published_at", "datetime", "date")))
        sentiment = str(self._pick(item, ("sentiment",)) or "neutral")
        impact_score = 0.6 if sentiment == "neutral" else 0.72
        return {
            "title": str(self._pick(item, ("title", "headline")) or "Tin thị trường hàng hóa quốc tế"),
            "summary": str(self._pick(item, ("summary", "description", "snippet")) or ""),
            "content": self._pick(item, ("content", "body")),
            "url": url,
            "source_url": url,
            "source_name": self.source_name,
            "published_at": published_at,
            "fetched_at": now,
            "crop_tags": [crop_name] if crop_name else [],
            "region_tags": [region] if region else [],
            "sentiment": sentiment,
            "impact_level": "medium" if impact_score >= 0.55 else "low",
            "impact_score": impact_score,
            "is_realtime": True,
            "is_mock": False,
            "metadata": {"provider": self.source_name, "role": "global_market_news"},
        }


twelvedata_client = TwelveDataClient()
