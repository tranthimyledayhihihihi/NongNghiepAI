import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.repositories.alert_repository import (
    create_alert,
    deactivate_alert,
    get_alert_by_id,
    get_alert_crop_name,
    get_alert_receiver,
    get_alerts,
)
from app.repositories.common import to_api_alert_condition
from app.schemas.alert_schema import AlertCreateRequest

logger = logging.getLogger(__name__)


class AlertService:

    # ------------------------------------------------------------------ #
    # API interface (dùng bởi alert.py endpoints)
    # ------------------------------------------------------------------ #

    def create_price_alert(self, db: Session, request: AlertCreateRequest) -> dict:
        alert = create_alert(
            db,
            crop_name=request.crop_name,
            region=request.region,
            target_price=request.target_price,
            condition=request.condition,
            notification_channel=request.notification_channel,
            receiver=request.receiver,
            is_active=True,
        )
        return self._to_response(db, alert, "Tao canh bao gia thanh cong.")

    def list_price_alerts(self, db: Session) -> list[dict]:
        return [
            self._to_response(
                db, alert,
                "Canh bao dang hoat dong." if alert.is_active else "Canh bao da tat.",
            )
            for alert in get_alerts(db)
        ]

    def get_price_alert(self, db: Session, alert_id: int) -> dict | None:
        alert = get_alert_by_id(db, alert_id)
        if not alert:
            return None
        status_msg = "Canh bao dang hoat dong." if alert.is_active else "Canh bao da tat."
        return self._to_response(db, alert, status_msg)

    def deactivate_price_alert(self, db: Session, alert_id: int) -> dict | None:
        alert = deactivate_alert(db, alert_id)
        if not alert:
            return None
        return {"alert_id": alert.id, "message": "Da tat canh bao gia."}

    def check_and_trigger_alerts(self, db: Session) -> list[dict]:
        from app.models.alert import PriceAlert

        try:
            alerts = db.query(PriceAlert).filter(PriceAlert.IsActive == True).all()
        except Exception as exc:
            logger.warning("Cannot load active price alerts: %s", exc)
            return []

        triggered = []
        for alert in alerts:
            result = self._evaluate_alert(db, alert)
            if result:
                triggered.append(result)
        return triggered

    def _evaluate_alert(self, db: Session, alert) -> dict | None:
        from app.models.price import MarketPrice

        crop_id = getattr(alert, "CropID", getattr(alert, "crop_id", None))
        region = getattr(alert, "Region", getattr(alert, "region", ""))
        latest = (
            db.query(MarketPrice)
            .filter(MarketPrice.CropID == crop_id, MarketPrice.Region == region)
            .order_by(desc(MarketPrice.PriceDate))
            .first()
        )
        if not latest:
            return None

        current_price = float(getattr(latest, "PricePerKg", getattr(latest, "price_per_kg", 0)))
        target_price = float(getattr(alert, "TargetPrice", getattr(alert, "target_price", 0)))
        raw_condition = getattr(alert, "AlertType", getattr(alert, "condition", ""))
        condition = str(raw_condition or "").strip().lower()
        is_above = condition in {">", ">=", "above"} or condition.startswith("tr")
        is_below = condition in {"<", "<=", "below"} or condition.startswith("du") or condition.startswith("dư")

        if is_above:
            matched = current_price >= target_price
        elif is_below:
            matched = current_price <= target_price
        else:
            matched = False

        if not matched:
            return None

        result = {
            "alert_id": getattr(alert, "AlertID", getattr(alert, "id", None)),
            "crop_name": get_alert_crop_name(db, alert),
            "region": region,
            "target_price": target_price,
            "current_price": current_price,
            "condition": to_api_alert_condition(raw_condition),
            "triggered": True,
            "triggered_at": datetime.now(),
        }
        self._send_alert_notification(db, alert, result)
        try:
            alert.LastTriggered = result["triggered_at"]
            db.add(alert)
            db.commit()
        except Exception:
            db.rollback()
        return result

    def _send_alert_notification(self, db: Session, alert, payload: dict):
        from app.services.notification_service import notification_service

        channel = (getattr(alert, "NotifyMethod", getattr(alert, "notification_channel", "Email")) or "Email").lower()
        receiver = get_alert_receiver(db, alert)
        if not receiver:
            return None
        subject, plain, html = notification_service.build_price_alert_message(
            crop_name=payload.get("crop_name") or "Nong san",
            region=payload.get("region") or "",
            current_price=payload.get("current_price") or 0,
            target_price=payload.get("target_price") or 0,
            condition=payload.get("condition") or "",
        )
        return notification_service.send(channel, receiver, subject, plain, html)

    @staticmethod
    def _to_response(db: Session, alert, message: str) -> dict:
        return {
            "alert_id": alert.id,
            "crop_name": get_alert_crop_name(db, alert),
            "region": alert.region,
            "target_price": float(alert.target_price),
            "condition": to_api_alert_condition(alert.condition),
            "notification_channel": (alert.notification_channel or "Email").lower(),
            "receiver": get_alert_receiver(db, alert),
            "is_active": bool(alert.is_active),
            "message": message,
            "created_at": getattr(alert, "created_at", None),
        }


alert_service = AlertService()
