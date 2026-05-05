from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.user import User


GRADE_API_TO_DB = {
    "grade_1": "Loại 1",
    "grade_2": "Loại 2",
    "grade_3": "Loại 3",
    "loai_1": "Loại 1",
    "loai_2": "Loại 2",
    "loai_3": "Loại 3",
    "loại 1": "Loại 1",
    "loại 2": "Loại 2",
    "loại 3": "Loại 3",
    "loai 1": "Loại 1",
    "loai 2": "Loại 2",
    "loai 3": "Loại 3",
}

GRADE_DB_TO_API = {
    "Loại 1": "grade_1",
    "Loại 2": "grade_2",
    "Loại 3": "grade_3",
}

ALERT_API_TO_DB = {
    "above": "Trên",
    "below": "Dưới",
    "change": "Thay đổi",
    "Trên": "Trên",
    "Dưới": "Dưới",
    "Thay đổi": "Thay đổi",
}

ALERT_DB_TO_API = {
    "Trên": "above",
    "Dưới": "below",
    "Thay đổi": "change",
}

CHANNEL_API_TO_DB = {
    "retail": "Thương lái",
    "wholesale": "Chợ đầu mối",
    "supermarket": "Chợ đầu mối",
    "processor": "Thương lái",
    "export": "Xuất khẩu",
}


def to_db_grade(value: str | None) -> str:
    if not value:
        return "Loại 1"
    return GRADE_API_TO_DB.get(value.strip().lower(), value)


def to_api_grade(value: str | None) -> str:
    if not value:
        return "grade_1"
    return GRADE_DB_TO_API.get(value, value)


def to_db_alert_condition(value: str | None) -> str:
    if not value:
        return "Trên"
    return ALERT_API_TO_DB.get(value, value)


def to_api_alert_condition(value: str | None) -> str:
    if not value:
        return "above"
    return ALERT_DB_TO_API.get(value, value)


def to_db_channel(value: str | None) -> str:
    if not value:
        return "Thương lái"
    return CHANNEL_API_TO_DB.get(value, value)


def ensure_crop(db: Session, crop_name: str) -> Crop:
    try:
        crop = db.query(Crop).filter(Crop.CropName == crop_name).first()
        if crop:
            return crop
        crop = Crop(
            CropName=crop_name,
            Category="Khác",
            GrowthDurationDays=70,
            TypicalPriceMin=10000,
            TypicalPriceMax=30000,
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop
    except SQLAlchemyError:
        db.rollback()
        crop = Crop(CropName=crop_name, Category="Khác", GrowthDurationDays=70)
        crop.CropID = 1
        return crop


def ensure_user(db: Session, receiver: str | None = None, region: str | None = None) -> User:
    try:
        query = db.query(User)
        if receiver:
            query = query.filter(
                or_(
                    User.Email == receiver,
                    User.PhoneNumber == receiver,
                    User.ZaloID == receiver,
                )
            )
            user = query.first()
            if user:
                return user
        if not receiver:
            user = db.query(User).order_by(User.UserID).first()
            if user:
                return user
        user = User(
            FullName="API User",
            Email=receiver if receiver and "@" in receiver else None,
            PhoneNumber=receiver if receiver and "@" not in receiver else None,
            PasswordHash="mock-password",
            Role="farmer",
            Region=region,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        user = User(
            FullName="API User",
            Email=receiver if receiver and "@" in receiver else None,
            PhoneNumber=receiver if receiver and "@" not in receiver else None,
            PasswordHash="mock-password",
            Role="farmer",
            Region=region,
        )
        user.UserID = 1
        return user
