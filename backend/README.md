# AgriAI Backend

FastAPI backend for harvest forecast, agricultural pricing, product quality check, market suggestion, weather data and price alerts.

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI is available at http://localhost:8000/docs.

`requirements.txt` contains only the backend core needed by person 1. Optional heavy dependencies are split out:

```bash
pip install -r requirements-ai.txt
pip install -r requirements-sqlserver.txt
```

Use Python 3.11 or 3.12 for the optional AI/SQL Server files if Python 3.14 does not have prebuilt wheels for those packages.

## Environment

The app reads `.env` with these keys:

```env
DATABASE_URL=sqlite:///./agri_ai.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-this-secret-key
UPLOAD_DIR=storage/uploads
ENVIRONMENT=development
```

SQLite is the default MVP database. If a SQL Server URL is configured but unavailable during local development, the app falls back to `sqlite:///./agri_ai.db`.

## SQL Server Schema

The SQLAlchemy models are aligned with `../NongNghiepAI_Full.sql`, including these backend tables:

- `Users`, `CropTypes`, `WeatherData`
- `HarvestSchedule`, `HarvestForecastResults`
- `MarketPrices`, `PriceHistory`, `PriceForecastResults`, `PricingRequests`
- `QualityRecords`, `MarketSuggestions`
- `AlertSubscriptions`, `AlertNotifications`
- `AIConversations`

For SQL Server, run the SQL file first, install optional drivers with `pip install -r requirements-sqlserver.txt`, then point `DATABASE_URL` to the `NongNghiepAI` database.

## Main API

- `GET /health`
- `POST /api/harvest/forecast`
- `POST /api/quality/check`
- `POST /api/pricing/suggest`
- `POST /api/price-forecast/predict`
- `POST /api/market/suggest`
- `POST /api/alert/create`
- `GET /api/alert/list`
- `DELETE /api/alert/{alert_id}`
- `GET /api/weather/current/{region}`
- `POST /api/weather/`

Legacy helpers are still available:

- `POST /api/pricing/current`
- `POST /api/pricing/forecast`
- `GET /api/pricing/history/{crop_name}/{region}`
- `GET /api/pricing/compare-regions/{crop_name}`
- `GET /api/quality/grades`
- `GET /api/market/channels`

## Tests

```bash
python -m pytest
```

## Person 1 Scope Completed

- FastAPI app, CORS, health check and router registration.
- Pydantic settings for database, Redis, secret key, upload directory and environment.
- SQLAlchemy `Base`, `SessionLocal`, `get_db` and `init_db`.
- MVP models, schemas and repositories for crop, market price, harvest forecast, quality check, alert and weather.
- Mock services so all API contracts can be tested before AI/crawler integration.
- Basic integration tests for the main API contract.
