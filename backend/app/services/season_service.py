from datetime import date, datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.season import Season
from app.schemas.season_schema import SeasonCreate, SeasonUpdate


ACTIVE_SEASON_STATUSES = {"active", "harvesting"}
IN_PROGRESS_STATUSES = {"planned", "active", "harvesting"}


class SeasonService:
    def get_seasons(
        self,
        db: Session,
        user_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        query = self._base_query(db, user_id)
        if status and status != "all":
            if status == "upcoming":
                today = date.today()
                query = query.filter(
                    Season.Status.in_(list(IN_PROGRESS_STATUSES)),
                    Season.ExpectedHarvestDate >= today,
                    Season.ExpectedHarvestDate <= today + timedelta(days=14),
                )
            elif status == "risk":
                query = query.filter(Season.HealthStatus == "risk")
            elif status == "active":
                query = query.filter(Season.Status.in_(list(ACTIVE_SEASON_STATUSES)))
            else:
                query = query.filter(Season.Status == status)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Season.CropName.ilike(pattern),
                    Season.Region.ilike(pattern),
                    Season.FarmName.ilike(pattern),
                )
            )
        rows = query.order_by(Season.CreatedAt.desc(), Season.SeasonID.desc()).all()
        return [self._serialize(row) for row in rows]

    def get_active_seasons(self, db: Session, user_id: int | None = None) -> list[dict]:
        rows = (
            self._base_query(db, user_id)
            .filter(Season.Status.in_(list(ACTIVE_SEASON_STATUSES)))
            .order_by(Season.ExpectedHarvestDate.asc(), Season.CreatedAt.desc())
            .all()
        )
        return [self._serialize(row) for row in rows]

    def get_season_by_id(self, db: Session, season_id: int, user_id: int | None = None) -> Season | None:
        return self._base_query(db, user_id).filter(Season.SeasonID == season_id).first()

    def create_season(self, db: Session, request: SeasonCreate, user_id: int | None = None) -> dict:
        payload = request.model_dump()
        payload = self._clean_payload(payload)
        self._validate_required_text(payload)
        if not payload.get("expected_harvest_date"):
            estimate = self.estimate_harvest_date(
                db,
                crop_name=payload["crop_name"],
                region=payload["region"],
                start_date=payload["start_date"],
            )
            payload["expected_harvest_date"] = estimate["expected_harvest_date"]
        self._validate_dates(
            payload["start_date"],
            payload["expected_harvest_date"],
            payload.get("actual_harvest_date"),
        )
        if payload.get("status") == "completed" and payload.get("actual_harvest_date") is None:
            payload["actual_harvest_date"] = date.today()
        season = Season(
            UserID=user_id,
            CropName=payload["crop_name"],
            Region=payload["region"],
            FarmName=payload.get("farm_name"),
            Area=payload.get("area"),
            AreaUnit=payload.get("area_unit") or "ha",
            StartDate=payload["start_date"],
            ExpectedHarvestDate=payload["expected_harvest_date"],
            ActualHarvestDate=payload.get("actual_harvest_date"),
            Status=payload.get("status") or "active",
            HealthStatus=payload.get("health_status") or "good",
            Note=payload.get("note"),
        )
        try:
            db.add(season)
            db.commit()
            db.refresh(season)
            return self._serialize(season)
        except SQLAlchemyError:
            db.rollback()
            raise

    def update_season(
        self,
        db: Session,
        season_id: int,
        request: SeasonUpdate,
        user_id: int | None = None,
    ) -> dict | None:
        season = self.get_season_by_id(db, season_id, user_id)
        if season is None:
            return None

        payload = self._clean_payload(request.model_dump(exclude_unset=True))
        self._validate_required_text(payload, partial=True)
        if "start_date" in payload and "expected_harvest_date" not in payload:
            estimate = self.estimate_harvest_date(
                db,
                crop_name=payload.get("crop_name") or season.CropName,
                region=payload.get("region") or season.Region,
                start_date=payload["start_date"],
            )
            payload["expected_harvest_date"] = estimate["expected_harvest_date"]
        start_date = payload.get("start_date", season.StartDate)
        expected_harvest_date = payload.get("expected_harvest_date", season.ExpectedHarvestDate)
        actual_harvest_date = payload.get("actual_harvest_date", season.ActualHarvestDate)
        self._validate_dates(start_date, expected_harvest_date, actual_harvest_date)

        field_map = {
            "crop_name": "CropName",
            "region": "Region",
            "farm_name": "FarmName",
            "area": "Area",
            "area_unit": "AreaUnit",
            "start_date": "StartDate",
            "expected_harvest_date": "ExpectedHarvestDate",
            "actual_harvest_date": "ActualHarvestDate",
            "status": "Status",
            "health_status": "HealthStatus",
            "note": "Note",
        }
        for key, value in payload.items():
            setattr(season, field_map[key], value)
        if season.Status == "completed" and season.ActualHarvestDate is None:
            season.ActualHarvestDate = date.today()
        season.UpdatedAt = datetime.utcnow()

        try:
            db.add(season)
            db.commit()
            db.refresh(season)
            return self._serialize(season)
        except SQLAlchemyError:
            db.rollback()
            raise

    def delete_season(self, db: Session, season_id: int, user_id: int | None = None) -> bool:
        season = self.get_season_by_id(db, season_id, user_id)
        if season is None:
            return False
        try:
            db.delete(season)
            db.commit()
            return True
        except SQLAlchemyError:
            db.rollback()
            raise

    def complete_season(self, db: Session, season_id: int, user_id: int | None = None) -> dict | None:
        season = self.get_season_by_id(db, season_id, user_id)
        if season is None:
            return None
        season.Status = "completed"
        if season.ActualHarvestDate is None:
            season.ActualHarvestDate = date.today()
        season.UpdatedAt = datetime.utcnow()
        try:
            db.add(season)
            db.commit()
            db.refresh(season)
            return self._serialize(season)
        except SQLAlchemyError:
            db.rollback()
            raise

    def count_active_seasons(self, db: Session, user_id: int | None = None) -> int:
        return (
            self._base_query(db, user_id)
            .filter(Season.Status.in_(list(ACTIVE_SEASON_STATUSES)))
            .count()
        )

    def serialize_season(self, season: Season) -> dict:
        return self._serialize(season)

    def estimate_harvest_date(self, db: Session, crop_name: str, region: str, start_date: date) -> dict:
        clean_crop = crop_name.strip()
        clean_region = region.strip()
        if not clean_crop:
            raise ValueError("crop_name is required")
        if not clean_region:
            raise ValueError("region is required")

        from app.services.harvest_service import harvest_service

        growth_days = harvest_service._resolve_growth_days(db, clean_crop)
        preliminary_date = start_date + timedelta(days=growth_days)
        weather_data = self._weather_for_estimated_harvest(db, clean_region, preliminary_date)
        predictor = harvest_service._get_predictor()
        warning = None
        recommendation = None
        confidence = 0.78
        source_name = weather_data.get("source_name") if weather_data else None

        if predictor:
            try:
                result = predictor.predict(
                    crop_name=clean_crop,
                    planting_date=datetime.combine(start_date, datetime.min.time()),
                    region=clean_region,
                    growth_duration_days=growth_days,
                    weather_data=weather_data,
                )
                raw_date = result.get("expected_harvest_date")
                expected_harvest_date = date.fromisoformat(str(raw_date)[:10])
                growth_days = int(result.get("growth_days") or (expected_harvest_date - start_date).days)
                warning = result.get("warning")
                recommendation = result.get("recommendation")
                confidence = float(result.get("confidence") or confidence)
            except Exception:
                expected_harvest_date = preliminary_date
                warning = harvest_service._warning_for(expected_harvest_date)
        else:
            expected_harvest_date = preliminary_date
            warning = harvest_service._warning_for(expected_harvest_date)

        weather_risk = harvest_service._weather_risk_label(db, clean_region)
        if not recommendation:
            recommendation = (
                f"Dự kiến thu hoạch {clean_crop} tại {clean_region} vào "
                f"{expected_harvest_date.strftime('%d/%m/%Y')}. Theo dõi thời tiết trước thu hoạch."
            )
        return {
            "crop_name": clean_crop,
            "region": clean_region,
            "start_date": start_date,
            "expected_harvest_date": expected_harvest_date,
            "growth_days": max(growth_days, 1),
            "confidence": confidence,
            "warning": warning,
            "recommendation": recommendation,
            "weather_risk": weather_risk,
            "weather_source_name": source_name or "Weather service",
        }

    def get_summary(self, db: Session, user_id: int | None = None) -> dict:
        today = date.today()
        query = self._base_query(db, user_id)
        total = query.count()
        active = query.filter(Season.Status.in_(list(ACTIVE_SEASON_STATUSES))).count()
        completed = query.filter(Season.Status == "completed").count()
        risk = query.filter(Season.HealthStatus == "risk").count()
        upcoming = query.filter(
            Season.Status.in_(list(IN_PROGRESS_STATUSES)),
            Season.ExpectedHarvestDate >= today,
            Season.ExpectedHarvestDate <= today + timedelta(days=14),
        ).count()
        return {
            "total_seasons": total,
            "active_seasons": active,
            "completed_seasons": completed,
            "risk_seasons": risk,
            "upcoming_harvest_count": upcoming,
        }

    @staticmethod
    def _base_query(db: Session, user_id: int | None = None):
        query = db.query(Season)
        if user_id is not None:
            query = query.filter(Season.UserID == user_id)
        return query

    @staticmethod
    def _clean_payload(payload: dict) -> dict:
        cleaned = dict(payload)
        for key in ("crop_name", "region", "farm_name", "area_unit", "status", "health_status", "note"):
            value = cleaned.get(key)
            if isinstance(value, str):
                cleaned[key] = value.strip()
        for key in ("farm_name", "note"):
            if cleaned.get(key) == "":
                cleaned[key] = None
        return cleaned

    @staticmethod
    def _validate_required_text(payload: dict, partial: bool = False) -> None:
        if (not partial or "crop_name" in payload) and not payload.get("crop_name"):
            raise ValueError("crop_name is required")
        if (not partial or "region" in payload) and not payload.get("region"):
            raise ValueError("region is required")

    @staticmethod
    def _validate_dates(start_date: date, expected_harvest_date: date, actual_harvest_date: date | None = None) -> None:
        if expected_harvest_date <= start_date:
            raise ValueError("expected_harvest_date must be after start_date")
        if actual_harvest_date and actual_harvest_date < start_date:
            raise ValueError("actual_harvest_date must be on or after start_date")

    @staticmethod
    def _weather_for_estimated_harvest(db: Session, region: str, expected_harvest_date: date) -> dict:
        try:
            from app.services.weather_service import weather_service

            days_ahead = (expected_harvest_date - date.today()).days
            if 0 <= days_ahead <= 7:
                forecast = weather_service.get_weather_forecast(db, region, 7)
                for item in forecast:
                    item_date = str(item.get("date") or "")[:10]
                    if item_date == expected_harvest_date.isoformat():
                        return {
                            "temperature": item.get("temperature") or item.get("temp_max"),
                            "temp_max": item.get("temp_max"),
                            "rainfall": item.get("rainfall"),
                            "humidity": item.get("humidity"),
                            "source_name": item.get("source_name") or "Weather forecast",
                            "updated_at": item.get("last_updated") or item.get("updated_at"),
                        }

            from app.services.harvest_service import harvest_service
            return harvest_service._get_latest_weather(db, region) or {}
        except Exception:
            return {}

    @staticmethod
    def _serialize(season: Season) -> dict:
        today = date.today()
        days_until_harvest = None
        if season.ExpectedHarvestDate:
            days_until_harvest = (season.ExpectedHarvestDate - today).days
        return {
            "id": season.SeasonID,
            "crop_name": season.CropName,
            "region": season.Region,
            "farm_name": season.FarmName,
            "area": float(season.Area) if season.Area is not None else None,
            "area_unit": season.AreaUnit,
            "start_date": season.StartDate,
            "expected_harvest_date": season.ExpectedHarvestDate,
            "actual_harvest_date": season.ActualHarvestDate,
            "status": season.Status,
            "health_status": season.HealthStatus,
            "note": season.Note,
            "days_until_harvest": days_until_harvest,
            "is_upcoming_harvest": (
                days_until_harvest is not None
                and 0 <= days_until_harvest <= 14
                and season.Status in IN_PROGRESS_STATUSES
            ),
            "created_at": season.CreatedAt,
            "updated_at": season.UpdatedAt,
        }


season_service = SeasonService()
