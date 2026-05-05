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
                db,
                alert,
                "Canh bao dang hoat dong." if alert.is_active else "Canh bao da tat.",
            )
            for alert in get_alerts(db)
        ]

    def get_price_alert(self, db: Session, alert_id: int) -> dict | None:
        alert = get_alert_by_id(db, alert_id)
        if not alert:
            return None
        message = "Canh bao dang hoat dong." if alert.is_active else "Canh bao da tat."
        return self._to_response(db, alert, message)

    def deactivate_price_alert(self, db: Session, alert_id: int) -> dict | None:
        alert = deactivate_alert(db, alert_id)
        if not alert:
            return None
        return {"alert_id": alert.id, "message": "Da tat canh bao gia."}

    def check_and_trigger_alerts(self, db: Session) -> List[Dict]:
        try:
            from app.models.alert import PriceAlert

            active_alerts = db.query(PriceAlert).filter(PriceAlert.IsActive.is_(True)).all()
            triggered = []
            for alert in active_alerts:
                result = self._evaluate_alert(db, alert)
                if result:
                    triggered.append(result)
            return triggered
        except Exception as exc:
            logger.error("check_and_trigger_alerts error: %s", exc)
            return []

    def _evaluate_alert(self, db: Session, alert) -> Optional[Dict]:
        try:
            from app.models.crop import CropType
            from app.models.price import MarketPrice

            latest = (
                db.query(MarketPrice)
                .filter(
                    MarketPrice.CropID == alert.CropID,
                    MarketPrice.Region == alert.Region,
                )
                .order_by(desc(MarketPrice.PriceDate), desc(MarketPrice.UpdatedAt))
                .first()
            )
            if not latest:
                return None

            current_price = float(latest.PricePerKg)
            target_price = float(alert.TargetPrice)
            condition = to_api_alert_condition(alert.AlertType)
            triggered = (
                (condition == "above" and current_price >= target_price)
                or (condition == "below" and current_price <= target_price)
            )
            if not triggered:
                return None

            crop = db.query(CropType).filter(CropType.CropID == alert.CropID).first()
            crop_name = crop.CropName if crop else get_alert_crop_name(db, alert) or "N/A"

            self._send_alert_notification(
                db=db,
                alert=alert,
                crop_name=crop_name,
                current_price=current_price,
            )

            alert.LastTriggered = datetime.now()
            db.add(alert)
            db.commit()

            return {
                "alert_id": alert.AlertID,
                "crop_name": crop_name,
                "region": alert.Region,
                "current_price": current_price,
                "target_price": target_price,
                "condition": condition,
                "triggered": True,
            }
        except Exception as exc:
            db.rollback()
            logger.error("_evaluate_alert error: %s", exc)
            return None

    @staticmethod
    def _send_alert_notification(db: Session, alert, crop_name: str, current_price: float) -> None:
        try:
            from app.services.notification_service import notification_service

            subject, plain, html = notification_service.build_price_alert_message(
                crop_name=crop_name,
                region=alert.Region,
                current_price=current_price,
                target_price=float(alert.TargetPrice),
                condition=to_api_alert_condition(alert.AlertType),
            )
            receiver = get_alert_receiver(db, alert) or f"user_{alert.UserID}@agriai.vn"
            notification_service.send(
                channel=(alert.NotifyMethod or "email").lower(),
                receiver=receiver,
                subject=subject,
                message=plain,
                html_message=html,
            )
        except Exception as exc:
            logger.error("_send_alert_notification error: %s", exc)

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
