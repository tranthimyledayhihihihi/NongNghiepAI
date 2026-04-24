# Scrapy items for data crawling
import scrapy

class MarketPriceItem(scrapy.Item):
    """Item for market price data"""
    crop_name = scrapy.Field()
    region = scrapy.Field()
    price_per_kg = scrapy.Field()
    quality_grade = scrapy.Field()
    market_type = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()
