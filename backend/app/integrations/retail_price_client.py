from __future__ import annotations

import html
import re
from datetime import datetime
from urllib.parse import quote_plus

from app.core.real_data import external_circuit_breaker
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text


class RetailPriceClient:
    TIMEOUT = build_timeout(total=8, connect=3, read=6)
    RETAILERS = [
        ("Bach Hoa Xanh", "https://www.bachhoaxanh.com/tim-kiem?s={query}"),
        ("WinMart", "https://winmart.vn/search?keyword={query}"),
        ("GO!", "https://go-vietnam.vn/search?text={query}"),
        ("Co.opmart", "https://cooponline.vn/search?keyword={query}"),
        ("MM Mega Market", "https://www.mmvietnam.com/?s={query}"),
    ]

    def fetch_retail_prices(self, crop_name: str, *, limit_per_site: int = 3) -> list[dict]:
        records: list[dict] = []
        query = quote_plus(self._search_query(crop_name))
        for retailer_name, template in self.RETAILERS:
            url = template.format(query=query)
            key = f"retail_price:{retailer_name}"
            try:
                external_circuit_breaker.before_call(key)
                response = resilient_request(
                    "GET",
                    url,
                    headers=self._headers(),
                    timeout=self.TIMEOUT,
                    retries=1,
                    backoff=0.5,
                    service_name=f"retail_price:{retailer_name}",
                )
                site_records = self._parse_prices(
                    response.text,
                    crop_name=crop_name,
                    retailer_name=retailer_name,
                    source_url=str(response.url or url),
                    limit=limit_per_site,
                )
                if site_records:
                    records.extend(site_records)
                    external_circuit_breaker.record_success(key)
                else:
                    external_circuit_breaker.record_failure(key, "no retail prices parsed")
            except Exception as exc:
                external_circuit_breaker.record_failure(key, exc)
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
    ) -> list[dict]:
        compact = self._clean_html(content)
        crop_key = normalize_text(crop_name)
        records: list[dict] = []
        fetched_at = datetime.now()
        for match in re.finditer(r"(.{0,90}?)(\d{1,3}(?:[.,]\d{3})+)\s*(?:d|đ|₫|vnd)", compact, flags=re.IGNORECASE):
            context = match.group(1).strip(" -:|")
            if crop_key and crop_key not in normalize_text(context):
                # Retail search pages often include noisy navigation; keep only hits
                # whose nearby text still mentions the requested product.
                continue
            price = self._parse_price(match.group(2))
            if not price:
                continue
            records.append(
                {
                    "crop_name": normalize_text(crop_name) or crop_name,
                    "product_name": context[-120:] or crop_name,
                    "region": "Vietnam",
                    "retailer_name": retailer_name,
                    "price_per_kg": price,
                    "unit": "VND/kg",
                    "source_name": retailer_name,
                    "source_url": source_url,
                    "observed_at": fetched_at,
                    "fetched_at": fetched_at,
                    "is_realtime": True,
                    "is_mock": False,
                    "metadata": {"raw_context": context[-200:]},
                }
            )
            if len(records) >= limit:
                break
        return records

    @staticmethod
    def _parse_price(value: str) -> float | None:
        text = value.strip()
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", text):
            digits = text.replace(".", "")
        elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", text):
            digits = text.replace(",", "")
        else:
            digits = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            price = float(digits)
        except ValueError:
            return None
        return price if price > 0 else None

    @staticmethod
    def _clean_html(value: str) -> str:
        text = re.sub(r"<script.*?</script>", " ", value or "", flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _search_query(crop_name: str) -> str:
        key = normalize_text(crop_name)
        mapping = {
            "ca phe": "ca phe",
            "lua": "gao",
            "gao": "gao",
            "rau qua": "rau",
        }
        return mapping.get(key, crop_name or "nong san")

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
        }


retail_price_client = RetailPriceClient()
