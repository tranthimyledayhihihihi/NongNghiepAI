# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from app.core.database import SessionLocal
from app.models.crop import Crop
from app.models.price import MarketPrice
db = SessionLocal()
rows = (db.query(Crop.CropName, MarketPrice).join(MarketPrice, Crop.CropID == MarketPrice.CropID)
        .order_by(MarketPrice.PriceDate.desc()).limit(10).all())
for name, mp in rows:
    print(f"{name} tại {mp.Region}: {mp.PricePerKg:,.0f} VNĐ/kg — {mp.PriceDate}")
db.close()
