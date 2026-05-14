"""
TDD: per-user chat history
Slice 1: POST /api/chat lưu hội thoại vào DB
Slice 2: GET  /api/chat/history trả về lịch sử của user đó
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ── helpers ─────────────────────────────────────────────────────────────────

def _register_and_login() -> str:
    """Tạo user ngẫu nhiên và trả về access_token."""
    email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    r = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "password123",
        "phone_number": None,
        "zalo_id": None,
        "region": None,
    })
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Slice 1: chat lưu hội thoại ─────────────────────────────────────────────

def test_chat_returns_answer():
    """Tracer bullet: POST /api/chat trả về câu trả lời."""
    r = client.post("/api/chat", json={"question": "Giá cà chua hôm nay?"})
    assert r.status_code == 200
    assert r.json()["answer"]


def test_chat_saves_conversation_for_authenticated_user():
    """Khi user đã đăng nhập, hội thoại phải được lưu vào DB."""
    token = _register_and_login()
    r = client.post("/api/chat", json={"question": "Giá lúa hôm nay?"},
                    headers=_auth(token))
    assert r.status_code == 200

    # Verify bằng cách gọi history — nếu lưu đúng sẽ có ít nhất 1 bản ghi
    h = client.get("/api/chat/history", headers=_auth(token))
    assert h.status_code == 200
    history = h.json()["history"]
    assert len(history) >= 1
    assert any("lúa" in item["user_message"].lower() or "lua" in item["user_message"].lower()
               for item in history)


# ── Slice 2: GET /api/chat/history ──────────────────────────────────────────

def test_chat_history_requires_auth():
    """Không có token → 401."""
    r = client.get("/api/chat/history")
    assert r.status_code == 401


def test_chat_history_isolated_per_user():
    """Lịch sử của user A không lộ sang user B."""
    token_a = _register_and_login()
    token_b = _register_and_login()

    # User A chat
    client.post("/api/chat", json={"question": "user_a_unique_question_xyz"},
                headers=_auth(token_a))

    # User B không thấy câu hỏi của A
    h = client.get("/api/chat/history", headers=_auth(token_b))
    assert h.status_code == 200
    assert not any("user_a_unique" in item["user_message"]
                   for item in h.json()["history"])


def test_chat_history_response_shape():
    """Response phải có đúng cấu trúc cần thiết cho frontend."""
    token = _register_and_login()
    client.post("/api/chat", json={"question": "Thời tiết Đà Nẵng?"},
                headers=_auth(token))

    h = client.get("/api/chat/history?limit=5", headers=_auth(token))
    assert h.status_code == 200
    data = h.json()
    assert "history" in data
    assert "total" in data
    item = data["history"][0]
    assert "id" in item
    assert "user_message" in item
    assert "ai_response" in item
    assert "created_at" in item
