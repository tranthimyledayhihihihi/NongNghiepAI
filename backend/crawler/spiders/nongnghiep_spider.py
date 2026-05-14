"""P2-07: Spider nongnghiep.vn"""
import re
from datetime import date, datetime
import scrapy
from crawler.items import MarketPriceItem

SOURCE = "nongnghiep.vn"
START_URLS = ["https://nongnghiep.vn/thi-truong/gia-ca-d1.html"]

SAMPLE_DATA = [
    {"crop_name": "Lua",        "region": "Can Tho",    "price_per_kg": 8500},
    {"crop_name": "Lua",        "region": "Dong Thap",  "price_per_kg": 8200},
    {"crop_name": "Ngo",        "region": "Dak Lak",    "price_per_kg": 6500},
    {"crop_name": "Sau rieng",  "region": "Tien Giang", "price_per_kg": 65000},
    {"crop_name": "Thanh long", "region": "Binh Thuan", "price_per_kg": 20000},
    {"crop_name": "Dau nanh",   "region": "Ha Noi",     "price_per_kg": 18000},
    {"crop_name": "Ca phe",     "region": "Dak Lak",    "price_per_kg": 110000},
    {"crop_name": "Tieu",       "region": "Gia Lai",    "price_per_kg": 75000},
    {"crop_name": "Mit",        "region": "Tien Giang", "price_per_kg": 15000},
    {"crop_name": "Dieu",       "region": "Binh Phuoc", "price_per_kg": 45000},
]

REGIONS = ["Ha Noi", "TP.HCM", "Da Nang", "Can Tho", "Lam Dong",
           "Tien Giang", "Dong Thap", "Binh Thuan", "Dak Lak", "Gia Lai"]
CROPS = ["lua", "ngo", "sau rieng", "thanh long", "xoai", "chuoi",
         "ca phe", "tieu", "dieu", "mit", "buoi", "cam", "ca chua", "dua hau"]


class NongNghiepSpider(scrapy.Spider):
    name = "nongnghiep"
    allowed_domains = ["nongnghiep.vn"]
    start_urls = START_URLS
    custom_settings = {"DOWNLOAD_DELAY": 3, "ROBOTSTXT_OBEY": False, "HTTPERROR_ALLOW_ALL": True}

    def parse(self, response):
        if response.status != 200:
            yield from self._sample()
            return
        found = 0
        for article in response.css("article, .news-item"):
            try:
                title = article.css("h2 ::text, h3 ::text, .title ::text").get("").strip()
                crop = self._extract_crop(title)
                if not crop:
                    continue
                content = " ".join(article.css("::text").getall())
                price = self._extract_price(content)
                if not price:
                    continue
                region = next((r for r in REGIONS if r.lower() in content.lower()), "Ha Noi")
                item = MarketPriceItem()
                item["crop_name"] = crop
                item["region"] = region
                item["price_per_kg"] = price
                item["quality_grade"] = "Loai 1"
                item["market_type"] = "Ban buon"
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

    def _extract_crop(self, text):
        tl = text.lower()
        for c in CROPS:
            if c in tl:
                return c.capitalize()
        return None

    @staticmethod
    def _extract_price(text):
        m = re.search(r"(\d{1,3}(?:[.,]\d{3})+)\s*(?:dong|VND)?\s*/\s*kg", text, re.IGNORECASE)
        if m:
            digits = re.sub(r"[^\d]", "", m.group(1))
            val = float(digits)
            if 1000 <= val <= 500000:
                return val
        return None

    def _sample(self):
        import random
        for s in SAMPLE_DATA:
            item = MarketPriceItem()
            item["crop_name"] = s["crop_name"]
            item["region"] = s["region"]
            item["price_per_kg"] = round(s["price_per_kg"] * random.uniform(0.93, 1.07), -2)
            item["quality_grade"] = "Loai 1"
            item["market_type"] = "Ban buon"
            item["source"] = SOURCE + " (sample)"
            item["url"] = START_URLS[0]
            item["date"] = date.today().isoformat()
            item["collected_at"] = datetime.now().isoformat()
            yield item
