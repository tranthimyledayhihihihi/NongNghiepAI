from datetime import datetime, date as date_type
from scrapy.exceptions import DropItem
from app.core.database import SessionLocal
from app.models.crop import CropType
from app.models.price import MarketPrice, PriceHistory


class DataCleaningPipeline:
    """Validate và làm sạch dữ liệu trước khi lưu."""

    def process_item(self, item, _spider):
        price = item.get("price_per_kg") or item.get("price")
        if not price or float(price) <= 0:
            raise DropItem(f"Giá không hợp lệ: {price}")

        if not item.get("crop_name") or not item.get("region"):
            raise DropItem(f"Thiếu crop_name hoặc region: {dict(item)}")

        return item


class MarketPricePipeline:
    """Lưu MarketPriceItem vào bảng MarketPrices (upsert theo crop+region+date)."""

    def __init__(self):
        self.db = None

    def open_spider(self, _spider):
        self.db = SessionLocal()

    def close_spider(self, _spider):
        if self.db:
            self.db.close()

    def process_item(self, item, spider):
        crop_name = item.get("crop_name", "").strip()
        region = item.get("region", "").strip()
        price = float(item.get("price_per_kg") or item.get("price") or 0)
        source_name = item.get("source", "")
        source_url = item.get("url", "")

        date_raw = item.get("date")
        try:
            price_date = date_type.fromisoformat(date_raw) if date_raw else date_type.today()
        except (ValueError, TypeError):
            price_date = date_type.today()

        crop = (
            self.db.query(CropType)
            .filter(CropType.CropName.ilike(f"%{crop_name}%"))
            .first()
        )
        if not crop:
            spider.logger.warning(f"Bỏ qua: '{crop_name}' chưa có trong CropType.")
            return item

        existing = (
            self.db.query(MarketPrice)
            .filter(
                MarketPrice.CropID == crop.CropID,
                MarketPrice.Region == region,
                MarketPrice.PriceDate == price_date,
            )
            .first()
        )

        if existing:
            existing.PricePerKg = price
            existing.SourceURL = source_url
            existing.SourceName = source_name
        else:
            # Không truyền QualityGrade/MarketType — dùng DEFAULT của DB (N'Loại 1', N'Bán lẻ')
            # để tránh lỗi encoding VARCHAR vs NVARCHAR CHECK constraint
            self.db.add(MarketPrice(
                CropID=crop.CropID,
                Region=region,
                PricePerKg=price,
                SourceURL=source_url,
                SourceName=source_name,
                PriceDate=price_date,
            ))

        self.db.commit()
        spider.logger.info(f"Đã lưu giá {crop_name} @ {region}: {price:,.0f} VND/kg")
        return item


class DatabasePipeline:
    """Pipeline cũ - lưu plain dict vào PriceHistory (dùng bởi agro_spider)."""

    def __init__(self):
        self.db = None

    def open_spider(self, _spider):
        self.db = SessionLocal()

    def close_spider(self, _spider):
        if self.db:
            self.db.close()

    def process_item(self, item, spider):
        crop_name = item.get("crop_name")
        region = item.get("region")
        price = item.get("price")
        collected_at = item.get("collected_at")

        crop = self.db.query(CropType).filter(CropType.CropName == crop_name).first()
        if not crop:
            spider.logger.warning(f"Bỏ qua: '{crop_name}' chưa có trong CropType.")
            return item

        try:
            record_date = datetime.fromisoformat(collected_at).date() if collected_at else datetime.now().date()
        except (ValueError, TypeError):
            record_date = datetime.now().date()

        existing = (
            self.db.query(PriceHistory)
            .filter(
                PriceHistory.CropID == crop.CropID,
                PriceHistory.Region == region,
                PriceHistory.RecordDate == record_date,
            )
            .first()
        )

        if existing:
            existing.AvgPrice = price
        else:
            self.db.add(PriceHistory(
                CropID=crop.CropID,
                Region=region,
                RecordDate=record_date,
                AvgPrice=price,
            ))

        self.db.commit()
        spider.logger.info(f"Đã lưu giá {crop_name} @ {region}: {price:,.0f}")
        return item
