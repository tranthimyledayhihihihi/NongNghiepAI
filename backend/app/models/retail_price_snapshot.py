from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.core.database import Base


class RetailPriceSnapshot(Base):
    __tablename__ = "retail_price_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)

    crop_name = Column(String(200), nullable=False, index=True)
    product_name = Column(String(250), nullable=False)

    retailer = Column(String(200), nullable=False, index=True)

    retail_price = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False, default="VNĐ/kg")

    source_url = Column(Text, nullable=True)

    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    is_realtime = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

