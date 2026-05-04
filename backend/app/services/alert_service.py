"""
P2-15: Alert Service
Kiểm tra alert đang active, so sánh target_price với giá mới nhất, tạo message cảnh báo.
Có logic phát hiện giá above/below.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.alert import AlertSubscription
from ..models.price import MarketPrice
from ..models.crop import CropType

logger = logging.getLogger(__name__)


class AlertService:
    """Service xử lý cảnh báo giá nông sản."""

    # ------------------------------------------------------------------ #
    # CRUD Alert
    # ------------------------------------------------------------------ #

    def create_alert(
        self,
        db: Session,
        user_id: int,
        crop_name: str,
        region: str,
        target_price: float,
        condition: str,          # "Trên" | "Dưới"
        notify_method: str = "Email",
        receiver: Optional[str] = None,
    ) -> Dict:
        """Tạo alert mới, trả về thông tin alert."""
        crop = db.query(CropType).filter(CropType.CropName == crop_name).first()
        if not crop:
            return {"success": False, "message": f"Không tìm thấy cây trồng: {crop_name}"}

        alert = AlertSubscription(
            UserID=user_id,
            CropID=crop.CropID,
            Region=region,
            TargetPrice=target_price,
            AlertType=condition,
            NotifyMethod=notify_method,
            IsActive=True,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        return {
            "success":  True,
            "alert_id": alert.AlertID,
            "message":  f"Đã tạo alert: {crop_name} tại {region} sẽ thông báo khi giá {condition.lower()} {target_price:,.0f} VND/kg.",
        }

    def get_alerts(self, db: Session, user_id: int) -> List[Dict]:
        """Lấy danh sách alert của user."""
        alerts = (
            db.query(AlertSubscription)
            .filter(AlertSubscription.UserID == user_id)
            .order_by(desc(AlertSubscription.CreatedAt))
            .all()
        )
        result = []
        for a in alerts:
            crop = db.query(CropType).filter(CropType.CropID == a.CropID).first()
            result.append({
                "alert_id":      a.AlertID,
                "crop_name":     crop.CropName if crop else "N/A",
                "region":        a.Region,
                "target_price":  float(a.TargetPrice),
                "condition":     a.AlertType,
                "notify_method": a.NotifyMethod,
                "is_active":     a.IsActive,
                "last_triggered": a.LastTriggered.isoformat() if a.LastTriggered else None,
                "created_at":    a.CreatedAt.isoformat() if a.CreatedAt else None,
            })
        return result

    def deactivate_alert(self, db: Session, alert_id: int) -> Dict:
        """Tắt alert theo ID."""
        alert = db.query(AlertSubscription).filter(AlertSubscription.AlertID == alert_id).first()
        if not alert:
            return {"success": False, "message": "Không tìm thấy alert."}
        alert.IsActive = False
        db.commit()
        return {"success": True, "alert_id": alert_id, "message": "Alert đã được tắt."}

    # ------------------------------------------------------------------ #
    # Kiểm tra và gửi cảnh báo
    # ------------------------------------------------------------------ #

    def check_and_trigger_alerts(self, db: Session) -> List[Dict]:
        """
        Chạy toàn bộ alert đang active, kiểm tra điều kiện giá.
        Gọi notification_service nếu điều kiện thỏa mãn.
        """
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

    def _evaluate_alert(self, db: Session, alert: AlertSubscription) -> Optional[Dict]:
        """Kiểm tra một alert cụ thể."""
        # Lấy giá mới nhất
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
        target        = float(alert.TargetPrice)
        condition     = (alert.AlertType or "Trên").strip()

        # Kiểm tra điều kiện
        triggered = (
            (condition in ("Trên", "above", ">") and current_price >= target)
            or (condition in ("Dưới", "below", "<") and current_price <= target)
        )

        if not triggered:
            return None

        crop = db.query(CropType).filter(CropType.CropID == alert.CropID).first()
        crop_name = crop.CropName if crop else "N/A"

        # Gửi thông báo
        self._send_alert_notification(
            alert=alert,
            crop_name=crop_name,
            current_price=current_price,
        )

        # Cập nhật LastTriggered
        alert.LastTriggered = datetime.now()
        db.commit()

        return {
            "alert_id":     alert.AlertID,
            "crop_name":    crop_name,
            "region":       alert.Region,
            "current_price": current_price,
            "target_price": target,
            "condition":    condition,
            "triggered":    True,
        }

    @staticmethod
    def _send_alert_notification(alert: AlertSubscription, crop_name: str, current_price: float):
        """Gọi notification_service để gửi thông báo."""
        try:
            from .notification_service import notification_service
            subject, plain, html = notification_service.build_price_alert_message(
                crop_name=crop_name,
                region=alert.Region,
                current_price=current_price,
                target_price=float(alert.TargetPrice),
                condition=alert.AlertType or "Trên",
            )
            # Receiver mặc định: dùng email từ UserID (trong MVP log ra)
            receiver = f"user_{alert.UserID}@agriai.vn"
            notification_service.send(
                channel=alert.NotifyMethod or "email",
                receiver=receiver,
                subject=subject,
                message=plain,
                html_message=html,
            )
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")


alert_service = AlertService()
