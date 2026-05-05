from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class QualityCheck(Base):
    __tablename__ = "QualityRecords"

    RecordID = Column("RecordID", Integer, primary_key=True, index=True)
    ScheduleID = Column("ScheduleID", Integer, ForeignKey("HarvestSchedule.ScheduleID"), nullable=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False, index=True)
    ImagePath = Column("ImagePath", String(500), nullable=False)
    AIGrade = Column("AIGrade", String(20), nullable=True)
    ConfidenceScore = Column("ConfidenceScore", Float, nullable=True)
    DetectedIssues = Column("DetectedIssues", Text, nullable=True)
    SuggestedPriceMin = Column("SuggestedPriceMin", Float, nullable=True)
    SuggestedPriceMax = Column("SuggestedPriceMax", Float, nullable=True)
    Recommendation = Column("Recommendation", Text, nullable=True)
    CheckDate = Column("CheckDate", DateTime, server_default=func.now(), nullable=False)

    id = synonym("RecordID")
    schedule_id = synonym("ScheduleID")
    user_id = synonym("UserID")
    crop_id = synonym("CropID")
    image_path = synonym("ImagePath")
    quality_grade = synonym("AIGrade")
    ai_grade = synonym("AIGrade")
    confidence = synonym("ConfidenceScore")
    confidence_score = synonym("ConfidenceScore")
    detected_issues = synonym("DetectedIssues")
    suggested_price_min = synonym("SuggestedPriceMin")
    suggested_price_max = synonym("SuggestedPriceMax")
    recommendation = synonym("Recommendation")
    checked_at = synonym("CheckDate")
    check_date = synonym("CheckDate")


QualityRecord = QualityCheck
