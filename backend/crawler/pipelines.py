# Scrapy pipelines for processing crawled data
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import os

class MarketPricePipeline:
    """Pipeline to save market prices to database"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def open_spider(self, spider):
        """Connect to database when spider opens"""
        database_url = os.getenv('DATABASE_URL', 'postgresql://agriuser:agripass@localhost:5432/agridb')
        self.connection = psycopg2.connect(database_url)
        self.cursor = self.connection.cursor()
    
    def close_spider(self, spider):
        """Close database connection when spider closes"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def process_item(self, item, spider):
        """Process and save item to database"""
        try:
            self.cursor.execute("""
                INSERT INTO market_prices (
                    crop_name, region, price_per_kg, quality_grade,
                    market_type, source, date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                item.get('crop_name'),
                item.get('region'),
                item.get('price_per_kg'),
                item.get('quality_grade', 'grade_1'),
                item.get('market_type', 'wholesale'),
                item.get('source'),
                item.get('date', datetime.now().date())
            ))
            self.connection.commit()
        except Exception as e:
            spider.logger.error(f"Error saving item: {e}")
            self.connection.rollback()
        
        return item

class DataCleaningPipeline:
    """Pipeline to clean and validate data"""
    
    def process_item(self, item, spider):
        """Clean and validate item data"""
        # Clean crop name
        if 'crop_name' in item:
            item['crop_name'] = item['crop_name'].strip()
        
        # Clean region
        if 'region' in item:
            item['region'] = item['region'].strip()
        
        # Validate price
        if 'price_per_kg' in item:
            try:
                item['price_per_kg'] = float(item['price_per_kg'])
                if item['price_per_kg'] <= 0:
                    raise ValueError("Price must be positive")
            except (ValueError, TypeError):
                spider.logger.warning(f"Invalid price: {item.get('price_per_kg')}")
                return None
        
        return item
