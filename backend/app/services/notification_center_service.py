from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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
            Notification.IsDeleted.is_(False),
        )
        if notification_type:
            query = query.filter(Notification.Type == notification_type)
        if unread_only:
            query = query.filter(Notification.IsRead.is_(False))

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
                Notification.IsDeleted.is_(False),
                Notification.IsRead.is_(False),
            )
            .scalar()
            or 0
        )
        return {
            "notifications": [self._to_dict(row) for row in rows],
            "total": total,
            "unread_count": int(unread_count),
        }

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
                Notification.IsDeleted.is_(False),
                Notification.IsRead.is_(False),
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
                Notification.IsDeleted.is_(False),
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
        }


notification_center_service = NotificationCenterService()
