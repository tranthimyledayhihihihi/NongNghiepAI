from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.apifarmer_client import apifarmer_client
from app.integrations.base_market_client import MarketPriceResult
from app.integrations.market_price_client import market_price_client
from app.integrations.twelvedata_client import twelvedata_client
from app.models.crop import Crop
from app.models.price import MarketPrice
from app.repositories.common import ensure_crop, normalize_text
from app.repositories.ingestion_repository import finish_ingestion_log, start_ingestion_log
from app.repositories.price_repository import bulk_upsert_market_prices


class PriceAggregatorService:
    """Single backend gateway for market price integrations."""

    def __init__(self) -> None:
        self.cache_ttl = timedelta(minutes=max(int(settings.PRICE_CACHE_TTL_MINUTES or 60), 1))

    def refresh_price_for_crop_region(self, db: Session, crop_name: str, region: str | None = None) -> dict:
        records: list[dict] = []
        api_results: list[MarketPriceResult] = []
        errors: list[str] = []
        selected_region = self._clean_region(region)

        if settings.ENABLE_REALTIME_PRICE:
            try:
                local_price = apifarmer_client.get_current_price(crop_name, selected_region)
                if local_price:
                    api_results.append(local_price)
            except Exception as exc:
                errors.append(f"APIFarmer: {exc}")

            try:
                global_price = twelvedata_client.get_current_price(crop_name, "Global Futures")
                if global_price:
                    api_results.append(global_price)
            except Exception as exc:
                errors.append(f"Twelve Data: {exc}")

        records.extend(self._result_to_record(result) for result in api_results)
        saved_result = bulk_upsert_market_prices(db, records) if records else {
            "records_saved": 0,
            "records_updated": 0,
            "errors": [],
        }
        return {
            "status": "success" if records else "empty",
            "records_fetched": len(records),
            "records_saved": saved_result.get("records_saved", 0),
            "records_updated": saved_result.get("records_updated", 0),
            "errors": errors + list(saved_result.get("errors") or []),
            "sources": [result.source_name for result in api_results],
        }

    def get_best_current_price(
        self,
        db: Session,
        crop_name: str,
        region: str | None = None,
        force_refresh: bool = False,
    ) -> dict:
        selected_crop = self._clean_crop(crop_name)
        selected_region = self._clean_region(region)
        cache_status = "from_db"
        refreshed = None

        local_row = self._latest_db_price(db, selected_crop, selected_region, prefer_local=True)
        cache_fresh = local_row is not None and self._is_fresh(local_row)

        if force_refresh or not cache_fresh:
            refreshed = self.refresh_price_for_crop_region(db, selected_crop, selected_region)
            db.expire_all()
            latest_after_refresh = self._latest_db_price(db, selected_crop, selected_region, prefer_local=True)
            if latest_after_refresh and (local_row is None or latest_after_refresh.UpdatedAt >= local_row.UpdatedAt):
                local_row = latest_after_refresh
                cache_status = (
                    "refreshed"
                    if refreshed.get("records_fetched")
                    else self.cache_status(local_row.FetchedAt or local_row.UpdatedAt)
                )
            elif local_row:
                cache_status = "stale"
            else:
                cache_status = "miss"
        elif local_row:
            cache_status = "fresh"

        global_reference = self.get_global_reference_price(db, selected_crop)

        if local_row:
            return self._row_to_current_response(
                db,
                local_row,
                crop_name=crop_name,
                region=selected_region,
                source_type="realtime" if cache_status == "refreshed" and bool(local_row.IsRealtime) else "database",
                cache_status=cache_status,
                global_reference=global_reference,
                refresh_result=refreshed,
            )

        if self._realtime_only():
            return self._no_realtime_price_response(
                crop_name=crop_name,
                region=selected_region,
                refresh_result=refreshed,
            )

        return self._mock_current_response(
            db,
            crop_name=crop_name,
            region=selected_region,
            global_reference=global_reference,
            refresh_result=refreshed,
        )

    def get_global_reference_price(self, db: Session, crop_name: str) -> dict | None:
        selected_crop = self._clean_crop(crop_name)
        row = self._latest_db_price(db, selected_crop, "Global Futures", prefer_global=True)
        if row and self._is_fresh(row):
            return self._row_to_reference(row)

        if settings.ENABLE_REALTIME_PRICE:
            result = twelvedata_client.get_current_price(selected_crop, "Global Futures")
            if result:
                bulk_upsert_market_prices(db, [self._result_to_record(result)])
                db.expire_all()
                row = self._latest_db_price(db, selected_crop, "Global Futures", prefer_global=True)
                if row:
                    return self._row_to_reference(row)

        return self._row_to_reference(row) if row else None

    def get_price_sources_status(self, db: Session) -> dict:
        price_count = db.query(MarketPrice).count()
        return {
            "sources": [
                {
                    "source_name": "APIFarmer",
                    "source_type": "local_agriculture",
                    "enabled": bool(settings.APIFARMER_ENABLED),
                    "configured": bool(settings.APIFARMER_API_BASE_URL and settings.APIFARMER_API_KEY),
                    "role": "Nguồn chính cho giá nông sản Việt Nam",
                },
                {
                    "source_name": "Twelve Data",
                    "source_type": "global_commodity",
                    "enabled": bool(settings.TWELVEDATA_ENABLED),
                    "configured": bool(settings.TWELVEDATA_API_KEY),
                    "role": "Nguồn tham chiếu hàng hóa quốc tế",
                },
                {
                    "source_name": "MarketPrices DB",
                    "source_type": "database",
                    "enabled": True,
                    "configured": True,
                    "role": "Cache và fallback nội bộ",
                    "records": price_count,
                },
            ],
            "cache_ttl_minutes": int(settings.PRICE_CACHE_TTL_MINUTES or 60),
            "checked_at": datetime.now(),
        }

    def refresh_prices(
        self,
        db: Session,
        *,
        crop_name: str | None = None,
        source_name: str | None = None,
    ) -> dict:
        selected_crop = crop_name or "lua"
        log_source = source_name or "price_aggregator"
        log = start_ingestion_log(db, "refresh_market_prices", log_source)
        try:
            result = self.refresh_price_for_crop_region(db, selected_crop, None)
            if result.get("records_fetched", 0) == 0 and source_name:
                legacy_records = market_price_client.fetch_all(source_name=source_name, crop_filter=selected_crop)
                legacy_result = bulk_upsert_market_prices(db, legacy_records)
                result = {
                    "status": "success" if legacy_records else "empty",
                    "records_fetched": len(legacy_records),
                    **legacy_result,
                }
            finish_ingestion_log(
                db,
                log,
                status="success",
                records_fetched=int(result.get("records_fetched") or 0),
                records_saved=int(result.get("records_saved") or 0) + int(result.get("records_updated") or 0),
                error_message="; ".join(result.get("errors") or []) or None,
            )
            return result
        except Exception as exc:
            finish_ingestion_log(db, log, status="failed", error_message=str(exc))
            return {"status": "failed", "error": str(exc), "records_fetched": 0, "records_saved": 0}

    def latest_global_references(self, db: Session, limit: int = 8) -> list[dict]:
        rows = (
            db.query(MarketPrice)
            .filter(MarketPrice.SourceType == "global_commodity")
            .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
            .limit(limit * 3)
            .all()
        )
        crop_map = {item.CropID: item.CropName for item in db.query(Crop).all()}
        result = []
        seen = set()
        for row in rows:
            if row.CropID in seen:
                continue
            seen.add(row.CropID)
            item = self._row_to_reference(row)
            item["crop_id"] = row.CropID
            item["crop_name"] = crop_map.get(row.CropID, item.get("crop_name"))
            item["last_updated"] = item.get("fetched_at") or row.UpdatedAt
            item["cache_status"] = self.cache_status(row.FetchedAt or row.UpdatedAt)
            result.append(item)
            if len(result) >= limit:
                break
        return result

    def cache_status(self, updated_at: datetime | None) -> str:
        if not updated_at:
            return "unknown"
        age = datetime.now() - updated_at
        if age <= self.cache_ttl:
            return "fresh"
        return "stale"

    def is_stale(self, updated_at: datetime | None) -> bool:
        return self.cache_status(updated_at) in {"stale", "unknown"}

    def exchange_rate(self, live: bool = False) -> dict:
        rate = market_price_client._fetch_usd_vnd_rate() if live else float(settings.USD_VND_FALLBACK_RATE)
        return {
            "pair": "USD/VND",
            "rate": rate,
            "source_name": "open.er-api" if live else "USD/VND fallback config",
            "source_url": "https://open.er-api.com",
            "cache_status": "live" if live else "cached",
            "is_realtime": live,
            "is_mock": False,
            "last_updated": datetime.now(),
        }

    def _latest_db_price(
        self,
        db: Session,
        crop_name: str,
        region: str | None,
        *,
        prefer_local: bool = False,
        prefer_global: bool = False,
    ) -> MarketPrice | None:
        try:
            crop = ensure_crop(db, crop_name)
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(100)
                .all()
            )
            target_region = normalize_text(region)
            for row in rows:
                if self._realtime_only() and bool(row.IsMock):
                    continue
                source_type = (row.SourceType or "").lower()
                if prefer_local and source_type == "global_commodity":
                    continue
                if prefer_global and source_type != "global_commodity":
                    continue
                if not target_region or normalize_text(row.Region) == target_region:
                    return row
            return None
        except Exception:
            db.rollback()
            return None

    def _is_fresh(self, row: MarketPrice) -> bool:
        return self.cache_status(row.FetchedAt or row.UpdatedAt) == "fresh"

    @staticmethod
    def _realtime_only() -> bool:
        return bool(settings.USE_REALTIME_ONLY) and not bool(settings.ALLOW_MOCK_DATA or settings.ALLOW_SAMPLE_DATA)

    def _row_to_current_response(
        self,
        db: Session,
        row: MarketPrice,
        *,
        crop_name: str,
        region: str,
        source_type: str,
        cache_status: str,
        global_reference: dict | None,
        refresh_result: dict | None,
    ) -> dict:
        current_price = float(row.PricePerKg or 0)
        previous = self._previous_price(db, crop_name, region, row.PriceID)
        price_change = round(current_price - previous, 2) if previous else 0.0
        price_change_percent = round(price_change / previous * 100, 2) if previous else 0.0
        confidence = float(row.ConfidenceScore or (0.82 if row.IsRealtime else 0.68))
        observed_at = row.ObservedAt or datetime.combine(row.PriceDate or date.today(), datetime.min.time())
        fetched_at = row.FetchedAt or row.UpdatedAt or datetime.now()
        local_price = {
            "price": current_price,
            "unit": self._display_unit(row),
            "currency": "VND",
            "source_name": row.SourceName or "MarketPrices DB",
            "source_type": row.SourceType or "database",
            "source_url": row.SourceURL,
        }
        return {
            "crop_name": crop_name.strip(),
            "crop": crop_name.strip(),
            "region": region,
            "current_price": round(current_price, 2),
            "market_price": round(current_price, 2),
            "price": round(current_price, 2),
            "unit": self._display_unit(row),
            "currency": "VND",
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "trend": self._trend_from_change(price_change_percent),
            "local_price": local_price,
            "global_reference": global_reference,
            "source": source_type,
            "source_type": source_type,
            "source_name": row.SourceName or "MarketPrices DB",
            "source_url": row.SourceURL,
            "fetched_at": fetched_at,
            "observed_at": observed_at,
            "last_updated": fetched_at,
            "price_date": row.PriceDate,
            "confidence_score": confidence,
            "confidence": confidence,
            "is_mock": bool(row.IsMock),
            "is_realtime": bool(row.IsRealtime and source_type == "realtime"),
            "cache_status": cache_status,
            "refresh_result": refresh_result,
        }

    def _mock_current_response(
        self,
        db: Session,
        *,
        crop_name: str,
        region: str,
        global_reference: dict | None,
        refresh_result: dict | None,
    ) -> dict:
        now = datetime.now()
        crop = ensure_crop(db, crop_name)
        if crop.TypicalPriceMin and crop.TypicalPriceMax:
            price = round((float(crop.TypicalPriceMin) + float(crop.TypicalPriceMax)) / 2, 2)
        else:
            base_prices = {
                "ca phe": 110000,
                "lua": 8500,
                "gao": 12000,
                "ngo": 6500,
                "sau rieng": 75000,
                "ho tieu": 75000,
                "dau nanh": 18000,
            }
            price = float(base_prices.get(normalize_text(crop_name), 20000))
        return {
            "crop_name": crop_name.strip(),
            "crop": crop_name.strip(),
            "region": region,
            "current_price": price,
            "market_price": price,
            "price": price,
            "unit": "VNĐ/kg",
            "currency": "VND",
            "price_change": 0.0,
            "price_change_percent": 0.0,
            "trend": "stable",
            "local_price": None,
            "global_reference": global_reference,
            "source": "mock",
            "source_type": "mock",
            "source_name": "Dữ liệu mô phỏng",
            "source_url": None,
            "fetched_at": now,
            "observed_at": now,
            "last_updated": now,
            "confidence_score": 0.35,
            "confidence": 0.35,
            "is_mock": True,
            "is_realtime": False,
            "cache_status": "mock",
            "refresh_result": refresh_result,
            "message": "Dữ liệu này là mô phỏng, chưa phải giá thị trường thực tế.",
        }

    @staticmethod
    def _no_realtime_price_response(
        *,
        crop_name: str,
        region: str,
        refresh_result: dict | None,
    ) -> dict:
        return {
            "_api_error": True,
            "error_code": "REALTIME_API_FAILED",
            "error_message": "Không thể tải giá realtime. Vui lòng thử lại sau.",
            "crop_name": crop_name.strip(),
            "region": region,
            "source": "realtime_api",
            "source_type": "realtime_api",
            "source_name": "Realtime market price API",
            "is_mock": False,
            "is_realtime": False,
            "cache_status": "miss",
            "refresh_result": refresh_result,
        }

    def _row_to_reference(self, row: MarketPrice | None) -> dict | None:
        if row is None:
            return None
        return {
            "price": float(row.PricePerKg or 0),
            "unit": "USD/ton" if (row.SourceType or "") == "global_commodity" else self._display_unit(row),
            "currency": "USD" if (row.SourceType or "") == "global_commodity" else "VND",
            "source_name": row.SourceName or "Twelve Data",
            "source_type": row.SourceType or "global_commodity",
            "source_url": row.SourceURL,
            "observed_at": row.ObservedAt,
            "fetched_at": row.FetchedAt or row.UpdatedAt,
            "confidence_score": float(row.ConfidenceScore or 0.7),
            "is_realtime": bool(row.IsRealtime),
            "is_mock": bool(row.IsMock),
        }

    def _result_to_record(self, result: MarketPriceResult) -> dict:
        market_type = "global_futures_reference" if result.source_type == "global_commodity" else "Ban le"
        return {
            "crop_name": result.crop_name,
            "region": result.region or ("Global Futures" if result.source_type == "global_commodity" else "Vietnam"),
            "price": result.price,
            "quality_grade": "grade_1",
            "source_name": result.source_name,
            "source_url": result.source_url,
            "source_type": result.source_type,
            "price_date": result.observed_at.date(),
            "market_type": market_type,
            "observed_at": result.observed_at,
            "fetched_at": result.fetched_at,
            "collected_at": result.fetched_at,
            "confidence_score": result.confidence_score,
            "is_realtime": result.is_realtime,
            "is_mock": False,
            "metadata": result.metadata,
        }

    def _previous_price(self, db: Session, crop_name: str, region: str, exclude_price_id: int) -> float | None:
        try:
            crop = ensure_crop(db, crop_name)
            rows = (
                db.query(MarketPrice)
                .filter(MarketPrice.CropID == crop.CropID, MarketPrice.PriceID != exclude_price_id)
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .limit(30)
                .all()
            )
            target_region = normalize_text(region)
            for row in rows:
                if normalize_text(row.Region) == target_region and (row.SourceType or "") != "global_commodity":
                    return float(row.PricePerKg)
            return None
        except Exception:
            db.rollback()
            return None

    @staticmethod
    def _clean_crop(crop_name: str | None) -> str:
        return " ".join((crop_name or "lua").strip().split()) or "lua"

    @staticmethod
    def _clean_region(region: str | None) -> str:
        return " ".join((region or "Vietnam").strip().split()) or "Vietnam"

    @staticmethod
    def _display_unit(row: MarketPrice) -> str:
        if (row.SourceType or "") == "global_commodity":
            return "USD/ton"
        return "VNĐ/kg"

    @staticmethod
    def _trend_from_change(change_percent: float) -> str:
        if change_percent > 1:
            return "up"
        if change_percent < -1:
            return "down"
        return "stable"


price_aggregator_service = PriceAggregatorService()
