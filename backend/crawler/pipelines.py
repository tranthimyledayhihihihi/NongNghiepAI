"""P2-08: Crawler Pipelines"""
import os, sys, logging
from datetime import datetime, date

logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    QUALITY_MAP = {
        "grade_1": "Loai 1", "1": "Loai 1", "loai 1": "Loai 1",
        "grade_2": "Loai 2", "2": "Loai 2", "loai 2": "Loai 2",
        "grade_3": "Loai 3", "3": "Loai 3", "loai 3": "Loai 3",
    }

    def process_item(self, item, spider):
        if "crop_name" in item and item["crop_name"]:
            item["crop_name"] = item["crop_name"].strip()
        if "region" in item and item["region"]:
            item["region"] = item["region"].strip()
        if "price_per_kg" in item:
            try:
                price = float(str(item["price_per_kg"]).replace(",", "").replace(".", ""))
                if price > 500000:
                    price = price / 1000
                if price <= 0 or price > 200000:
                    spider.logger.warning(f"Bad price {price} for {item.get('crop_name')}")
                    return None
                item["price_per_kg"] = price
            except (ValueError, TypeError):
                spider.logger.warning(f"Invalid price: {item.get('price_per_kg')}")
                return None
        grade = str(item.get("quality_grade", "")).lower()
        item["quality_grade"] = self.QUALITY_MAP.get(grade, "Loai 1")
        if not item.get("date"):
            item["date"] = date.today().isoformat()
        if not item.get("collected_at"):
            item["collected_at"] = datetime.now().isoformat()
        return item


class MarketPricePipeline:
    def open_spider(self, spider):
        self.session = None
        self.crop_cache = {}
        try:
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            if backend_dir not in sys.path:
                sys.path.insert(0, backend_dir)
            from app.core.database import SessionLocal
            self.session = SessionLocal()
            spider.logger.info("DB session opened")
        except Exception as e:
            spider.logger.error(f"Cannot open DB: {e}")

    def close_spider(self, spider):
        if self.session:
            self.session.close()

    def process_item(self, item, spider):
        if not self.session:
            logger.info(f"[NO DB] {item.get('crop_name')} @ {item.get('region')}: {item.get('price_per_kg')}")
            return item
        try:
            crop_id = self._get_crop_id(item.get("crop_name", ""))
            if not crop_id:
                return item
            from app.models.price import MarketPrice
            raw_date = item.get("date")
            if isinstance(raw_date, str):
                price_date = date.fromisoformat(raw_date)
            elif isinstance(raw_date, date):
                price_date = raw_date
            else:
                price_date = date.today()
            record = MarketPrice(
                CropID=crop_id, Region=item.get("region", ""),
                PricePerKg=item.get("price_per_kg", 0),
                QualityGrade=item.get("quality_grade", "Loai 1"),
                MarketType=item.get("market_type", "Ban buon"),
                SourceURL=item.get("url", ""), SourceName=item.get("source", ""),
                PriceDate=price_date,
            )
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"DB save error: {e}")
        return item

    def _get_crop_id(self, crop_name):
        if not crop_name:
            return None
        if crop_name in self.crop_cache:
            return self.crop_cache[crop_name]
        try:
            from app.models.crop import CropType
            crop = self.session.query(CropType).filter(CropType.CropName == crop_name).first()
            if not crop:
                crop = CropType(CropName=crop_name, Category="Rau cu qua")
                self.session.add(crop)
                self.session.commit()
                self.session.refresh(crop)
            self.crop_cache[crop_name] = crop.CropID
            return crop.CropID
        except Exception as e:
            logger.error(f"Crop resolve error: {e}")
            return None
