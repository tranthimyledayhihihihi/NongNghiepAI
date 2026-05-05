from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class PriceAlert(Base):
    __tablename__ = "AlertSubscriptions"

    AlertID = Column("AlertID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False, index=True)
    CropID = Column("CropID", Integer, ForeignKey("CropTypes.CropID"), nullable=False, index=True)
    Region = Column("Region", String(100), nullable=False, index=True)
    TargetPrice = Column("TargetPrice", Float, nullable=False)
    AlertType = Column("AlertType", String(20), nullable=False, default="Trên")
    NotifyMethod = Column("NotifyMethod", String(20), nullable=False, default="Email")
    IsActive = Column("IsActive", Boolean, nullable=False, default=True)
    LastTriggered = Column("LastTriggered", DateTime, nullable=True)
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("AlertID")
    user_id = synonym("UserID")
    crop_id = synonym("CropID")
    region = synonym("Region")
    target_price = synonym("TargetPrice")
    condition = synonym("AlertType")
    alert_type = synonym("AlertType")
    notification_channel = synonym("NotifyMethod")
    notify_method = synonym("NotifyMethod")
    is_active = synonym("IsActive")
    last_triggered_at = synonym("LastTriggered")
    created_at = synonym("CreatedAt")


class AlertNotification(Base):
    __tablename__ = "AlertNotifications"

    NotificationID = Column("NotificationID", Integer, primary_key=True, index=True)
    AlertID = Column("AlertID", Integer, ForeignKey("AlertSubscriptions.AlertID"), nullable=False, index=True)
    CurrentPrice = Column("CurrentPrice", Float, nullable=True)
    Message = Column("Message", Text, nullable=True)
    NotifyMethod = Column("NotifyMethod", String(20), nullable=True)
    SendStatus = Column("SendStatus", String(20), nullable=False, default="Pending")
    SentAt = Column("SentAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("NotificationID")
    alert_id = synonym("AlertID")
    current_price = synonym("CurrentPrice")
    message = synonym("Message")
    notify_method = synonym("NotifyMethod")
    send_status = synonym("SendStatus")
    sent_at = synonym("SentAt")


AlertSubscription = PriceAlert
