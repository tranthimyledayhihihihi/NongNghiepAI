"""
Alert Service - merged Tien (API interface + repositories) + Quang (business logic)
- API endpoints dùng: create_price_alert, list_price_alerts, deactivate_price_alert
- Task/scheduler dùng: check_and_trigger_alerts
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.repositories.alert_repository import (
    create_alert,
    deactivate_alert,
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

    def deactivate_price_alert(self, db: Session, alert_id: int) -> dict | None:
        alert = deactivate_alert(db, alert_id)
        if not alert:
            return None
        return {"alert_id": alert.id, "message": "Da tat canh bao gia."}

    # ------------------------------------------------------------------ #
    # Business logic - kiểm tra và kích hoạt cảnh báo (Quang)
    # ------------------------------------------------------------------ #

    def check_and_trigger_alerts(self, db: Session) -> List[Dict]:
        """Chạy toàn bộ alert đang active, kiểm tra điều kiện giá, gửi thông báo nếu thỏa."""
        try:
            from app.models.alert import AlertSubscription

            active_alerts = (
                db.query(AlertSubscription)
                .filter(AlertSubscription.IsActive == True)  # noqa: E712
                .all()
            )
            triggered = []
            for alert in active_alerts:
                result = self._evaluate_alert(db, alert)
                if result:
                    triggered.append(result)
            return triggered
        except Exception as exc:
            logger.error(f"check_and_trigger_alerts error: {exc}")
            return []

    def _evaluate_alert(self, db: Session, alert) -> Optional[Dict]:
        """Kiểm tra một alert: so sánh giá mới nhất với target_price."""
        try:
            from app.models.alert import AlertSubscription
            from app.models.crop import CropType
            from app.models.price import MarketPrice

            latest = (
                db.query(MarketPrice)
                .filter(
                    MarketPrice.CropID == alert.CropID,
                    MarketPrice.Region == alert.Region,
                )
                .order_by(desc(MarketPrice.PriceDate))
                .first()
            )
            if not latest:
                return None

            current_price = float(latest.PricePerKg)
            target = float(alert.TargetPrice)
            condition = (alert.AlertType or "Trên").strip()

            triggered = (
                (condition in ("Trên", "above", ">") and current_price >= target)
                or (condition in ("Dưới", "below", "<") and current_price <= target)
            )
            if not triggered:
                return None

            crop = db.query(CropType).filter(CropType.CropID == alert.CropID).first()
            crop_name = crop.CropName if crop else "N/A"

            self._send_alert_notification(
                alert=alert,
                crop_name=crop_name,
                current_price=current_price,
            )

            alert.LastTriggered = datetime.now()
            db.commit()

            return {
                "alert_id": alert.AlertID,
                "crop_name": crop_name,
                "region": alert.Region,
                "current_price": current_price,
                "target_price": target,
                "condition": condition,
                "triggered": True,
            }
        except Exception as exc:
            logger.error(f"_evaluate_alert error: {exc}")
            return None

    @staticmethod
    def _send_alert_notification(alert, crop_name: str, current_price: float):
        """Gửi thông báo qua notification_service (email/zalo)."""
        try:
            from app.services.notification_service import notification_service
            subject, plain, html = notification_service.build_price_alert_message(
                crop_name=crop_name,
                region=alert.Region,
                current_price=current_price,
                target_price=float(alert.TargetPrice),
                condition=alert.AlertType or "Trên",
            )
            receiver = f"user_{alert.UserID}@agriai.vn"
            notification_service.send(
                channel=alert.NotifyMethod or "email",
                receiver=receiver,
                subject=subject,
                message=plain,
                html_message=html,
            )
        except Exception as exc:
            logger.error(f"_send_alert_notification error: {exc}")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

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
