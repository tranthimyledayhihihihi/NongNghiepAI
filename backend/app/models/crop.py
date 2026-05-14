from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class Crop(Base):
    __tablename__ = "CropTypes"

    CropID = Column("CropID", Integer, primary_key=True, index=True)
    CropName = Column("CropName", String(100), nullable=False, unique=True, index=True)
    CropNameEN = Column("CropNameEN", String(100), nullable=True)
    Category = Column("Category", String(50), nullable=False, default="Khác")
    GrowthDurationDays = Column("GrowthDurationDays", Integer, nullable=True)
    HarvestSeason = Column("HarvestSeason", String(100), nullable=True)
    TypicalPriceMin = Column("TypicalPriceMin", Float, nullable=True)
    TypicalPriceMax = Column("TypicalPriceMax", Float, nullable=True)
    Description = Column("Description", Text, nullable=True)
    ImageURL = Column("ImageURL", String(500), nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("CropID")
    name = synonym("CropName")
    crop_name = synonym("CropName")
    crop_name_en = synonym("CropNameEN")
    category = synonym("Category")
    growth_duration_days = synonym("GrowthDurationDays")
    avg_growth_days = synonym("GrowthDurationDays")
    harvest_season = synonym("HarvestSeason")
    typical_price_min = synonym("TypicalPriceMin")
    typical_price_max = synonym("TypicalPriceMax")
    description = synonym("Description")
    image_url = synonym("ImageURL")
    created_at = synonym("CreatedAt")

    @property
    def default_unit(self) -> str:
        return "kg"


CropType = Crop
