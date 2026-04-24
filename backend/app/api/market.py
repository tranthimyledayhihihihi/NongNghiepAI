from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/channels")
async def get_market_channels():
    """Get available market channels - Phase 2"""
    return {
        "channels": [
            {
                "id": "wholesale",
                "name": "Chợ đầu mối",
                "description": "Bán buôn số lượng lớn",
                "commission": "5-10%"
            },
            {
                "id": "retail",
                "name": "Chợ bán lẻ",
                "description": "Bán lẻ trực tiếp",
                "commission": "0%"
            },
            {
                "id": "export",
                "name": "Xuất khẩu",
                "description": "Xuất khẩu ra nước ngoài",
                "commission": "15-20%"
            }
        ]
    }

@router.post("/suggest")
async def suggest_market_channel(
    crop_name: str,
    quantity_kg: float,
    quality_grade: str,
    db: Session = Depends(get_db)
):
    """Suggest best market channel - Phase 2"""
    return {
        "message": "Market channel suggestion feature coming in Phase 2",
        "crop_name": crop_name,
        "quantity_kg": quantity_kg,
        "quality_grade": quality_grade,
        "suggestions": []
    }

@router.get("/demand/{crop_name}")
async def get_market_demand(crop_name: str):
    """Get market demand forecast - Phase 2"""
    return {
        "message": "Market demand feature coming in Phase 2",
        "crop_name": crop_name,
        "demand": "medium"
    }
