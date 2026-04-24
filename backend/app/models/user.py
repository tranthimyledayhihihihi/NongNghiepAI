from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    __tablename__ = "Users"
    
    UserID = Column("UserID", Integer, primary_key=True, index=True)
    FullName = Column("FullName", String(100), nullable=False)
    Email = Column("Email", String(100), unique=True)
    PhoneNumber = Column("PhoneNumber", String(20))
    ZaloID = Column("ZaloID", String(100))
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.UserID
    
    @property
    def user_id(self):
        return self.UserID
    
    @property
    def full_name(self):
        return self.FullName
    
    @property
    def email(self):
        return self.Email
    
    @property
    def phone_number(self):
        return self.PhoneNumber
    
    @property
    def zalo_id(self):
        return self.ZaloID
