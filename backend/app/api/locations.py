from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.response import api_response
from app.core.database import get_db
from app.services.location_service import location_service

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
async def list_locations(db: Session = Depends(get_db)):
    locations = location_service.list_locations(db)
    return api_response({"total": len(locations), "locations": locations})


@router.get("/")
async def list_locations_with_slash(db: Session = Depends(get_db)):
    locations = location_service.list_locations(db)
    return api_response({"total": len(locations), "locations": locations})
