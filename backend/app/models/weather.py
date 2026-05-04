from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from ..core.database import Base

class WeatherData(Base):
    __tablename__ = "WeatherData"
    
    WeatherID = Column("WeatherID", Integer, primary_key=True, index=True)
    Region = Column("Region", String(100), nullable=False)
    RecordDate = Column("RecordDate", Date, nullable=False)
    TempMin = Column("TempMin", Float)
    TempMax = Column("TempMax", Float)
    Humidity = Column("Humidity", Float)
    Rainfall = Column("Rainfall", Float)
    SunshineHours = Column("SunshineHours", Float)
    WeatherDesc = Column("WeatherDesc", String(100))
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.WeatherID
    
    @property
    def weather_id(self):
        return self.WeatherID
    
    @property
    def region(self):
        return self.Region
    
    @property
    def record_date(self):
        return self.RecordDate
    
    @property
    def temp_min(self):
        return self.TempMin
    
    @property
    def temp_max(self):
        return self.TempMax
    
    @property
    def humidity(self):
        return self.Humidity
    
    @property
    def rainfall(self):
        return self.Rainfall
    
    @property
    def sunshine_hours(self):
        return self.SunshineHours
    
    @property
    def weather_desc(self):
        return self.WeatherDesc
