from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from ..core.database import Base

class AlertSubscription(Base):
    __tablename__ = "AlertSubscriptions"
    
    AlertID = Column("AlertID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    Region = Column("Region", String(100), nullable=False)
    TargetPrice = Column("TargetPrice", Numeric(18, 2), nullable=False)
    AlertType = Column("AlertType", String(20), default='Trên')
    NotifyMethod = Column("NotifyMethod", String(20), default='Email')
    IsActive = Column("IsActive", Boolean, default=True)
    LastTriggered = Column("LastTriggered", DateTime)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.AlertID
    
    @property
    def alert_id(self):
        return self.AlertID
    
    @property
    def user_id(self):
        return self.UserID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def target_price(self):
        return self.TargetPrice
    
    @property
    def is_active(self):
        return self.IsActive
