from fastapi.testclient import TestClient

from app.main import app
from app.services.ai_context_service import AIContextService
from app.services.ai_intent_service import classify_user_intent


client = TestClient(app)


def test_classify_greeting_does_not_match_price():
    assert classify_user_intent("chào bạn") == "greeting"
    assert classify_user_intent("bạn ơi") == "greeting"


def test_classify_analysis_intents():
    assert classify_user_intent("phân tích giá cà chua ở Hà Nội hôm nay") == "price_analysis"
    assert classify_user_intent("hôm nay có nên tưới lúa không?") == "weather_analysis"
    assert classify_user_intent("mùa vụ của tôi khi nào thu hoạch?") == "harvest_analysis"
    assert classify_user_intent("có cảnh báo gì không") == "alert_analysis"
    assert classify_user_intent("phân tích tình hình nông trại") == "full_farm_analysis"


def test_context_general_question_does_not_load_default_agri_data(monkeypatch):
    calls: list[str] = []
    import app.services.ai_context_service as context_module

    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_weather_bundle",
        lambda *args, **kwargs: calls.append("weather") or {},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_pricing_bundle",
        lambda *args, **kwargs: calls.append("pricing") or {},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_market_bundle",
        lambda *args, **kwargs: calls.append("market") or {},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_alert_notification_bundle",
        lambda *args, **kwargs: calls.append("alerts") or {},
    )

    context = AIContextService().build_ai_context(
        None,
        region="Hà Nội",
        crop="cà chua",
        intent="general_question",
    )

    assert calls == []
    assert context["intent"] == "general_question"
    assert context["pricing"] == {}
    assert context["weather"] == {}
    assert context["market"] == {"news": [], "trends": {}, "opportunities": [], "risks": []}


def test_context_price_analysis_only_loads_price_and_market(monkeypatch):
    calls: list[str] = []
    import app.services.ai_context_service as context_module

    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_weather_bundle",
        lambda *args, **kwargs: calls.append("weather") or {},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_pricing_bundle",
        lambda *args, **kwargs: calls.append("pricing") or {"current": {"current_price": 10000}},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_market_bundle",
        lambda *args, **kwargs: calls.append("market") or {"trends": {"trend": "stable"}},
    )
    monkeypatch.setattr(
        context_module.agri_data_aggregator_service,
        "get_alert_notification_bundle",
        lambda *args, **kwargs: calls.append("alerts") or {},
    )

    context = AIContextService().build_ai_context(
        None,
        region="Hà Nội",
        crop="cà chua",
        intent="price_analysis",
    )

    assert calls == ["pricing", "market"]
    assert context["pricing"]["current_price"] == 10000
    assert context["weather"] == {}
    assert context["alerts"] == []


def test_ai_chat_greeting_returns_local_reply_without_market_analysis():
    response = client.post("/api/ai-chat/message", json={"message": "chào bạn"})

    assert response.status_code == 200
    payload = response.json()
    reply = payload["reply"].lower()
    assert payload["data"]["intent"] == "greeting"
    assert "chào bạn" in reply
    assert "giá cà chua" not in reply
    assert "thời tiết hà nội" not in reply
