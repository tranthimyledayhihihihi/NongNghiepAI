"""P2-06: Crawler Items - format chuan."""
import scrapy

class MarketPriceItem(scrapy.Item):
    crop_name     = scrapy.Field()
    region        = scrapy.Field()
    price_per_kg  = scrapy.Field()
    source        = scrapy.Field()
    collected_at  = scrapy.Field()
    quality_grade = scrapy.Field()
    market_type   = scrapy.Field()
    unit          = scrapy.Field()
    url           = scrapy.Field()
    date          = scrapy.Field()
