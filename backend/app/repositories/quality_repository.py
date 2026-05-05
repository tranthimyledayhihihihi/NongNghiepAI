import json

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.quality import QualityCheck
from app.repositories.common import ensure_crop, ensure_user, to_db_grade


def create_quality_check(
    db: Session,
    *,
    crop_name: str,
    region: str,
    image_path: str,
    quality_grade: str,
    disease_detected: bool,
    damage_level: str,
    suggested_price: float,
    confidence: float,
) -> QualityCheck:
    crop = ensure_crop(db, crop_name)
    user = ensure_user(db, region=region)
    detected_issues = {
        "disease_detected": disease_detected,
        "damage_level": damage_level,
    }
    quality_check = QualityCheck(
        UserID=user.UserID,
        CropID=crop.CropID,
        ImagePath=image_path,
        AIGrade=to_db_grade(quality_grade),
        ConfidenceScore=confidence,
        DetectedIssues=json.dumps(detected_issues, ensure_ascii=False),
        SuggestedPriceMin=round(suggested_price * 0.92, 2),
        SuggestedPriceMax=round(suggested_price * 1.08, 2),
        Recommendation="Kết quả mock, người 2 có thể thay bằng YOLO detector.",
    )
    try:
        db.add(quality_check)
        db.commit()
        db.refresh(quality_check)
    except SQLAlchemyError:
        db.rollback()
    return quality_check


def get_quality_checks(
    db: Session,
    crop_name: str | None = None,
    region: str | None = None,
    limit: int = 20,
) -> list[QualityCheck]:
    try:
        query = db.query(QualityCheck)
        if crop_name:
            crop = ensure_crop(db, crop_name)
            query = query.filter(QualityCheck.CropID == crop.CropID)
        return query.order_by(desc(QualityCheck.CheckDate)).limit(limit).all()
    except SQLAlchemyError:
        db.rollback()
        return []
