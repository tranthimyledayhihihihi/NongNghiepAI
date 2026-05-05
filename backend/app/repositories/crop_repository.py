from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.repositories.common import ensure_crop


def create_crop(db: Session, *, name: str, category: str | None = None, default_unit: str = "kg") -> Crop:
    try:
        crop = Crop(CropName=name, Category=category or "Khác")
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop
    except SQLAlchemyError:
        db.rollback()
        return ensure_crop(db, name)


def get_crop_by_name(db: Session, name: str) -> Crop | None:
    try:
        return db.query(Crop).filter(Crop.CropName == name).first()
    except SQLAlchemyError:
        db.rollback()
        return None


def list_crops(db: Session) -> list[Crop]:
    try:
        return db.query(Crop).order_by(Crop.CropName).all()
    except SQLAlchemyError:
        db.rollback()
        return []
