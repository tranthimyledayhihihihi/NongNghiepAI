import asyncio
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.quality_schema import QualityCheckResponse
from app.services.quality_service import quality_service

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.post("/check", response_model=QualityCheckResponse)
async def check_quality(
    image: UploadFile | None = File(None),
    file: UploadFile | None = File(None),
    crop_name: str = Form(""),
    region: str = Form("Đà Nẵng"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    upload = image or file
    if upload is None:
        raise HTTPException(status_code=400, detail="image file is required")
    if upload.content_type and not upload.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="file must be an image")

    upload_dir = Path(settings.UPLOAD_DIR) / "quality_check"
    upload_dir.mkdir(parents=True, exist_ok=True)
    extension = Path(upload.filename or "").suffix or ".jpg"
    file_path = upload_dir / f"{uuid.uuid4()}{extension}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    return await asyncio.to_thread(
        quality_service.check_quality,
        db,
        image_path=str(file_path),
        crop_name=crop_name,
        region=region,
        user_id=current_user.UserID if current_user else None,
    )


@router.get("/grades")
async def get_quality_grades():
    return {
        "grades": [
            {
                "grade": "grade_1",
                "name": "Loại 1",
                "description": "Chất lượng cao, không khuyết tật rõ ràng",
                "price_multiplier": 1.0,
            },
            {
                "grade": "grade_2",
                "name": "Loại 2",
                "description": "Chất lượng trung bình, có khuyết tật nhẹ",
                "price_multiplier": 0.82,
            },
            {
                "grade": "grade_3",
                "name": "Loại 3",
                "description": "Chất lượng thấp, cần bán nhanh hoặc chế biến",
                "price_multiplier": 0.58,
            },
        ]
    }


@router.get("/history/{user_id}")
async def get_quality_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    history = quality_service.get_history(db, user_id, limit)
    return {"user_id": user_id, "total": len(history), "history": history}


@router.get("/{record_id}")
async def get_quality_detail(record_id: int, db: Session = Depends(get_db)):
    record = quality_service.get_detail(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="quality record not found")
    return record
