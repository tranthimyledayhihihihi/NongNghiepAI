# Backend - AgriAI

FastAPI backend cho hệ thống AgriAI.

## Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core config (database, redis, settings)
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # FastAPI application
├── ai_models/        # AI/ML models
├── tests/            # Tests
└── requirements.txt  # Dependencies
```

## Quick Start

### With Docker
```bash
docker-compose up -d backend
```

### Local Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/quality/check` - Quality check
- `GET /api/quality/grades` - Quality grades
- `POST /api/pricing/current` - Current price
- `POST /api/pricing/forecast` - Price forecast
- `GET /api/pricing/history/{crop}/{region}` - Price history
- `GET /api/pricing/compare-regions/{crop}` - Compare regions

## Testing

```bash
pytest
pytest --cov=app tests/
```

## Documentation

API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
