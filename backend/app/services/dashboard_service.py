from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta

from sqlalchemy import desc, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.integrations.weather_client import WeatherClient
from app.models.crop import Crop
from app.models.harvest import HarvestSchedule
from app.models.market_news import MarketNews
from app.models.notification import Notification
from app.models.price import MarketPrice
from app.models.quality import QualityCheck
from app.models.weather import WeatherData, WeatherObservation
from app.repositories.common import ensure_crop
from app.services.market_news_service import market_news_service
from app.services.price_aggregator_service import price_aggregator_service
from app.services.pricing_service import pricing_service
from app.services.weather_service import weather_service


DEFAULT_REGIONS = ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho", "Lam Dong", "Dak Lak"]


class DashboardService:
    def __init__(self):
        self.weather_client = WeatherClient()

    def get_summary(
        self,
        db: Session,
        user_id: int | None = None,
        region: str | None = None,
        crop_name: str = "lua",
        force_refresh_weather: bool = False,
        force_refresh_market: bool = False,
        force_refresh_news: bool = False,
    ) -> dict:
        selected_region = self._clean_region(region)
        selected_crop = self._clean_crop(crop_name)

        if force_refresh_market:
            price_aggregator_service.refresh_prices(db, crop_name=selected_crop)
        if force_refresh_news:
            market_news_service.refresh_news()

        featured = self.get_featured_crop(
            db,
            crop_name=selected_crop,
            region=selected_region,
            force_refresh=False,
        )
        weather_risk = self.get_weather_risk(
            db,
            region=selected_region,
            crop_name=selected_crop,
            force_refresh=force_refresh_weather,
        )
        trend = self.get_price_trend(db, crop_name=selected_crop, region=selected_region, days=7)
        news = self.get_news(db, limit=6, crop_name=selected_crop, region=None, force_refresh=False)
        regional_prices = self.get_regional_prices(db, crop_name=selected_crop)["regions"]
        realtime_market = self.get_realtime_market(db, crop_name=selected_crop, region=selected_region)

        try:
            schedules_query = db.query(HarvestSchedule)
            quality_query = db.query(QualityCheck)
            notification_query = db.query(Notification).filter(Notification.IsDeleted.is_(False))
            if user_id:
                schedules_query = schedules_query.filter(HarvestSchedule.UserID == user_id)
                quality_query = quality_query.filter(QualityCheck.UserID == user_id)
                notification_query = notification_query.filter(Notification.UserID == user_id)
            active_seasons = schedules_query.filter(HarvestSchedule.ActualHarvestDate.is_(None)).count()
            quality_checks = quality_query.count()
            unread_notifications = notification_query.filter(Notification.IsRead.is_(False)).count()
        except SQLAlchemyError:
            db.rollback()
            active_seasons = quality_checks = unread_notifications = 0

        return {
            "region": selected_region,
            "crop_name": selected_crop,
            "featured_crop": featured,
            "weather": self.get_weather_overview(db, selected_region, force_refresh=False),
            "weather_risk": weather_risk,
            "forecast": trend["forecast"],
            "price_trend": trend,
            "regional_prices": regional_prices,
            "news": news["news"],
            "realtime_market": realtime_market,
            "alert_center": weather_risk.get("alerts", []),
            "ai_recommendation": self.get_ai_recommendation(db, selected_crop, selected_region),
            "active_seasons": active_seasons,
            "quality_checks": quality_checks,
            "unread_notifications": unread_notifications,
            "generated_at": datetime.now(),
            "cache_status": "from_db",
        }

    def reset_and_load_dashboard(
        self,
        db: Session,
        user_id: int | None = None,
        region: str | None = None,
        crop_name: str = "lua",
    ) -> dict:
        selected_region = self._clean_region(region)
        selected_crop = self._clean_crop(crop_name)

        self._delete_dashboard_realtime_data(db, selected_region, selected_crop)

        refresh_results: dict[str, dict] = {}
        tasks = {
            "weather": lambda: self._refresh_weather_in_new_session(selected_region),
            "prices": lambda: self._refresh_prices_in_new_session(selected_crop),
            "news": market_news_service.refresh_news,
        }
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(task): name for name, task in tasks.items()}
            for future in as_completed(futures):
                name = futures[future]
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

    def get_featured_crop(
        self,
        db: Session,
        crop_name: str = "lua",
        region: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_region = self._clean_region(region)
        selected_crop = self._clean_crop(crop_name)
        if force_refresh:
            price_aggregator_service.refresh_prices(db, crop_name=selected_crop)

        row = self._latest_market_price_for_crop(db, selected_crop, selected_region)
        if row:
            current_price = float(row.PricePerKg)
            last_updated = row.UpdatedAt
            source_name = row.SourceName or "database"
            source_url = row.SourceURL
            is_mock = False
            cache_status = "from_db"
        else:
            current = pricing_service.get_current_price(db, selected_crop, selected_region)
            current_price = float(current["current_price"])
            last_updated = current.get("last_updated") or datetime.now()
            source_name = current.get("source_name") or "pricing_service"
            source_url = None
            is_mock = bool(current.get("is_mock"))
            cache_status = "mock" if is_mock else "from_db"

        history = pricing_service.get_price_history(db, selected_crop, selected_region, 7)
        previous_day = history[-2]["avg_price"] if len(history) >= 2 else current_price
        first_week = history[0]["avg_price"] if history else current_price

        return {
            "name": selected_crop,
            "display_name": self._display_crop(selected_crop),
            "location": selected_region,
            "price": current_price,
            "unit": "VND/kg",
            "change": self._format_pct(self._pct_change(current_price, previous_day)),
            "change_day_pct": self._pct_change(current_price, previous_day),
            "change_week_pct": self._pct_change(current_price, first_week),
            "trend": pricing_service.analyze_price_trend(db, selected_crop, selected_region),
            "last_updated": last_updated,
            "source_name": source_name,
            "source_url": source_url,
            "is_realtime": False,
            "is_mock": is_mock,
            "cache_status": cache_status,
        }

    def get_price_trend(self, db: Session, crop_name: str = "lua", region: str = "Ha Noi", days: int = 7) -> dict:
        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        history = pricing_service.get_price_history(db, selected_crop, selected_region, max(days, 7))
        recent = history[-days:] if history else []
        base_price = recent[-1]["avg_price"] if recent else pricing_service.get_current_price(db, selected_crop, selected_region)["current_price"]
        trend = pricing_service.analyze_price_trend(db, selected_crop, selected_region)
        forecast = []
        for offset in range(1, days + 1):
            direction = 0.006 if trend in {"up", "increasing", "stable"} else -0.003
            predicted = round(float(base_price) * (1 + offset * direction), 2)
            forecast.append(
                {
                    "date": (date.today() + timedelta(days=offset)).isoformat(),
                    "forecast_price": predicted,
                    "predicted_price": predicted,
                    "confidence": "high" if offset <= 3 else "medium",
                    "trend": "up" if direction > 0 else "down",
                    "reason_codes": ["db_price_history", "rule_based_trend"],
                }
            )
        return {
            "crop_name": selected_crop,
            "region": selected_region,
            "history": recent,
            "forecast": forecast,
            "trend": trend,
            "is_mock": any(item.get("is_mock") for item in recent) if recent else True,
        }

    def get_weather_overview(self, db: Session, region: str = "Ha Noi", force_refresh: bool = False) -> dict:
        selected_region = self._clean_region(region)
        if force_refresh:
            current = weather_service.get_current_weather(db, selected_region, force_refresh=True)
        else:
            current = self._current_weather_from_db(db, selected_region) or weather_service.get_current_weather(db, selected_region)
        forecast = self._weather_forecast_from_db(db, selected_region, 7)
        if not forecast:
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
        }

    def get_weather_risk(
        self,
        db: Session,
        region: str = "Ha Noi",
        crop_name: str = "lua",
        growth_stage: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        overview = self.get_weather_overview(db, region, force_refresh=force_refresh)
        current = overview.get("current", {})
        forecast = overview.get("forecast", [])
        hourly = weather_service._build_hourly(current)[:24]
        alerts = weather_service.generate_alerts(current, forecast, crop_name=crop_name, growth_stage=growth_stage)
        recommendations = weather_service.build_activity_recommendations(current, forecast, hourly, crop_name, growth_stage)
        risk_score = self._weather_risk_score(current, forecast, alerts)
        risk_level = "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low"
        rain_24h = round(sum(float(item.get("rainfall") or 0) for item in hourly[:24]), 1)
        return {
            "region": self._clean_region(region),
            "crop_name": self._clean_crop(crop_name),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "current": current,
            "forecast": forecast,
            "hourly_forecast": hourly,
            "rain_24h": rain_24h,
            "alerts": alerts,
            "activity_recommendations": recommendations,
            "ai_recommendation": {
                "provider": "rule_based_ai",
                "summary": "Du lieu thoi tiet duoc nap lai khi mo dashboard, sau do doc nhanh tu DB/cache.",
                "risk_explanation": "Risk score duoc tinh tu mua, UV, gio, do am va canh bao nong vu hien co.",
                "action_plan": [item.get("reason") for item in recommendations[:3] if item.get("reason")],
                "data_note": "Dashboard reset se cap nhat du lieu API truoc khi hien thi.",
            },
            "source_name": current.get("source_name") or "Weather DB",
            "source_url": current.get("source_url"),
            "is_realtime": current.get("is_realtime", False),
            "is_mock": current.get("is_mock", False),
            "cache_status": current.get("cache_status", "from_db"),
            "last_updated": current.get("last_updated"),
        }

    def get_regional_prices(
        self,
        db: Session,
        crop_name: str = "lua",
        regions: list[str] | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_crop = self._clean_crop(crop_name)
        if force_refresh:
            price_aggregator_service.refresh_prices(db, crop_name=selected_crop)

        crop = ensure_crop(db, selected_crop)
        rows = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop.CropID)
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .limit(80)
            .all()
        )
        wanted = regions or DEFAULT_REGIONS
        by_region: dict[str, MarketPrice] = {}
        for row in rows:
            if row.Region not in by_region:
                by_region[row.Region] = row

        result = []
        for region_name in wanted:
            row = by_region.get(region_name)
            if row is None:
                current = pricing_service.get_current_price(db, selected_crop, region_name)
                result.append(
                    {
                        "region": region_name,
                        "price": float(current["current_price"]),
                        "unit": "VND/kg",
                        "source_name": current.get("source_name") or "pricing_service",
                        "last_updated": current.get("last_updated"),
                        "is_mock": bool(current.get("is_mock")),
                        "cache_status": "mock" if current.get("is_mock") else "from_db",
                    }
                )
                continue
            result.append(
                {
                    "region": row.Region,
                    "price": float(row.PricePerKg),
                    "unit": "VND/kg",
                    "source_name": row.SourceName,
                    "source_url": row.SourceURL,
                    "last_updated": row.UpdatedAt,
                    "is_mock": False,
                    "cache_status": "from_db",
                }
            )
        return {"crop_name": selected_crop, "regions": result, "cache_status": "from_db"}

    def get_realtime_market(self, db: Session, crop_name: str = "lua", region: str = "Ha Noi", force_refresh: bool = False) -> dict:
        featured = self.get_featured_crop(db, crop_name=crop_name, region=region, force_refresh=force_refresh)
        return {
            "featured_crop": featured,
            "global_references": price_aggregator_service.latest_global_references(db, limit=6),
            "exchange_rate": price_aggregator_service.exchange_rate(live=False),
            "cache_status": featured.get("cache_status", "from_db"),
            "last_updated": featured.get("last_updated"),
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
        return market_news_service.get_latest(db, limit=limit, crop_name=crop_name, region=region)

    def get_data_health(self, db: Session, region: str = "Ha Noi", crop_name: str = "lua") -> dict:
        weather_count = db.query(WeatherData).filter(WeatherData.Region == self._clean_region(region)).count()
        news_count = db.query(MarketNews).count()
        price_count = db.query(MarketPrice).count()
        score = min(100, weather_count * 8 + min(news_count, 20) + min(price_count, 20))
        return {
            "score": score,
            "sources": [
                {"name": "Open-Meteo Forecast", "status": "OK" if weather_count else "EMPTY", "role": "Weather forecast"},
                {"name": "Market RSS", "status": "OK" if news_count else "EMPTY", "role": "Market news"},
                {"name": "Market Price APIs", "status": "OK" if price_count else "EMPTY", "role": "Price references"},
            ],
        }

    def refresh_dashboard(self, db: Session, source: str = "all", region: str = "Ha Noi", crop_name: str = "lua") -> dict:
        selected_region = self._clean_region(region)
        selected_crop = self._clean_crop(crop_name)
        result = {}
        if source in {"weather", "all"}:
            result["weather"] = self._refresh_weather(db, selected_region)
        if source in {"price", "prices", "all"}:
            result["prices"] = price_aggregator_service.refresh_prices(db, crop_name=selected_crop)
        if source in {"news", "all"}:
            result["news"] = market_news_service.refresh_news()
        result["refreshed_at"] = datetime.now()
        return result

    def get_ai_recommendation(self, db: Session, crop_name: str = "lua", region: str = "Ha Noi") -> dict:
        current_price = pricing_service.get_current_price(db, crop_name, region)
        weather = self.get_weather_overview(db, region)
        trend = current_price.get("price_trend", "stable")
        rainy_days = sum(1 for item in weather["forecast"] if float(item.get("rainfall") or 0) >= 5)

        if trend in {"increasing", "up"} and rainy_days <= 2:
            action = "hold"
            title = "Nen giu hang"
            confidence = 0.78
            description = "Xu huong gia dang cai thien va rui ro thoi tiet o muc chap nhan duoc."
        elif rainy_days >= 4:
            action = "sell_sooner"
            title = "Nen ban som hon"
            confidence = 0.72
            description = "Rui ro mua cao, nen giam thoi gian ton kho de han che hao hut."
        else:
            action = "sell_in_batches"
            title = "Ban theo nhieu dot"
            confidence = 0.70
            description = "Tin hieu thi truong trung tinh; chia nho san luong giup giam rui ro gia va thoi tiet."

        return {
            "crop_name": crop_name,
            "region": region,
            "action": action,
            "title": title,
            "description": description,
            "confidence": confidence,
            "expected_price": round(float(current_price["current_price"]) * 1.02, 2),
            "period": "7 ngay toi",
            "source": "rule_based_ai",
            "is_mock": bool(current_price.get("is_mock")) or weather["is_mock"],
            "last_updated": datetime.now(),
        }

    def _delete_dashboard_realtime_data(self, db: Session, region: str, crop_name: str) -> None:
        try:
            crop = ensure_crop(db, crop_name)
            today = date.today()
            db.query(MarketNews).delete(synchronize_session=False)
            db.query(MarketPrice).filter(
                MarketPrice.CropID == crop.CropID,
                or_(MarketPrice.SourceURL.is_not(None), MarketPrice.Region == "Global Futures"),
            ).delete(synchronize_session=False)
            db.query(WeatherData).filter(
                WeatherData.Region == region,
                WeatherData.RecordDate >= today,
                WeatherData.RecordDate <= today + timedelta(days=7),
            ).delete(synchronize_session=False)
            db.query(WeatherObservation).filter(WeatherObservation.Region == region).delete(synchronize_session=False)
            db.commit()
            redis_client.delete("market_news:latest")
        except Exception:
            db.rollback()

    def _refresh_weather_in_new_session(self, region: str) -> dict:
        db = SessionLocal()
        try:
            return self._refresh_weather(db, region)
        finally:
            db.close()

    def _refresh_prices_in_new_session(self, crop_name: str) -> dict:
        db = SessionLocal()
        try:
            return price_aggregator_service.refresh_prices(db, crop_name=crop_name)
        finally:
            db.close()

    def _refresh_weather(self, db: Session, region: str) -> dict:
        today = date.today()
        deleted_weather = (
            db.query(WeatherData)
            .filter(WeatherData.Region == region, WeatherData.RecordDate >= today, WeatherData.RecordDate <= today + timedelta(days=7))
            .delete(synchronize_session=False)
        )
        deleted_observations = db.query(WeatherObservation).filter(WeatherObservation.Region == region).delete(synchronize_session=False)
        current = self.weather_client.get_current(region)
        forecast = self.weather_client.get_forecast(region, days=7)

        observation = WeatherObservation(
            Region=region,
            ObservedAt=current.get("source_updated_at") or datetime.now(),
            Temperature=current.get("temperature"),
            Humidity=current.get("humidity"),
            Rainfall=current.get("rainfall"),
            WindSpeed=current.get("wind_speed"),
            UVIndex=current.get("uv_index"),
            Pressure=current.get("pressure"),
            WeatherCode=current.get("weather_code"),
            WeatherDesc=current.get("condition"),
            SourceName=current.get("source_name") or "Open-Meteo",
            SourceUpdatedAt=current.get("source_updated_at"),
        )
        db.add(observation)

        for item in forecast:
            record_date = date.fromisoformat(str(item["date"])[:10])
            db.add(
                WeatherData(
                    Region=region,
                    RecordDate=record_date,
                    TempMin=item.get("temp_min"),
                    TempMax=item.get("temp_max"),
                    Humidity=item.get("humidity"),
                    Rainfall=item.get("rainfall"),
                    WeatherDesc=item.get("condition"),
                    Latitude=current.get("latitude"),
                    Longitude=current.get("longitude"),
                    WindSpeed=item.get("wind_speed"),
                    UVIndex=item.get("uv_index"),
                    WeatherCode=item.get("weather_code"),
                    SourceName=item.get("source_name") or "Open-Meteo",
                    SourceUpdatedAt=item.get("last_updated") or datetime.now(),
                )
            )
        db.commit()
        return {
            "cache_status": "refreshed",
            "saved_daily_rows": len(forecast),
            "saved_observations": 1,
            "deleted": {"weather_data": deleted_weather, "observations": deleted_observations},
        }

    def _latest_market_price_for_crop(self, db: Session, crop_name: str, region: str | None = None) -> MarketPrice | None:
        try:
            crop = ensure_crop(db, crop_name)
            query = db.query(MarketPrice).filter(MarketPrice.CropID == crop.CropID)
            if region:
                query = query.filter(MarketPrice.Region == region)
            return query.order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt)).first()
        except SQLAlchemyError:
            db.rollback()
            return None

    def _current_weather_from_db(self, db: Session, region: str) -> dict | None:
        row = (
            db.query(WeatherData)
            .filter(WeatherData.Region == region, WeatherData.RecordDate <= date.today())
            .order_by(desc(WeatherData.RecordDate), desc(WeatherData.CreatedAt))
            .first()
        )
        if not row:
            return None
        temp = row.temperature
        updated = row.SourceUpdatedAt or row.CreatedAt or datetime.now()
        return {
            "region": row.Region,
            "temperature": float(temp) if temp is not None else None,
            "temp_min": float(row.TempMin) if row.TempMin is not None else None,
            "temp_max": float(row.TempMax) if row.TempMax is not None else None,
            "rainfall": float(row.Rainfall) if row.Rainfall is not None else 0,
            "humidity": float(row.Humidity) if row.Humidity is not None else None,
            "condition": row.WeatherDesc,
            "wind_speed": float(row.WindSpeed) if row.WindSpeed is not None else None,
            "uv_index": float(row.UVIndex) if row.UVIndex is not None else None,
            "pressure": float(row.Pressure) if row.Pressure is not None else None,
            "weather_code": row.WeatherCode,
            "source_name": row.SourceName or "Open-Meteo",
            "source_url": "https://open-meteo.com",
            "is_realtime": False,
            "is_mock": False,
            "last_updated": updated,
            "cache_status": "from_db",
        }

    def _weather_forecast_from_db(self, db: Session, region: str, days: int) -> list[dict]:
        rows = (
            db.query(WeatherData)
            .filter(
                WeatherData.Region == region,
                WeatherData.RecordDate >= date.today(),
                WeatherData.RecordDate <= date.today() + timedelta(days=days),
            )
            .order_by(WeatherData.RecordDate)
            .all()
        )
        result = []
        for row in rows[:days]:
            temp = row.temperature
            result.append(
                {
                    "date": row.RecordDate.isoformat(),
                    "temperature": float(temp) if temp is not None else None,
                    "temp_min": float(row.TempMin) if row.TempMin is not None else None,
                    "temp_max": float(row.TempMax) if row.TempMax is not None else None,
                    "humidity": float(row.Humidity) if row.Humidity is not None else None,
                    "rainfall": float(row.Rainfall) if row.Rainfall is not None else 0,
                    "condition": row.WeatherDesc,
                    "wind_speed": float(row.WindSpeed) if row.WindSpeed is not None else None,
                    "uv_index": float(row.UVIndex) if row.UVIndex is not None else None,
                    "source_name": row.SourceName or "Open-Meteo",
                    "is_mock": False,
                    "cache_status": "from_db",
                }
            )
        return result

    @staticmethod
    def _weather_risk_score(current: dict, forecast: list[dict], alerts: list[dict]) -> int:
        score = 0
        temp = float(current.get("temperature") or 0)
        humidity = float(current.get("humidity") or 0)
        wind = float(current.get("wind_speed") or 0)
        uv = float(current.get("uv_index") or 0)
        rain_total = sum(float(item.get("rainfall") or 0) for item in forecast[:3])
        if temp >= 35:
            score += 25
        if humidity >= 88:
            score += 15
        if wind >= 25:
            score += 15
        if uv >= 8:
            score += 10
        if rain_total >= 40:
            score += 25
        score += min(20, len(alerts) * 5)
        return min(100, int(score))

    @staticmethod
    def _clean_region(region: str | None) -> str:
        return (region or "Ha Noi").strip() or "Ha Noi"

    @staticmethod
    def _clean_crop(crop_name: str | None) -> str:
        return (crop_name or "lua").strip().lower() or "lua"

    @staticmethod
    def _display_crop(crop_name: str) -> str:
        labels = {"lua": "Lua", "gao": "Gao", "ca phe": "Ca phe", "ho tieu": "Ho tieu"}
        return labels.get(crop_name, crop_name.title())

    @staticmethod
    def _pct_change(current: float, previous: float | None) -> float:
        if not previous:
            return 0.0
        return round(((float(current) - float(previous)) / float(previous)) * 100, 1)

    @staticmethod
    def _format_pct(value: float) -> str:
        return f"{value:+.1f}%"


dashboard_service = DashboardService()
