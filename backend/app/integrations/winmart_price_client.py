from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Any

from app.core.config import settings
from app.core.real_data import external_circuit_breaker
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text

logger = logging.getLogger(__name__)


WINMART_SOURCE_NAME = "WinMart"
WINMART_SOURCE_URL = "https://winmart.vn/"


class WinMartPriceClient:
    """Fetch retail product prices directly from WinMart's public search API."""

    SOURCE_NAME = WINMART_SOURCE_NAME
    SOURCE_URL = WINMART_SOURCE_URL

    PRODUCT_URL = "https://winmart.vn/products/{seo_name}"

    def __init__(self) -> None:
        self.base_url = (getattr(settings, "WINMART_API_BASE_URL", "") or "https://api-crownx.winmart.vn").rstrip("/")
        self.search_endpoint = (
            getattr(settings, "WINMART_ITEM_SEARCH_ENDPOINT", "") or "/ss/api/v2/public/winmart/item-search"
        )
        self.store_no = str(getattr(settings, "WINMART_STORE_NO", "") or "1535")
        self.store_group_code = str(getattr(settings, "WINMART_STORE_GROUP_CODE", "") or "1998")
        self.application_type = str(getattr(settings, "WINMART_APPLICATION_TYPE", "") or "Winmart")
        self.timeout = build_timeout(
            total=min(float(getattr(settings, "EXTERNAL_TOTAL_TIMEOUT_SECONDS", 12.0)), 12.0),
            connect=min(float(getattr(settings, "EXTERNAL_CONNECT_TIMEOUT_SECONDS", 3.0)), 3.0),
            read=min(float(getattr(settings, "EXTERNAL_READ_TIMEOUT_SECONDS", 8.0)), 8.0),
        )
        self.retries = min(max(int(getattr(settings, "EXTERNAL_RETRY_COUNT", 1)), 1), 2)

    def fetch_prices(self, crop_name: str | None = None, region: str | None = None) -> list[dict[str, Any]]:
        if not getattr(settings, "WINMART_ENABLED", True):
            return []

        selected_crop = normalize_text(crop_name or "rau") or "rau"
        key = f"winmart_price:{selected_crop}"
        external_circuit_breaker.before_call(key)

        try:
            candidates: list[dict[str, Any]] = []
            seen: set[str] = set()
            for query in self._queries_for_crop(crop_name or selected_crop):
                for item in self._search_items(query):
                    sku = str(item.get("sku") or item.get("id") or item.get("seoName") or "")
                    if sku and sku in seen:
                        continue
                    record = self._item_to_record(
                        item,
                        requested_crop=selected_crop,
                        requested_region=region,
                        query=query,
                    )
                    if not record:
                        continue
                    seen.add(sku)
                    candidates.append(record)

            if not candidates:
                external_circuit_breaker.record_failure(key, "no WinMart prices parsed")
                return []

            candidates.sort(key=lambda record: record["metadata"].get("match_score", 0), reverse=True)
            external_circuit_breaker.record_success(key)
            return [candidates[0]]
        except Exception as exc:
            external_circuit_breaker.record_failure(key, exc)
            logger.warning("[WinMartPrice] failed crop=%s region=%s error=%s", crop_name, region, exc)
            return []

    def fetch_current_price(self, crop_name: str, region: str | None = None) -> dict[str, Any] | None:
        records = self.fetch_prices(crop_name=crop_name, region=region)
        return records[0] if records else None

    def _search_items(self, keyword: str) -> list[dict[str, Any]]:
        payload = {
            "keyword": keyword,
            "storeNo": self.store_no,
            "storeGroupCode": self.store_group_code,
            "applicationType": self.application_type,
            "pageNumber": 1,
            "pageSize": 12,
        }
        response = resilient_request(
            "POST",
            f"{self.base_url}{self.search_endpoint}",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
            retries=self.retries,
            backoff=float(getattr(settings, "EXTERNAL_BACKOFF_SECONDS", 0.4)),
            service_name="winmart_price",
        )
        data = response.json()
        items = data.get("data") if isinstance(data, dict) else []
        if isinstance(items, dict):
            items = items.get("itemUoms") or items.get("items") or []
        return items if isinstance(items, list) else []

    def _item_to_record(
        self,
        item: dict[str, Any],
        *,
        requested_crop: str,
        requested_region: str | None,
        query: str,
    ) -> dict[str, Any] | None:
        product_name = self._product_name(item)
        price = self._product_price(item)
        if not product_name or price is None:
            return None
        if not self._is_available(item):
            return None
        if not self._is_food_item(item):
            return None
        if not self._product_matches(product_name, query, requested_crop):
            return None

        package_kg = self._extract_package_kg(product_name, item)
        if not package_kg:
            return None

        price_per_kg = round(float(price) / package_kg, 2)
        if price_per_kg <= 0:
            return None

        seo_name = str(item.get("seoName") or "").strip()
        source_url = self.PRODUCT_URL.format(seo_name=seo_name) if seo_name else self.SOURCE_URL
        fetched_at = datetime.now()
        region = self._region_label(requested_region)
        match_score = self._match_score(product_name, query, requested_crop, item)

        return {
            "crop_name": requested_crop,
            "region": region,
            "price": price_per_kg,
            "unit": "VND/kg",
            "currency": "VND",
            "price_date": date.today().isoformat(),
            "quality_grade": "grade_1",
            "market_type": "retail",
            "source_name": self.SOURCE_NAME,
            "source_url": source_url,
            "source_type": "winmart_retail_price",
            "fetched_at": fetched_at,
            "observed_at": fetched_at,
            "is_realtime": True,
            "is_mock": False,
            "confidence_score": min(0.92, 0.7 + match_score / 100),
            "metadata": {
                "retailer": self.SOURCE_NAME,
                "product_name": product_name,
                "raw_price": price,
                "package_kg": package_kg,
                "sku": item.get("sku"),
                "item_no": item.get("itemNo"),
                "uom": item.get("uom"),
                "uom_name": item.get("uomName"),
                "store_no": self.store_no,
                "store_group_code": self.store_group_code,
                "requested_region": requested_region,
                "query": query,
                "match_score": match_score,
            },
        }

    @staticmethod
    def _product_name(item: dict[str, Any]) -> str:
        description = str(item.get("description") or "").strip()
        long_description = str(item.get("longDescription") or "").strip()
        if description and long_description:
            desc_key = normalize_text(description)
            long_key = normalize_text(long_description)
            if desc_key in long_key or long_key in desc_key:
                return description if len(description) <= len(long_description) else long_description
            return f"{description} {long_description}".strip()
        return description or long_description or str(item.get("name") or "").strip()

    @staticmethod
    def _product_price(item: dict[str, Any]) -> float | None:
        price_data = item.get("price") if isinstance(item.get("price"), dict) else {}
        raw_price = price_data.get("salePrice") or price_data.get("originPrice") or item.get("salePrice") or item.get("price")
        try:
            price = float(raw_price)
        except (TypeError, ValueError):
            return None
        return price if price > 0 else None

    @staticmethod
    def _is_available(item: dict[str, Any]) -> bool:
        price_data = item.get("price") if isinstance(item.get("price"), dict) else {}
        if price_data.get("publish") is False:
            return False
        warehouse = item.get("warehouse") if isinstance(item.get("warehouse"), dict) else {}
        available_quantity = warehouse.get("availableQuantity")
        if available_quantity is None:
            return True
        try:
            return float(available_quantity) > 0
        except (TypeError, ValueError):
            return True

    @staticmethod
    def _is_food_item(item: dict[str, Any]) -> bool:
        text = normalize_text(
            " ".join(
                str(item.get(key) or "")
                for key in ("mch1Name", "mch2Name", "mch3Name", "mch4Name", "mch5Name", "categoryName")
            )
        )
        if not text:
            return True
        if "phi thuc pham" in text:
            return False
        return any(token in text for token in ("thuc pham", "tuoi song", "rau", "cu", "qua", "nong san"))

    @classmethod
    def _product_matches(cls, product_name: str, query: str, requested_crop: str) -> bool:
        product_lower = product_name.lower()
        query_lower = query.lower().strip()
        if query_lower and query_lower in product_lower:
            return True

        product_key = normalize_text(product_name)
        crop_key = normalize_text(requested_crop)
        aliases = cls._aliases_for_crop(crop_key)
        return any(alias and alias in product_key for alias in aliases)

    @classmethod
    def _match_score(cls, product_name: str, query: str, requested_crop: str, item: dict[str, Any]) -> int:
        product_lower = product_name.lower()
        product_key = normalize_text(product_name)
        query_lower = query.lower().strip()
        crop_key = normalize_text(requested_crop)
        score = 0
        if query_lower and query_lower in product_lower:
            score += 30
        for alias in cls._aliases_for_crop(crop_key):
            if alias and alias in product_key:
                score += 20
        if cls._extract_package_kg(product_name, item):
            score += 15
        if (item.get("warehouse") or {}).get("availableQuantity"):
            score += 10
        return score

    @staticmethod
    def _extract_package_kg(product_name: str, item: dict[str, Any] | None = None) -> float | None:
        text = f"{product_name} {item.get('uomName', '') if item else ''} {item.get('uom', '') if item else ''}"
        normalized = normalize_text(text)
        if re.search(r"\d+(?:[.,]\d+)?\s*(?:ml|lit|l)\b", normalized) and not re.search(
            r"\d+(?:[.,]\d+)?\s*(?:kg|g|gr|gram|gam)\b", normalized
        ):
            return None

        multi_gram_match = re.search(r"(\d+)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:g|gr|gram|gam)", normalized)
        if multi_gram_match:
            packs = WinMartPriceClient._positive_float(multi_gram_match.group(1))
            grams = WinMartPriceClient._positive_float(multi_gram_match.group(2))
            if packs and grams:
                return packs * grams / 1000

        multi_kg_match = re.search(r"(\d+)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:kg|kilogram|kilo)", normalized)
        if multi_kg_match:
            packs = WinMartPriceClient._positive_float(multi_kg_match.group(1))
            kg = WinMartPriceClient._positive_float(multi_kg_match.group(2))
            if packs and kg:
                return packs * kg

        kg_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:kg|kilogram|kilo)", normalized)
        if kg_match:
            return WinMartPriceClient._positive_float(kg_match.group(1))

        gram_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:g|gr|gram|gam)\b", normalized)
        if gram_match:
            grams = WinMartPriceClient._positive_float(gram_match.group(1))
            return grams / 1000 if grams else None

        if re.search(r"\bkg\b", normalized) or str((item or {}).get("uom") or "").upper() == "KG":
            return 1.0

        return None

    @staticmethod
    def _positive_float(value: str) -> float | None:
        try:
            number = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None
        return number if number > 0 else None

    @staticmethod
    def _region_label(region: str | None) -> str:
        return " ".join((region or "WinMart Online").strip().split()) or "WinMart Online"

    @staticmethod
    def _queries_for_crop(crop_name: str) -> list[str]:
        key = normalize_text(crop_name)
        aliases = {
            "lua": ["gạo", "gạo thơm", "gạo ST25"],
            "gao": ["gạo", "gạo thơm", "gạo ST25"],
            "ca chua": ["cà chua"],
            "rau muong": ["rau muống"],
            "rau": ["rau"],
            "rau qua": ["rau", "củ quả"],
            "ca phe": ["cà phê", "cafe"],
            "ho tieu": ["tiêu", "tiêu đen", "hồ tiêu"],
            "tieu": ["tiêu", "tiêu đen"],
            "chuoi": ["chuối"],
            "xoai": ["xoài"],
            "sau rieng": ["sầu riêng"],
            "thanh long": ["thanh long"],
            "khoai lang": ["khoai lang"],
            "khoai tay": ["khoai tây"],
            "dua hau": ["dưa hấu"],
            "dua chuot": ["dưa chuột", "dưa leo"],
        }
        values = aliases.get(key, [crop_name.strip() or key or "rau"])
        deduped: list[str] = []
        for value in values:
            if value and value not in deduped:
                deduped.append(value)
        return deduped

    @staticmethod
    def _aliases_for_crop(crop_key: str) -> tuple[str, ...]:
        aliases = {
            "lua": ("gao", "gao thom", "gao st25"),
            "gao": ("gao", "gao thom", "gao st25"),
            "ca chua": ("ca chua",),
            "rau muong": ("rau muong",),
            "rau": ("rau",),
            "rau qua": ("rau", "cu qua"),
            "ca phe": ("ca phe", "cafe"),
            "ho tieu": ("ho tieu", "tieu den", "tieu xanh", "tieu"),
            "tieu": ("tieu den", "tieu xanh", "tieu"),
            "chuoi": ("chuoi",),
            "xoai": ("xoai",),
            "sau rieng": ("sau rieng",),
            "thanh long": ("thanh long",),
            "khoai lang": ("khoai lang",),
            "khoai tay": ("khoai tay",),
            "dua hau": ("dua hau",),
            "dua chuot": ("dua chuot", "dua leo"),
        }
        return aliases.get(crop_key, (crop_key,))

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0; +https://winmart.vn)",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://winmart.vn",
            "Referer": "https://winmart.vn/",
            "X-API-MERCHANT": "WCM",
        }


winmart_price_client = WinMartPriceClient()
