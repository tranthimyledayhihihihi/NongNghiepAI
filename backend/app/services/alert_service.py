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
