from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from ..core.database import Base

class MarketPrice(Base):
    __tablename__ = "MarketPrices"
    
    PriceID = Column("PriceID", Integer, primary_key=True, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"))
    Region = Column("Region", String(100))
    PricePerKg = Column("PricePerKg", Numeric(18, 2))
    SourceURL = Column("SourceURL", String(255))
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
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"))
    Region = Column("Region", String(100))
    OldPrice = Column("OldPrice", Numeric(18, 2))
    NewPrice = Column("NewPrice", Numeric(18, 2))
    ChangeDate = Column("ChangeDate", DateTime, server_default=func.getdate())
    
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
    def old_price(self):
        return self.OldPrice
    
    @property
    def new_price(self):
        return self.NewPrice
    
    @property
    def change_date(self):
        return self.ChangeDate
