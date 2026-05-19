from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode
from sqlalchemy.sql import func

from ..core.database import Base


class StorePrice(Base):
    __tablename__ = "StorePrices"

    ID = Column("ID", Integer, primary_key=True, index=True, autoincrement=True)
    CropName = Column("CropName", Unicode(100), nullable=False, index=True)
    Region = Column("Region", Unicode(100), nullable=False, index=True)
    StoreID = Column("StoreID", String(50), nullable=False)
    StoreName = Column("StoreName", Unicode(100), nullable=False)
    StoreType = Column("StoreType", Unicode(50), nullable=True)
    Price = Column("Price", Float, nullable=False)
    Unit = Column("Unit", String(20), nullable=True, default="đ/kg")
    Source = Column("Source", String(50), nullable=True)
    SourceModel = Column("SourceModel", String(100), nullable=True)
    FetchedAt = Column("FetchedAt", DateTime, server_default=func.now(), nullable=False)
    UpdatedAt = Column("UpdatedAt", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
