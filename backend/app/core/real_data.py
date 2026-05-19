from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


OFFICIAL_AGRI_SOURCE_NAME = "Th\u00f4ng tin th\u1ecb tr\u01b0\u1eddng n\u00f4ng s\u1ea3n"
OFFICIAL_PRICE_URL = "https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx"
OFFICIAL_NEWS_URL = "https://thitruongnongsan.gov.vn/vn/xc0_tin-tuc.html"
OPEN_METEO_SOURCE_NAME = "Open-Meteo"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


CACHE_TTL_MINUTES = {
    "weather_current": 30,
    "weather_hourly": 30,
    "weather_forecast": 180,
    "official_price": 180,
    "market_news": 120,
    "retail_price": 360,
    "market_analysis": 60,
}

VALID_CACHE_STATUSES = {"live", "fresh_cache", "stale_cache", "miss", "error"}


def normalize_cache_status(value: Any, *, default: str = "miss") -> str:
    raw = str(value or "").strip().lower()
    mapping = {
        "live": "live",
        "realtime": "live",
        "refreshed": "live",
        "reset_refreshed": "live",
        "fresh": "fresh_cache",
        "cached": "fresh_cache",
        "cache": "fresh_cache",
        "hit": "fresh_cache",
        "from_cache": "fresh_cache",
        "from_db": "fresh_cache",
        "database": "fresh_cache",
        "db": "fresh_cache",
        "computed": "fresh_cache",
        "stale": "stale_cache",
        "stale_cache": "stale_cache",
        "miss": "miss",
        "empty": "miss",
        "no_data": "miss",
        "processing": "miss",
        "error": "error",
        "failed": "error",
        "partial_success": "error",
    }
    normalized = mapping.get(raw, raw)
    if normalized in VALID_CACHE_STATUSES:
        return normalized
    return default if default in VALID_CACHE_STATUSES else "miss"


STALE_TTL_MINUTES = {
    "weather_current": 180,
    "weather_hourly": 120,
    "weather_forecast": 720,
    "official_price": 1440,
    "market_news": 1440,
    "retail_price": 1440,
    "market_analysis": 240,
}


def utcnow() -> datetime:
    return datetime.utcnow()


def coerce_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def age_minutes(value: Any) -> int | None:
    dt = coerce_datetime(value)
    if not dt:
        return None
    return max(int((datetime.now() - dt).total_seconds() // 60), 0)


def cache_status_for(value: Any, kind: str) -> str:
    age = age_minutes(value)
    if age is None:
        return "miss"
    if age <= CACHE_TTL_MINUTES[kind]:
        return "fresh_cache"
    if age <= STALE_TTL_MINUTES[kind]:
        return "stale_cache"
    return "miss"


def required_public_metadata(
    *,
    source_name: str | None,
    source_url: str | None,
    fetched_at: Any,
    cache_status: str,
    is_realtime: bool = False,
) -> dict:
    fetched = coerce_datetime(fetched_at)
    return {
        "source_name": source_name,
        "source_url": source_url,
        "is_realtime": bool(is_realtime),
        "is_mock": False,
        "cache_status": normalize_cache_status(cache_status),
        "fetched_at": fetched,
        "last_updated": fetched,
        "data_age_minutes": age_minutes(fetched) if fetched else None,
    }


def is_cache_usable(value: Any, kind: str, *, allow_stale: bool = True) -> bool:
    status = cache_status_for(value, kind)
    if status == "fresh_cache":
        return True
    return allow_stale and status == "stale_cache"


def is_real_cache_record(
    *,
    source_url: str | None,
    source_name: str | None,
    fetched_at: Any,
    is_mock: bool | None = False,
) -> bool:
    return bool(source_url and source_name and coerce_datetime(fetched_at) and not is_mock)


def attach_cache_metadata(
    payload: dict,
    *,
    source_name: str,
    source_url: str,
    fetched_at: Any,
    cache_status: str,
    is_realtime: bool = False,
    warning: str | None = None,
) -> dict:
    fetched = coerce_datetime(fetched_at) or datetime.now()
    result = {
        **payload,
        "source_name": source_name,
        "source_url": source_url,
        "is_realtime": bool(is_realtime),
        "is_mock": False,
        "cache_status": normalize_cache_status(cache_status),
        "fetched_at": fetched,
        "last_updated": fetched,
        "data_age_minutes": age_minutes(fetched) or 0,
    }
    if warning:
        result["warning"] = warning
    return result


def realtime_error(
    *,
    code: str,
    message: str,
    source_name: str,
    source_url: str,
    detail: str | None = None,
) -> dict:
    now = datetime.now()
    payload = {
        "_api_error": True,
        "error_code": code,
        "error_message": message,
        "source": "realtime_api",
        "source_name": source_name,
        "source_url": source_url,
        "is_realtime": False,
        "is_mock": False,
        "cache_status": "miss",
        "fetched_at": now,
        "last_updated": now,
        "data_age_minutes": None,
    }
    if detail:
        payload["error_detail"] = detail
    return payload


@dataclass
class CircuitState:
    failures: int = 0
    opened_until: datetime | None = None
    last_error: str | None = None


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 3, cooldown_seconds: int = 600):
        self.failure_threshold = max(failure_threshold, 1)
        self.cooldown = timedelta(seconds=max(cooldown_seconds, 1))
        self._states: dict[str, CircuitState] = {}

    def before_call(self, key: str) -> None:
        state = self._states.get(key)
        if state and state.opened_until and state.opened_until > datetime.now():
            raise CircuitOpenError(f"{key} circuit open until {state.opened_until.isoformat()}")

    def record_success(self, key: str) -> None:
        self._states[key] = CircuitState()

    def record_failure(self, key: str, error: Exception | str) -> None:
        state = self._states.setdefault(key, CircuitState())
        state.failures += 1
        state.last_error = str(error)
        if state.failures >= self.failure_threshold:
            state.opened_until = datetime.now() + self.cooldown

    def status(self, key: str) -> str:
        state = self._states.get(key)
        if not state or state.failures == 0:
            return "active"
        if state.opened_until and state.opened_until > datetime.now():
            return "error"
        return "cache"


external_circuit_breaker = CircuitBreaker()
