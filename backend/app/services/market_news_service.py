from datetime import datetime, timedelta, timezone
import re
import unicodedata

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.integrations.rss_client import rss_client
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.repositories.market_news_repository import list_market_news, upsert_market_news
from app.services.pricing_service import pricing_service


class MarketNewsService:
    LATEST_CACHE_PREFIX = "market_news:latest:agriculture"
    LATEST_WINDOW_DAYS = 7
    AGRICULTURE_NEWS_KEYWORDS = (
        "nông nghiệp",
        "nông sản",
        "sản xuất nông nghiệp",
        "trồng trọt",
        "canh tác",
        "cây trồng",
        "mùa vụ",
        "gieo trồng",
        "thu hoạch",
        "đồng ruộng",
        "nhà vườn",
        "nông dân",
        "hợp tác xã",
        "lúa",
        "gạo",
        "rau",
        "rau màu",
        "cà phê",
        "hồ tiêu",
        "sầu riêng",
        "thanh long",
        "xoài",
        "cà chua",
        "dưa chuột",
        "phân bón",
        "sâu bệnh",
        "dịch bệnh cây",
        "thủy lợi",
        "hạn hán",
        "mưa bão",
        "xuất khẩu nông sản",
        "giá nông sản",
    )

    def refresh_news(self) -> dict:
        db = SessionLocal()
        log = start_ingestion_log(db, "refresh_market_news", "rss")
        try:
            fetched_records = rss_client.fetch_market_news()
            records = self._filter_relevant_news(fetched_records, since=self._recent_since())
            result = upsert_market_news(db, records)
            self._clear_latest_cache()
            finish_ingestion_log(
                db,
                log,
                status="success",
                records_fetched=len(fetched_records),
                records_saved=result["records_saved"] + result["records_updated"],
            )
            return {
                "status": "success",
                "records_fetched": len(fetched_records),
                "records_filtered": len(records),
                **result,
            }
        except Exception as exc:
            finish_ingestion_log(db, log, status="failed", error_message=str(exc))
            return {"status": "failed", "error": str(exc)}
        finally:
            db.close()

    def get_latest(self, db, limit: int = 20, crop_name: str | None = None, region: str | None = None) -> dict:
        since = self._recent_since()
        cache_key = (
            f"{self.LATEST_CACHE_PREFIX}:{limit}:{self.LATEST_WINDOW_DAYS}d"
            if not crop_name and not region
            else None
        )
        cached = redis_client.get(cache_key) if cache_key else None
        if cached:
            return {**cached, "cache_status": "hit"}

        fetch_limit = max(limit * 5, 20)
        rows = self._filter_relevant_news(
            list_market_news(db, limit=fetch_limit, crop_name=crop_name, region=region, since=since),
            since=since,
        )
        if not rows and (crop_name or region):
            rows = self._filter_relevant_news(list_market_news(db, limit=fetch_limit, since=since), since=since)
        if not rows:
            return {
                "news": self._fallback_news(limit, crop_name=crop_name, region=region),
                "source": "mock",
                "source_name": "Market news fallback",
                "is_realtime": False,
                "is_mock": True,
                "window_days": self.LATEST_WINDOW_DAYS,
                "cache_status": "mock",
                "fallback_used": True,
                "message": "Tin thi truong realtime/cache chua san sang, he thong dang hien thi du lieu du phong.",
            }

        response = {
            "news": [self._to_dict(row) for row in rows[:limit]],
            "source": "cached",
            "source_name": "RSS market news cache",
            "is_realtime": False,
            "is_mock": False,
            "window_days": self.LATEST_WINDOW_DAYS,
            "cache_status": "from_db",
        }
        if cache_key:
            redis_client.set(cache_key, response, expire=1800)
        return response

    @staticmethod
    def _fallback_news(limit: int, crop_name: str | None = None, region: str | None = None) -> list[dict]:
        crop = crop_name or "nong san"
        area = region or "Viet Nam"
        base = [
            {
                "news_id": f"fallback-{index}",
                "title": title.format(crop=crop, region=area),
                "summary": summary.format(crop=crop, region=area),
                "source_name": "Market news fallback",
                "source_url": None,
                "published_at": datetime.utcnow().isoformat(),
                "region": area,
                "sentiment": "neutral",
                "impact": "neutral",
                "source": "mock",
                "fetched_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "confidence": 0.35,
                "is_mock": True,
                "fallback_used": True,
            }
            for index, (title, summary) in enumerate(
                [
                    (
                        "Theo doi bien dong gia {crop} tai {region}",
                        "Chua co tin RSS phu hop trong cache gan day. Nen ket hop gia DB, canh bao gia va nguon dia phuong truoc khi ra quyet dinh.",
                    ),
                    (
                        "Khuyen nghi ban theo dot de giam rui ro",
                        "Khi tin thi truong realtime cham, he thong uu tien du lieu du phong va lich su gia noi bo.",
                    ),
                    (
                        "Kiem tra chat luong va thoi tiet truoc khi chot don",
                        "Fallback nay nhac nguoi dung doi chieu thoi tiet, chat luong va lich thu hoach.",
                    ),
                ],
                start=1,
            )
        ]
        return base[:limit]

    def _filter_agriculture_news(self, items):
        return [item for item in (items or []) if self._is_agriculture_production_news(item)]

    def _filter_relevant_news(self, items, since: datetime):
        return [
            item
            for item in (items or [])
            if self._is_recent_news(item, since)
            and self._is_agriculture_production_news(item)
            and not self._has_text_corruption(item)
        ]

    def _has_text_corruption(self, item) -> bool:
        text = " ".join(
            str(self._get_value(item, field) or "")
            for field in (
                "title",
                "summary",
                "source_name",
                "Title",
                "Summary",
                "SourceName",
            )
        )
        if "\ufffd" in text:
            return True
        return bool(re.search(r"[A-Za-zÀ-ỹ]\?[A-Za-zÀ-ỹ]", text) or text.count("?") >= 3)

    def _is_recent_news(self, item, since: datetime) -> bool:
        published_at = self._get_value(item, "published_at") or self._get_value(item, "PublishedAt")
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            except ValueError:
                return False
        if not isinstance(published_at, datetime):
            return False
        if published_at.tzinfo:
            published_at = published_at.astimezone(timezone.utc).replace(tzinfo=None)
        return published_at >= since

    def _is_agriculture_production_news(self, item) -> bool:
        haystack = self._normalize_text(" ".join(
            str(self._get_value(item, field) or "")
            for field in (
                "title",
                "summary",
                "source_name",
                "Title",
                "Summary",
                "SourceName",
            )
        ))
        return any(self._normalize_text(keyword) in haystack for keyword in self.AGRICULTURE_NEWS_KEYWORDS)

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower()).replace("đ", "d")
        return "".join(char for char in normalized if unicodedata.category(char) != "Mn")

    @staticmethod
    def _get_value(item, field: str):
        if isinstance(item, dict):
            return item.get(field)
        return getattr(item, field, None)

    def _clear_latest_cache(self) -> None:
        redis_client.delete("market_news:latest")
        redis_client.delete(self.LATEST_CACHE_PREFIX)
        for limit in (4, 6, 20):
            redis_client.delete(f"{self.LATEST_CACHE_PREFIX}:{limit}")
            redis_client.delete(f"{self.LATEST_CACHE_PREFIX}:{limit}:{self.LATEST_WINDOW_DAYS}d")

    def _recent_since(self) -> datetime:
        return datetime.utcnow() - timedelta(days=self.LATEST_WINDOW_DAYS)

    @staticmethod
    def _repair_mojibake(value: str | None) -> str | None:
        """
        Fix common Vietnamese mojibake from bad RSS encodings, e.g.:
        - Ã¢â€žÂ¢, Ã©, Â, â€™, Ã¼ ...
        by trying latin1->utf-8 decode when the string looks corrupted.
        """
        if value is None:
            return None

        if not isinstance(value, str) or not value:
            return value

        looks_mojibake = any(token in value for token in ["Ã", "Â", "â€™", "â€œ", "â€", "â€“", "â€ž"])
        if not looks_mojibake:
            return value

        try:
            # Undo the typical "wrongly decoded as latin1 then interpreted as utf-8" pattern.
            return value.encode("latin1", errors="ignore").decode("utf-8", errors="replace")
        except Exception:
            return value

    @staticmethod
    def _to_dict(row) -> dict:
        return {
            "news_id": row.NewsID,
            "title": MarketNewsService._repair_mojibake(row.Title),
            "summary": MarketNewsService._repair_mojibake(row.Summary),
            "source_name": MarketNewsService._repair_mojibake(row.SourceName),
            "source_url": row.SourceURL,
            "published_at": row.PublishedAt.isoformat() if row.PublishedAt else None,
            "region": row.Region,
            "sentiment": row.Sentiment,
            "impact": row.Sentiment or "neutral",
            "source": "cached",
            "fetched_at": datetime.utcnow().isoformat(),
            "updated_at": row.PublishedAt.isoformat() if row.PublishedAt else None,
            "confidence": 0.7,
        }

    def get_market_news(self, db, crop: str | None = None, region: str | None = None, limit: int = 10) -> dict:
        return self.get_latest(db, limit=limit, crop_name=crop, region=region)

    def analyze_news_impact(self, news_item: dict) -> dict:
        text = f"{news_item.get('title', '')} {news_item.get('summary', '')}".lower()
        positive_words = ("tang", "xuat khau", "don hang", "duoc gia", "co hoi")
        negative_words = ("giam", "dich", "bao", "han", "thua", "rui ro")
        score = sum(word in text for word in positive_words) - sum(word in text for word in negative_words)
        impact = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        return {
            "impact": impact,
            "impact_score": 0.68 if impact != "neutral" else 0.5,
            "price_effect": "likely_increase" if impact == "positive" else "likely_decrease" if impact == "negative" else "stable",
            "source": "ai_generated",
            "source_name": "News impact rule engine",
            "confidence": 0.58,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def get_market_trends(self, db, crop: str | None = None, region: str | None = None) -> dict:
        selected_crop = crop or "lua"
        selected_region = region or "Ha Noi"
        pricing = pricing_service.get_ai_price_recommendation(db, selected_crop, selected_region)
        return {
            "crop": selected_crop,
            "crop_name": selected_crop,
            "region": selected_region,
            "trend": pricing.get("trend", "stable"),
            "confidence": pricing.get("confidence", 0.0),
            "evidence": pricing.get("reasons", []),
            "forecast": pricing.get("forecast", []),
            "recommendation": pricing.get("recommendation"),
            "source": "ai_generated" if not pricing.get("is_mock") else "mock",
            "source_name": "Market trend engine",
            "is_mock": pricing.get("is_mock", False),
            "cache_status": pricing.get("cache_status", "computed"),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def get_market_opportunities(self, db, crop: str | None = None, region: str | None = None) -> dict:
        trend = self.get_market_trends(db, crop=crop, region=region)
        return {
            "opportunities": [
                {
                    "title": "Batch selling opportunity",
                    "crop": trend["crop"],
                    "region": trend["region"],
                    "reason": trend.get("recommendation"),
                    "confidence": trend.get("confidence", 0.0),
                    "source": trend.get("source"),
                    "source_name": trend.get("source_name"),
                    "updated_at": trend.get("updated_at"),
                }
            ],
            "source": trend.get("source"),
            "source_name": "AI Market Intelligence",
            "is_mock": trend.get("is_mock", False),
            "confidence": trend.get("confidence", 0.0),
            "updated_at": trend.get("updated_at"),
        }

    def get_market_risks(self, db, crop: str | None = None, region: str | None = None) -> dict:
        trend = self.get_market_trends(db, crop=crop, region=region)
        risk = "high" if trend.get("trend") == "decreasing" else "medium" if trend.get("is_mock") else "low"
        return {
            "risks": [
                {
                    "title": "Price volatility",
                    "severity": risk,
                    "crop": trend["crop"],
                    "region": trend["region"],
                    "recommendation": "Create price alert and avoid selling all stock at one time.",
                    "source": trend.get("source"),
                    "source_name": "AI Market Risk Engine",
                    "updated_at": trend.get("updated_at"),
                }
            ],
            "source": trend.get("source"),
            "source_name": "AI Market Risk Engine",
            "is_mock": trend.get("is_mock", False),
            "confidence": trend.get("confidence", 0.0),
            "updated_at": trend.get("updated_at"),
        }


market_news_service = MarketNewsService()
