from __future__ import annotations

import html
import json
import logging
import re
from datetime import date, datetime, timedelta
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.real_data import external_circuit_breaker
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text

logger = logging.getLogger(__name__)


class ThiTruongNongSanPriceClient:
    def __init__(self) -> None:
        self.source_name = "Thông tin thị trường nông sản"
        self.source_url = (settings.THITRUONG_NONGSAN_PRICE_URL or "https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx").strip()
        self.timeout = build_timeout(
            total=min(float(getattr(settings, "EXTERNAL_TOTAL_TIMEOUT_SECONDS", 12.0)), 12.0),
            connect=min(float(getattr(settings, "EXTERNAL_CONNECT_TIMEOUT_SECONDS", 3.0)), 3.0),
            read=min(float(getattr(settings, "EXTERNAL_READ_TIMEOUT_SECONDS", 8.0)), 8.0),
        )
        self.retries = min(max(int(getattr(settings, "EXTERNAL_RETRY_COUNT", 1)), 1), 2)
        self.allowed_crops = (
            "ca phe",
            "lua gao",
            "lua",
            "gao",
            "rau",
            "rau qua",
            "ho tieu",
            "cao su",
            "sau rieng",
            "thanh long",
            "xoai",
            "cu",
            "cay an trai",
        )

    def fetch_prices(self, crop_name: str | None = None, region: str | None = None) -> list[dict]:
        from app.integrations.winmart_price_client import winmart_price_client

        return winmart_price_client.fetch_prices(crop_name=crop_name, region=region)

    def fetch_current_price(self, crop_name: str, region: str | None = None) -> dict | None:
        records = self.fetch_prices(crop_name=crop_name, region=region)
        return records[0] if records else None

    def fetch_price_history(self, crop_name: str, region: str | None = None, days: int = 30) -> list[dict]:
        records = self.fetch_prices(crop_name=crop_name, region=region)
        if not records:
            return []
        cutoff = date.today() - timedelta(days=max(days, 1))
        history: list[dict] = []

        for record in records:
            price_date = record.get("price_date")
            if isinstance(price_date, str):
                try:
                    price_date = datetime.fromisoformat(price_date).date()
                except ValueError:
                    price_date = None
            if isinstance(price_date, date) and price_date >= cutoff:
                history.append(record)
        return history

    def _fetch_page(self) -> str:
        response = resilient_request(
            "GET",
            self.source_url,
            headers=self._headers(),
            timeout=self.timeout,
            retries=self.retries,
            backoff=float(getattr(settings, "EXTERNAL_BACKOFF_SECONDS", 0.4)),
            service_name="thitruongnongsan_price",
        )
        return response.text

    def _parse_prices(self, content: str, *, crop_name: str | None, region: str | None) -> list[dict]:
        soup = BeautifulSoup(content, "lxml")
        records: list[dict] = []
        normalized_crop = normalize_text(crop_name or "")
        normalized_region = normalize_text(region or "")
        fetched_at = datetime.now()

        table_candidates = soup.find_all("table")
        for table in table_candidates:
            headers = self._table_headers(table)
            if not headers:
                continue
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = [self._clean_html(cell.get_text(" ", strip=True)) for cell in row.find_all(["td", "th"])]
                if len(cells) < 2:
                    continue
                parsed = self._row_to_record(cells, headers=headers, fetched_at=fetched_at)
                if not parsed:
                    continue
                if normalized_crop and not self._crop_matches(normalized_crop, parsed["crop_name"], parsed.get("metadata", {})):
                    continue
                if normalized_region and not self._region_matches(normalized_region, parsed["region"]):
                    continue
                records.append(parsed)

        if not records:
            logger.error(
                "Parse tables yielded 0 records from %s (crop_name=%s, region=%s)",
                self.source_url,
                crop_name,
                region,
            )
            records.extend(
                self._parse_text_fallback(
                    soup,
                    normalized_crop=normalized_crop,
                    normalized_region=normalized_region,
                    fetched_at=fetched_at,
                )
            )


        deduped: list[dict] = []
        seen: set[tuple[str, str, str, float, str]] = set()
        for record in records:
            key = (
                normalize_text(record.get("crop_name") or ""),
                normalize_text(record.get("region") or ""),
                normalize_text(record.get("source_url") or ""),
                float(record.get("price") or 0),
                str(record.get("price_date") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(record)

        return deduped

    def _parse_text_fallback(
        self,
        soup: BeautifulSoup,
        *,
        normalized_crop: str,
        normalized_region: str,
        fetched_at: datetime,
    ) -> list[dict]:
        text = self._clean_html(soup.get_text(" ", strip=True))
        candidates: list[dict] = []

        patterns = [
            r"(?P<product>[A-Za-zÀ-ỹ0-9\s\-]{3,80})(?P<region>\s+[A-Za-zÀ-ỹ0-9\s\-]{2,50})?(?:\:|\-|\–|\—)?\s*(?P<price>\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:vnđ|vnd|đ|d)?(?:/kg|kg|k?g)?",
            r"(?P<price>\d{1,3}(?:[.,]\d{3})+|\d{4,7})\s*(?:vnđ|vnd|đ|d)?(?:/kg|kg|k?g)?\s*(?P<product>[A-Za-zÀ-ỹ0-9\s\-]{3,80})",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                product = self._clean_text(match.groupdict().get("product"))
                region = self._clean_text(match.groupdict().get("region")) or "Việt Nam"
                price = self._parse_price(match.groupdict().get("price"))
                if not product or price is None:
                    continue
                record = self._build_record(
                    crop_name=self._infer_crop_name(product, normalized_crop),
                    product_name=product,
                    region=region,
                    price=price,
                    source_url=self.source_url,
                    fetched_at=fetched_at,
                    metadata={"matched_text": match.group(0)[:240]},
                )
                if normalized_crop and not self._crop_matches(normalized_crop, record["crop_name"], record.get("metadata", {})):
                    continue
                if normalized_region and not self._region_matches(normalized_region, record["region"]):
                    continue
                candidates.append(record)

        return candidates[:20]

    def _row_to_record(self, cells: list[str], *, headers: list[str], fetched_at: datetime) -> dict | None:
        header_map = {self._normalize_header(header): idx for idx, header in enumerate(headers)}
        row_text = " | ".join(cells)

        product = self._pick_cell(cells, header_map, ("san pham", "mat hang", "ten", "ten san pham", "nong san", "product", "commodity"))
        region = self._pick_cell(cells, header_map, ("khu vuc", "vung", "noi ban", "dia phuong", "tinh", "region", "province", "area"))
        price_text = self._pick_cell(cells, header_map, ("gia", "gia ban", "price", "don gia", "muc gia", "price/kg", "price per kg"))
        date_text = self._pick_cell(cells, header_map, ("ngay", "thoi gian", "date", "updated", "cap nhat", "published"))
        market_type = self._pick_cell(cells, header_map, ("thi truong", "market", "loai thi truong", "market type"))
        unit = self._pick_cell(cells, header_map, ("don vi", "unit", "dvt")) or "VNĐ/kg"

        if not product and not price_text:
            return None

        price = self._parse_price(price_text)
        if price is None:
            price = self._price_from_row_text(row_text)
        if price is None:
            return None

        price_date = self._parse_date(date_text) or date.today()
        product_name = self._clean_text(product) or self._guess_product_from_text(row_text)
        region_name = self._clean_text(region) or "Việt Nam"
        crop_name = self._infer_crop_name(product_name, normalize_text(product_name))

        return self._build_record(
            crop_name=crop_name,
            product_name=product_name,
            region=region_name,
            price=price,
            source_url=self.source_url,
            fetched_at=fetched_at,
            price_date=price_date.isoformat() if hasattr(price_date, "isoformat") else price_date,
            unit=unit or "VNĐ/kg",
            market_type=market_type or "official_vietnam_agriculture",

            metadata={
                "row_text": row_text[:400],
                "headers": headers,
            },
        )

    def _build_record(
        self,
        *,
        crop_name: str,
        product_name: str,
        region: str,
        price: float,
        source_url: str,
        fetched_at: datetime,
        price_date: date | None = None,
        unit: str = "VNĐ/kg",
        market_type: str = "official_vietnam_agriculture",
        metadata: dict[str, Any] | None = None,
    ) -> dict:
        final_date = price_date or date.today()
        final_price_date = final_date.isoformat() if hasattr(final_date, "isoformat") else str(final_date)
        final_price_date_obj = date.fromisoformat(final_price_date) if isinstance(final_price_date, str) else final_date

        return {
            "crop_name": crop_name,
            "region": region,
            "price": round(float(price), 2),
            "unit": unit or "VNĐ/kg",
            "currency": "VND",
            "price_date": final_price_date,
            "market_type": market_type or "official_vietnam_agriculture",
            "source_name": self.source_name,
            "source_url": source_url,
            "source_type": "official_vietnam_agriculture",
            "fetched_at": fetched_at,
            "observed_at": datetime.combine(final_price_date_obj, datetime.min.time()),

            "is_realtime": True,
            "is_mock": False,
            "metadata": {
                "official_product_name": product_name,
                "source_url": source_url,
                **(metadata or {}),
            },
        }

    @staticmethod
    def _table_headers(table) -> list[str]:
        first_row = table.find("tr")
        if not first_row:
            return []
        cells = first_row.find_all(["th", "td"])
        return [ThiTruongNongSanPriceClient._clean_html(cell.get_text(" ", strip=True)) for cell in cells]

    @staticmethod
    def _pick_cell(cells: list[str], header_map: dict[str, int], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            idx = header_map.get(key)
            if idx is not None and idx < len(cells):
                value = cells[idx]
                if value:
                    return value
        return None

    @staticmethod
    def _normalize_header(value: str | None) -> str:
        return normalize_text(value or "").replace("-", " ").replace("_", " ").strip()

    @staticmethod
    def _clean_html(value: str | None) -> str:
        text = html.unescape(value or "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _clean_text(value: str | None) -> str:
        if not value:
            return ""
        text = ThiTruongNongSanPriceClient._clean_html(value)
        text = re.sub(r"^[\-\:\|]+", "", text).strip()
        return text

    @staticmethod
    def _parse_price(value: Any) -> float | None:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().lower()
        if not text:
            return None
        digits = re.sub(r"[^\d,\.]", "", text)
        if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", digits):
            digits = digits.replace(".", "").replace(",", "")
        else:
            digits = digits.replace(",", "")
        try:
            price = float(digits)
        except ValueError:
            return None
        return price if price > 0 else None

    @staticmethod
    def _price_from_row_text(text: str) -> float | None:
        candidates = re.findall(r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})", text)
        for candidate in candidates:
            price = ThiTruongNongSanPriceClient._parse_price(candidate)
            if price:
                return price
        return None

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if isinstance(value, date):
            return value
        text = str(value or "").strip()
        if not text:
            return None
        text = text.replace("Ngày", "").replace("ngày", "").strip()
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"):
            try:
                return datetime.strptime(text[:10], fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _guess_product_from_text(text: str) -> str:
        return ThiTruongNongSanPriceClient._clean_text(text[:120]) or "Nông sản"

    @staticmethod
    def _infer_crop_name(product_name: str, normalized_crop: str) -> str:
        product = normalize_text(product_name)
        if normalized_crop:
            if "ca phe" in normalized_crop:
                return "ca phe"
            if any(token in normalized_crop for token in ("lua", "gao")):
                return "lua"
            if "ho tieu" in normalized_crop:
                return "ho tieu"
            if "cao su" in normalized_crop:
                return "cao su"
            if "sau rieng" in normalized_crop:
                return "sau rieng"
            if "thanh long" in normalized_crop:
                return "thanh long"
            if "xoai" in normalized_crop:
                return "xoai"
            if "rau" in normalized_crop:
                return "rau"
        mapping = {
            "ca phe": ("ca phe", "coffee"),
            "lua": ("lua", "gao", "rice", "paddy"),
            "ho tieu": ("ho tieu", "tieu", "pepper"),
            "cao su": ("cao su", "rubber"),
            "sau rieng": ("sau rieng", "durian"),
            "thanh long": ("thanh long", "dragon fruit"),
            "xoai": ("xoai", "mango"),
            "rau": ("rau", "cu", "qua", "vegetable", "fruit"),
            "rau qua": ("rau", "cu", "qua", "vegetable", "fruit"),
        }
        for crop, keywords in mapping.items():
            if any(keyword in product for keyword in keywords):
                return crop
        return normalized_crop or "rau"

    @staticmethod
    def _crop_matches(normalized_crop: str, crop_name: str, metadata: dict[str, Any]) -> bool:
        target = normalize_text(crop_name)
        meta_text = normalize_text(json.dumps(metadata, ensure_ascii=False))
        if not normalized_crop:
            return True
        if normalized_crop in target or target in normalized_crop:
            return True
        aliases = {
            "ca phe": ("ca phe", "coffee"),
            "lua": ("lua", "gao", "rice", "paddy"),
            "gao": ("lua", "gao", "rice", "paddy"),
            "ho tieu": ("ho tieu", "pepper", "tieu"),
            "cao su": ("cao su", "rubber"),
            "sau rieng": ("sau rieng", "durian"),
            "thanh long": ("thanh long", "dragon fruit"),
            "xoai": ("xoai", "mango"),
            "rau": ("rau", "cu", "qua", "vegetable", "fruit"),
            "rau qua": ("rau", "cu", "qua", "vegetable", "fruit"),
        }
        accepted = aliases.get(normalized_crop, (normalized_crop,))
        return any(keyword in target or keyword in meta_text for keyword in accepted)

    @staticmethod
    def _region_matches(normalized_region: str, region: str) -> bool:
        if not normalized_region:
            return True
        return normalized_region in normalize_text(region) or normalize_text(region) in normalized_region

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0; +https://thitruongnongsan.gov.vn)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }


thitruong_nongsan_price_client = ThiTruongNongSanPriceClient()
