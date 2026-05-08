from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.response import api_response
from app.core.database import get_db
from app.models.user import User
from app.services.notification_center_service import notification_center_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def list_my_notifications(
    type: str | None = Query(default=None),
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.list_notifications(
        db,
        current_user,
        notification_type=type,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return api_response(data)


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.mark_all_as_read(db, current_user)
    return api_response(data, message=data["message"])


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.mark_as_read(db, current_user, notification_id)
    if data is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return api_response(data, message=data["message"])


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.delete_notification(db, current_user, notification_id)
    if data is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return api_response(data, message=data["message"])
