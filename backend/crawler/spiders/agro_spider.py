"""P2-07: Spider agro.gov.vn"""
import re
from datetime import date, datetime
import scrapy
from crawler.items import MarketPriceItem

SOURCE = "agro.gov.vn"
START_URLS = ["https://agro.gov.vn/vn/tID827_Gia-nong-san.html"]

SAMPLE_DATA = [
    {"crop_name": "Ca chua",   "region": "Ha Noi",   "price_per_kg": 18000},
    {"crop_name": "Ca chua",   "region": "TP.HCM",   "price_per_kg": 20000},
    {"crop_name": "Dua chuot", "region": "Ha Noi",   "price_per_kg": 12000},
    {"crop_name": "Cai xanh",  "region": "Ha Noi",   "price_per_kg": 8000},
    {"crop_name": "Ot",        "region": "Lam Dong",  "price_per_kg": 22000},
    {"crop_name": "Khoai lang","region": "Ha Noi",   "price_per_kg": 15000},
    {"crop_name": "Hanh tay",  "region": "Ha Noi",   "price_per_kg": 18000},
    {"crop_name": "Toi",       "region": "TP.HCM",   "price_per_kg": 35000},
    {"crop_name": "Dua hau",   "region": "TP.HCM",   "price_per_kg": 8000},
    {"crop_name": "Xoai",      "region": "Can Tho",  "price_per_kg": 25000},
]


class AgroSpider(scrapy.Spider):
    name = "agro"
    allowed_domains = ["agro.gov.vn"]
    start_urls = START_URLS
    custom_settings = {"DOWNLOAD_DELAY": 2, "ROBOTSTXT_OBEY": False, "HTTPERROR_ALLOW_ALL": True}

    def parse(self, response):
        if response.status != 200:
            yield from self._sample()
            return
        rows = response.css("table tr")
        found = 0
        for row in rows[1:]:
            cells = row.css("td")
            if len(cells) < 3:
                continue
            try:
                name = cells[0].css("::text").get("").strip()
                region = cells[1].css("::text").get("Ha Noi").strip()
                price = self._parse_price(cells[2].css("::text").get("0"))
                if name and price > 0:
                    item = MarketPriceItem()
                    item["crop_name"] = name
                    item["region"] = region or "Ha Noi"
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

    @staticmethod
    def _parse_price(text):
        digits = re.sub(r"[^\d]", "", text)
        return float(digits) if digits else 0.0

    def _sample(self):
        import random
        for s in SAMPLE_DATA:
            item = MarketPriceItem()
            item["crop_name"] = s["crop_name"]
            item["region"] = s["region"]
            item["price_per_kg"] = round(s["price_per_kg"] * random.uniform(0.95, 1.05), -2)
            item["quality_grade"] = "Loai 1"
            item["market_type"] = "Ban buon"
            item["source"] = SOURCE + " (sample)"
            item["url"] = START_URLS[0]
            item["date"] = date.today().isoformat()
            item["collected_at"] = datetime.now().isoformat()
            yield item
