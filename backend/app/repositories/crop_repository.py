from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.repositories.common import ensure_crop


DEFAULT_CROPS = [
    {
        "CropName": "ca chua",
        "CropNameEN": "Tomato",
        "Category": "rau qua",
        "GrowthDurationDays": 75,
        "HarvestSeason": "quanh nam",
        "TypicalPriceMin": 18000,
        "TypicalPriceMax": 26000,
        "Description": "Cay rau qua ngan ngay, phu hop nhieu vung trong.",
        "ImageURL": None,
    },
    {
        "CropName": "dua chuot",
        "CropNameEN": "Cucumber",
        "Category": "rau qua",
        "GrowthDurationDays": 60,
        "HarvestSeason": "quanh nam",
        "TypicalPriceMin": 14000,
        "TypicalPriceMax": 22000,
        "Description": "Cay ngan ngay, thu hoach nhanh va can tieu thu som.",
        "ImageURL": None,
    },
    {
        "CropName": "rau muong",
        "CropNameEN": "Water spinach",
        "Category": "rau an la",
        "GrowthDurationDays": 30,
        "HarvestSeason": "quanh nam",
        "TypicalPriceMin": 7000,
        "TypicalPriceMax": 12000,
        "Description": "Rau an la pho bien, chu ky canh tac ngan.",
        "ImageURL": None,
    },
    {
        "CropName": "cai xanh",
        "CropNameEN": "Mustard greens",
        "Category": "rau an la",
        "GrowthDurationDays": 45,
        "HarvestSeason": "dong xuan",
        "TypicalPriceMin": 9000,
        "TypicalPriceMax": 16000,
        "Description": "Rau an la phu hop khi hau mat, gia bien dong theo mua.",
        "ImageURL": None,
    },
    {
        "CropName": "ot",
        "CropNameEN": "Chili",
        "Category": "gia vi",
        "GrowthDurationDays": 90,
        "HarvestSeason": "quanh nam",
        "TypicalPriceMin": 22000,
        "TypicalPriceMax": 38000,
        "Description": "Cay gia vi co gia tri cao, nhay cam voi thoi tiet.",
        "ImageURL": None,
    },
    {
        "CropName": "lua",
        "CropNameEN": "Rice",
        "Category": "ngu coc",
        "GrowthDurationDays": 105,
        "HarvestSeason": "dong xuan, he thu",
        "TypicalPriceMin": 7500,
        "TypicalPriceMax": 11000,
        "Description": "Cay luong thuc chu luc, gia phu thuoc chat luong va khu vuc.",
        "ImageURL": None,
    },
]


def _default_crop_objects() -> list[Crop]:
    return [
        Crop(CropID=index, **seed)
        for index, seed in enumerate(DEFAULT_CROPS, start=1)
    ]


def seed_default_crops(db: Session) -> list[Crop]:
    """Ensure the local MVP database has crop options for the frontend."""
    try:
        existing_names = {name for (name,) in db.query(Crop.CropName).all()}
        missing = [
            Crop(**seed)
            for seed in DEFAULT_CROPS
            if seed["CropName"] not in existing_names
        ]
        if missing:
            db.add_all(missing)
            db.commit()
        return db.query(Crop).order_by(Crop.CropName).all()
    except SQLAlchemyError:
        db.rollback()
        return _default_crop_objects()


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


def get_crop_by_id(db: Session, crop_id: int) -> Crop | None:
    try:
        crop = db.query(Crop).filter(Crop.CropID == crop_id).first()
        if crop:
            return crop
        seed_default_crops(db)
        return db.query(Crop).filter(Crop.CropID == crop_id).first()
    except SQLAlchemyError:
        db.rollback()
        return next((crop for crop in _default_crop_objects() if crop.CropID == crop_id), None)


def list_crops(db: Session) -> list[Crop]:
    try:
        crops = db.query(Crop).order_by(Crop.CropName).all()
        return crops or seed_default_crops(db)
    except SQLAlchemyError:
        db.rollback()
        return _default_crop_objects()


def search_crops(db: Session, keyword: str) -> list[Crop]:
    try:
        pattern = f"%{keyword.strip()}%"
        crops = (
            db.query(Crop)
            .filter((Crop.CropName.ilike(pattern)) | (Crop.CropNameEN.ilike(pattern)))
            .order_by(Crop.CropName)
            .all()
        )
        if crops:
            return crops
        seed_default_crops(db)
        return (
            db.query(Crop)
            .filter((Crop.CropName.ilike(pattern)) | (Crop.CropNameEN.ilike(pattern)))
            .order_by(Crop.CropName)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        normalized_keyword = keyword.strip().lower()
        return [
            crop
            for crop in _default_crop_objects()
            if normalized_keyword in crop.CropName.lower()
            or normalized_keyword in (crop.CropNameEN or "").lower()
        ]
