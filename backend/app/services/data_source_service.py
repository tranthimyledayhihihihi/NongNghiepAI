from datetime import datetime
from typing import Any


SOURCE_REALTIME = "realtime_api"
SOURCE_DATABASE = "database"
SOURCE_CACHED = "cached"
SOURCE_AI = "ai_generated"
SOURCE_MOCK = "mock"
SOURCE_LEGACY = "legacy"


class DataSourceService:
    """Normalize source metadata across service and API payloads."""

    def normalize_source(self, item: dict | None = None, default_source: str = SOURCE_DATABASE) -> str:
        item = item or {}
        meta = item.get("meta") or {}
        raw = str(item.get("source") or meta.get("source") or default_source or "").lower()
        cache_status = str(item.get("cache_status") or meta.get("cache_status") or "").lower()
        is_mock = bool(item.get("is_mock") or meta.get("is_mock"))
        is_realtime = bool(item.get("is_realtime") or meta.get("is_realtime"))

        if raw in {"legacy", "old_api", "deprecated"}:
            return SOURCE_LEGACY
        if is_mock or raw in {"mock", "demo"} or cache_status == "mock":
            return SOURCE_MOCK
        if raw in {"ai", "ai_generated", "rule_based_ai", "explainable_rule_ai"}:
            return SOURCE_AI
        if is_realtime or raw in {"realtime", "realtime_api", "open-meteo", "rss"} or cache_status in {"live", "realtime", "refreshed"}:
            return SOURCE_REALTIME
        if raw in {"cached", "cache", "fallback"} or cache_status in {"cached", "hit", "from_cache", "stale"}:
            return SOURCE_CACHED
        if raw in {"database", "db", "market_db"} or cache_status in {"db", "from_db", "db_fresh"}:
            return SOURCE_DATABASE
        return raw or default_source or SOURCE_DATABASE

    def source_meta(
        self,
        item: dict | None = None,
        *,
        default_source: str = SOURCE_DATABASE,
        source_name: str | None = None,
        confidence: float | None = None,
    ) -> dict:
        item = item or {}
        meta = item.get("meta") or {}
        updated_at = (
            item.get("updated_at")
            or item.get("last_updated")
            or item.get("observed_at")
            or item.get("published_at")
            or item.get("created_at")
            or meta.get("updated_at")
            or meta.get("last_updated")
            or datetime.now()
        )
        fetched_at = item.get("fetched_at") or meta.get("fetched_at") or updated_at
        resolved_confidence = confidence if confidence is not None else item.get("confidence", meta.get("confidence"))
        return {
            "source": self.normalize_source(item, default_source),
            "source_name": source_name or item.get("source_name") or meta.get("source_name") or default_source,
            "fetched_at": fetched_at,
            "updated_at": updated_at,
            "confidence": resolved_confidence,
            "cache_status": item.get("cache_status") or meta.get("cache_status"),
            "is_mock": bool(item.get("is_mock") or meta.get("is_mock")),
            "is_realtime": bool(item.get("is_realtime") or meta.get("is_realtime")),
        }

    def attach_source_meta(
        self,
        item: dict,
        *,
        default_source: str = SOURCE_DATABASE,
        source_name: str | None = None,
        confidence: float | None = None,
    ) -> dict:
        meta = self.source_meta(
            item,
            default_source=default_source,
            source_name=source_name,
            confidence=confidence,
        )
        result = {**item}
        result.setdefault("source", meta["source"])
        result.setdefault("source_name", meta["source_name"])
        result.setdefault("fetched_at", meta["fetched_at"])
        result.setdefault("updated_at", meta["updated_at"])
        if meta["confidence"] is not None:
            result.setdefault("confidence", meta["confidence"])
        result["meta"] = {**meta, **(result.get("meta") or {})}
        return result

    def collect_data_sources(self, payload: Any) -> list[dict]:
        sources: dict[tuple[str, str], dict] = {}

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                if value.get("source") or value.get("source_name") or value.get("meta"):
                    meta = self.source_meta(value)
                    key = (meta["source"], meta["source_name"])
                    sources[key] = meta
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(payload)
        return list(sources.values())


data_source_service = DataSourceService()
