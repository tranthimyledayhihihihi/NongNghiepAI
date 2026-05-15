import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from statistics import mean
from typing import Any

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.integrations.weather_client import canonical_region_name, normalize_location_key
from app.models.crop import Crop
from app.models.dashboard import DashboardCache
from app.models.harvest import HarvestSchedule
from app.models.ingestion import DataIngestionLog
from app.models.market_news import MarketNews
from app.models.notification import Notification
from app.models.price import MarketPrice
from app.models.quality import QualityCheck
from app.repositories.common import ensure_crop
from app.services.market_news_service import market_news_service
from app.services.price_aggregator_service import price_aggregator_service
from app.services.pricing_service import pricing_service
from app.services.weather_service import weather_service


DASHBOARD_CACHE_TTL_SECONDS = 300
DEFAULT_CROP = "lua"
DEFAULT_REGION = "Ha Noi"
DEFAULT_REGIONS = ["Ha Noi", "Can Tho", "Dak Lak", "Lam Dong", "TP.HCM", "Da Nang"]
DEFAULT_CROPS = [
    {"value": "lua", "label": "Lúa"},
    {"value": "ca phe", "label": "Cà phê"},
    {"value": "ho tieu", "label": "Hồ tiêu"},
    {"value": "sau rieng", "label": "Sầu riêng"},
    {"value": "thanh long", "label": "Thanh long"},
    {"value": "ngo", "label": "Ngô"},
]

REGION_LABELS = {
    "Ha Noi": "Hà Nội",
    "Can Tho": "Cần Thơ",
    "Dak Lak": "Đắk Lắk",
    "Lam Dong": "Lâm Đồng",
    "TP.HCM": "TP.HCM",
    "Da Nang": "Đà Nẵng",
}

CROP_LABELS = {item["value"]: item["label"] for item in DEFAULT_CROPS}


class DashboardService:
    def get_summary(
        self,
        db: Session,
        user_id: int | None = None,
        region: str | None = None,
        crop_name: str | None = None,
        force_refresh_weather: bool = False,
        force_refresh_market: bool = False,
        force_refresh_news: bool = False,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        cache_key = self._cache_key("summary", selected_region, selected_crop, user_id)

        if not any([force_refresh_weather, force_refresh_market, force_refresh_news]):
            cached = self._read_cache(db, cache_key)
            if cached:
                cached["cache_status"] = "hit"
                return cached

        if force_refresh_market:
            self._refresh_prices(db, crop_name=selected_crop)
        if force_refresh_news:
            market_news_service.refresh_news()

        featured = self.get_featured_crop(db, crop_name=selected_crop, region=selected_region)
        weather = self.get_weather_overview(db, region=selected_region, force_refresh=force_refresh_weather)
        weather_risk = self.get_weather_risk(
            db,
            region=selected_region,
            crop_name=selected_crop,
            force_refresh=force_refresh_weather,
        )
        regional = self.get_regional_prices(db, crop_name=selected_crop, regions=DEFAULT_REGIONS)
        news = self.get_news(db, limit=6, crop_name=selected_crop, region=selected_region, force_refresh=False)
        trend = self.get_price_trend(db, crop_name=selected_crop, region=selected_region, days=7)
        ai_recommendation = self._build_ai_from_signals(selected_crop, selected_region, featured, weather_risk, trend)
        realtime_market = self.get_realtime_market(db, crop_name=selected_crop, region=selected_region)
        alert_center = self._build_alert_center(featured, weather_risk, news.get("news", []), regional["regions"])
        data_sources = self.get_data_health(db, region=selected_region, crop_name=selected_crop)["sources"]

        schedules_query = db.query(HarvestSchedule)
        quality_query = db.query(QualityCheck)
        notification_query = db.query(Notification).filter(Notification.IsDeleted.is_(False))
        if user_id:
            schedules_query = schedules_query.filter(HarvestSchedule.UserID == user_id)
            quality_query = quality_query.filter(QualityCheck.UserID == user_id)
            notification_query = notification_query.filter(Notification.UserID == user_id)

        try:
            active_seasons = schedules_query.filter(HarvestSchedule.ActualHarvestDate.is_(None)).count()
            quality_checks = quality_query.count()
            unread_notifications = notification_query.filter(Notification.IsRead.is_(False)).count()
        except SQLAlchemyError:
            db.rollback()
            active_seasons = 0
            quality_checks = 0
            unread_notifications = 0

        result = {
            "region": selected_region,
            "region_label": REGION_LABELS.get(selected_region, selected_region),
            "crop_name": selected_crop,
            "crop_label": CROP_LABELS.get(selected_crop, selected_crop.title()),
            "available_regions": self._available_regions(),
            "available_crops": DEFAULT_CROPS,
            "generated_at": datetime.now(),
            "featured_crop": featured,
            "weather": weather,
            "weather_risk": weather_risk,
            "forecast": trend["forecast"],
            "price_trend": trend,
            "ai_recommendation": ai_recommendation,
            "regional_prices": regional["regions"],
            "news": news.get("news", []),
            "news_preview": news.get("news", [])[:3],
            "alert_center": alert_center,
            "weather_alerts_count": len(weather_risk.get("alerts", [])),
            "price_alerts_count": len([item for item in alert_center if item["type"] == "price"]),
            "event_alerts_count": len([item for item in alert_center if item["type"] == "event"]),
            "data_sources": data_sources,
            "data_quality_score": self._data_quality_score(featured, weather_risk, regional["regions"], news, data_sources),
            "active_seasons": active_seasons,
            "quality_checks": quality_checks,
            "unread_notifications": unread_notifications,
            "realtime_market": realtime_market,
            "cache_status": "refreshed" if any([force_refresh_weather, force_refresh_market, force_refresh_news]) else "fresh",
        }
        self._write_cache(db, cache_key, result)
        return result

    def get_featured_crop(
        self,
        db: Session,
        crop_name: str = DEFAULT_CROP,
        region: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        row = self._latest_market_price(db, selected_crop, selected_region)
        if force_refresh and settings.ENVIRONMENT.lower() != "test":
            self._refresh_prices(db, crop_name=selected_crop)
            row = self._latest_market_price(db, selected_crop, selected_region)

        if row:
            price = float(row.PricePerKg)
            last_updated = row.CollectedAt or row.UpdatedAt
            source_name = row.SourceName or "Database"
            is_mock = False
            source_url = row.SourceURL
            market_type = row.MarketType
        else:
            current = pricing_service.get_current_price(db, selected_crop, selected_region, include_weather=False)
            price = float(current["current_price"])
            last_updated = self._parse_datetime(current.get("last_updated")) or datetime.now()
            source_name = current.get("source_name") or "Pricing fallback"
            is_mock = True
            source_url = None
            market_type = "local"

        change_day = self._price_change_pct(db, selected_crop, selected_region, days_back=1)
        change_week = self._price_change_pct(db, selected_crop, selected_region, days_back=7)
        return {
            "name": selected_crop,
            "display_name": CROP_LABELS.get(selected_crop, selected_crop.title()),
            "location": selected_region,
            "price": price,
            "unit": "VND/kg",
            "change": self._format_pct(change_day),
            "change_day_pct": change_day,
            "change_week_pct": change_week,
            "trend": self._trend_from_change(change_week if change_week is not None else change_day),
            "market_type": market_type,
            "source_name": source_name,
            "source_url": source_url,
            "last_updated": last_updated,
            "data_age_minutes": self._age_minutes(last_updated),
            "cache_status": "mock" if is_mock else price_aggregator_service.cache_status(last_updated),
            "is_realtime": False,
            "is_mock": is_mock,
            "is_scraped": bool(source_url and not is_mock),
        }

    def get_price_trend(
        self,
        db: Session,
        crop_name: str = DEFAULT_CROP,
        region: str = DEFAULT_REGION,
        days: int = 7,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        history = self._load_price_history(db, selected_crop, selected_region, days=60)
        current = self.get_featured_crop(db, selected_crop, selected_region)
        weather = self.get_weather_overview(db, selected_region)
        news = self.get_news(db, limit=8, crop_name=selected_crop, region=selected_region)
        futures = self._latest_global_reference(db, selected_crop)

        forecast, reasons, confidence = self._build_forecast(
            current_price=float(current["price"]),
            history=history,
            days=days,
            weather=weather,
            news_items=news.get("news", []),
            futures=futures,
            current_is_mock=bool(current.get("is_mock")),
        )
        return {
            "crop_name": selected_crop,
            "region": selected_region,
            "history": history[-days:],
            "forecast": forecast,
            "trend": self._forecast_trend(forecast),
            "confidence": confidence,
            "reason_codes": reasons,
            "data_sources": [
                {"name": current.get("source_name"), "type": "price", "cache_status": current.get("cache_status")},
                {"name": weather.get("current", {}).get("source_name"), "type": "weather", "cache_status": weather.get("cache_status")},
                {"name": news.get("source_name", "Market RSS"), "type": "news", "cache_status": news.get("cache_status")},
                {"name": futures.get("source_name") if futures else None, "type": "global_reference", "cache_status": futures.get("cache_status") if futures else "missing"},
            ],
            "is_mock": bool(current.get("is_mock")) and not history,
            "last_updated": datetime.now(),
        }

    def get_weather_overview(self, db: Session, region: str = DEFAULT_REGION, force_refresh: bool = False) -> dict:
        selected_region = self._canonical_region(region)
        current = weather_service.get_current_weather(db, selected_region, force_refresh=force_refresh)
        forecast = weather_service.get_forecast(db, selected_region, 7)
        alerts = weather_service.generate_alerts(current, forecast)
        return {
            "current": current,
            "forecast": forecast,
            "alerts": alerts,
            "is_mock": bool(current.get("is_mock")) or any(item.get("is_mock") for item in forecast),
            "is_realtime": bool(current.get("is_realtime")),
            "cache_status": current.get("cache_status", "unknown"),
            "last_updated": current.get("last_updated"),
            "checked_at": current.get("checked_at"),
            "source_updated_at": current.get("source_updated_at"),
            "source_name": current.get("source_name") or "Open-Meteo",
            "source_url": current.get("source_url") or "https://open-meteo.com",
        }

    def get_weather_risk(
        self,
        db: Session,
        region: str = DEFAULT_REGION,
        crop_name: str = DEFAULT_CROP,
        growth_stage: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        if force_refresh:
            agriculture = weather_service.get_agriculture_weather(
                db,
                selected_region,
                crop_name=selected_crop,
                growth_stage=growth_stage,
                days=7,
                include_hourly=True,
                force_refresh=True,
            )
            current = agriculture.get("current", {})
            forecast = agriculture.get("forecast", [])
            hourly = agriculture.get("hourly_forecast", [])
            alerts = agriculture.get("alerts", [])
            recommendations = agriculture.get("activity_recommendations", [])
            ai_recommendation = agriculture.get("ai_recommendation")
            source_summary = agriculture.get("source_summary", {})
        else:
            overview = self.get_weather_overview(db, selected_region, force_refresh=False)
            current = overview.get("current", {})
            forecast = overview.get("forecast", [])
            hourly = weather_service._build_hourly_fallback(current, 24)
            alerts = weather_service.generate_alerts(current, forecast, crop_name=selected_crop, growth_stage=growth_stage)
            recommendations = weather_service.build_activity_recommendations(
                current,
                forecast,
                hourly,
                crop_name=selected_crop,
                growth_stage=growth_stage,
            )
            ai_recommendation = {
                "provider": "rule_based_ai",
                "summary": "Dữ liệu thời tiết được nạp lại khi mở dashboard, sau đó đọc nhanh từ DB/cache.",
                "risk_explanation": "Risk score được tính từ mưa, UV, gió, độ ẩm và cảnh báo nông vụ hiện có.",
                "action_plan": [item.get("reason") for item in recommendations[:3] if item.get("reason")],
                "data_note": "Fast-load mode dùng DB/cache để tránh timeout khi mở dashboard.",
            }
            source_summary = {
                "cache_status": overview.get("cache_status", "unknown"),
                "is_mock": overview.get("is_mock", False),
            }
        air_quality = self._air_quality(selected_region, live=force_refresh)
        risk_score = self._weather_risk_score(current, forecast, hourly, alerts, air_quality)
        rain_24h = round(sum(float(item.get("rainfall") or 0) for item in hourly[:24]), 1)
        high_rain_hours = [
            item
            for item in hourly[:24]
            if float(item.get("rainfall") or 0) >= 2 or float(item.get("rain_probability") or 0) >= 60
        ]

        return {
            "region": selected_region,
            "crop_name": selected_crop,
            "risk_score": risk_score,
            "risk_level": self._risk_level(risk_score),
            "alerts": alerts,
            "recommendations": recommendations,
            "ai_recommendation": ai_recommendation,
            "current": current,
            "forecast": forecast,
            "hourly_forecast": hourly[:24],
            "rain_24h_mm": rain_24h,
            "rain_window_24h": self._rain_window(high_rain_hours),
            "uv_index": current.get("uv_index"),
            "wind_speed": current.get("wind_speed"),
            "humidity": current.get("humidity"),
            "air_quality": air_quality,
            "agro_climate_anomaly": self._agro_climate_anomaly(current, forecast),
            "drying_risk": self._drying_risk(current, forecast, hourly),
            "source_name": "Open-Meteo",
            "source_url": "https://open-meteo.com",
            "cache_status": source_summary.get("cache_status", current.get("cache_status", "unknown")),
            "is_mock": bool(source_summary.get("is_mock")),
            "is_realtime": bool(current.get("is_realtime")),
            "last_updated": current.get("last_updated") or datetime.now(),
        }

    def get_regional_prices(
        self,
        db: Session,
        crop_name: str = DEFAULT_CROP,
        regions: list[str] | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_crop = self._canonical_crop(crop_name)
        selected_regions = [self._canonical_region(item) for item in (regions or DEFAULT_REGIONS)]
        if force_refresh:
            self._refresh_prices(db, crop_name=selected_crop)

        rows = self._latest_prices_by_region(db, selected_crop)
        result = []
        for region in selected_regions:
            row = rows.get(normalize_location_key(region))
            if row:
                updated_at = row.CollectedAt or row.UpdatedAt
                item = {
                    "region": region,
                    "region_label": REGION_LABELS.get(region, region),
                    "price": float(row.PricePerKg),
                    "avg_price": float(row.PricePerKg),
                    "min_price": float(row.PricePerKg),
                    "max_price": float(row.PricePerKg),
                    "unit": "VND/kg",
                    "source_name": row.SourceName or "Database",
                    "source_url": row.SourceURL,
                    "last_updated": updated_at,
                    "cache_status": price_aggregator_service.cache_status(updated_at),
                    "is_realtime": bool(row.IsRealtime),
                    "is_mock": False,
                    "is_scraped": bool(row.IsScraped),
                }
            else:
                fallback_price = pricing_service.get_current_price(db, selected_crop, region, include_weather=False)
                item = {
                    "region": region,
                    "region_label": REGION_LABELS.get(region, region),
                    "price": float(fallback_price["current_price"]),
                    "avg_price": float(fallback_price["current_price"]),
                    "min_price": round(float(fallback_price["current_price"]) * 0.96, 2),
                    "max_price": round(float(fallback_price["current_price"]) * 1.04, 2),
                    "unit": "VND/kg",
                    "source_name": "Pricing fallback",
                    "source_url": None,
                    "last_updated": self._parse_datetime(fallback_price.get("last_updated")) or datetime.now(),
                    "cache_status": "mock",
                    "is_realtime": False,
                    "is_mock": True,
                    "is_scraped": False,
                }
            result.append(item)

        prices = [item["price"] for item in result if item.get("price")]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        span = max(max_price - min_price, 1)
        for item in result:
            item["price_index"] = round(((item["price"] - min_price) / span) * 100, 1) if prices else 0
            item["delta_vs_average_pct"] = self._delta_vs_average(item["price"], prices)

        return {
            "crop_name": selected_crop,
            "regions": result,
            "source_name": "MarketPrices DB + configured crawlers",
            "cache_status": "from_db" if any(not item["is_mock"] for item in result) else "mock",
            "generated_at": datetime.now(),
        }

    def get_news(
        self,
        db: Session,
        limit: int = 6,
        crop_name: str | None = None,
        region: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        if force_refresh:
            market_news_service.refresh_news()
        data = market_news_service.get_latest(
            db,
            limit=limit,
            crop_name=self._canonical_crop(crop_name) if crop_name else None,
            region=self._canonical_region(region) if region else None,
        )
        news = data.get("news", [])
        if crop_name and len(news) < limit:
            fallback = market_news_service.get_latest(db, limit=limit)
            seen = {item.get("news_id") or item.get("source_url") for item in news}
            for item in fallback.get("news", []):
                key = item.get("news_id") or item.get("source_url")
                if key in seen:
                    continue
                news.append(item)
                if len(news) >= limit:
                    break
        return {
            **data,
            "news": news[:limit],
            "source_name": "Market RSS",
            "source_url": "Configured RSS feeds",
            "is_realtime": True,
            "is_mock": False,
        }

    def get_realtime_market(
        self,
        db: Session,
        crop_name: str = DEFAULT_CROP,
        region: str = DEFAULT_REGION,
        force_refresh: bool = False,
    ) -> dict:
        selected_crop = self._canonical_crop(crop_name)
        selected_region = self._canonical_region(region)
        if force_refresh:
            self._refresh_prices(db, crop_name=selected_crop)

        featured = self.get_featured_crop(db, selected_crop, selected_region)
        return {
            "featured_crop": featured,
            "futures_reference": self._global_references(db),
            "exchange_rate": price_aggregator_service.exchange_rate(live=force_refresh),
            "stale_flags": {
                "local_price": featured.get("cache_status") in {"stale", "unknown", "mock"},
                "futures": not bool(self._global_references(db)),
                "exchange_rate": False,
            },
            "source_name": "Price aggregator",
            "source_url": "Configured price sources + Stooq",
            "cache_status": featured.get("cache_status", "unknown"),
            "last_updated": datetime.now(),
        }

    def get_data_health(
        self,
        db: Session,
        region: str = DEFAULT_REGION,
        crop_name: str = DEFAULT_CROP,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        latest_weather = self.get_weather_overview(db, selected_region)
        latest_price = self.get_featured_crop(db, selected_crop, selected_region)
        latest_news = db.query(MarketNews).order_by(desc(MarketNews.PublishedAt), desc(MarketNews.CreatedAt)).first()
        latest_price_log = self._latest_ingestion_log(db, "refresh_market_prices")
        latest_news_log = self._latest_ingestion_log(db, "refresh_market_news")

        sources = [
            self._source_health_item(
                "Open-Meteo Forecast",
                "weather_api",
                "https://open-meteo.com/en/docs",
                latest_weather.get("last_updated"),
                latest_weather.get("cache_status"),
                latest_weather.get("is_mock"),
                "Realtime weather, hourly forecast, UV, wind and rain risk.",
            ),
            self._source_health_item(
                "Open-Meteo Air Quality",
                "air_quality_api",
                "https://open-meteo.com/en/docs/air-quality-api",
                datetime.now(),
                "available",
                False,
                "Hourly PM2.5/PM10/O3 used for spraying, drying and outdoor-work risk.",
            ),
            self._source_health_item(
                "Market RSS",
                "rss",
                "Configured RSS feeds",
                latest_news.PublishedAt if latest_news else None,
                "ok" if latest_news else "degraded",
                False,
                "Near-realtime market news with sentiment badge.",
                latest_news_log,
            ),
            self._source_health_item(
                "Vietnam Food Association / configured crawlers",
                "crawler",
                "https://e.vietfood.org.vn/market-update/export-price/",
                latest_price.get("last_updated"),
                latest_price.get("cache_status"),
                latest_price.get("is_mock"),
                "Scraped market price source; never labelled realtime if stale.",
                latest_price_log,
            ),
            self._source_health_item(
                "Stooq commodity futures",
                "global_futures",
                "https://stooq.com",
                self._latest_global_updated_at(db),
                "ok" if self._global_references(db) else "missing",
                False,
                "Global reference for coffee, corn, soybean, rice and related commodities.",
            ),
            self._source_health_item(
                "Exchange rate USD/VND",
                "exchange_rate",
                "https://open.er-api.com",
                datetime.now(),
                "available",
                False,
                "Used when converting futures/export reference prices.",
            ),
            self._source_health_item(
                "NASA POWER agro-climate",
                "monthly_reference",
                "https://power.larc.nasa.gov",
                None,
                "planned",
                False,
                "Reference source for climate anomaly; dashboard currently uses local rule baseline when unavailable.",
            ),
            self._source_health_item(
                "FAO / World Bank monthly references",
                "monthly_reference",
                "https://www.worldbank.org/en/research/commodity-markets",
                None,
                "planned",
                False,
                "Monthly macro context, not labelled realtime.",
            ),
            self._source_health_item(
                "Application DB cache",
                "database",
                "local database",
                datetime.now(),
                "ok",
                False,
                "Stores history, fallback rows, dashboard cache and ingestion logs.",
            ),
        ]
        return {
            "region": selected_region,
            "crop_name": selected_crop,
            "sources": sources,
            "score": self._source_score(sources),
            "generated_at": datetime.now(),
        }

    def refresh_dashboard(
        self,
        db: Session,
        *,
        source: str = "all",
        region: str = DEFAULT_REGION,
        crop_name: str = DEFAULT_CROP,
    ) -> dict:
        selected_source = source.lower()
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        results: dict[str, Any] = {}

        if selected_source in {"all", "weather"}:
            results["weather"] = weather_service.refresh_region_weather(db, selected_region, days=7)
        if selected_source in {"all", "prices", "price"}:
            results["prices"] = self._refresh_prices(db, crop_name=selected_crop)
        if selected_source in {"all", "news"}:
            results["news"] = market_news_service.refresh_news()

        self._invalidate_cache(db, selected_region, selected_crop)
        return {
            "source": selected_source,
            "region": selected_region,
            "crop_name": selected_crop,
            "results": results,
            "data_health": self.get_data_health(db, selected_region, selected_crop),
            "refreshed_at": datetime.now(),
        }

    def reset_and_load_dashboard(
        self,
        db: Session,
        *,
        user_id: int | None = None,
        region: str = DEFAULT_REGION,
        crop_name: str = DEFAULT_CROP,
    ) -> dict:
        selected_region = self._canonical_region(region)
        selected_crop = self._canonical_crop(crop_name)
        self._delete_dashboard_realtime_data(db, selected_region, selected_crop)

        refresh_results: dict[str, Any] = {}
        jobs = {
            "weather": lambda: self._refresh_weather_in_new_session(selected_region),
            "prices": lambda: self._refresh_prices_in_new_session(selected_crop),
            "news": market_news_service.refresh_news,
        }
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {executor.submit(job): name for name, job in jobs.items()}
            for future in as_completed(future_map):
                name = future_map[future]
                try:
                    refresh_results[name] = future.result()
                except Exception as exc:
                    refresh_results[name] = {"status": "failed", "error": str(exc)}

        db.expire_all()
        summary = self.get_summary(
            db,
            user_id=user_id,
            region=selected_region,
            crop_name=selected_crop,
            force_refresh_weather=False,
            force_refresh_market=False,
            force_refresh_news=False,
        )
        summary["reset_refresh"] = refresh_results
        summary["cache_status"] = "reset_refreshed"
        return summary

    def get_ai_recommendation(self, db: Session, crop_name: str = DEFAULT_CROP, region: str = DEFAULT_REGION) -> dict:
        selected_crop = self._canonical_crop(crop_name)
        selected_region = self._canonical_region(region)
        market = self.get_featured_crop(db, selected_crop, selected_region)
        weather_risk = self.get_weather_risk(db, selected_region, selected_crop)
        trend = self.get_price_trend(db, selected_crop, selected_region, days=7)
        return self._build_ai_from_signals(selected_crop, selected_region, market, weather_risk, trend)

    def _build_ai_from_signals(
        self,
        selected_crop: str,
        selected_region: str,
        market: dict,
        weather_risk: dict,
        trend: dict,
    ) -> dict:
        risk_score = weather_risk.get("risk_score", 0)
        forecast_trend = trend.get("trend", "stable")

        if forecast_trend == "increasing" and risk_score < 55:
            action = "hold"
            title = "Nên giữ hàng có kiểm soát"
            description = "Giá dự báo nhích lên trong khi rủi ro thời tiết chưa quá cao. Chỉ giữ nếu kho bảo quản ổn và theo dõi mưa/độ ẩm hằng ngày."
        elif risk_score >= 70:
            action = "sell_sooner"
            title = "Nên bán sớm hoặc chia lô"
            description = "Rủi ro thời tiết cao có thể ảnh hưởng phơi/sấy, bảo quản hoặc vận chuyển. Ưu tiên giảm tồn kho nhạy cảm với ẩm."
        else:
            action = "sell_in_batches"
            title = "Nên bán từng phần"
            description = "Tín hiệu giá và thời tiết còn lẫn lộn. Bán từng phần giúp giảm rủi ro biến động giá và sự kiện thị trường."

        confidence = min(0.86, max(0.42, float(trend.get("confidence", 0.55)) - (0.08 if market.get("is_mock") else 0)))
        return {
            "crop_name": selected_crop,
            "region": selected_region,
            "action": action,
            "title": title,
            "description": description,
            "confidence": round(confidence, 2),
            "expected_price": trend["forecast"][-1]["forecast_price"] if trend.get("forecast") else market["price"],
            "period": "7 ngày tới",
            "reason_codes": trend.get("reason_codes", []) + [f"weather_risk_{weather_risk.get('risk_level')}"],
            "source": "explainable_rule_ai",
            "summary_provider": "llm_ready" if (settings.CLAUDE_API_KEY or settings.AI_API_KEY) else "rule_based",
            "is_mock": bool(market.get("is_mock")) or bool(weather_risk.get("is_mock")),
            "last_updated": datetime.now(),
        }

    # ------------------------------------------------------------------ #
    # Forecast, alerts and risk helpers
    # ------------------------------------------------------------------ #

    def _build_forecast(
        self,
        *,
        current_price: float,
        history: list[dict],
        days: int,
        weather: dict,
        news_items: list[dict],
        futures: dict | None,
        current_is_mock: bool,
    ) -> tuple[list[dict], list[str], float]:
        history_prices = [float(item["avg_price"]) for item in history if item.get("avg_price")]
        if len(history_prices) >= 2:
            recent_base = mean(history_prices[-min(7, len(history_prices)):])
            previous_base = mean(history_prices[: max(1, min(7, len(history_prices)))])
            history_drift = ((recent_base - previous_base) / previous_base) / max(len(history_prices), 1)
        else:
            history_drift = 0

        forecast_weather = weather.get("forecast", [])
        rainy_days = sum(1 for item in forecast_weather[:days] if float(item.get("rainfall") or 0) >= 10)
        hot_days = sum(1 for item in forecast_weather[:days] if float(item.get("temp_max") or 0) >= 35)
        positive_news = sum(1 for item in news_items if (item.get("sentiment") or "").lower() == "positive")
        negative_news = sum(1 for item in news_items if (item.get("sentiment") or "").lower() == "negative")

        weather_factor = min(0.006, rainy_days * 0.0015 + hot_days * 0.0008)
        news_factor = max(-0.006, min(0.006, (positive_news - negative_news) * 0.0015))
        futures_factor = 0.002 if futures else 0
        daily_drift = max(-0.018, min(0.018, history_drift + weather_factor + news_factor + futures_factor))

        reasons = []
        if history_prices:
            reasons.append("history_trend")
        else:
            reasons.append("limited_history")
        if rainy_days:
            reasons.append("weather_rain")
        if hot_days:
            reasons.append("weather_heat_uv")
        if positive_news or negative_news:
            reasons.append("news_sentiment")
        if futures:
            reasons.append("global_futures_reference")
        if current_is_mock:
            reasons.append("mock_or_fallback_price")

        confidence = 0.72
        if len(history_prices) < 7:
            confidence -= 0.16
        if current_is_mock:
            confidence -= 0.18
        if not news_items:
            confidence -= 0.05
        if not futures:
            confidence -= 0.04
        confidence = round(max(0.35, min(0.86, confidence)), 2)
        spread = 0.06 + (1 - confidence) * 0.12

        forecast = []
        price = float(current_price)
        for offset in range(1, days + 1):
            day_weather = forecast_weather[offset - 1] if offset - 1 < len(forecast_weather) else {}
            weather_bump = 0.001 if float(day_weather.get("rainfall") or 0) >= 10 else 0
            price = price * (1 + daily_drift + weather_bump)
            forecast.append(
                {
                    "date": (date.today() + timedelta(days=offset)).isoformat(),
                    "forecast_price": round(price, 2),
                    "predicted_price": round(price, 2),
                    "lower_bound": round(price * (1 - spread), 2),
                    "upper_bound": round(price * (1 + spread), 2),
                    "confidence": confidence,
                    "confidence_label": self._confidence_label(confidence),
                    "trend": self._trend_from_change(daily_drift * 100),
                    "reason_codes": reasons,
                    "source_name": "Dashboard explainable forecast",
                    "cache_status": "computed",
                    "is_mock": current_is_mock and len(history_prices) < 2,
                }
            )
        return forecast, reasons, confidence

    def _build_alert_center(
        self,
        featured: dict,
        weather_risk: dict,
        news_items: list[dict],
        regional_prices: list[dict],
    ) -> list[dict]:
        alerts = []
        for alert in weather_risk.get("alerts", [])[:3]:
            alerts.append(
                {
                    "type": "weather",
                    "severity": alert.get("severity", "medium"),
                    "title": alert.get("title", "Cảnh báo thời tiết"),
                    "message": alert.get("message") or alert.get("recommendation"),
                    "source_name": weather_risk.get("source_name", "Open-Meteo"),
                    "last_updated": weather_risk.get("last_updated"),
                    "cache_status": weather_risk.get("cache_status"),
                }
            )

        week_change = featured.get("change_week_pct")
        if week_change is not None and abs(week_change) >= 5:
            alerts.append(
                {
                    "type": "price",
                    "severity": "high" if abs(week_change) >= 10 else "medium",
                    "title": f"Giá biến động {week_change:+.1f}% trong tuần",
                    "message": "Kiểm tra ngưỡng cảnh báo giá và so sánh thêm vùng lân cận.",
                    "source_name": featured.get("source_name"),
                    "last_updated": featured.get("last_updated"),
                    "cache_status": featured.get("cache_status"),
                }
            )

        if regional_prices:
            current = next((item for item in regional_prices if item["region"] == featured.get("location")), None)
            highest = max(regional_prices, key=lambda item: item.get("price") or 0)
            if current and current.get("price") and highest.get("price", 0) > current["price"] * 1.05:
                alerts.append(
                    {
                        "type": "price",
                        "severity": "medium",
                        "title": f"{highest['region_label']} cao hơn {self._delta_pct(highest['price'], current['price']):.1f}%",
                        "message": "Có thể cân nhắc kênh bán hoặc vận chuyển sang vùng giá tốt hơn nếu chi phí phù hợp.",
                        "source_name": highest.get("source_name"),
                        "last_updated": highest.get("last_updated"),
                        "cache_status": highest.get("cache_status"),
                    }
                )

        for item in news_items:
            if (item.get("sentiment") or "").lower() == "negative":
                alerts.append(
                    {
                        "type": "event",
                        "severity": "medium",
                        "title": item.get("title", "Tin tức thị trường cần chú ý"),
                        "message": item.get("summary"),
                        "source_name": item.get("source_name"),
                        "source_url": item.get("source_url"),
                        "last_updated": item.get("published_at"),
                        "cache_status": "rss",
                    }
                )
                break

        if not alerts:
            alerts.append(
                {
                    "type": "system",
                    "severity": "low",
                    "title": "Chưa có cảnh báo lớn",
                    "message": "Dữ liệu hiện tại chưa vượt ngưỡng rủi ro thời tiết, giá hoặc tin tức.",
                    "source_name": "Dashboard rules",
                    "cache_status": "computed",
                    "last_updated": datetime.now(),
                }
            )
        return alerts[:6]

    def _weather_risk_score(
        self,
        current: dict,
        forecast: list[dict],
        hourly: list[dict],
        alerts: list[dict],
        air_quality: dict,
    ) -> int:
        score = 15
        score += min(35, len([item for item in alerts if item.get("severity") == "high"]) * 18)
        score += min(20, len([item for item in alerts if item.get("severity") == "medium"]) * 8)
        score += min(15, sum(float(item.get("rainfall") or 0) for item in forecast[:3]) / 4)
        score += 12 if float(current.get("uv_index") or 0) >= 8 else 0
        score += 10 if float(current.get("wind_speed") or 0) >= 25 else 0
        score += 8 if float(current.get("humidity") or 0) >= 90 else 0
        score += 10 if (air_quality.get("aqi") or 0) >= 101 else 0
        score += 5 if any(float(item.get("rain_probability") or 0) >= 70 for item in hourly[:24]) else 0
        return int(max(0, min(100, round(score))))

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 70:
            return "high"
        if score >= 45:
            return "medium"
        return "low"

    def _air_quality(self, region: str, live: bool = False) -> dict:
        if not live:
            return {
                "region": region,
                "aqi": None,
                "pm25": None,
                "pm10": None,
                "o3": None,
                "source_name": "Open-Meteo Air Quality",
                "source_url": "https://open-meteo.com/en/docs/air-quality-api",
                "cache_status": "on_refresh",
                "is_realtime": False,
                "is_mock": False,
                "last_updated": None,
                "recommendation": "PM2.5/AQI được cập nhật trong luồng nạp lại dữ liệu khi mở dashboard.",
            }
        try:
            return weather_service.client.get_air_quality(region, hours=24)
        except Exception as exc:
            return {
                "region": region,
                "aqi": None,
                "pm25": None,
                "pm10": None,
                "o3": None,
                "source_name": "Open-Meteo Air Quality",
                "source_url": "https://open-meteo.com/en/docs/air-quality-api",
                "cache_status": "degraded",
                "is_realtime": False,
                "is_mock": True,
                "last_updated": datetime.now(),
                "recommendation": "Chưa lấy được chất lượng không khí; dùng cảnh báo mưa, UV và gió làm chính.",
                "error": str(exc),
            }

    @staticmethod
    def _agro_climate_anomaly(current: dict, forecast: list[dict]) -> dict:
        baseline_temp = 29.0
        baseline_rain_7d = 35.0
        avg_temp = mean([float(item.get("temperature") or baseline_temp) for item in forecast[:7]]) if forecast else float(current.get("temperature") or baseline_temp)
        rain_7d = sum(float(item.get("rainfall") or 0) for item in forecast[:7])
        return {
            "temperature_anomaly_c": round(avg_temp - baseline_temp, 1),
            "rainfall_anomaly_mm": round(rain_7d - baseline_rain_7d, 1),
            "source_name": "Local climate baseline; NASA POWER reference pending",
            "source_url": "https://power.larc.nasa.gov",
            "cache_status": "computed",
            "is_mock": False,
        }

    @staticmethod
    def _drying_risk(current: dict, forecast: list[dict], hourly: list[dict]) -> dict:
        rain_24h = sum(float(item.get("rainfall") or 0) for item in hourly[:24])
        humidity = float(current.get("humidity") or 0)
        sunshine = mean([float(item.get("sunshine_hours") or 0) for item in forecast[:3]]) if forecast else 0
        score = min(100, round(rain_24h * 4 + max(0, humidity - 75) + max(0, 6 - sunshine) * 5))
        if score >= 70:
            label = "high"
            recommendation = "Hạn chế phơi ngoài trời, ưu tiên sấy có mái che và kiểm tra ẩm kho."
        elif score >= 40:
            label = "medium"
            recommendation = "Theo dõi mưa trong 24h, chỉ phơi/sấy khi xác suất mưa thấp."
        else:
            label = "low"
            recommendation = "Điều kiện tương đối phù hợp cho phơi/sấy, vẫn tránh khung giờ UV cao."
        return {"score": score, "level": label, "recommendation": recommendation}

    # ------------------------------------------------------------------ #
    # DB helpers
    # ------------------------------------------------------------------ #

    def _latest_market_price(self, db: Session, crop_name: str, region: str) -> MarketPrice | None:
        try:
            crop = ensure_crop(db, crop_name)
            accepted = {
                normalize_location_key(region),
                normalize_location_key(self._canonical_region(region)),
                normalize_location_key(REGION_LABELS.get(region, region)),
            }
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(100)
                .all()
            )
            for row in rows:
                if normalize_location_key(row.Region) in accepted:
                    return row
        except SQLAlchemyError:
            db.rollback()
        return None

    def _latest_prices_by_region(self, db: Session, crop_name: str) -> dict[str, MarketPrice]:
        try:
            crop = ensure_crop(db, crop_name)
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(500)
                .all()
            )
        except SQLAlchemyError:
            db.rollback()
            return {}

        result = {}
        for row in rows:
            key = normalize_location_key(row.Region)
            if key not in result:
                result[key] = row
        return result

    def _load_price_history(self, db: Session, crop_name: str, region: str, days: int = 60) -> list[dict]:
        try:
            history = pricing_service.get_price_history(db, crop_name, region, days)
            rows = []
            for item in history:
                avg_price = item.get("avg_price")
                if avg_price is None:
                    continue
                rows.append(
                    {
                        "date": item.get("date"),
                        "avg_price": float(avg_price),
                        "min_price": float(item.get("min_price") or avg_price),
                        "max_price": float(item.get("max_price") or avg_price),
                        "source_name": item.get("source_name", "PriceHistory"),
                    }
                )
            return rows
        except Exception:
            return []

    def _price_change_pct(self, db: Session, crop_name: str, region: str, days_back: int) -> float | None:
        try:
            crop = ensure_crop(db, crop_name)
            latest = self._latest_market_price(db, crop_name, region)
            if not latest:
                return None
            target_date = latest.PriceDate - timedelta(days=days_back)
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.PriceDate <= target_date)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(100)
                .all()
            )
            accepted = {normalize_location_key(region), normalize_location_key(self._canonical_region(region))}
            previous = next((row for row in rows if normalize_location_key(row.Region) in accepted), None)
            if previous and previous.PricePerKg:
                return self._delta_pct(float(latest.PricePerKg), float(previous.PricePerKg))
        except SQLAlchemyError:
            db.rollback()
        return None

    def _latest_global_reference(self, db: Session, crop_name: str) -> dict | None:
        references = self._global_references(db)
        normalized_crop = normalize_location_key(crop_name)
        for item in references:
            if normalize_location_key(item.get("crop_name") or "") in {normalized_crop, "gao" if normalized_crop == "lua" else normalized_crop}:
                return item
        return references[0] if references else None

    def _global_references(self, db: Session) -> list[dict]:
        try:
            rows = (
                db.query(MarketPrice, Crop)
                .join(Crop, Crop.CropID == MarketPrice.CropID)
                .filter(MarketPrice.Region == "Global Futures")
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(30)
                .all()
            )
        except SQLAlchemyError:
            db.rollback()
            return []

        result = []
        seen = set()
        for row, crop in rows:
            if crop.CropID in seen:
                continue
            seen.add(crop.CropID)
            updated_at = row.CollectedAt or row.UpdatedAt
            result.append(
                {
                    "crop_name": crop.CropName,
                    "display_name": CROP_LABELS.get(crop.CropName, crop.CropName.title()),
                    "price": float(row.PricePerKg),
                    "unit": "VND/kg",
                    "market_type": row.MarketType,
                    "source_name": row.SourceName or "Stooq commodity futures",
                    "source_url": row.SourceURL,
                    "last_updated": updated_at,
                    "cache_status": price_aggregator_service.cache_status(updated_at),
                    "is_realtime": bool(row.IsRealtime),
                    "is_mock": False,
                }
            )
        return result[:8]

    def _latest_global_updated_at(self, db: Session) -> datetime | None:
        refs = self._global_references(db)
        dates = [self._parse_datetime(item.get("last_updated")) for item in refs if item.get("last_updated")]
        dates = [item for item in dates if item]
        return max(dates) if dates else None

    def _refresh_prices(self, db: Session, crop_name: str | None = None) -> dict:
        return price_aggregator_service.refresh_prices(db, crop_name=crop_name)

    def _refresh_weather_in_new_session(self, region: str) -> dict:
        session = SessionLocal()
        try:
            return weather_service.refresh_region_weather(session, region, days=7)
        finally:
            session.close()

    def _refresh_prices_in_new_session(self, crop_name: str) -> dict:
        session = SessionLocal()
        try:
            return price_aggregator_service.refresh_prices(session, crop_name=crop_name)
        finally:
            session.close()

    def _delete_dashboard_realtime_data(self, db: Session, region: str, crop_name: str) -> None:
        self._invalidate_cache(db, region, crop_name)
        try:
            db.query(MarketNews).delete(synchronize_session=False)
            crop = ensure_crop(db, crop_name)
            db.query(MarketPrice).filter(
                MarketPrice.CropID == crop.CropID,
                (MarketPrice.SourceURL.is_not(None)) | (MarketPrice.Region == "Global Futures"),
            ).delete(synchronize_session=False)
            db.commit()
        except Exception:
            db.rollback()

    # ------------------------------------------------------------------ #
    # Cache and source health helpers
    # ------------------------------------------------------------------ #

    def _read_cache(self, db: Session, key: str) -> dict | None:
        try:
            row = db.query(DashboardCache).filter(DashboardCache.Key == key).first()
            if not row or row.ExpiresAt <= datetime.now():
                return None
            return json.loads(row.PayloadJSON)
        except Exception:
            db.rollback()
            return None

    def _write_cache(self, db: Session, key: str, payload: dict) -> None:
        try:
            row = db.query(DashboardCache).filter(DashboardCache.Key == key).first()
            if row is None:
                row = DashboardCache(Key=key)
                db.add(row)
            row.PayloadJSON = json.dumps(payload, ensure_ascii=False, default=str)
            row.ExpiresAt = datetime.now() + timedelta(seconds=DASHBOARD_CACHE_TTL_SECONDS)
            db.commit()
        except Exception:
            db.rollback()

    def _invalidate_cache(self, db: Session, region: str, crop_name: str) -> None:
        try:
            prefix = self._cache_key("summary", region, crop_name, None).rsplit(":", 1)[0]
            rows = db.query(DashboardCache).filter(DashboardCache.Key.like(f"{prefix}%")).all()
            for row in rows:
                db.delete(row)
            db.commit()
        except Exception:
            db.rollback()

    @staticmethod
    def _cache_key(namespace: str, region: str, crop_name: str, user_id: int | None) -> str:
        return f"dashboard:{namespace}:{normalize_location_key(region)}:{normalize_location_key(crop_name)}:{user_id or 'anon'}"

    def _source_health_item(
        self,
        name: str,
        source_type: str,
        url: str,
        last_updated: Any,
        cache_status: str | None,
        is_mock: bool | None,
        note: str,
        log: DataIngestionLog | None = None,
    ) -> dict:
        last_success_at = log.FinishedAt if log and log.Status == "success" else self._parse_datetime(last_updated)
        if is_mock:
            status = "mock"
        elif cache_status in {"fresh", "live", "updated", "refreshed", "hit", "from_db", "ok", "available"}:
            status = "ok"
        elif cache_status in {"planned"}:
            status = "planned"
        elif cache_status in {"stale"}:
            status = "stale"
        else:
            status = cache_status or "unknown"
        return {
            "name": name,
            "type": source_type,
            "url": url,
            "status": status,
            "cache_status": cache_status or "unknown",
            "last_success_at": last_success_at,
            "last_error": log.ErrorMessage if log and log.Status == "failed" else None,
            "reliability_score": self._reliability_score(status),
            "note": note,
        }

    @staticmethod
    def _latest_ingestion_log(db: Session, job_name: str) -> DataIngestionLog | None:
        try:
            return (
                db.query(DataIngestionLog)
                .filter(DataIngestionLog.JobName == job_name)
                .order_by(desc(DataIngestionLog.StartedAt))
                .first()
            )
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def _source_score(sources: list[dict]) -> int:
        if not sources:
            return 0
        values = [float(item.get("reliability_score") or 0) for item in sources]
        return int(round(mean(values)))

    @staticmethod
    def _reliability_score(status: str) -> int:
        return {
            "ok": 95,
            "available": 90,
            "fresh": 95,
            "stale": 65,
            "degraded": 50,
            "missing": 35,
            "mock": 25,
            "planned": 40,
        }.get(status, 55)

    def _data_quality_score(
        self,
        featured: dict,
        weather_risk: dict,
        regional_prices: list[dict],
        news: dict,
        sources: list[dict],
    ) -> int:
        base = self._source_score(sources)
        penalties = 0
        if featured.get("is_mock"):
            penalties += 12
        if weather_risk.get("is_mock"):
            penalties += 10
        if any(item.get("is_mock") for item in regional_prices):
            penalties += 8
        if not news.get("news"):
            penalties += 8
        return max(0, min(100, base - penalties))

    # ------------------------------------------------------------------ #
    # Small utility helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _canonical_region(region: str | None) -> str:
        if not region:
            return DEFAULT_REGION
        canonical = canonical_region_name(region)
        key = normalize_location_key(canonical)
        for known in DEFAULT_REGIONS:
            if normalize_location_key(known) == key or normalize_location_key(REGION_LABELS.get(known, known)) == key:
                return known
        return canonical

    @staticmethod
    def _canonical_crop(crop_name: str | None) -> str:
        if not crop_name:
            return DEFAULT_CROP
        key = normalize_location_key(crop_name)
        aliases = {
            "lúa": "lua",
            "lua": "lua",
            "gao": "lua",
            "rice": "lua",
            "cafe": "ca phe",
            "ca phe": "ca phe",
            "coffee": "ca phe",
            "pepper": "ho tieu",
            "ho tieu": "ho tieu",
            "tieu": "ho tieu",
            "durian": "sau rieng",
            "sau rieng": "sau rieng",
            "dragon fruit": "thanh long",
            "thanh long": "thanh long",
            "corn": "ngo",
            "ngo": "ngo",
        }
        return aliases.get(key, crop_name.strip().lower())

    @staticmethod
    def _available_regions() -> list[dict]:
        return [{"value": item, "label": REGION_LABELS.get(item, item)} for item in DEFAULT_REGIONS]

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                return None
        return None

    @staticmethod
    def _age_minutes(value: datetime | None) -> int | None:
        if not value:
            return None
        return max(0, int((datetime.now() - value).total_seconds() / 60))

    @staticmethod
    def _format_pct(value: float | None) -> str:
        if value is None:
            return "+0.0%"
        return f"{value:+.1f}%"

    @staticmethod
    def _trend_from_change(value: float | None) -> str:
        if value is None:
            return "stable"
        if value > 0.5:
            return "up"
        if value < -0.5:
            return "down"
        return "stable"

    @staticmethod
    def _forecast_trend(forecast: list[dict]) -> str:
        if len(forecast) < 2:
            return "stable"
        return DashboardService._trend_from_change(
            DashboardService._delta_pct(forecast[-1]["forecast_price"], forecast[0]["forecast_price"])
        )

    @staticmethod
    def _confidence_label(value: float) -> str:
        if value >= 0.72:
            return "high"
        if value >= 0.52:
            return "medium"
        return "low"

    @staticmethod
    def _delta_pct(current: float, previous: float) -> float:
        if not previous:
            return 0.0
        return ((float(current) - float(previous)) / float(previous)) * 100

    @staticmethod
    def _delta_vs_average(price: float, prices: list[float]) -> float:
        if not prices:
            return 0.0
        avg = mean(prices)
        if not avg:
            return 0.0
        return round(((price - avg) / avg) * 100, 1)

    @staticmethod
    def _rain_window(items: list[dict]) -> str | None:
        if not items:
            return None
        first = items[0].get("time") or items[0].get("forecast_at")
        last = items[min(len(items) - 1, 3)].get("time") or items[min(len(items) - 1, 3)].get("forecast_at")
        return f"{first} - {last}" if first and last else None


dashboard_service = DashboardService()
