import json
import re
from unicodedata import category, normalize

from sqlalchemy import distinct, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.price import MarketPrice
from app.models.weather import WeatherLocation


DEFAULT_LOCATIONS = [
    {"region_key": "ha_noi", "display_name": "Hà Nội", "province_code": "HN", "latitude": 21.0285, "longitude": 105.8542},
    {"region_key": "tp_hcm", "display_name": "TP.HCM", "province_code": "HCM", "latitude": 10.8231, "longitude": 106.6297},
    {"region_key": "da_nang", "display_name": "Đà Nẵng", "province_code": "DN", "latitude": 16.0544, "longitude": 108.2022},
    {"region_key": "can_tho", "display_name": "Cần Thơ", "province_code": "CT", "latitude": 10.0452, "longitude": 105.7469},
    {"region_key": "lam_dong", "display_name": "Lâm Đồng", "province_code": "LD", "latitude": 11.9404, "longitude": 108.4583},
    {"region_key": "hai_phong", "display_name": "Hải Phòng", "province_code": "HP", "latitude": 20.8449, "longitude": 106.6881},
]

BAD_QUESTION_MARK = chr(63)

DISPLAY_ALIASES = {
    "Ha Noi": "Hà Nội",
    "Hanoi": "Hà Nội",
    f"Hà N{BAD_QUESTION_MARK}i": "Hà Nội",
    f"Hŕ N{BAD_QUESTION_MARK}i": "Hà Nội",
    f"H{BAD_QUESTION_MARK} N{BAD_QUESTION_MARK}i": "Hà Nội",
    "TP.HCM": "TP.HCM",
    "TP HCM": "TP.HCM",
    "Ho Chi Minh": "TP.HCM",
    "Da Nang": "Đà Nẵng",
    f"Đà N{BAD_QUESTION_MARK}ng": "Đà Nẵng",
    f"{BAD_QUESTION_MARK}{BAD_QUESTION_MARK} N{BAD_QUESTION_MARK}ng": "Đà Nẵng",
    "Can Tho": "Cần Thơ",
    f"C{BAD_QUESTION_MARK}n Thơ": "Cần Thơ",
    f"C{BAD_QUESTION_MARK}n Th{BAD_QUESTION_MARK}": "Cần Thơ",
    "Lam Dong": "Lâm Đồng",
    f"Lâm Đ{BAD_QUESTION_MARK}ng": "Lâm Đồng",
    f"L{BAD_QUESTION_MARK}m {BAD_QUESTION_MARK}{BAD_QUESTION_MARK}ng": "Lâm Đồng",
    "Da Lat": "Đà Lạt",
    "Hai Phong": "Hải Phòng",
    f"H{BAD_QUESTION_MARK}i Ph{BAD_QUESTION_MARK}ng": "Hải Phòng",
}


class LocationService:
    def list_locations(self, db: Session) -> list[dict]:
        self.ensure_default_locations(db)
        rows = self._load_weather_locations(db)
        seen = set()
        result = []

        for item in DEFAULT_LOCATIONS:
            row = next((location for location in rows if self.region_key(location.Region) == item["region_key"]), None)
            result.append(self._to_dict(row, fallback=item, source="db" if row else "seed"))
            seen.add(item["region_key"])

        for row in rows:
            key = self.region_key(row.Region)
            if key in seen:
                continue
            result.append(self._to_dict(row, source="db"))
            seen.add(key)

        for region in self._market_regions(db):
            key = self.region_key(region)
            if key in seen:
                continue
            result.append(
                {
                    "region_key": key,
                    "display_name": self.display_name(region),
                    "province_code": None,
                    "latitude": None,
                    "longitude": None,
                    "source": "market_prices",
                }
            )
            seen.add(key)

        return result

    def resolve_region(self, db: Session, value: str | None) -> str:
        if not value:
            return DEFAULT_LOCATIONS[0]["display_name"]
        key = self.region_key(value)
        for item in self.list_locations(db):
            if item["region_key"] == key or self.region_key(item["display_name"]) == key:
                return item["display_name"]
        return self.display_name(value)

    def ensure_default_locations(self, db: Session) -> None:
        try:
            existing_keys = {
                self.region_key(row.Region)
                for row in db.query(WeatherLocation.Region).all()
            }
            for item in self._configured_locations():
                if item["region_key"] in existing_keys:
                    continue
                db.add(
                    WeatherLocation(
                        Region=item["display_name"],
                        Province=item["display_name"],
                        Latitude=item.get("latitude"),
                        Longitude=item.get("longitude"),
                        IsDefault=True,
                    )
                )
            db.commit()
        except SQLAlchemyError:
            db.rollback()

    def _configured_locations(self) -> list[dict]:
        configured = {item["region_key"]: item.copy() for item in DEFAULT_LOCATIONS}
        try:
            raw = json.loads(settings.REGION_COORDINATES_JSON or "{}")
        except json.JSONDecodeError:
            raw = {}
        for name, coords in raw.items():
            key = self.region_key(name)
            configured[key] = {
                "region_key": key,
                "display_name": self.display_name(name),
                "province_code": configured.get(key, {}).get("province_code"),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
            }
        return list(configured.values())

    @staticmethod
    def _load_weather_locations(db: Session) -> list[WeatherLocation]:
        try:
            return db.query(WeatherLocation).order_by(WeatherLocation.IsDefault.desc(), WeatherLocation.Region).all()
        except SQLAlchemyError:
            db.rollback()
            return []

    @staticmethod
    def _market_regions(db: Session) -> list[str]:
        try:
            rows = (
                db.query(distinct(MarketPrice.Region))
                .filter(MarketPrice.Region.isnot(None))
                .order_by(func.lower(MarketPrice.Region))
                .all()
            )
            return [row[0] for row in rows if row[0]]
        except SQLAlchemyError:
            db.rollback()
            return []

    def _to_dict(self, row: WeatherLocation | None = None, *, fallback: dict | None = None, source: str = "db") -> dict:
        fallback = fallback or {}
        display = self.display_name(row.Region if row else fallback.get("display_name"))
        return {
            "region_key": fallback.get("region_key") or self.region_key(display),
            "display_name": display,
            "province_code": fallback.get("province_code"),
            "latitude": row.Latitude if row and row.Latitude is not None else fallback.get("latitude"),
            "longitude": row.Longitude if row and row.Longitude is not None else fallback.get("longitude"),
            "source": source,
        }

    @staticmethod
    def display_name(value: str | None) -> str:
        if not value:
            return ""
        stripped = value.strip()
        return DISPLAY_ALIASES.get(stripped, stripped)

    @staticmethod
    def region_key(value: str | None) -> str:
        if not value:
            return ""
        canonical = LocationService.display_name(value)
        normalized = normalize("NFD", canonical.strip().lower())
        ascii_text = "".join(char for char in normalized if category(char) != "Mn")
        ascii_text = ascii_text.replace("đ", "d")
        return re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")


location_service = LocationService()
