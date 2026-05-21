from __future__ import annotations

import html
import re
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import urljoin

from app.core.real_data import (
    OFFICIAL_AGRI_SOURCE_NAME,
    OFFICIAL_NEWS_URL,
    OFFICIAL_PRICE_URL,
    external_circuit_breaker,
)
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text


class ThiTruongNongSanError(RuntimeError):
    pass


class ThiTruongNongSanClient:
    price_url = OFFICIAL_PRICE_URL
    news_url = OFFICIAL_NEWS_URL
    source_name = OFFICIAL_AGRI_SOURCE_NAME

    PRICE_TIMEOUT = build_timeout(total=15, connect=5, read=12)
    NEWS_TIMEOUT = build_timeout(total=12, connect=5, read=10)

    def fetch_prices(
        self,
        crop_name: str | None = None,
        *,
        region: str | None = None,
        days: int = 30,
    ) -> list[dict]:
        from app.integrations.winmart_price_client import winmart_price_client

        return winmart_price_client.fetch_prices(crop_name=crop_name, region=region)

    def fetch_news(self, limit: int = 30) -> list[dict]:
        key = "thitruongnongsan_news"
        external_circuit_breaker.before_call(key)
        try:
            response = resilient_request(
                "GET",
                self.news_url,
                headers=self._headers(),
                timeout=self.NEWS_TIMEOUT,
                retries=1,
                backoff=0.5,
                service_name="thitruongnongsan_news",
            )
            records = self._parse_news(response.text, limit=limit)
            external_circuit_breaker.record_success(key)
            return records
        except Exception as exc:
            external_circuit_breaker.record_failure(key, exc)
            raise ThiTruongNongSanError(str(exc)) from exc

    def _fetch_price_category(
        self,
        category: str,
        *,
        requested_crop: str,
        region: str | None,
        days: int,
    ) -> list[dict]:
        key = f"thitruongnongsan_price:{category}"
        external_circuit_breaker.before_call(key)
        try:
            initial = resilient_request(
                "GET",
                self.price_url,
                headers=self._headers(),
                timeout=self.PRICE_TIMEOUT,
                retries=1,
                backoff=0.5,
                service_name="thitruongnongsan_price",
            )
            fields = self._hidden_fields(initial.text)
            body = {
                **fields,
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "ctl00$maincontent$tu_ngay": (date.today() - timedelta(days=max(days, 1))).strftime("%d/%m/%Y"),
                "ctl00$maincontent$den_ngay": date.today().strftime("%d/%m/%Y"),
                "ctl00$maincontent$Ng\u00e0nh_h\u00e0ng": category,
                "ctl00$maincontent$Theo_th\u1eddi_gian": "ngay",
                "ctl00$maincontent$Xem": "Xem",
            }
            response = resilient_request(
                "POST",
                self.price_url,
                data=body,
                headers={
                    **self._headers(),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://thitruongnongsan.gov.vn",
                    "Referer": self.price_url,
                },
                timeout=self.PRICE_TIMEOUT,
                retries=1,
                backoff=0.5,
                service_name="thitruongnongsan_price",
            )
            records = self._parse_price_rows(
                response.text,
                category=category,
                requested_crop=requested_crop,
                region=region,
            )
            external_circuit_breaker.record_success(key)
            return records
        except Exception as exc:
            external_circuit_breaker.record_failure(key, exc)
            raise ThiTruongNongSanError(str(exc)) from exc

    def _parse_price_rows(
        self,
        content: str,
        *,
        category: str,
        requested_crop: str,
        region: str | None,
    ) -> list[dict]:
        records: list[dict] = []
        target_region = normalize_text(region or "")
        fetched_at = datetime.now()
        default_crop = requested_crop or self._canonical_crop_for_category(category)
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", content, flags=re.IGNORECASE | re.DOTALL):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.IGNORECASE | re.DOTALL)
            if len(cells) != 4:
                continue
            product, row_region, observed, raw_price = [self._clean_html(cell) for cell in cells]
            if not product or not row_region:
                continue
            if target_region and target_region not in normalize_text(row_region):
                continue
            price = self._parse_price(raw_price)
            observed_date = self._parse_date(observed)
            if price is None or observed_date is None:
                continue
            records.append(
                {
                    "crop_name": default_crop,
                    "region": row_region,
                    "price": price,
                    "quality_grade": "grade_1",
                    "source_name": self.source_name,
                    "source_url": self.price_url,
                    "source_type": "official_agriculture_price",
                    "price_date": observed_date,
                    "market_type": "Cho dau moi",
                    "observed_at": datetime.combine(observed_date, datetime.min.time()),
                    "fetched_at": fetched_at,
                    "collected_at": fetched_at,
                    "confidence_score": 0.9,
                    "is_realtime": True,
                    "is_mock": False,
                    "metadata": {
                        "official_product_name": product,
                        "official_category": category,
                    },
                }
            )
        return records

    def _parse_news(self, content: str, *, limit: int) -> list[dict]:
        blocks = re.findall(
            r"<div class=\"khung_dv_con\">(.*?)</div>\s*</div>\s*</div>",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not blocks:
            blocks = re.findall(r"<h4 class=\"title_dv\">(.*?)</div>\s*</div>", content, flags=re.IGNORECASE | re.DOTALL)
        records: list[dict] = []
        fetched_at = datetime.now()
        for block in blocks:
            link_match = re.search(r"<a\s+href=[\"']([^\"']+)[\"'][^>]*>\s*(.*?)\s*</a>", block, flags=re.IGNORECASE | re.DOTALL)
            if not link_match:
                continue
            url = urljoin(self.news_url, self._clean_html(link_match.group(1)))
            title = self._clean_html(link_match.group(2))
            if not title or "img" in title.lower():
                title_match = re.search(r"<h4[^>]*>.*?<a[^>]*>(.*?)</a>", block, flags=re.IGNORECASE | re.DOTALL)
                title = self._clean_html(title_match.group(1)) if title_match else title
            date_match = re.search(r"<div class=\"time_up\">\s*<p>(.*?)</p>", block, flags=re.IGNORECASE | re.DOTALL)
            summary_match = re.search(r"<div class=\"descript_dv\">\s*<p>(.*?)</p>", block, flags=re.IGNORECASE | re.DOTALL)
            published_at = self._parse_date(self._clean_html(date_match.group(1)) if date_match else "")
            summary = self._clean_html(summary_match.group(1)) if summary_match else None
            if not title or not url:
                continue
            records.append(
                {
                    "title": title,
                    "summary": summary,
                    "content": summary,
                    "url": url,
                    "source_name": self.source_name,
                    "source_url": url,
                    "published_at": datetime.combine(published_at, datetime.min.time()) if published_at else fetched_at,
                    "fetched_at": fetched_at,
                    "region": None,
                    "crop_tags": self._infer_crop_tags(f"{title} {summary or ''}"),
                    "region_tags": [],
                    "sentiment": "neutral",
                    "impact_level": "medium",
                    "impact_score": 0.6,
                    "is_realtime": True,
                    "is_mock": False,
                    "metadata": {"listing_url": self.news_url},
                }
            )
            if len(records) >= limit:
                break
        return records

    @staticmethod
    def _hidden_fields(content: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for name in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "__LASTFOCUS"):
            match = re.search(rf'name="{re.escape(name)}"[^>]*value="([^"]*)"', content, flags=re.IGNORECASE)
            if match:
                fields[name] = html.unescape(match.group(1))
        return fields

    @staticmethod
    def _clean_html(value: str) -> str:
        text = re.sub(r"<[^>]+>", " ", value or "")
        text = html.unescape(text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _parse_price(value: Any) -> float | None:
        text = str(value or "").strip()
        if not text:
            return None
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
    def _parse_date(value: Any) -> date | None:
        text = str(value or "").strip()
        if not text:
            return None
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(text[:10], fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
        }

    @staticmethod
    def _categories_for_crop(crop_name: str | None) -> list[str]:
        crop = normalize_text(crop_name or "")
        if not crop:
            return ["C\u00e0 ph\u00ea", "L\u00faa g\u1ea1o", "Rau, qu\u1ea3"]
        if any(token in crop for token in ("ca phe", "coffee")):
            return ["C\u00e0 ph\u00ea"]
        if any(token in crop for token in ("lua", "gao", "rice")):
            return ["L\u00faa g\u1ea1o"]
        return ["Rau, qu\u1ea3"]

    @staticmethod
    def _canonical_crop_for_category(category: str) -> str:
        key = normalize_text(category)
        if "ca phe" in key:
            return "ca phe"
        if "lua" in key or "gao" in key:
            return "lua"
        return "rau qua"

    @staticmethod
    def _infer_crop_tags(text: str) -> list[str]:
        normalized = normalize_text(text)
        tags = []
        for label, tokens in {
            "lua": ("lua", "gao", "rice"),
            "ca phe": ("ca phe", "coffee"),
            "rau qua": ("rau", "qua", "trai cay"),
            "ho tieu": ("ho tieu", "tieu"),
        }.items():
            if any(token in normalized for token in tokens):
                tags.append(label)
        return tags


thitruongnongsan_client = ThiTruongNongSanClient()
