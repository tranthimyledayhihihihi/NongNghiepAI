#!/usr/bin/env python3
"""
Initialize database with sample data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date, timedelta
from backend.app.core.database import SessionLocal, init_db
from backend.app.models.price import MarketPrice, PriceHistory
from backend.app.models.crop import CropType, HarvestSchedule
import random

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        print("🌱 Creating sample data...")
        
        # Create crop types
        crops = [
            CropType(name="Cà chua", name_en="Tomato", category="vegetable", avg_growth_days=75),
            CropType(name="Dưa chuột", name_en="Cucumber", category="vegetable", avg_growth_days=60),
            CropType(name="Rau muống", name_en="Water spinach", category="vegetable", avg_growth_days=30),
            CropType(name="Cải xanh", name_en="Bok choy", category="vegetable", avg_growth_days=45),
            CropType(name="Ớt", name_en="Chili", category="vegetable", avg_growth_days=90),
        ]
        
        for crop in crops:
            existing = db.query(CropType).filter(CropType.name == crop.name).first()
            if not existing:
                db.add(crop)
        
        db.commit()
        print("✓ Created crop types")
        
        # Create sample market prices
        regions = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]
        grades = ["grade_1", "grade_2", "grade_3"]
        
        for crop in crops:
            for region in regions:
                for grade in grades:
                    # Create prices for last 30 days
                    for i in range(30):
                        price_date = date.today() - timedelta(days=i)
                        base_price = random.randint(15000, 30000)
                        
                        # Adjust by grade
                        if grade == "grade_2":
                            base_price *= 0.7
                        elif grade == "grade_3":
                            base_price *= 0.4
                        
                        price = MarketPrice(
                            crop_name=crop.name,
                            region=region,
                            price_per_kg=base_price,
                            quality_grade=grade,
                            market_type="wholesale",
                            source="sample_data",
                            date=price_date
                        )
                        db.add(price)
        
        db.commit()
        print("✓ Created market prices")
        
        # Create price history
        for crop in crops:
            for region in regions:
                for i in range(30):
                    history_date = date.today() - timedelta(days=i)
                    avg_price = random.randint(15000, 30000)
                    
                    history = PriceHistory(
                        crop_name=crop.name,
                        region=region,
                        avg_price=avg_price,
                        min_price=avg_price * 0.9,
                        max_price=avg_price * 1.1,
                        date=history_date
                    )
                    db.add(history)
        
        db.commit()
        print("✓ Created price history")
        
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_db()
    print("✓ Database tables created")
    
    create_sample_data()
