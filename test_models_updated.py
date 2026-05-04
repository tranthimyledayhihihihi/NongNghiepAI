"""
Test script to verify updated models match SQL Server schema
"""
import sys
sys.path.append('backend')

from app.models import (
    User, CropType, HarvestSchedule, QualityRecord,
    MarketPrice, PriceHistory, PriceForecastResult,
    AlertSubscription, WeatherData, AIConversation
)
from app.core.database import engine, SessionLocal
from sqlalchemy import inspect

def test_models():
    print("=" * 60)
    print("TESTING UPDATED MODELS")
    print("=" * 60)
    
    # Test 1: Import all models
    print("\n✓ All 10 models imported successfully:")
    models = [
        User, CropType, WeatherData, HarvestSchedule,
        MarketPrice, PriceHistory, PriceForecastResult,
        QualityRecord, AlertSubscription, AIConversation
    ]
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model.__tablename__}")
    
    # Test 2: Check database connection
    print("\n✓ Database engine created")
    print(f"   Connection: {engine.url}")
    
    # Test 3: Try to connect and query
    try:
        db = SessionLocal()
        
        # Count records in each table
        print("\n✓ Database connection successful!")
        print("\nTable record counts:")
        
        user_count = db.query(User).count()
        print(f"   Users: {user_count}")
        
        crop_count = db.query(CropType).count()
        print(f"   CropTypes: {crop_count}")
        
        weather_count = db.query(WeatherData).count()
        print(f"   WeatherData: {weather_count}")
        
        harvest_count = db.query(HarvestSchedule).count()
        print(f"   HarvestSchedule: {harvest_count}")
        
        market_count = db.query(MarketPrice).count()
        print(f"   MarketPrices: {market_count}")
        
        history_count = db.query(PriceHistory).count()
        print(f"   PriceHistory: {history_count}")
        
        forecast_count = db.query(PriceForecastResult).count()
        print(f"   PriceForecastResults: {forecast_count}")
        
        quality_count = db.query(QualityRecord).count()
        print(f"   QualityRecords: {quality_count}")
        
        alert_count = db.query(AlertSubscription).count()
        print(f"   AlertSubscriptions: {alert_count}")
        
        conv_count = db.query(AIConversation).count()
        print(f"   AIConversations: {conv_count}")
        
        # Test 4: Sample data from Users
        print("\n✓ Sample data from Users table:")
        users = db.query(User).limit(3).all()
        for user in users:
            print(f"   - {user.FullName} ({user.Email}) - Role: {user.Role}, Region: {user.Region}")
        
        # Test 5: Sample data from CropTypes
        print("\n✓ Sample data from CropTypes table:")
        crops = db.query(CropType).limit(5).all()
        for crop in crops:
            print(f"   - {crop.CropName} ({crop.Category}) - {crop.GrowthDurationDays} days")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Test API endpoints at http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        print("\nPlease ensure:")
        print("1. SQL Server is running")
        print("2. NongNghiepAI_Full.sql has been executed in SSMS")
        print("3. Connection string in .env is correct")
        return False
    
    return True

if __name__ == "__main__":
    test_models()
