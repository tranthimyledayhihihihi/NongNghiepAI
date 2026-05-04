from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from ..core.database import Base

class AIConversation(Base):
    __tablename__ = "AIConversations"
    
    ConvID = Column("ConvID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"))
    SessionID = Column("SessionID", String(100))
    UserMessage = Column("UserMessage", Text, nullable=False)
    AIResponse = Column("AIResponse", Text, nullable=False)
    Topic = Column("Topic", String(50))
    RelatedCropID = Column("RelatedCropID", Integer, ForeignKey("CropTypes.CropID"))
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.ConvID
    
    @property
    def conv_id(self):
        return self.ConvID
    
    @property
    def user_id(self):
        return self.UserID
    
    @property
    def session_id(self):
        return self.SessionID
    
    @property
    def user_message(self):
        return self.UserMessage
    
    @property
    def ai_response(self):
        return self.AIResponse
    
    @property
    def topic(self):
        return self.Topic
    
    @property
    def related_crop_id(self):
        return self.RelatedCropID
