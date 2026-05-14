# Scrapy settings for crawler project

BOT_NAME = 'agri_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Crawl responsibly
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2

# User agent
USER_AGENT = 'AgriAI Price Crawler (+http://agriai.vn)'

# Pipelines
ITEM_PIPELINES = {
    'crawler.pipelines.DataCleaningPipeline': 100,
    'crawler.pipelines.MarketPricePipeline': 300,
}

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler.log'

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# HTTP Cache
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
