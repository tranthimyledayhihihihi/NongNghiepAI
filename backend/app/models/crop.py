from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, Numeric
from sqlalchemy.sql import func
from ..core.database import Base

class CropType(Base):
    __tablename__ = "CropTypes"
    
    CropID = Column("CropID", Integer, primary_key=True, index=True)
    CropName = Column("CropName", String(100), nullable=False)
    GrowthDurationDays = Column("GrowthDurationDays", Integer)
    Description = Column("Description", Text)
    
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
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"))
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"))
    PlantingDate = Column("PlantingDate", Date, nullable=False)
    AreaSize = Column("AreaSize", Float)
    Region = Column("Region", String(100))
    ExpectedHarvestDate = Column("ExpectedHarvestDate", Date)
    Status = Column("Status", String(50), default='Growing')
    
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
    ImagePath = Column("ImagePath", String(500))
    AIGrade = Column("AIGrade", String(20))  # Loại 1, 2, 3
    ConfidenceScore = Column("ConfidenceScore", Float)
    DetectedDiseases = Column("DetectedDiseases", Text)
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
