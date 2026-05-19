from __future__ import annotations

import html
import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

from app.core.real_data import external_circuit_breaker
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text

logger = logging.getLogger(__name__)


class VietnamRetailPriceClient:
    """Fetch retail reference prices (not official) from major VN retailers.

    Spec requirements:
    - Only for market analysis deltas.
    - Must NOT be treated as official prices.
    - No fake/mock prices.
    - If a website blocks crawl, log error and skip that source.
    - One failing source must not crash the whole API.

    Output format is normalized to dicts with:
      product_name, crop_name, retailer, retail_price, unit, source_url,
      fetched_at, is_realtime, is_mock
    """

    TIMEOUT = build_timeout(total=12, connect=5, read=10)

    # (retailer, url template) where template must contain {query}
    RETAILERS: list[tuple[str, str]] = [
        ("Bách Hóa Xanh", "https://www.bachhoaxanh.com/tim-kiem?s={query}"),
        ("WinMart", "https://winmart.vn/search?keyword={query}"),
        ("GO!", "https://go-vietnam.vn/search?text={query}"),
        ("Co.opmart", "https://cooponline.vn/search?keyword={query}"),
        ("MM Mega Market", "https://www.mmvietnam.com/?s={query}"),
    ]

    # Retail reference unit mapping
    DEFAULT_UNIT = "VNĐ/kg"

    def fetch_retail_prices(self, crop_name: str, *, limit_per_retailer: int = 3) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        query = quote_plus(self._search_query(crop_name))

        for retailer_name, template in self.RETAILERS:
            url = template.format(query=query)
            key = f"vietnam_retail:{retailer_name}"
            try:
                external_circuit_breaker.before_call(key)
                response = resilient_request(
                    "GET",
                    url,
                    headers=self._headers(),
                    timeout=self.TIMEOUT,
                    retries=1,
                    backoff=0.5,
                    service_name=key,
                )

                site_records = self._parse_prices(
                    response.text,
                    crop_name=crop_name,
                    retailer_name=retailer_name,
                    source_url=str(getattr(response, "url", None) or url),
                    limit=limit_per_retailer,
                )

                if site_records:
                    records.extend(site_records)
                    external_circuit_breaker.record_success(key)
                else:
                    external_circuit_breaker.record_failure(key, "no retail prices parsed")

            except Exception as exc:
                external_circuit_breaker.record_failure(key, exc)
                # If blocked/captcha/403/429, log and skip that retailer.
                logger.warning("[RetailPrice] Skip retailer=%s url=%s error=%s", retailer_name, url, exc)
                continue

        return records

    def _parse_prices(
        self,
        content: str,
        *,
        crop_name: str,
        retailer_name: str,
        source_url: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        compact = self._clean_html(content)
        crop_key = normalize_text(crop_name)
        fetched_at = datetime.now()

        results: list[dict[str, Any]] = []

        # Generic VN retail search pages: try to capture price numbers and surrounding context.
        # Examples of patterns: 25.000đ/kg, 25.000 đ/100g, 25000 VND, ...
        # We then heuristically normalize to VNĐ/kg.
        price_pattern = re.compile(
            r"(?P<context>.{0,120}?)"
            r"(?P<price>\d{1,3}(?:[\.,]\d{3})+|\d{4,7})"
            r"\s*(?:đ|d|vnd)?\s*(?:/\s*(?P<unit>100\s*g|200\s*g|500\s*g|1\s*kg|kg))?",
            flags=re.IGNORECASE | re.DOTALL,
        )

        for match in price_pattern.finditer(compact):
            context = (match.group("context") or "").strip(" -:|\n\r\t")

            # Filter: keep hits where context mentions the requested crop (best-effort).
            if crop_key and crop_key not in normalize_text(context):
                # if context doesn't mention crop, skip.
                continue

            raw_price = match.group("price")
            unit_token = (match.group("unit") or "kg").lower().replace(" ", "")

            price = self._parse_price_to_vnd(raw_price)
            if not price:
                continue

            # Unit normalization to VNĐ/kg
            if unit_token.startswith("100g"):
                price *= 10
            elif unit_token.startswith("200g"):
                price *= 5
            elif unit_token.startswith("500g"):
                price *= 2
            elif unit_token.startswith("1kg") or unit_token.startswith("kg"):
                pass
            else:
                # Unknown unit => skip to avoid fake/incorrect prices.
                continue

            price = round(float(price))
            if price <= 0:
                continue

            product_name = self._guess_product_name(context, crop_name)

            results.append(
                {
                    "product_name": product_name,
                    "crop_name": normalize_text(crop_name) or crop_name,
                    "retailer": retailer_name,
                    "retail_price": int(price),
                    "unit": self.DEFAULT_UNIT,
                    "source_url": source_url,
                    "fetched_at": fetched_at,
                    "is_realtime": True,
                    "is_mock": False,
                }
            )

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def _guess_product_name(context: str, crop_name: str) -> str:
        # Keep last meaningful chunk as product name.
        ctx = re.sub(r"\s+", " ", context or "").strip()
        if not ctx:
            return crop_name
        # Remove price-like tokens
        ctx = re.sub(r"\d{1,3}(?:[\.,]\d{3})+|\d{4,7}", " ", ctx)
        ctx = re.sub(r"(đ|vnd|VNĐ)", " ", ctx, flags=re.IGNORECASE)
        ctx = re.sub(r"\b(kg|g|100g|200g|500g)\b", " ", ctx, flags=re.IGNORECASE)
        ctx = re.sub(r"[^\p{L}\p{N} ]+", " ", ctx, flags=re.UNICODE)
        ctx = re.sub(r"\s+", " ", ctx).strip()
        return ctx[:120] if ctx else crop_name

    @staticmethod
    def _parse_price_to_vnd(raw_price: str) -> float | None:
        if not raw_price:
            return None
        text = raw_price.strip()
        # Remove thousand separators
        if re.fullmatch(r"\d{1,3}(?:[\.,]\d{3})+", text):
            digits = text.replace(".", "").replace(",", "")
        else:
            digits = re.sub(r"[^\d]", "", text)
        try:
            val = float(digits)
        except ValueError:
            return None
        return val if val > 0 else None

    @staticmethod
    def _clean_html(value: str) -> str:
        text = re.sub(r"<script.*?</script>", " ", value or "", flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _search_query(crop_name: str) -> str:
        # Best-effort: use a few common aliases; otherwise use raw.
        key = normalize_text(crop_name)
        mapping = {
            "ca phe": "ca phe",
            "lua": "gao",
            "gao": "gao",
            "rau qua": "rau",
            "cà chua": "ca chua",
            "ca chua": "ca chua",
        }
        return mapping.get(key, crop_name or "nong san")

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
        }


vietnam_retail_price_client = VietnamRetailPriceClient()

