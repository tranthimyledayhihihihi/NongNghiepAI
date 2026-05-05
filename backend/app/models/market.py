from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class MarketSuggestion(Base):
    __tablename__ = "MarketSuggestions"

    SuggestionID = Column("SuggestionID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False, index=True)
    Region = Column("Region", String(100), nullable=False)
    QuantityKg = Column("QuantityKg", Float, nullable=False)
    QualityGrade = Column("QualityGrade", String(20), nullable=True)
    RecommendedChannel = Column("RecommendedChannel", String(50), nullable=True)
    EstimatedProfit = Column("EstimatedProfit", Float, nullable=True)
    Reason = Column("Reason", Text, nullable=True)
    Warning = Column("Warning", Text, nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("SuggestionID")
    user_id = synonym("UserID")
    crop_id = synonym("CropID")
    region = synonym("Region")
    quantity_kg = synonym("QuantityKg")
    quality_grade = synonym("QualityGrade")
    recommended_channel = synonym("RecommendedChannel")
    estimated_profit = synonym("EstimatedProfit")
    reason = synonym("Reason")
    warning = synonym("Warning")
    created_at = synonym("CreatedAt")
