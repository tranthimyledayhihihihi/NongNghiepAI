"""
TDD: WeatherClient.get_hourly_forecast() returns detailed per-hour metrics.
Vertical slices:
  1. apparent_temperature (feels like)
  2. dew_point
  3. visibility
  4. wind_gusts
  5. cloud_cover
"""
import pytest
from unittest.mock import MagicMock, patch


def _make_client(extra_hourly: dict = None):
    """Build WeatherClient with a mocked _get_json that returns minimal valid payload."""
    from datetime import datetime, timedelta
    from app.integrations.weather_client import WeatherClient

    # Use future timestamps so they pass the start_at filter
    future = datetime.now() + timedelta(hours=1)
    t0 = future.strftime("%Y-%m-%dT%H:00")
    t1 = (future + timedelta(hours=1)).strftime("%Y-%m-%dT%H:00")

    base_hourly = {
        "time": [t0, t1],
        "temperature_2m": [28.0, 27.5],
        "apparent_temperature": [32.0, 31.0],
        "relative_humidity_2m": [75, 78],
        "dew_point_2m": [20.5, 21.0],
        "precipitation_probability": [10, 15],
        "precipitation": [0.0, 0.0],
        "weather_code": [1, 1],
        "wind_speed_10m": [10.0, 12.0],
        "wind_gusts_10m": [18.0, 20.0],
        "uv_index": [3.0, 2.0],
        "visibility": [15000.0, 16000.0],
        "cloud_cover": [20, 30],
        "surface_pressure": [1012.0, 1011.0],
    }
    if extra_hourly:
        base_hourly.update(extra_hourly)

    payload = {"hourly": base_hourly}
    client = WeatherClient(base_url="http://mock")
    client._get_json = MagicMock(return_value=payload)
    return client


# ── Test 1: apparent_temperature ──────────────────────────────────────────────

def test_hourly_forecast_includes_apparent_temperature():
    client = _make_client()
    result = client.get_hourly_forecast("Da Nang", hours=2)
    assert len(result) > 0
    item = result[0]
    assert "apparent_temperature" in item
    assert item["apparent_temperature"] == 32.0


# ── Test 2: dew_point ─────────────────────────────────────────────────────────

def test_hourly_forecast_includes_dew_point():
    client = _make_client()
    result = client.get_hourly_forecast("Da Nang", hours=2)
    item = result[0]
    assert "dew_point" in item
    assert item["dew_point"] == 20.5


# ── Test 3: visibility ────────────────────────────────────────────────────────

def test_hourly_forecast_includes_visibility():
    client = _make_client()
    result = client.get_hourly_forecast("Da Nang", hours=2)
    item = result[0]
    assert "visibility" in item
    assert item["visibility"] == 15000.0


# ── Test 4: wind_gusts ────────────────────────────────────────────────────────

def test_hourly_forecast_includes_wind_gusts():
    client = _make_client()
    result = client.get_hourly_forecast("Da Nang", hours=2)
    item = result[0]
    assert "wind_gusts" in item
    assert item["wind_gusts"] == 18.0


# ── Test 5: cloud_cover ───────────────────────────────────────────────────────

def test_hourly_forecast_includes_cloud_cover():
    client = _make_client()
    result = client.get_hourly_forecast("Da Nang", hours=2)
    item = result[0]
    assert "cloud_cover" in item
    assert item["cloud_cover"] == 20
