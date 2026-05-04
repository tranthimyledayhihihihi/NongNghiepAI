from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Text, Float
from sqlalchemy.sql import func
from ..core.database import Base

class MarketPrice(Base):
    __tablename__ = "MarketPrices"
    
    PriceID = Column("PriceID", Integer, primary_key=True, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    Region = Column("Region", String(100), nullable=False)
    PricePerKg = Column("PricePerKg", Numeric(18, 2), nullable=False)
    QualityGrade = Column("QualityGrade", String(20), default='Loại 1')
    MarketType = Column("MarketType", String(50), default='Bán lẻ')
    SourceURL = Column("SourceURL", String(500))
    SourceName = Column("SourceName", String(100))
    PriceDate = Column("PriceDate", Date, nullable=False)
    UpdatedAt = Column("UpdatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.PriceID
    
    @property
    def price_id(self):
        return self.PriceID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def region(self):
        return self.Region
    
    @property
    def price_per_kg(self):
        return self.PricePerKg
    
    @property
    def source_url(self):
        return self.SourceURL
    
    @property
    def updated_at(self):
        return self.UpdatedAt

class PriceHistory(Base):
    __tablename__ = "PriceHistory"
    
    HistoryID = Column("HistoryID", Integer, primary_key=True, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    Region = Column("Region", String(100), nullable=False)
    AvgPrice = Column("AvgPrice", Numeric(18, 2), nullable=False)
    MinPrice = Column("MinPrice", Numeric(18, 2))
    MaxPrice = Column("MaxPrice", Numeric(18, 2))
    Volume = Column("Volume", Float)
    RecordDate = Column("RecordDate", Date, nullable=False)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.HistoryID
    
    @property
    def history_id(self):
        return self.HistoryID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def region(self):
        return self.Region
    
    @property
    def avg_price(self):
        return self.AvgPrice
    
    @property
    def min_price(self):
        return self.MinPrice
    
    @property
    def max_price(self):
        return self.MaxPrice
    
    @property
    def volume(self):
        return self.Volume
    
    @property
    def record_date(self):
        return self.RecordDate

class PriceForecastResult(Base):
    __tablename__ = "PriceForecastResults"
    
    ForecastID = Column("ForecastID", Integer, primary_key=True, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    Region = Column("Region", String(100), nullable=False)
    ForecastDate = Column("ForecastDate", Date, nullable=False)
    PredictedPrice = Column("PredictedPrice", Numeric(18, 2), nullable=False)
    ConfidenceLow = Column("ConfidenceLow", Numeric(18, 2))
    ConfidenceHigh = Column("ConfidenceHigh", Numeric(18, 2))
    PriceTrend = Column("PriceTrend", String(20))
    ModelVersion = Column("ModelVersion", String(50))
    GeneratedAt = Column("GeneratedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.ForecastID
    
    @property
    def forecast_id(self):
        return self.ForecastID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def region(self):
        return self.Region
    
    @property
    def forecast_date(self):
        return self.ForecastDate
    
    @property
    def predicted_price(self):
        return self.PredictedPrice
    
    @property
    def confidence_low(self):
        return self.ConfidenceLow
    
    @property
    def confidence_high(self):
        return self.ConfidenceHigh
    
    @property
    def price_trend(self):
        return self.PriceTrend
    
    @property
    def model_version(self):
        return self.ModelVersion

