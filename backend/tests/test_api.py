from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_person_1_api_contract_is_registered():
    paths = {route.path for route in app.routes}
    expected_paths = {
        "/api/harvest/forecast",
        "/api/quality/check",
        "/api/pricing/suggest",
        "/api/price-forecast/predict",
        "/api/market/suggest",
        "/api/alert/create",
        "/api/alert/list",
        "/api/alert/{alert_id}",
        "/api/weather/current/{region}",
    }
    assert expected_paths.issubset(paths)


def test_harvest_forecast():
    response = client.post(
        "/api/harvest/forecast",
        json={
            "crop_name": "ca chua",
            "region": "Ha Noi",
            "planting_date": "2026-01-01",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["expected_harvest_date"] == "2026-03-17"
    assert data["confidence"] > 0


def test_quality_upload_mock():
    response = client.post(
        "/api/quality/check",
        data={"crop_name": "ca chua", "region": "Ha Noi"},
        files={"image": ("sample.jpg", b"fake-image-content", "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quality_grade"] in {"grade_1", "grade_2", "grade_3"}
    assert "suggested_price" in data


def test_pricing_suggest():
    response = client.post(
        "/api/pricing/suggest",
        json={
            "crop_name": "ca chua",
            "region": "Ha Noi",
            "quantity": 100,
            "quality_grade": "grade_1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["suggested_price"] > 0
    assert data["min_price"] <= data["suggested_price"] <= data["max_price"]


def test_price_forecast_predict():
    response = client.post(
        "/api/price-forecast/predict",
        json={
            "crop_name": "ca chua",
            "region": "Ha Noi",
            "forecast_days": 7,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["predicted_prices"]) == 7
    assert data["trend"] in {"increasing", "decreasing", "stable"}


def test_market_suggest():
    response = client.post(
        "/api/market/suggest",
        json={
            "crop_name": "ca chua",
            "region": "Ha Noi",
            "quantity": 1200,
            "quality_grade": "grade_1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_channel"]
    assert data["profit_comparison"]


def test_alert_create_list_delete():
    create_response = client.post(
        "/api/alert/create",
        json={
            "crop_name": "ca chua",
            "region": "Ha Noi",
            "target_price": 25000,
            "condition": "above",
            "notification_channel": "email",
            "receiver": "farmer@example.com",
        },
    )
    assert create_response.status_code == 200
    alert_id = create_response.json()["alert_id"]

    list_response = client.get("/api/alert/list")
    assert list_response.status_code == 200
    assert any(alert["alert_id"] == alert_id for alert in list_response.json()["alerts"])

    delete_response = client.delete(f"/api/alert/{alert_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["alert_id"] == alert_id


def test_weather_current():
    response = client.get("/api/weather/current/Ha%20Noi")
    assert response.status_code == 200
    assert response.json()["region"] == "Ha Noi"
