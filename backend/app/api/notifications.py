import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.response import api_response
from app.core.database import SessionLocal, get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.notification_center_service import notification_center_service
from app.services.notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/summary")
async def get_notifications_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.summary(db, current_user)
    return api_response(data)


@router.get("/stream")
async def stream_notifications(token: str = Query(...)):
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="invalid authentication credentials")
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="invalid authentication credentials") from exc

    async def event_generator():
        last_payload = None
        while True:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.UserID == user_id, User.IsActive == True).first()
                if user is None:
                    yield "event: error\ndata: {\"detail\":\"user not found\"}\n\n"
                    return
                summary = notification_center_service.summary(db, user)
                payload_text = json.dumps(summary, default=str, ensure_ascii=False)
                if payload_text != last_payload:
                    last_payload = payload_text
                    yield f"event: summary\ndata: {payload_text}\n\n"
                else:
                    yield "event: ping\ndata: {}\n\n"
            finally:
                db.close()
            await asyncio.sleep(10)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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


class BulkNotificationRequest(BaseModel):
    action: str
    ids: list[int] | None = None
    type: str | None = None
    unread_only: bool = False


@router.patch("/bulk")
async def bulk_update_notifications(
    body: BulkNotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.action not in {"mark_read", "read", "delete", "archive"}:
        raise HTTPException(status_code=400, detail="unsupported bulk action")
    data = notification_center_service.bulk_update(
        db,
        current_user,
        action=body.action,
        ids=body.ids,
        notification_type=body.type,
        unread_only=body.unread_only,
    )
    return api_response(data, message=data["message"])


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.mark_all_as_read(db, current_user)
    return api_response(data, message=data["message"])


class TestNotificationRequest(BaseModel):
    channel: str
    receiver: str


@router.post("/test")
async def send_test_notification(
    body: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
):
    display_name = current_user.FullName or current_user.Email or "AgriAI user"
    result = notification_service.send(
        channel=body.channel,
        receiver=body.receiver,
        subject="[AgriAI] Thông báo thử nghiệm",
        message=(
            f"Xin chào {display_name}!\n"
            "Đây là tin nhắn thử nghiệm từ hệ thống AgriAI. "
            "Kênh thông báo của bạn đang hoạt động."
        ),
        html_message=(
            "<html><body>"
            f"<h2>Xin chào {display_name}!</h2>"
            "<p>Đây là tin nhắn thử nghiệm từ hệ thống <strong>AgriAI</strong>.</p>"
            "<p>Kênh thông báo của bạn đang hoạt động.</p>"
            "</body></html>"
        ),
    )
    return api_response(result, message="Đã gửi thử thông báo")


@router.get("/{notification_id}")
async def get_notification_detail(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.get_detail(db, current_user, notification_id)
    if data is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return api_response(data)


@router.get("/{notification_id}/deliveries")
async def get_notification_deliveries(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.deliveries(db, current_user, notification_id)
    if data is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return api_response({"deliveries": data})


@router.post("/{notification_id}/retry-delivery")
async def retry_notification_delivery(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = notification_center_service.retry_delivery(db, current_user, notification_id)
    if data is None:
        raise HTTPException(status_code=404, detail="notification not found")
    return api_response(data)


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
