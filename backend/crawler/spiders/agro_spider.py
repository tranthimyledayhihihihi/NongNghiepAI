import scrapy
from datetime import datetime

class AgroSpider(scrapy.Spider):
    name = "agro_spider"
    allowed_domains = ["giacaphe.com", "giatieu.com"] # Đổi domain thực tế
    start_urls = ["https://giacaphe.com/gia-ca-phe-noi-dia/"]

    custom_settings = {
        'ITEM_PIPELINES': {'crawler.pipelines.DatabasePipeline': 300}
    }

    def parse(self, response):
        # Chú ý: Selector thực tế phụ thuộc vào cấu trúc DOM của trang web đích
        # Ví dụ xpath giả định lấy bảng giá
        rows = response.xpath('//table[@id="gianoidia"]/tbody/tr')
        
        for row in rows:
            region = row.xpath('.//td[1]/text()').get()
            price_str = row.xpath('.//td[2]/text()').get()
            
            if region and price_str:
                # Clean data
                price = float(price_str.replace(',', '').replace('.', '').strip())
                
                yield {
                    "crop_name": "Cà phê",
                    "region": region.strip(),
                    "price": price,
                    "unit": "VND/kg",
                    "source": response.url,
                    "collected_at": datetime.now().isoformat()
                }