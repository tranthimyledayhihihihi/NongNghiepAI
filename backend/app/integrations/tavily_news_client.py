from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.core.real_data import external_circuit_breaker

logger = logging.getLogger(__name__)


class TavilyNewsClient:
    """Nguồn tin bổ sung từ Tavily.

    Quy tắc anti-gian lận / anti-fake:
    - Tavily chỉ là nguồn bổ sung; nguồn chính vẫn là thitruongnongsan.gov.vn
    - Không crash khi thiếu TAVILY_API_KEY
    - Nếu Tavily lỗi => log lỗi, trả [] (không làm hỏng API tin tức)
    - Chỉ lưu record có title và source_url rõ ràng
    - Chỉ giữ tin liên quan nông sản Việt Nam (filter theo keyword + tag)
    """

    source_name = "Tavily Search"
    source_type = "tavily_search_source"

    # Keyword filter: chỉ giữ nội dung liên quan nông sản ở Việt Nam
    _AGRI_KEYWORDS = (
        "nông sản",
        "nông nghiệp",
        "thị trường nông sản",
        "giá nông sản",
        "giá cà phê",
        "giá lúa gạo",
        "giá rau",
        "giá rau củ",
        "xuất khẩu nông sản",
        "thị trường cà phê",
        "thị trường lúa gạo",
        "cà phê",
        "lúa gạo",
        "lúa",
        "gạo",
        "rau",
        "rau củ",
        "hạt điều",
        "hồ tiêu",
        "sầu riêng",
        "thanh long",
        "xoài",
        "Việt Nam",
        "tin",
        "giá",
    )

    _CROP_MAP = {
        "cà phê": ("cà phê", "ca phe", "coffee"),
        "lúa": ("lúa", "lua", "gạo", "gao", "rice", "paddy"),
        "rau": ("rau", "rau củ", "rau cu", "cu", "vegetable", "fruit", "rau quả"),
        "hồ tiêu": ("hồ tiêu", "ho tieu", "pepper", "tiêu"),
        "sầu riêng": ("sầu riêng", "sau rieng", "durian"),
        "thanh long": ("thanh long", "dragon fruit"),
        "xoài": ("xoài", "xoai", "mango"),
        "hạt điều": ("hạt điều", "hat dieu", "cashew"),
    }

    _REGION_MAP = {
        "Việt Nam": ("việt nam", "viet nam", "vn"),
        "Đắk Lắk": ("đắk lắk", "dak lak", "buôn ma thuột", "buon ma thuot"),
        "Đồng bằng sông Cửu Long": ("đồng bằng sông cửu long", "dong bang song cuu long", "mekong"),
    }

    # Public query templates (the same suggestions user gave)
    _QUERY_TEMPLATES = [
        "giá nông sản Việt Nam hôm nay",
        "thị trường nông sản Việt Nam",
        "giá cà phê Việt Nam",
        "giá lúa gạo Việt Nam",
        "giá rau củ Việt Nam",
        "xuất khẩu nông sản Việt Nam",
        "thị trường cà phê Đắk Lắk",
        "thị trường lúa gạo Đồng bằng sông Cửu Long",
        "thị trường rau quả Việt Nam",
    ]

    def _get_api_key(self) -> str:
        return getattr(settings, "TAVILY_API_KEY", "") or ""

    def _is_available(self) -> bool:
        return bool(self._get_api_key())

    @staticmethod
    def _safe_text(val: Any) -> str:
        return str(val or "").strip()

    @staticmethod
    def _extract_domain(url: str) -> str:
        try:
            host = urlparse(url).netloc
            return host.lower() if host else ""
        except Exception:
            return ""

    @staticmethod
    def _guess_published_at(result: Dict[str, Any], fallback: datetime) -> str:
        # Tavily result fields are not guaranteed.
        for key in ("published_date", "published_at", "date", "datetime"):
            v = result.get(key)
            if not v:
                continue
            if isinstance(v, datetime):
                return v.isoformat()
            # string: best-effort
            s = str(v).strip()
            if not s:
                continue
            # If it already looks ISO
            if "T" in s:
                return s
            # Try common dd/mm/yyyy
            try:
                for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                    return datetime.strptime(s, fmt).isoformat()
            except Exception:
                pass
        return fallback.isoformat()

    @classmethod
    def _infer_crop_tags(cls, text: str) -> List[str]:
        t = text.lower()
        tags: List[str] = []
        for tag, keywords in cls._CROP_MAP.items():
            if any(k.lower() in t for k in keywords):
                tags.append(tag)
        return tags

    @classmethod
    def _infer_region_tags(cls, text: str) -> List[str]:
        t = text.lower()
        tags: List[str] = []
        for label, keywords in cls._REGION_MAP.items():
            if any(k.lower() in t for k in keywords):
                tags.append(label)
        # Always include Việt Nam if we see Vietnamese markers
        if "việt nam" in t or "viet nam" in t:
            if "Việt Nam" not in tags:
                tags.append("Việt Nam")
        return tags

    @staticmethod
    def _infer_sentiment(text: str) -> str:
        t = text.lower()
        positive = (
            "tăng",
            "tăng giá",
            "cải thiện",
            "hồi phục",
            "khả quan",
            "kỳ vọng",
            "kỷ lục",
            "được giá",
            "thắt chặt",
            "khan hiếm",
        )
        negative = (
            "giảm",
            "giảm giá",
            "áp lực",
            "rủi ro",
            "bất lợi",
            "tồn",
            "ế",
            "dư",
            "dịch",
            "hạn hán",
            "thiệt hại",
        )
        score = sum(tok in t for tok in positive) - sum(tok in t for tok in negative)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        return "neutral"

    @classmethod
    def _impact_level_from_sentiment(cls, sentiment: str, text: str) -> str:
        # Keep it simple/deterministic.
        length_factor = min(max(len(text) / 1500.0, 0.2), 1.0)
        if sentiment in {"positive", "negative"}:
            return "high" if length_factor > 0.75 else "medium"
        return "medium" if length_factor > 0.55 else "low"

    @classmethod
    def _is_relevant_agri_vn(cls, title: str, content: str, url: str) -> bool:
        haystack = f"{title}\n{content}\n{url}".lower()

        # Must mention VN/nông sản keywords.
        has_agri = any(k.lower() in haystack for k in cls._AGRI_KEYWORDS)
        has_vn = ("việt nam" in haystack) or ("viet nam" in haystack)
        # Allow cases where VN is implied by Vietnamese diacritics/terms.
        return has_agri and has_vn

    @classmethod
    def _tags_match_optional(cls, crop_name: Optional[str], region: Optional[str], record: Dict[str, Any]) -> bool:
        # If user provides filters, ensure record matches.
        if crop_name:
            cn = str(crop_name).strip().lower()
            hay = " ".join(record.get("crop_tags", [])).lower() + " " + record.get("title", "").lower() + " " + record.get("summary", "").lower()
            if cn and cn not in hay:
                # also allow substring in Vietnamese no-diacritics would be better,
                # but we keep it simple (repo đã có normalizer ở official client).
                return False

        if region:
            rg = str(region).strip().lower()
            hay = " ".join(record.get("region_tags", [])).lower() + " " + record.get("title", "").lower() + " " + record.get("summary", "").lower()
            if rg and rg not in hay:
                return False

        return True

    def search_agriculture_news(
        self,
        crop_name: str | None = None,
        region: str | None = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Tìm tin nông sản VN theo crop/region (Tavily chỉ bổ sung)."""
        if not self._is_available():
            return []
        circuit_key = "tavily_news"
        external_circuit_breaker.before_call(circuit_key)

        # Lazy import to avoid crashing if tavily-python not installed.
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self._get_api_key())
        except Exception as e:
            external_circuit_breaker.record_failure(circuit_key, e)
            logger.exception("[TavilyNews] Cannot init Tavily client: %s", e)
            return []

        limit = max(1, int(limit or 10))
        fallback_now = datetime.now()

        # Pick queries: prioritize those matching crop/region if possible.
        queries: List[str] = []
        if crop_name:
            cn = str(crop_name).strip().lower()
            if "cà phê" in cn or "ca phe" in cn or "coffee" in cn:
                queries.append("giá cà phê Việt Nam")
                queries.append("thị trường cà phê Đắk Lắk")
            elif "lúa" in cn or "lua" in cn or "gạo" in cn or "gao" in cn or "rice" in cn:
                queries.append("giá lúa gạo Việt Nam")
                queries.append("thị trường lúa gạo Đồng bằng sông Cửu Long")
            elif "rau" in cn or "vegetable" in cn or "rau củ" in cn:
                queries.append("giá rau củ Việt Nam")
                queries.append("thị trường rau quả Việt Nam")
            else:
                queries.append("thị trường nông sản Việt Nam")
                queries.append("giá nông sản Việt Nam hôm nay")
        else:
            queries.extend(self._QUERY_TEMPLATES)

        if region:
            rg = str(region).strip().lower()
            if "đắk lắk" in rg or "dak lak" in rg:
                queries.insert(0, "thị trường cà phê Đắk Lắk")
            if "đồng bằng" in rg or "cửu long" in rg or "cuu long" in rg or "mekong" in rg:
                queries.insert(0, "thị trường lúa gạo Đồng bằng sông Cửu Long")

        # Ensure uniqueness & cap number of queries to Tavily credits.
        seen_q = set()
        ordered: List[str] = []
        for q in queries + self._QUERY_TEMPLATES:
            q2 = q.strip()
            if not q2:
                continue
            if q2 in seen_q:
                continue
            seen_q.add(q2)
            ordered.append(q2)

        max_queries = min(len(ordered), max(1, int(getattr(settings, "TAVILY_MAX_RESULTS", 10) and 3 or 3)))
        selected_queries = ordered[:max_queries]

        results: List[Dict[str, Any]] = []
        seen_source_urls: set[str] = set()

        # Prepare Tavily params
        search_depth = getattr(settings, "TAVILY_SEARCH_DEPTH", "advanced") or "advanced"

        for q in selected_queries:
            if len(results) >= limit:
                break

            try:
                resp: Dict[str, Any] = client.search(
                    query=f"{q}",
                    search_depth=search_depth,
                    max_results=min(5, limit),
                    include_answer=False,
                    include_raw_content=False,
                )
            except Exception as e:
                external_circuit_breaker.record_failure(circuit_key, e)
                logger.exception("[TavilyNews] Tavily search failed for query='%s': %s", q, e)
                continue

            for item in resp.get("results", []) or []:
                if len(results) >= limit:
                    break

                title = self._safe_text(item.get("title"))
                source_url = self._safe_text(item.get("url"))
                if not title or not source_url:
                    # Requirement: không lưu kết quả thiếu source_url
                    continue

                if source_url in seen_source_urls:
                    continue

                # Build content/summary fields
                content = self._safe_text(item.get("content"))
                # Tavily thường có content nhưng không chắc; fallback snippet
                snippet = self._safe_text(item.get("snippet"))
                summary = (snippet[:350] if snippet else "") or (content[:350] if content else "")
                summary = summary or title[:350]

                # Anti-fake filter: chỉ giữ tin liên quan nông sản Việt Nam
                if not self._is_relevant_agri_vn(title=title, content=f"{summary} {content}", url=source_url):
                    continue

                crop_tags = self._infer_crop_tags(f"{title} {summary} {content}")
                region_tags = self._infer_region_tags(f"{title} {summary} {content}")

                record_text_for_rules = f"{title} {summary} {content}"
                sentiment = self._infer_sentiment(record_text_for_rules)
                impact_level = self._impact_level_from_sentiment(sentiment, record_text_for_rules)

                published_at = self._guess_published_at(item, fallback_now)
                fetched_at = datetime.now()

                record: Dict[str, Any] = {
                    "title": title,
                    "summary": summary,
                    "content": (content or summary)[:2000],
                    "source_name": self.source_name,
                    "source_url": source_url,
                    "published_at": published_at,
                    "fetched_at": fetched_at,
                    "crop_tags": crop_tags,
                    "region_tags": region_tags or ["Việt Nam"],
                    "sentiment": "neutral" if not sentiment else sentiment,
                    "impact_level": impact_level,
                    "source_type": self.source_type,
                    "is_realtime": True,
                    "is_mock": False,
                    "metadata": {
                        "provider": "Tavily",
                        "query": q,
                        "score": float(item.get("score") or 0.0),
                    },
                }

                if not self._tags_match_optional(crop_name=crop_name, region=region, record=record):
                    continue

                # Ensure requirement: only keep if source_url exists already done.
                if not record.get("source_url"):
                    continue

                results.append(record)
                seen_source_urls.add(source_url)

        if results:
            external_circuit_breaker.record_success(circuit_key)
        else:
            external_circuit_breaker.record_failure(circuit_key, "no tavily news results")
        return results[:limit]


# Singleton (pattern similar to other integration clients)

tavily_news_client = TavilyNewsClient()

