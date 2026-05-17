from datetime import datetime
from typing import Any


SOURCE_REALTIME = "realtime_api"
SOURCE_DATABASE = "database"
SOURCE_AI = "ai_generated"
SOURCE_CACHED = "cached"
SOURCE_MOCK = "mock"


def _normalized_source(
    source: str | None,
    *,
    is_realtime: bool = False,
    is_mock: bool = False,
    cache_status: str | None = None,
) -> str:
    raw = (source or "").lower()
    cache = (cache_status or "").lower()
    if is_mock or raw in {"mock", "fallback", "demo"} or cache in {"mock", "miss"}:
        return SOURCE_MOCK
    if raw in {"ai", "ai_generated", "rule", "rule_based_ai", "explainable_rule_ai"}:
        return SOURCE_AI
    if is_realtime or cache in {"live", "realtime", "refreshed"} or raw in {"realtime", "realtime_api", "open-meteo", "rss"}:
        return SOURCE_REALTIME
    if raw in {"cached", "cache"}:
        return SOURCE_CACHED
    if cache in {"cached", "hit", "from_cache", "from_db", "db", "stale"}:
        return SOURCE_CACHED if cache in {"cached", "hit", "from_cache", "stale"} else SOURCE_DATABASE
    if raw in {"database", "db", "market_db"}:
        return SOURCE_DATABASE
    return raw or SOURCE_DATABASE


def api_response(
    data: Any,
    *,
    source: str = "database",
    source_name: str | None = None,
    is_realtime: bool = False,
    is_mock: bool = False,
    cache_status: str = "from_db",
    last_updated: datetime | None = None,
    fetched_at: datetime | None = None,
    confidence: float | None = None,
    message: str = "OK",
) -> dict:
    if isinstance(data, dict):
        source_name = source_name or data.get("source_name") or data.get("source") or source
        last_updated = last_updated or data.get("last_updated") or data.get("updated_at") or data.get("created_at")
        confidence = confidence if confidence is not None else data.get("confidence")
        is_realtime = is_realtime or bool(data.get("is_realtime"))
        is_mock = is_mock or bool(data.get("is_mock"))
        cache_status = data.get("cache_status") or cache_status

    fetched_at = fetched_at or last_updated or datetime.now()
    normalized_source = _normalized_source(
        source,
        is_realtime=is_realtime,
        is_mock=is_mock,
        cache_status=cache_status,
    )

    response = dict(data) if isinstance(data, dict) else {}
    response.update({
        "success": True,
        "data": data,
        "source": normalized_source,
        "source_name": source_name or source,
        "fetched_at": fetched_at,
        "confidence": confidence if confidence is not None else 0.0,
        "message": message,
        "meta": {
            "source": normalized_source,
            "source_name": source_name or source,
            "is_realtime": is_realtime,
            "is_mock": is_mock,
            "cache_status": cache_status,
            "last_updated": last_updated or datetime.now(),
            "fetched_at": fetched_at,
            "confidence": confidence if confidence is not None else 0.0,
        },
    })
    return response
