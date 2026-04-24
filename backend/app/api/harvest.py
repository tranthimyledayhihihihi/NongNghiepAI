from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.services.harvest_service import harvest_service

router = APIRouter(prefix="/api/harvest", tags=["harvest"])

@router.post("/predict")
async def predict_harvest(
    crop_name: str,
    planting_date: str,
    region: str,
    db: Session = Depends(get_db)
):
    """
    Predict harvest date - Basic implementation
    Full Prophet model integration in Phase 2
    """
    try:
        planting_dt = datetime.fromisoformat(planting_date)
        result = harvest_service.predict_harvest_date(
            db=db,
            crop_name=crop_name,
            planting_date=planting_dt,
            region=region
        )
        
        if not result:
            return {
                "message": "Crop not found or insufficient data",
                "status": "error"
            }
        
        return result
    
    except Exception as e:
        return {
            "message": f"Error predicting harvest: {str(e)}",
            "status": "error"
        }

@router.get("/schedule")
async def get_harvest_schedule(db: Session = Depends(get_db)):
    """Get harvest schedule - Phase 2"""
    return {
        "message": "Harvest schedule feature coming in Phase 2",
        "schedules": []
    }
