from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.crop import Crop
from app.repositories.crop_repository import get_crop_by_id, list_crops, search_crops

router = APIRouter(prefix="/api/crops", tags=["crops"])


def _crop_to_dict(crop: Crop) -> dict:
    return {
        "crop_id": crop.id,
        "crop_name": crop.name,
        "crop_name_en": crop.crop_name_en,
        "category": crop.category,
        "growth_duration_days": crop.growth_duration_days,
        "harvest_season": crop.harvest_season,
        "typical_price_min": crop.typical_price_min,
        "typical_price_max": crop.typical_price_max,
        "description": crop.description,
        "image_url": crop.image_url,
        "default_unit": crop.default_unit,
        "created_at": crop.created_at,
    }


@router.get("")
async def get_crops(db: Session = Depends(get_db)):
    crops = [_crop_to_dict(crop) for crop in list_crops(db)]
    return {"total": len(crops), "crops": crops}


@router.get("/")
async def get_crops_with_slash(db: Session = Depends(get_db)):
    crops = [_crop_to_dict(crop) for crop in list_crops(db)]
    return {"total": len(crops), "crops": crops}


@router.get("/search")
async def search_crop_types(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    crops = [_crop_to_dict(crop) for crop in search_crops(db, keyword)]
    return {"keyword": keyword, "total": len(crops), "crops": crops}


@router.get("/{crop_id}")
async def get_crop_detail(crop_id: int, db: Session = Depends(get_db)):
    crop = get_crop_by_id(db, crop_id)
    if crop is None:
        raise HTTPException(status_code=404, detail="crop not found")
    return _crop_to_dict(crop)
