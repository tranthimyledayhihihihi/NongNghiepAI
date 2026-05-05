from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class AIConversation(Base):
    __tablename__ = "AIConversations"

    ConvID = Column("ConvID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=True, index=True)
    SessionID = Column("SessionID", String(100), nullable=True)
    UserMessage = Column("UserMessage", Text, nullable=False)
    AIResponse = Column("AIResponse", Text, nullable=False)
    Topic = Column("Topic", String(50), nullable=True)
    RelatedCropID = Column("RelatedCropID", Integer, ForeignKey("CropTypes.CropID"), nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("ConvID")
    user_id = synonym("UserID")
    session_id = synonym("SessionID")
    user_message = synonym("UserMessage")
    ai_response = synonym("AIResponse")
    topic = synonym("Topic")
    related_crop_id = synonym("RelatedCropID")
    created_at = synonym("CreatedAt")
