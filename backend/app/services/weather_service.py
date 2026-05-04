"""P2-13: Weather Service"""
import os, random
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.weather import WeatherData

MOCK_WEATHER = {
    "default":   {"temp_min": 22, "temp_max": 32, "humidity": 75, "rainfall": 5, "sunshine_hours": 7, "condition": "Nang nhe"},
    "Ha Noi":    {"temp_min": 24, "temp_max": 34, "humidity": 80, "rainfall": 3, "sunshine_hours": 6, "condition": "Nhieu may"},
    "TP.HCM":    {"temp_min": 25, "temp_max": 36, "humidity": 70, "rainfall": 0, "sunshine_hours": 9, "condition": "Nang"},
    "Da Nang":   {"temp_min": 23, "temp_max": 33, "humidity": 78, "rainfall": 8, "sunshine_hours": 7, "condition": "Co mua"},
    "Can Tho":   {"temp_min": 24, "temp_max": 35, "humidity": 82, "rainfall": 10, "sunshine_hours": 6, "condition": "Mua rao"},
    "Lam Dong":  {"temp_min": 15, "temp_max": 24, "humidity": 85, "rainfall": 15, "sunshine_hours": 5, "condition": "Suong mu"},
}

ALERT_THRESHOLDS = {"temp_max_high": 35, "temp_min_cold": 12, "rainfall_heavy": 100, "humidity_high": 92, "humidity_low": 30}


class WeatherService:
    def get_current_weather(self, db, region):
        db_w = self._get_from_db(db, region)
        if db_w:
            return db_w
        mock = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        return {
            "region": region, "date": date.today().isoformat(),
            "temp_min": mock["temp_min"], "temp_max": mock["temp_max"],
            "humidity": mock["humidity"], "rainfall": mock["rainfall"],
            "sunshine_hours": mock["sunshine_hours"], "condition": mock["condition"],
            "warnings": self._analyze_warnings(mock), "source": "mock",
        }

    def get_forecast(self, db, region, days=7):
        base = MOCK_WEATHER.get(region, MOCK_WEATHER["default"])
        result = []
        for i in range(1, days + 1):
            dt = (date.today() + timedelta(days=i)).isoformat()
            v = random.uniform(-2, 2)
            rain = max(0, base["rainfall"] + random.uniform(-5, 10))
            hum = min(100, max(30, base["humidity"] + random.uniform(-5, 5)))
            result.append({
                "date": dt, "temp_min": round(base["temp_min"] + v, 1),
                "temp_max": round(base["temp_max"] + v, 1),
                "humidity": round(hum, 1), "rainfall": round(rain, 1),
                "condition": base["condition"],
                "warnings": self._analyze_warnings({"temp_max": base["temp_max"]+v, "temp_min": base["temp_min"]+v, "rainfall": rain, "humidity": hum}),
            })
        return result

    def get_harvest_weather_warning(self, db, region):
        w = self.get_current_weather(db, region)
        warnings = w.get("warnings", [])
        return " | ".join(warnings) if warnings else None

    def save_weather_data(self, db, region, record_date, temp_min, temp_max, humidity, rainfall, sunshine_hours=0, condition=""):
        record = WeatherData(Region=region, RecordDate=record_date, TempMin=temp_min, TempMax=temp_max,
                             Humidity=humidity, Rainfall=rainfall, SunshineHours=sunshine_hours, WeatherDesc=condition)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def _get_from_db(db, region):
        row = db.query(WeatherData).filter(WeatherData.Region == region).order_by(WeatherData.RecordDate.desc()).first()
        if not row:
            return None
        return {
            "region": row.Region, "date": row.RecordDate.isoformat() if row.RecordDate else None,
            "temp_min": float(row.TempMin) if row.TempMin else None,
            "temp_max": float(row.TempMax) if row.TempMax else None,
            "humidity": float(row.Humidity) if row.Humidity else None,
            "rainfall": float(row.Rainfall) if row.Rainfall else None,
            "sunshine_hours": float(row.SunshineHours) if row.SunshineHours else None,
            "condition": row.WeatherDesc or "",
            "warnings": WeatherService._analyze_warnings({
                "temp_max": float(row.TempMax) if row.TempMax else 25,
                "temp_min": float(row.TempMin) if row.TempMin else 18,
                "rainfall": float(row.Rainfall) if row.Rainfall else 0,
                "humidity": float(row.Humidity) if row.Humidity else 70,
            }),
            "source": "database",
        }

    @staticmethod
    def _analyze_warnings(data):
        w = []
        t = data.get("temp_max", 30)
        tm = data.get("temp_min", 20)
        r = data.get("rainfall", 0)
        h = data.get("humidity", 70)
        if t and t > ALERT_THRESHOLDS["temp_max_high"]: w.append(f"Nang nong ({t}C) - tang tuoi nuoc.")
        if tm and tm < ALERT_THRESHOLDS["temp_min_cold"]: w.append(f"Lanh ({tm}C) - nguy co suong muoi.")
        if r and r > ALERT_THRESHOLDS["rainfall_heavy"]: w.append(f"Mua lon ({r}mm) - kiem tra thoat nuoc.")
        if h and h > ALERT_THRESHOLDS["humidity_high"]: w.append(f"Do am cao ({h}%) - nguy co nam benh.")
        if h and h < ALERT_THRESHOLDS["humidity_low"]: w.append(f"Do am thap ({h}%) - tang tuoi.")
        return w


weather_service = WeatherService()
