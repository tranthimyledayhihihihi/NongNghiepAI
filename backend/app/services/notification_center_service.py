from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification, NotificationDelivery
from app.models.user import User
from app.schemas.notification_schema import NotificationCreate


class NotificationCenterService:
    def list_notifications(
        self,
        db: Session,
        user: User,
        *,
        notification_type: str | None = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        self._seed_welcome_notifications(db, user)
        query = db.query(Notification).filter(
            Notification.UserID == user.UserID,
            Notification.IsDeleted == False,
        )
        if notification_type:
            query = query.filter(Notification.Type == notification_type)
        if unread_only:
            query = query.filter(Notification.IsRead == False)

        total = query.count()
        rows = (
            query.order_by(desc(Notification.CreatedAt))
            .offset(max(offset, 0))
            .limit(min(max(limit, 1), 100))
            .all()
        )
        unread_count = (
            db.query(func.count(Notification.NotificationID))
            .filter(
                Notification.UserID == user.UserID,
                Notification.IsDeleted == False,
                Notification.IsRead == False,
            )
            .scalar()
            or 0
        )
        return {
            "notifications": [self._to_dict(row) for row in rows],
            "total": total,
            "unread_count": int(unread_count),
        }

    def summary(self, db: Session, user: User) -> dict:
        self._seed_welcome_notifications(db, user)
        base = db.query(Notification).filter(
            Notification.UserID == user.UserID,
            Notification.IsDeleted == False,
        )
        total = base.count()
        unread = base.filter(Notification.IsRead == False).count()
        by_type = {
            row[0]: int(row[1])
            for row in (
                db.query(Notification.Type, func.count(Notification.NotificationID))
                .filter(Notification.UserID == user.UserID, Notification.IsDeleted == False)
                .group_by(Notification.Type)
                .all()
            )
        }
        by_priority = {
            row[0]: int(row[1])
            for row in (
                db.query(Notification.Priority, func.count(Notification.NotificationID))
                .filter(Notification.UserID == user.UserID, Notification.IsDeleted == False)
                .group_by(Notification.Priority)
                .all()
            )
        }
        delivery_failed = (
            db.query(func.count(NotificationDelivery.DeliveryID))
            .join(Notification, NotificationDelivery.NotificationID == Notification.NotificationID)
            .filter(
                Notification.UserID == user.UserID,
                Notification.IsDeleted == False,
                NotificationDelivery.Status.in_(["failed", "error"]),
            )
            .scalar()
            or 0
        )
        return {
            "total": int(total),
            "unread": int(unread),
            "by_type": by_type,
            "by_priority": by_priority,
            "delivery_failed": int(delivery_failed),
            "high_priority": int(by_priority.get("high", 0)),
            "updated_at": datetime.now(),
            "source": "database",
            "source_name": "Notifications DB",
            "confidence": 0.7,
        }

    def get_priority_notifications(self, db: Session, user: User, min_priority: str = "high") -> dict:
        priority_order = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
        listed = self.list_notifications(db, user, limit=100)
        threshold = priority_order.get(min_priority, 2)
        items = [
            item for item in listed.get("notifications", [])
            if priority_order.get(item.get("priority", "low"), 0) >= threshold
        ]
        return {
            "notifications": items,
            "total": len(items),
            "source": "database",
            "source_name": "Notifications priority view",
            "confidence": 0.7,
            "updated_at": datetime.now(),
        }

    def get_unread_notification_count(self, db: Session, user: User) -> dict:
        summary = self.summary(db, user)
        return {
            "unread_count": summary.get("unread", 0),
            "summary": summary,
            "source": "database",
            "source_name": "Notifications DB",
            "confidence": 0.7,
            "updated_at": datetime.now(),
        }

    def create_notification_from_alert(self, db: Session, user: User, alert: dict) -> dict:
        notification = self.create_notification(
            db,
            NotificationCreate(
                user_id=user.UserID,
                type=alert.get("alert_type") or "alert",
                title=alert.get("title") or "AgriAI alert",
                message=alert.get("message") or alert.get("suggested_action") or "Alert requires review.",
                priority=alert.get("priority") or alert.get("severity") or "medium",
                channel="app",
                related_entity_type="alert",
                related_entity_id=alert.get("alert_id") or alert.get("related_alert_id"),
            ),
        )
        notification["related_alert_id"] = alert.get("alert_id") or alert.get("related_alert_id")
        notification["severity"] = alert.get("severity")
        notification["suggested_action"] = alert.get("suggested_action")
        notification["action_required"] = alert.get("action_required", notification.get("priority") in {"high", "urgent"})
        return notification

    def get_detail(self, db: Session, user: User, notification_id: int) -> dict | None:
        row = self._get_owned(db, user, notification_id)
        if row is None:
            return None
        data = self._to_dict(row)
        data["deliveries"] = [
            self._delivery_to_dict(delivery)
            for delivery in self._deliveries(db, notification_id)
        ]
        data["related_entity"] = self._related_entity(db, row)
        return data

    def create_notification(self, db: Session, request: NotificationCreate) -> dict:
        row = Notification(
            UserID=request.user_id,
            Type=request.type,
            Title=request.title,
            Message=request.message,
            Priority=request.priority,
            Channel=request.channel,
            RelatedEntityType=request.related_entity_type,
            RelatedEntityID=request.related_entity_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        self._create_delivery(db, row, request.channel)
        return self._to_dict(row)

    def mark_as_read(self, db: Session, user: User, notification_id: int) -> dict | None:
        row = self._get_owned(db, user, notification_id)
        if row is None:
            return None
        if not row.IsRead:
            row.IsRead = True
            row.ReadAt = datetime.now()
            db.add(row)
            db.commit()
        return {"notification_id": notification_id, "message": "notification marked as read"}

    def mark_all_as_read(self, db: Session, user: User) -> dict:
        now = datetime.now()
        rows = (
            db.query(Notification)
            .filter(
                Notification.UserID == user.UserID,
                Notification.IsDeleted == False,
                Notification.IsRead == False,
            )
            .all()
        )
        for row in rows:
            row.IsRead = True
            row.ReadAt = now
            db.add(row)
        db.commit()
        return {"updated": len(rows), "message": "all notifications marked as read"}

    def delete_notification(self, db: Session, user: User, notification_id: int) -> dict | None:
        row = self._get_owned(db, user, notification_id)
        if row is None:
            return None
        row.IsDeleted = True
        db.add(row)
        db.commit()
        return {"notification_id": notification_id, "message": "notification deleted"}

    def deliveries(self, db: Session, user: User, notification_id: int) -> list[dict] | None:
        if self._get_owned(db, user, notification_id) is None:
            return None
        return [self._delivery_to_dict(row) for row in self._deliveries(db, notification_id)]

    def bulk_update(
        self,
        db: Session,
        user: User,
        *,
        action: str,
        ids: list[int] | None = None,
        notification_type: str | None = None,
        unread_only: bool = False,
    ) -> dict:
        query = db.query(Notification).filter(
            Notification.UserID == user.UserID,
            Notification.IsDeleted == False,
        )
        if ids:
            query = query.filter(Notification.NotificationID.in_(ids))
        if notification_type:
            query = query.filter(Notification.Type == notification_type)
        if unread_only:
            query = query.filter(Notification.IsRead == False)

        rows = query.all()
        now = datetime.now()
        for row in rows:
            if action in {"mark_read", "read"}:
                row.IsRead = True
                row.ReadAt = now
            elif action in {"delete", "archive"}:
                row.IsDeleted = True
            db.add(row)
        db.commit()
        return {"updated": len(rows), "action": action, "message": "bulk update completed"}

    def retry_delivery(self, db: Session, user: User, notification_id: int) -> dict | None:
        row = self._get_owned(db, user, notification_id)
        if row is None:
            return None
        from app.services.notification_service import notification_service

        deliveries = [
            delivery
            for delivery in self._deliveries(db, notification_id)
            if delivery.Channel != "app" and delivery.Status in {"failed", "pending", "error", "missing_token"}
        ]
        results = []
        for delivery in deliveries:
            if not delivery.Receiver:
                delivery.Status = "failed"
                delivery.ErrorMessage = "Receiver is missing"
                db.add(delivery)
                results.append(self._delivery_to_dict(delivery))
                continue
            result = notification_service.send(
                delivery.Channel,
                delivery.Receiver,
                row.Title,
                row.Message,
            )
            delivery.Status = result.get("status") or "failed"
            delivery.ProviderMessageID = result.get("message_id")
            delivery.ErrorMessage = result.get("error")
            delivery.SentAt = datetime.now()
            db.add(delivery)
            results.append(self._delivery_to_dict(delivery))
        db.commit()
        return {"notification_id": notification_id, "retried": len(results), "deliveries": results}

    def create_price_alert_inbox(
        self,
        db: Session,
        *,
        user_id: int,
        crop_name: str,
        region: str,
        message: str,
        alert_id: int | None = None,
    ) -> dict | None:
        try:
            request = NotificationCreate(
                user_id=user_id,
                type="price",
                title=f"Price alert for {crop_name} in {region}",
                message=message,
                priority="high",
                channel="app",
                related_entity_type="price_alert",
                related_entity_id=alert_id,
            )
            return self.create_notification(db, request)
        except SQLAlchemyError:
            db.rollback()
            return None

    def _seed_welcome_notifications(self, db: Session, user: User) -> None:
        if settings.USE_REALTIME_ONLY and not (settings.ALLOW_MOCK_DATA or settings.ALLOW_SAMPLE_DATA):
            return
        exists = (
            db.query(Notification.NotificationID)
            .filter(Notification.UserID == user.UserID)
            .first()
        )
        if exists:
            return
        defaults = [
            NotificationCreate(
                user_id=user.UserID,
                type="system",
                title="AgriAI inbox is ready",
                message="Notifications from price alerts, weather checks and harvest reminders will be stored here.",
                priority="medium",
                channel="app",
            ),
            NotificationCreate(
                user_id=user.UserID,
                type="weather",
                title="Weather monitor enabled",
                message=f"Weather overview is configured for {user.Region or 'your farm region'}.",
                priority="medium",
                channel="app",
            ),
        ]
        try:
            for item in defaults:
                row = Notification(
                    UserID=item.user_id,
                    Type=item.type,
                    Title=item.title,
                    Message=item.message,
                    Priority=item.priority,
                    Channel=item.channel,
                )
                db.add(row)
            db.commit()
        except SQLAlchemyError:
            db.rollback()

    @staticmethod
    def _get_owned(db: Session, user: User, notification_id: int) -> Notification | None:
        return (
            db.query(Notification)
            .filter(
                Notification.NotificationID == notification_id,
                Notification.UserID == user.UserID,
                Notification.IsDeleted == False,
            )
            .first()
        )

    @staticmethod
    def _create_delivery(db: Session, row: Notification, channel: str) -> None:
        delivery = NotificationDelivery(
            NotificationID=row.NotificationID,
            Channel=channel,
            Receiver=None,
            Status="stored" if channel == "app" else "pending",
        )
        db.add(delivery)
        db.commit()

    @staticmethod
    def _deliveries(db: Session, notification_id: int) -> list[NotificationDelivery]:
        return (
            db.query(NotificationDelivery)
            .filter(NotificationDelivery.NotificationID == notification_id)
            .order_by(NotificationDelivery.SentAt)
            .all()
        )

    @staticmethod
    def _delivery_to_dict(row: NotificationDelivery) -> dict:
        return {
            "delivery_id": row.DeliveryID,
            "notification_id": row.NotificationID,
            "channel": row.Channel,
            "receiver": row.Receiver,
            "status": row.Status,
            "provider_message_id": row.ProviderMessageID,
            "error_message": row.ErrorMessage,
            "sent_at": row.SentAt,
        }

    @staticmethod
    def _related_entity(db: Session, row: Notification) -> dict | None:
        if row.RelatedEntityType != "price_alert" or not row.RelatedEntityID:
            return None
        try:
            from app.models.alert import PriceAlert
            from app.repositories.alert_repository import get_alert_crop_name
            from app.repositories.common import to_api_alert_condition

            alert = db.query(PriceAlert).filter(PriceAlert.AlertID == row.RelatedEntityID).first()
            if not alert:
                return None
            return {
                "type": "price_alert",
                "id": alert.AlertID,
                "crop_name": get_alert_crop_name(db, alert),
                "region": alert.Region,
                "target_price": float(alert.TargetPrice),
                "condition": to_api_alert_condition(alert.AlertType),
                "is_active": bool(alert.IsActive),
                "last_triggered_at": alert.LastTriggered,
            }
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def _to_dict(row: Notification) -> dict:
        return {
            "notification_id": row.NotificationID,
            "user_id": row.UserID,
            "type": row.Type,
            "title": row.Title,
            "message": row.Message,
            "priority": row.Priority,
            "is_read": bool(row.IsRead),
            "is_deleted": bool(row.IsDeleted),
            "related_entity_type": row.RelatedEntityType,
            "related_entity_id": row.RelatedEntityID,
            "channel": row.Channel,
            "created_at": row.CreatedAt,
            "read_at": row.ReadAt,
            "related_alert_id": row.RelatedEntityID if row.RelatedEntityType in {"alert", "price_alert", "weather_alert"} else None,
            "severity": row.Priority,
            "suggested_action": None,
            "action_required": row.Priority in {"high", "urgent"},
            "source": "database",
            "source_name": "Notifications DB",
            "fetched_at": datetime.now(),
            "updated_at": row.CreatedAt,
            "confidence": 0.7,
        }


notification_center_service = NotificationCenterService()
