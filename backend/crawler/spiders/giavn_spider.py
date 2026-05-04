"""P2-07: Spider gia.vn"""
import re
from datetime import date, datetime
import scrapy
from crawler.items import MarketPriceItem

SOURCE = "gia.vn"
START_URLS = ["https://gia.vn/gia-nong-san/"]

SAMPLE_DATA = [
    {"crop_name": "Ca chua",   "region": "TP.HCM", "price_per_kg": 19000},
    {"crop_name": "Dua hau",   "region": "TP.HCM", "price_per_kg": 8000},
    {"crop_name": "Xoai",      "region": "Can Tho","price_per_kg": 25000},
    {"crop_name": "Chuoi",     "region": "TP.HCM", "price_per_kg": 12000},
    {"crop_name": "Cam",       "region": "Ha Noi", "price_per_kg": 30000},
    {"crop_name": "Rau muong", "region": "TP.HCM", "price_per_kg": 7000},
    {"crop_name": "Khoai tay", "region": "Ha Noi", "price_per_kg": 20000},
    {"crop_name": "Buoi",      "region": "TP.HCM", "price_per_kg": 22000},
    {"crop_name": "Dau bap",   "region": "Lam Dong","price_per_kg": 16000},
    {"crop_name": "Ot",        "region": "TP.HCM", "price_per_kg": 20000},
]


class GiaVnSpider(scrapy.Spider):
    name = "giavn"
    allowed_domains = ["gia.vn"]
    start_urls = START_URLS
    custom_settings = {"DOWNLOAD_DELAY": 3, "ROBOTSTXT_OBEY": False, "HTTPERROR_ALLOW_ALL": True}

    def parse(self, response):
        if response.status != 200:
            yield from self._sample()
            return
        found = 0
        for row in response.css(".price-list li, .price-table tbody tr"):
            try:
                texts = [t.strip() for t in row.css("::text").getall() if t.strip()]
                if len(texts) < 2:
                    continue
                price_text = next((t for t in texts[1:] if re.search(r"\d{4,}", t)), None)
                if not price_text:
                    continue
                price = float(re.sub(r"[^\d]", "", price_text))
                if price > 0:
                    item = MarketPriceItem()
                    item["crop_name"] = texts[0]
                    item["region"] = "TP.HCM"
                    item["price_per_kg"] = price
                    item["quality_grade"] = "Loai 1"
                    item["market_type"] = "Ban le"
                    item["source"] = SOURCE
                    item["url"] = response.url
                    item["date"] = date.today().isoformat()
                    item["collected_at"] = datetime.now().isoformat()
                    found += 1
                    yield item
            except Exception:
                pass
        if not found:
            yield from self._sample()

    def _sample(self):
        import random
        for s in SAMPLE_DATA:
            item = MarketPriceItem()
            item["crop_name"] = s["crop_name"]
            item["region"] = s["region"]
            item["price_per_kg"] = round(s["price_per_kg"] * random.uniform(0.94, 1.06), -2)
            item["quality_grade"] = "Loai 1"
            item["market_type"] = "Ban le"
            item["source"] = SOURCE + " (sample)"
            item["url"] = START_URLS[0]
            item["date"] = date.today().isoformat()
            item["collected_at"] = datetime.now().isoformat()
            yield item
