from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.alert import PriceAlert
from app.repositories.common import ensure_crop, ensure_user, to_db_alert_condition

_memory_alerts: list[PriceAlert] = []
_memory_receivers: dict[int, str] = {}
_memory_next_id = 1

NOTIFY_METHODS = {
    "email": "Email",
    "zalo": "Zalo",
    "sms": "SMS",
    "app": "App",
}


def _store_in_memory(alert: PriceAlert, receiver: str | None = None) -> PriceAlert:
    global _memory_next_id
    alert.AlertID = _memory_next_id
    _memory_next_id += 1
    alert.CreatedAt = datetime.now()
    _memory_alerts.append(alert)
    if receiver:
        _memory_receivers[alert.AlertID] = receiver
    return alert


def create_alert(db: Session, **data) -> PriceAlert:
    receiver = data.pop("receiver", None)
    crop_name = data.pop("crop_name")
    crop = ensure_crop(db, crop_name)
    user = ensure_user(db, receiver=receiver, region=data.get("region"))
    alert = PriceAlert(
        UserID=user.UserID,
        CropID=crop.CropID,
        Region=data["region"],
        TargetPrice=data["target_price"],
        AlertType=to_db_alert_condition(data.get("condition")),
        NotifyMethod=NOTIFY_METHODS.get((data.get("notification_channel") or "email").lower(), "Email"),
        IsActive=data.get("is_active", True),
    )
    alert._crop_name = crop_name
    alert._receiver = receiver
    try:
        db.add(alert)
        db.commit()
        db.refresh(alert)
    except SQLAlchemyError:
        db.rollback()
        _store_in_memory(alert, receiver)
    return alert


def get_alerts(db: Session, active_only: bool = False) -> list[PriceAlert]:
    try:
        query = db.query(PriceAlert)
        if active_only:
            query = query.filter(PriceAlert.IsActive.is_(True))
        return query.order_by(desc(PriceAlert.CreatedAt)).all()
    except SQLAlchemyError:
        db.rollback()
        if active_only:
            return [alert for alert in _memory_alerts if alert.IsActive]
        return list(_memory_alerts)


def get_alert_by_id(db: Session, alert_id: int) -> PriceAlert | None:
    try:
        return db.query(PriceAlert).filter(PriceAlert.AlertID == alert_id).first()
    except SQLAlchemyError:
        db.rollback()
        return next((alert for alert in _memory_alerts if alert.AlertID == alert_id), None)


def deactivate_alert(db: Session, alert_id: int) -> PriceAlert | None:
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        return None
    alert.IsActive = False
    try:
        db.add(alert)
        db.commit()
        db.refresh(alert)
    except SQLAlchemyError:
        db.rollback()
    return alert


def get_alert_receiver(db: Session, alert: PriceAlert) -> str:
    if getattr(alert, "_receiver", None):
        return alert._receiver
    if alert.AlertID in _memory_receivers:
        return _memory_receivers[alert.AlertID]
    try:
        from app.models.user import User

        user = db.query(User).filter(User.UserID == alert.UserID).first()
        if user:
            return user.Email or user.PhoneNumber or user.ZaloID or ""
    except SQLAlchemyError:
        db.rollback()
    return ""


def get_alert_crop_name(db: Session, alert: PriceAlert) -> str:
    if getattr(alert, "_crop_name", None):
        return alert._crop_name
    try:
        from app.models.crop import Crop

        crop = db.query(Crop).filter(Crop.CropID == alert.CropID).first()
        if crop:
            return crop.CropName
    except SQLAlchemyError:
        db.rollback()
    return ""
