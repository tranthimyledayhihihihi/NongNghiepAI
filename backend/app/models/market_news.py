from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Unicode, UnicodeText
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class MarketNews(Base):
    __tablename__ = "MarketNews"

    NewsID = Column("NewsID", Integer, primary_key=True, index=True)
    Title = Column("Title", Unicode(300), nullable=False)
    Summary = Column("Summary", UnicodeText, nullable=True)
    SourceName = Column("SourceName", Unicode(100), nullable=True)
    SourceURL = Column("SourceURL", String(500), nullable=True, unique=True)
    PublishedAt = Column("PublishedAt", DateTime, nullable=True, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=True, index=True)
    Region = Column("Region", Unicode(100), nullable=True, index=True)
    Sentiment = Column("Sentiment", String(20), nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("NewsID")
    title = synonym("Title")
    summary = synonym("Summary")
    source_name = synonym("SourceName")
    source_url = synonym("SourceURL")
    published_at = synonym("PublishedAt")
    crop_id = synonym("CropID")
    region = synonym("Region")
    sentiment = synonym("Sentiment")
    created_at = synonym("CreatedAt")
