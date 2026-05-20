from __future__ import annotations

import html
import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.real_data import external_circuit_breaker
from app.core.resilience import build_timeout, resilient_request
from app.repositories.common import normalize_text

logger = logging.getLogger(__name__)


class ThiTruongNongSanNewsClient:
    def __init__(self) -> None:
        self.source_name = "Thông tin thị trường nông sản"
        self.source_url = (settings.THITRUONG_NONGSAN_NEWS_URL or "https://thitruongnongsan.gov.vn/vn/xc0_tin-tuc.html").strip()
        self.timeout = build_timeout(
            total=min(float(getattr(settings, "EXTERNAL_TOTAL_TIMEOUT_SECONDS", 12.0)), 12.0),
            connect=min(float(getattr(settings, "EXTERNAL_CONNECT_TIMEOUT_SECONDS", 3.0)), 3.0),
            read=min(float(getattr(settings, "EXTERNAL_READ_TIMEOUT_SECONDS", 8.0)), 8.0),
        )
        self.retries = min(max(int(getattr(settings, "EXTERNAL_RETRY_COUNT", 1)), 1), 2)

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (compatible; NongNghiepAI/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7",
        }

    def fetch_latest_news(
        self,
        limit: int = 20,
        crop_name: str | None = None,
        region: str | None = None,
    ) -> list[dict]:
        if not getattr(settings, "ENABLE_THITRUONG_NONGSAN_NEWS", True):
            return []

        key = "thitruongnongsan_official_news"
        external_circuit_breaker.before_call(key)
        try:
            page = self._fetch_page()
            records = self._parse_news(page, limit=limit, crop_name=crop_name, region=region)
            external_circuit_breaker.record_success(key)
            return records
        except Exception as exc:
            external_circuit_breaker.record_failure(key, exc)
            logger.exception("Failed to fetch official agriculture news: %s", exc)
            return []

    def fetch_news_detail(self, url: str) -> dict | None:
        if not url:
            return None

        key = f"thitruongnongsan_official_news_detail:{normalize_text(url)}"
        external_circuit_breaker.before_call(key)
        try:
            response = resilient_request(
                "GET",
                url,
                headers=self._headers(),
                timeout=self.timeout,
                retries=self.retries,
                backoff=float(getattr(settings, "EXTERNAL_BACKOFF_SECONDS", 0.4)),
                service_name="thitruongnongsan_news",
            )
            detail = self._parse_detail(response.text, url=response.url or url)
            external_circuit_breaker.record_success(key)
            return detail
        except Exception as exc:
            external_circuit_breaker.record_failure(key, exc)
            logger.exception("Failed to fetch official agriculture news detail: %s", exc)
            return None

    def _fetch_page(self) -> str:
        response = resilient_request(
            "GET",
            self.source_url,
            headers=self._headers(),
            timeout=self.timeout,
            retries=self.retries,
            backoff=float(getattr(settings, "EXTERNAL_BACKOFF_SECONDS", 0.4)),
            service_name="thitruongnongsan_news",
        )
        return response.text

    def _parse_news(
        self,
        content: str,
        *,
        limit: int,
        crop_name: str | None,
        region: str | None,
    ) -> list[dict]:
        soup = BeautifulSoup(content, "lxml")
        article_nodes = self._find_article_nodes(soup)
        records: list[dict] = []
        fetched_at = datetime.now()
        normalized_crop = normalize_text(crop_name or "")
        normalized_region = normalize_text(region or "")

        for node in article_nodes:
            record = self._parse_article_node(node, fetched_at=fetched_at)
            if not record:
                continue
            if normalized_crop and not self._tags_match(normalized_crop, record.get("crop_tags", []), record.get("title", ""), record.get("summary", "")):
                continue
            if normalized_region and not self._tags_match(normalized_region, record.get("region_tags", []), record.get("title", ""), record.get("summary", "")):
                continue
            records.append(record)
            if len(records) >= limit:
                break

        # Không dùng fallback tạo record khi không parse được source_url.
        return records[:limit]


    def _parse_detail(self, content: str, *, url: str) -> dict | None:
        soup = BeautifulSoup(content, "lxml")
        node = self._find_best_title_node(soup)
        title = self._extract_title(node, soup)
        summary = self._extract_summary(soup)
        published_at = self._extract_published_at(soup)
        category = self._extract_category(soup)
        text = self._clean_text(f"{title} {summary or ''} {self._page_text(soup)}")
        crop_tags = self._infer_crop_tags(text)
        region_tags = self._infer_region_tags(text)
        sentiment = self._infer_sentiment(text)
        impact_level = self._impact_level(sentiment, text)

        if not title:
            return None

        now = datetime.now()
        published = published_at or now
        return {
            "title": title,
            "summary": summary,
            "source_name": self.source_name,
            "source_url": url,
            "published_at": published,
            "fetched_at": now,
            "crop_tags": crop_tags,
            "region_tags": region_tags,
            "sentiment": sentiment,
            "impact_level": impact_level,
            "source_type": "official_government_source",
            "is_realtime": True,
            "is_mock": False,
            "category": category,
            "impact_score": self._impact_score(sentiment, text),
            "metadata": {"source_url": url},
        }


    def _parse_article_node(self, node, *, fetched_at: datetime) -> dict | None:
        link = node.find("a", href=True)
        title = self._extract_title(node)
        if link and not title:
            title = self._clean_text(link.get_text(" ", strip=True))
        summary = self._extract_summary_from_node(node)

        href = link.get("href") if link else None
        if not href:
            # Tin nào thiếu source_url => bỏ qua
            return None
        source_url = urljoin(self.source_url, href)

        if not title:
            return None


        text = self._clean_text(f"{title} {summary or ''} {node.get_text(' ', strip=True)}")
        published_at = self._extract_date_from_text(text)
        category = self._extract_category_from_text(text)
        crop_tags = self._infer_crop_tags(text)
        region_tags = self._infer_region_tags(text)
        sentiment = self._infer_sentiment(text)
        impact_level = self._impact_level(sentiment, text)
        now = datetime.now()

        return {
            "title": title,
            "summary": summary,
            "content": summary,
            "url": source_url,
            "source_url": source_url,
            "source_name": self.source_name,
            "published_at": published_at or now,
            "fetched_at": now,
            "category": category,
            "crop_tags": crop_tags,
            "region_tags": region_tags,
            "sentiment": sentiment,
            "impact_level": impact_level,
            "impact_score": self._impact_score(sentiment, text),
            "is_realtime": True,
            "is_mock": False,
            "metadata": {"listing_url": self.source_url},
        }

    def _parse_text_fallback(
        self,
        soup: BeautifulSoup,
        *,
        limit: int,
        fetched_at: datetime,
        crop_name: str,
        region: str,
    ) -> list[dict]:

        text = self._page_text(soup)
        snippets = re.split(r"(?:\n|\r|\|){2,}", text)
        records: list[dict] = []
        for snippet in snippets:
            clean = self._clean_text(snippet)
            if len(clean) < 40:
                continue
            if not any(keyword in normalize_text(clean) for keyword in ("nong san", "gia", "thi truong", "cafe", "ca phe", "lua", "gao", "rau", "ho tieu", "sau rieng", "thanh long", "xoai")):
                continue
            title = clean[:160]
            published_at = self._extract_date_from_text(clean)
            crop_tags = self._infer_crop_tags(clean)
            region_tags = self._infer_region_tags(clean)
            if crop_name and not self._tags_match(crop_name, crop_tags, title, clean):
                continue
            if region and not self._tags_match(region, region_tags, title, clean):
                continue
            records.append(
                {
                    "title": title,
                    "summary": clean[160:360] or None,
                    "content": clean[:2000],
                    "url": self.source_url,
                    "source_url": self.source_url,
                    "source_name": self.source_name,
                    "published_at": published_at or fetched_at,
                    "fetched_at": fetched_at,
                    "category": self._extract_category_from_text(clean),
                    "crop_tags": crop_tags,
                    "region_tags": region_tags,
                    "sentiment": self._infer_sentiment(clean),
                    "impact_level": self._impact_level(self._infer_sentiment(clean), clean),
                    "impact_score": self._impact_score(self._infer_sentiment(clean), clean),
                    "is_realtime": True,
                    "is_mock": False,
                    "metadata": {"source_url": self.source_url},
                }
            )
            if len(records) >= limit:
                break
        return records

    @staticmethod
    def _find_article_nodes(soup: BeautifulSoup) -> list:
        selectors = [
            "article",
            ".news-item",
            ".tin_tuc",
            ".news-list li",
            ".list-news li",
            ".item-news",
            ".khung_dv_con",
            ".descript_dv",
            ".news",
        ]
        nodes = []
        for selector in selectors:
            nodes.extend(soup.select(selector))
        if nodes:
            return nodes
        return soup.find_all("a", href=True)

    @staticmethod
    def _find_best_title_node(soup: BeautifulSoup):
        for selector in ("h1", "h2", "h3", ".title", ".title_dv", ".news-title", "article h1", "article h2"):
            node = soup.select_one(selector)
            if node and ThiTruongNongSanNewsClient._clean_text(node.get_text(" ", strip=True)):
                return node
        return None

    def _extract_title(self, node, soup: BeautifulSoup | None = None) -> str | None:
        if node is None:
            return None
        if getattr(node, "name", None) == "a":
            return self._clean_text(node.get_text(" ", strip=True))
        link = node.find("a")
        if link:
            return self._clean_text(link.get_text(" ", strip=True))
        text = self._clean_text(node.get_text(" ", strip=True))
        if len(text) > 200:
            return text[:200]
        return text or None

    @staticmethod
    def _extract_summary_from_node(node) -> str | None:
        for selector in (".summary", ".descript_dv", ".excerpt", ".description", "p"):
            found = node.select_one(selector) if hasattr(node, "select_one") else None
            if found:
                text = ThiTruongNongSanNewsClient._clean_text(found.get_text(" ", strip=True))
                if text:
                    return text
        text = ThiTruongNongSanNewsClient._clean_text(node.get_text(" ", strip=True))
        if len(text) > 120:
            return text[:280]
        return None

    @staticmethod
    def _extract_summary(soup: BeautifulSoup) -> str | None:
        for selector in (".summary", ".descript_dv", ".excerpt", ".description", ".article-summary", "p"):
            found = soup.select_one(selector)
            if found:
                text = ThiTruongNongSanNewsClient._clean_text(found.get_text(" ", strip=True))
                if text:
                    return text
        return None

    @staticmethod
    def _extract_category(soup: BeautifulSoup) -> str | None:
        breadcrumbs = soup.select(".breadcrumb a, .breadcrumbs a, nav a")
        for item in breadcrumbs:
            text = ThiTruongNongSanNewsClient._clean_text(item.get_text(" ", strip=True))
            if text and normalize_text(text) not in {"trang chu", "home"}:
                return text
        return None

    @staticmethod
    def _extract_category_from_text(text: str) -> str | None:
        normalized = normalize_text(text)
        if "thi truong" in normalized:
            return "Thị trường"
        if "gia ca phe" in normalized or "ca phe" in normalized:
            return "Cà phê"
        if "lua" in normalized or "gao" in normalized:
            return "Lúa gạo"
        if "rau" in normalized:
            return "Rau quả"
        if "ho tieu" in normalized:
            return "Hồ tiêu"
        if "sau rieng" in normalized:
            return "Sầu riêng"
        if "thanh long" in normalized:
            return "Thanh long"
        if "xoai" in normalized:
            return "Xoài"
        return None

    @staticmethod
    def _extract_date_from_text(text: str) -> datetime | None:
        patterns = [
            r"(\d{1,2}/\d{1,2}/\d{4})",
            r"(\d{1,2}-\d{1,2}-\d{4})",
            r"(\d{4}-\d{1,2}-\d{1,2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if not match:
                continue
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(match.group(1), fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _extract_published_at(soup: BeautifulSoup) -> datetime | None:
        text = ""
        for selector in (".time_up", ".date", ".published", "time"):
            found = soup.select_one(selector)
            if found:
                text = ThiTruongNongSanNewsClient._clean_text(found.get_text(" ", strip=True))
                if text:
                    break
        if text:
            parsed = ThiTruongNongSanNewsClient._extract_date_from_text(text)
            if parsed:
                return parsed
        return None

    @staticmethod
    def _infer_crop_tags(text: str) -> list[str]:
        normalized = normalize_text(text)
        mapping = {
            "ca phe": ("ca phe", "coffee"),
            "lua": ("lua", "gao", "rice", "paddy"),
            "rau": ("rau", "cu", "qua", "vegetable", "fruit"),
            "ho tieu": ("ho tieu", "pepper", "tieu"),
            "cao su": ("cao su", "rubber"),
            "sau rieng": ("sau rieng", "durian"),
            "thanh long": ("thanh long", "dragon fruit"),
            "xoai": ("xoai", "mango"),
        }
        tags: list[str] = []
        for label, keywords in mapping.items():
            if any(keyword in normalized for keyword in keywords):
                tags.append(label)
        return tags

    @staticmethod
    def _infer_region_tags(text: str) -> list[str]:
        normalized = normalize_text(text)
        regions = {
            "Việt Nam": ("viet nam", "vn", "toan quoc", "cả nước"),
            "Đắk Lắk": ("dak lak", "daklak", "buon ma thuot"),
            "Lâm Đồng": ("lam dong", "lamdong", "bao loc", "da lat"),
            "Gia Lai": ("gia lai", "pleiku"),
            "Đồng Nai": ("dong nai",),
            "Tiền Giang": ("tien giang",),
            "Long An": ("long an",),
            "Bình Thuận": ("binh thuan",),
            "TP.HCM": ("tp hcm", "tphcm", "ho chi minh", "sai gon"),
            "Hà Nội": ("ha noi", "hanoi"),
            "Cần Thơ": ("can tho", "cantho"),
        }
        tags: list[str] = []
        for label, keywords in regions.items():
            if any(keyword in normalized for keyword in keywords):
                tags.append(label)
        return tags

    @staticmethod
    def _infer_sentiment(text: str) -> str:
        normalized = normalize_text(text)
        positive = ("tang", "tăng", "cao", "ky luc", "kỷ lục", "hoi phuc", "hồi phục", "thuan loi", "thuận lợi")
        negative = ("giam", "giảm", "ap luc", "áp lực", "sut", "sụt", "rui ro", "rủi ro", "lao doc", "lao dốc")
        score = sum(token in normalized for token in positive) - sum(token in normalized for token in negative)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    @staticmethod
    def _impact_score(sentiment: str, text: str) -> float:
        density = min(max(len(text) / 1000.0, 0.2), 1.0)
        if sentiment == "positive":
            return round(0.7 + density * 0.2, 2)
        if sentiment == "negative":
            return round(0.7 + density * 0.2, 2)
        return round(0.45 + density * 0.1, 2)

    @staticmethod
    def _impact_level(sentiment: str, text: str) -> str:
        if sentiment in {"positive", "negative"}:
            return "medium" if len(text) < 1200 else "high"
        return "low" if len(text) < 900 else "medium"

    @staticmethod
    def _tags_match(target: str, tags: list[str], title: str, summary: str | None) -> bool:
        text = normalize_text(" ".join([title, summary or "", " ".join(tags)]))
        return target in text or any(target in normalize_text(tag) or normalize_text(tag) in target for tag in tags)

    @staticmethod
    def _page_text(soup: BeautifulSoup) -> str:
        return ThiTruongNongSanNewsClient._clean_text(soup.get_text(" ", strip=True))

    @staticmethod
    def _clean_text(value: str | None) -> str:
        text = html.unescape(value or "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()


thitruong_nongsan_news_client = ThiTruongNongSanNewsClient()
