from sqlalchemy import Column, Integer, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func
from ..core.database import Base

class AlertSubscription(Base):
    __tablename__ = "AlertSubscriptions"
    
    AlertID = Column("AlertID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"))
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"))
    TargetPrice = Column("TargetPrice", Numeric(18, 2))
    IsActive = Column("IsActive", Boolean, default=True)
    
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
