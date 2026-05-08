from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func

from ..core.database import Base


class Notification(Base):
    __tablename__ = "Notifications"

    NotificationID = Column("NotificationID", Integer, primary_key=True, index=True)
    UserID = Column("UserID", Integer, ForeignKey("Users.UserID"), nullable=False, index=True)
    Type = Column("Type", String(50), nullable=False, default="system", index=True)
    Title = Column("Title", String(255), nullable=False)
    Message = Column("Message", Text, nullable=False)
    Priority = Column("Priority", String(30), nullable=False, default="medium")
    IsRead = Column("IsRead", Boolean, nullable=False, default=False)
    IsDeleted = Column("IsDeleted", Boolean, nullable=False, default=False)
    RelatedEntityType = Column("RelatedEntityType", String(50), nullable=True)
    RelatedEntityID = Column("RelatedEntityID", Integer, nullable=True)
    Channel = Column("Channel", String(30), nullable=False, default="app")
    CreatedAt = Column("CreatedAt", DateTime, server_default=func.now(), nullable=False)
    ReadAt = Column("ReadAt", DateTime, nullable=True)

    id = synonym("NotificationID")
    user_id = synonym("UserID")
    type = synonym("Type")
    title = synonym("Title")
    message = synonym("Message")
    priority = synonym("Priority")
    is_read = synonym("IsRead")
    is_deleted = synonym("IsDeleted")
    related_entity_type = synonym("RelatedEntityType")
    related_entity_id = synonym("RelatedEntityID")
    channel = synonym("Channel")
    created_at = synonym("CreatedAt")
    read_at = synonym("ReadAt")


class NotificationDelivery(Base):
    __tablename__ = "NotificationDeliveries"

    DeliveryID = Column("DeliveryID", Integer, primary_key=True, index=True)
    NotificationID = Column("NotificationID", Integer, ForeignKey("Notifications.NotificationID"), nullable=False, index=True)
    Channel = Column("Channel", String(30), nullable=False)
    Receiver = Column("Receiver", String(255), nullable=True)
    Status = Column("Status", String(30), nullable=False, default="pending")
    ProviderMessageID = Column("ProviderMessageID", String(100), nullable=True)
    ErrorMessage = Column("ErrorMessage", Text, nullable=True)
    SentAt = Column("SentAt", DateTime, server_default=func.now(), nullable=False)

    id = synonym("DeliveryID")
    notification_id = synonym("NotificationID")
    channel = synonym("Channel")
    receiver = synonym("Receiver")
    status = synonym("Status")
    provider_message_id = synonym("ProviderMessageID")
    error_message = synonym("ErrorMessage")
    sent_at = synonym("SentAt")
