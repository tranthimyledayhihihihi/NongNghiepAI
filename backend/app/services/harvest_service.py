from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from ..models.crop import CropType, HarvestSchedule

class HarvestService:
    """Service for harvest operations"""
    
    @staticmethod
    def predict_harvest_date(
        db: Session,
        crop_name: str,
        planting_date: datetime,
        region: str
    ) -> Optional[Dict]:
        """Predict harvest date based on crop type and planting date"""
        
        # Get crop info
        crop = db.query(CropType).filter(
            CropType.name == crop_name
        ).first()
        
        if not crop or not crop.avg_growth_days:
            return None
        
        # Calculate predicted harvest date
        predicted_date = planting_date + timedelta(days=crop.avg_growth_days)
        
        # TODO: Integrate weather data and Prophet model in Phase 2
        
        return {
            "crop_name": crop_name,
            "region": region,
            "planting_date": planting_date.isoformat(),
            "predicted_harvest_date": predicted_date.isoformat(),
            "growth_days": crop.avg_growth_days,
            "confidence": 0.85,
            "recommendations": [
                f"Dự kiến thu hoạch sau {crop.avg_growth_days} ngày",
                "Theo dõi thời tiết để điều chỉnh kế hoạch",
                "Chuẩn bị nhân lực trước 1 tuần"
            ]
        }
    
    @staticmethod
    def create_harvest_schedule(
        db: Session,
        crop_type_id: int,
        region: str,
        planting_date: datetime,
        predicted_harvest_date: datetime,
        quantity_kg: Optional[float] = None,
        notes: Optional[str] = None
    ) -> HarvestSchedule:
        """Create a new harvest schedule"""
        
        schedule = HarvestSchedule(
            crop_type_id=crop_type_id,
            region=region,
            planting_date=planting_date,
            predicted_harvest_date=predicted_harvest_date,
            quantity_kg=quantity_kg,
            notes=notes
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        return schedule

harvest_service = HarvestService()
