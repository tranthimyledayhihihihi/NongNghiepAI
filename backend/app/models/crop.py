from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from ..core.database import Base

class CropType(Base):
    __tablename__ = "CropTypes"
    
    CropID = Column("CropID", Integer, primary_key=True, index=True)
    CropName = Column("CropName", String(100), nullable=False, unique=True)
    CropNameEN = Column("CropNameEN", String(100))
    Category = Column("Category", String(50), nullable=False)
    GrowthDurationDays = Column("GrowthDurationDays", Integer)
    HarvestSeason = Column("HarvestSeason", String(100))
    TypicalPriceMin = Column("TypicalPriceMin", Numeric(18, 2))
    TypicalPriceMax = Column("TypicalPriceMax", Numeric(18, 2))
    Description = Column("Description", Text)
    ImageURL = Column("ImageURL", String(500))
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.CropID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def name(self):
        return self.CropName
    
    @property
    def crop_name(self):
        return self.CropName
    
    @property
    def growth_duration_days(self):
        return self.GrowthDurationDays

class HarvestSchedule(Base):
    __tablename__ = "HarvestSchedule"
    
    ScheduleID = Column("ScheduleID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    PlantingDate = Column("PlantingDate", Date, nullable=False)
    AreaSize = Column("AreaSize", Float)
    Region = Column("Region", String(100), nullable=False)
    ExpectedHarvestDate = Column("ExpectedHarvestDate", Date)
    ActualHarvestDate = Column("ActualHarvestDate", Date)
    EstimatedYieldKg = Column("EstimatedYieldKg", Float)
    ActualYieldKg = Column("ActualYieldKg", Float)
    FertilizerUsed = Column("FertilizerUsed", String(200))
    PesticideUsed = Column("PesticideUsed", String(200))
    Status = Column("Status", String(50), default='Đang trồng')
    Notes = Column("Notes", Text)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.getdate())
    UpdatedAt = Column("UpdatedAt", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.ScheduleID
    
    @property
    def schedule_id(self):
        return self.ScheduleID
    
    @property
    def user_id(self):
        return self.UserID
    
    @property
    def crop_id(self):
        return self.CropID
    
    @property
    def planting_date(self):
        return self.PlantingDate
    
    @property
    def area_size(self):
        return self.AreaSize
    
    @property
    def region(self):
        return self.Region
    
    @property
    def expected_harvest_date(self):
        return self.ExpectedHarvestDate
    
    @property
    def status(self):
        return self.Status

class QualityRecord(Base):
    __tablename__ = "QualityRecords"
    
    RecordID = Column("RecordID", Integer, primary_key=True, index=True)
    ScheduleID = Column("ScheduleID", Integer, ForeignKey("HarvestSchedule.ScheduleID"))
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False)
    ImagePath = Column("ImagePath", String(500), nullable=False)
    AIGrade = Column("AIGrade", String(20))  # Loại 1, 2, 3
    ConfidenceScore = Column("ConfidenceScore", Float)
    DetectedIssues = Column("DetectedIssues", Text)  # JSON format
    SuggestedPriceMin = Column("SuggestedPriceMin", Numeric(18, 2))
    SuggestedPriceMax = Column("SuggestedPriceMax", Numeric(18, 2))
    Recommendation = Column("Recommendation", Text)
    CheckDate = Column("CheckDate", DateTime, server_default=func.getdate())
    
    # Aliases for backward compatibility
    @property
    def id(self):
        return self.RecordID
    
    @property
    def record_id(self):
        return self.RecordID
    
    @property
    def schedule_id(self):
        return self.ScheduleID
    
    @property
    def image_path(self):
        return self.ImagePath
    
    @property
    def ai_grade(self):
        return self.AIGrade
    
    @property
    def quality_grade(self):
        return self.AIGrade
    
    @property
    def confidence_score(self):
        return self.ConfidenceScore
    
    @property
    def confidence(self):
        return self.ConfidenceScore
    
    @property
    def detected_diseases(self):
        return self.DetectedDiseases
