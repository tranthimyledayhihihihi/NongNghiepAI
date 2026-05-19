from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MarketPriceResult:
    crop_name: str
    region: str | None
    price: float
    unit: str
    currency: str
    source_type: str
    source_name: str
    source_url: str | None
    observed_at: datetime
    fetched_at: datetime
    confidence_score: float
    is_realtime: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseMarketClient:
    def get_current_price(self, crop_name: str, region: str | None = None) -> MarketPriceResult | None:
        raise NotImplementedError

    def get_price_history(
        self,
        crop_name: str,
        region: str | None = None,
        days: int = 30,
    ) -> list[MarketPriceResult]:
        raise NotImplementedError

    def search_market_news(
        self,
        crop_name: str | None = None,
        region: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        raise NotImplementedError
