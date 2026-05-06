from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.market_schema import MarketSuggestRequest, MarketSuggestResponse
from app.services.market_service import market_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/channels")
async def get_market_channels():
    return {
        "channels": [
            {"id": "wholesale", "name": "Cho dau moi", "commission": "5-10%"},
            {"id": "retail", "name": "Cho ban le", "commission": "0%"},
            {"id": "supermarket", "name": "Sieu thi/cua hang sach", "commission": "10-15%"},
            {"id": "processor", "name": "Co so che bien", "commission": "0-5%"},
        ]
    }


@router.post("/suggest", response_model=MarketSuggestResponse)
async def suggest_market_channel(
    request: MarketSuggestRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    return market_service.suggest_market(
        db,
        request,
        user_id=current_user.UserID if current_user else None,
    )


@router.get("/history/{user_id}")
async def get_market_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = market_service.get_history(db, user_id, limit)
    return {"user_id": user_id, "total": len(history), "history": history}


@router.get("/demand/{crop_name}")
async def get_market_demand(crop_name: str):
    return {"crop_name": crop_name, "demand": "medium"}
