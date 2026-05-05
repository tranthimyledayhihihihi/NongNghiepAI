from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class WeatherData(Base):
    __tablename__ = "WeatherData"

    WeatherID = Column("WeatherID", Integer, primary_key=True, index=True)
    Region = Column("Region", String(100), nullable=False, index=True)
    RecordDate = Column("RecordDate", Date, nullable=False, index=True)
    TempMin = Column("TempMin", Float, nullable=True)
    TempMax = Column("TempMax", Float, nullable=True)
    Humidity = Column("Humidity", Float, nullable=True)
    Rainfall = Column("Rainfall", Float, nullable=True)
    SunshineHours = Column("SunshineHours", Float, nullable=True)
    WeatherDesc = Column("WeatherDesc", String(100), nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("WeatherID")
    region = synonym("Region")
    record_date = synonym("RecordDate")
    temp_min = synonym("TempMin")
    temp_max = synonym("TempMax")
    humidity = synonym("Humidity")
    rainfall = synonym("Rainfall")
    sunshine_hours = synonym("SunshineHours")
    weather_desc = synonym("WeatherDesc")
    created_at = synonym("CreatedAt")

    @property
    def temperature(self) -> float | None:
        if self.TempMin is None and self.TempMax is None:
            return None
        if self.TempMin is None:
            return self.TempMax
        if self.TempMax is None:
            return self.TempMin
        return (self.TempMin + self.TempMax) / 2

    @property
    def condition(self) -> str | None:
        return self.WeatherDesc

    @property
    def recorded_at(self):
        return self.CreatedAt
