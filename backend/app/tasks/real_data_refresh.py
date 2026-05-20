from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable

from app.core.database import SessionLocal
from app.services.market_analysis_service import market_analysis_service
from app.services.market_news_service import market_news_service
from app.services.price_aggregator_service import price_aggregator_service
from app.services.retail_price_service import retail_price_service
from app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


DEFAULT_REGIONS = ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho", "Lam Dong", "Dak Lak"]
DEFAULT_CROPS = ["lua", "ca phe", "ho tieu", "rau"]


def _csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name, "")
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or default


def _interval_seconds(name: str, default_minutes: int) -> int:
    return max(int(os.getenv(name, str(default_minutes * 60))), 60)


def _enabled() -> bool:
    return os.getenv("REAL_REFRESH_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}


def _run_with_db(name: str, fn: Callable) -> None:
    db = SessionLocal()
    try:
        fn(db)
    except Exception as exc:
        logger.warning("[real-data-refresh] %s failed: %s", name, exc)
    finally:
        db.close()


def _refresh_weather_current(regions: list[str]) -> None:
    _run_with_db(
        "weather_current",
        lambda db: [weather_service.get_current_weather(db, region, force_refresh=True) for region in regions],
    )


def _refresh_weather_hourly(regions: list[str]) -> None:
    _run_with_db(
        "weather_hourly",
        lambda db: [weather_service.get_hourly_forecast(db, region, 168, force_refresh=True) for region in regions],
    )


def _refresh_weather_forecast(regions: list[str]) -> None:
    _run_with_db(
        "weather_forecast",
        lambda db: [weather_service.get_forecast(db, region, 7, force_refresh=True) for region in regions],
    )


def _refresh_prices(crops: list[str]) -> None:
    _run_with_db(
        "official_prices",
        lambda db: [price_aggregator_service.refresh_prices(db, crop_name=crop) for crop in crops],
    )


def _refresh_retail_prices(crops: list[str]) -> None:
    _run_with_db(
        "retail_prices",
        lambda db: [retail_price_service.refresh_retail_prices(db, crop) for crop in crops],
    )


def _refresh_market_analysis(crops: list[str], regions: list[str]) -> None:
    def _job(db):
        for crop in crops:
            for region in regions[:2]:
                market_analysis_service.refresh_analysis(db, crop_name=crop, region=region)

    _run_with_db("market_analysis", _job)


async def real_data_refresh_loop() -> None:
    if not _enabled():
        logger.info("[real-data-refresh] disabled by REAL_REFRESH_ENABLED=false")
        return

    regions = _csv_env("REAL_REFRESH_REGIONS", DEFAULT_REGIONS)
    crops = _csv_env("REAL_REFRESH_CROPS", DEFAULT_CROPS)
    jobs: dict[str, tuple[int, Callable[[], None]]] = {
        "weather_current": (_interval_seconds("WEATHER_CURRENT_REFRESH_SECONDS", 20), lambda: _refresh_weather_current(regions)),
        "weather_hourly": (_interval_seconds("WEATHER_HOURLY_REFRESH_SECONDS", 30), lambda: _refresh_weather_hourly(regions)),
        "weather_forecast": (_interval_seconds("WEATHER_FORECAST_REFRESH_SECONDS", 120), lambda: _refresh_weather_forecast(regions)),
        "official_prices": (_interval_seconds("OFFICIAL_PRICE_REFRESH_SECONDS", 120), lambda: _refresh_prices(crops)),
        "market_news": (_interval_seconds("MARKET_NEWS_REFRESH_SECONDS", 120), market_news_service.refresh_news),
        "retail_prices": (_interval_seconds("RETAIL_PRICE_REFRESH_SECONDS", 240), lambda: _refresh_retail_prices(crops)),
        "market_analysis": (_interval_seconds("MARKET_ANALYSIS_REFRESH_SECONDS", 45), lambda: _refresh_market_analysis(crops, regions)),
    }
    await asyncio.sleep(int(os.getenv("REAL_REFRESH_STARTUP_DELAY_SECONDS", "10")))
    stagger_seconds = max(int(os.getenv("REAL_REFRESH_STAGGER_SECONDS", "45")), 5)
    base = time.monotonic()
    next_run = {name: base + index * stagger_seconds for index, name in enumerate(jobs)}

    while True:
        try:
            now = time.monotonic()
            for name, (interval, fn) in jobs.items():
                if now < next_run[name]:
                    continue
                next_run[name] = now + interval
                asyncio.create_task(asyncio.to_thread(fn))
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            logger.info("[real-data-refresh] stopped")
            raise
        except Exception as exc:
            logger.warning("[real-data-refresh] scheduler tick failed: %s", exc)
            await asyncio.sleep(30)
