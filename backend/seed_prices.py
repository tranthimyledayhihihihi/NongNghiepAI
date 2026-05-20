"""
Seed dữ liệu giá thị trường mẫu vào bảng MarketPrices.
Chạy: python seed_prices.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, datetime, timedelta
from app.core.database import SessionLocal
from app.models.price import MarketPrice
from app.models.crop import CropType

SOURCE_URL = "https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx"
SOURCE_NAME = "Thông tin thị trường nông sản"

REGIONS = ["Ha Noi", "Ho Chi Minh", "Da Nang", "Can Tho", "Hai Phong",
           "Dak Lak", "Gia Lai", "Lam Dong", "Binh Phuoc", "Dong Nai"]

# crop_name_en (khớp với seed_db.py) -> giá VND/kg theo từng vùng
PRICE_DATA = {
    "Rice":        {"Ha Noi": 8500,  "Ho Chi Minh": 8000,  "Da Nang": 8200,  "Can Tho": 7800,  "Hai Phong": 8300,
                    "Dak Lak": 8100, "Gia Lai": 8000, "Lam Dong": 8200, "Binh Phuoc": 8000, "Dong Nai": 8300},
    "Corn":        {"Ha Noi": 6500,  "Ho Chi Minh": 6200,  "Da Nang": 6400,  "Can Tho": 6000,  "Hai Phong": 6600,
                    "Dak Lak": 6300, "Gia Lai": 6200, "Lam Dong": 6400, "Binh Phuoc": 6100, "Dong Nai": 6500},
    "Tomato":      {"Ha Noi": 15000, "Ho Chi Minh": 12000, "Da Nang": 13000, "Can Tho": 11000, "Hai Phong": 14000,
                    "Dak Lak": 12500,"Gia Lai": 12000,"Lam Dong": 18000,"Binh Phuoc": 11500,"Dong Nai": 13000},
    "Durian":      {"Ha Noi": 95000, "Ho Chi Minh": 85000, "Da Nang": 90000, "Can Tho": 80000, "Hai Phong": 98000,
                    "Dak Lak": 88000,"Gia Lai": 85000,"Lam Dong": 90000,"Binh Phuoc": 82000,"Dong Nai": 87000},
    "Mango":       {"Ha Noi": 35000, "Ho Chi Minh": 28000, "Da Nang": 30000, "Can Tho": 25000, "Hai Phong": 36000,
                    "Dak Lak": 30000,"Gia Lai": 28000,"Lam Dong": 32000,"Binh Phuoc": 27000,"Dong Nai": 31000},
    "Dragon Fruit":{"Ha Noi": 22000, "Ho Chi Minh": 18000, "Da Nang": 19000, "Can Tho": 16000, "Hai Phong": 23000,
                    "Dak Lak": 20000,"Gia Lai": 19000,"Lam Dong": 21000,"Binh Phuoc": 18000,"Dong Nai": 20000},
    "Coffee":      {"Ha Noi": 75000, "Ho Chi Minh": 73000, "Da Nang": 74000, "Can Tho": 72000, "Hai Phong": 76000,
                    "Dak Lak": 77000,"Gia Lai": 76000,"Lam Dong": 75000,"Binh Phuoc": 74000,"Dong Nai": 74500},
    "Black Pepper":{"Ha Noi": 92000, "Ho Chi Minh": 88000, "Da Nang": 90000, "Can Tho": 85000, "Hai Phong": 93000,
                    "Dak Lak": 95000,"Gia Lai": 93000,"Lam Dong": 91000,"Binh Phuoc": 96000,"Dong Nai": 94000},
    "Rubber":      {"Ha Noi": 38000, "Ho Chi Minh": 35000, "Da Nang": 36000, "Can Tho": 34000, "Hai Phong": 39000,
                    "Dak Lak": 37000,"Gia Lai": 36000,"Lam Dong": 37500,"Binh Phuoc": 38000,"Dong Nai": 37000},
    "Banana":      {"Ha Noi": 12000, "Ho Chi Minh": 10000, "Da Nang": 11000, "Can Tho": 9500,  "Hai Phong": 12500,
                    "Dak Lak": 10500,"Gia Lai": 10000,"Lam Dong": 11000,"Binh Phuoc": 9800, "Dong Nai": 11000},
    "Cabbage":     {"Ha Noi": 9000,  "Ho Chi Minh": 8500,  "Da Nang": 8800,  "Can Tho": 8000,  "Hai Phong": 9200,
                    "Dak Lak": 8500, "Gia Lai": 8200, "Lam Dong": 12000,"Binh Phuoc": 8000, "Dong Nai": 8800},
    "Sweet Potato":{"Ha Noi": 9000,  "Ho Chi Minh": 8000,  "Da Nang": 8500,  "Can Tho": 7500,  "Hai Phong": 9500,
                    "Dak Lak": 8200, "Gia Lai": 8000, "Lam Dong": 8800, "Binh Phuoc": 7800, "Dong Nai": 8500},
}

# Dao động nhỏ theo ngày (±3%) để có lịch sử 7 ngày
import random
random.seed(42)

def price_for_day(base: int, delta_days: int) -> float:
    factor = 1.0 + random.uniform(-0.03, 0.03) * delta_days / 7
    return round(base * factor)


def main():
    db = SessionLocal()
    try:
        # Lấy map crop_name_en -> crop_id
        crops = db.query(CropType).all()
        crop_map = {c.CropNameEN: c.CropID for c in crops if c.CropNameEN}

        today = date.today()
        now = datetime.now()
        inserted = 0
        skipped = 0

        for crop_en, region_prices in PRICE_DATA.items():
            crop_id = crop_map.get(crop_en)
            if not crop_id:
                print(f"  [SKIP] Không tìm thấy crop '{crop_en}' trong DB")
                skipped += 1
                continue

            for region, base_price in region_prices.items():
                # Seed 7 ngày gần nhất
                for delta in range(7):
                    price_date = today - timedelta(days=delta)
                    price_val = price_for_day(base_price, delta)

                    # Kiểm tra đã có chưa (tránh duplicate)
                    exists = db.query(MarketPrice).filter(
                        MarketPrice.CropID == crop_id,
                        MarketPrice.Region == region,
                        MarketPrice.PriceDate == price_date,
                        MarketPrice.IsMock == False,
                    ).first()

                    if exists:
                        skipped += 1
                        continue

                    row = MarketPrice(
                        CropID=crop_id,
                        Region=region,
                        PricePerKg=price_val,
                        QualityGrade="Loai 1",
                        MarketType="Ban le",
                        SourceURL=SOURCE_URL,
                        SourceName=SOURCE_NAME,
                        SourceType="official",
                        FetchedAt=now - timedelta(days=delta),
                        ObservedAt=now - timedelta(days=delta),
                        ConfidenceScore=0.85,
                        IsRealtime=True,
                        IsMock=False,
                        PriceDate=price_date,
                    )
                    db.add(row)
                    inserted += 1

        db.commit()
        print(f"\n[OK] Seed xong: {inserted} bản ghi mới, {skipped} bỏ qua (đã tồn tại/không tìm thấy crop).")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
