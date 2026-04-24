import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_quality_grades():
    """Test quality grades endpoint"""
    response = client.get("/api/quality/grades")
    assert response.status_code == 200
    data = response.json()
    assert "grades" in data
    assert len(data["grades"]) == 3

def test_current_price():
    """Test current price endpoint"""
    response = client.post(
        "/api/pricing/current",
        json={
            "crop_name": "Cà chua",
            "region": "Hà Nội",
            "quality_grade": "grade_1"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "current_price" in data
    assert "price_trend" in data

def test_price_forecast():
    """Test price forecast endpoint"""
    response = client.post(
        "/api/pricing/forecast",
        json={
            "crop_name": "Cà chua",
            "region": "Hà Nội",
            "days": 7
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "forecast_data" in data
    assert len(data["forecast_data"]) == 7
