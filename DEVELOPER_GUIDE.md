# 👨‍💻 Developer Guide

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git
- VS Code (recommended)

### Local Development (Without Docker)

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/agridb"
export REDIS_URL="redis://localhost:6379/0"

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### With Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build
```

## Project Structure

### Backend Architecture

```
backend/
├── app/
│   ├── api/              # API endpoints (routes)
│   │   ├── quality.py    # Quality check endpoints
│   │   └── pricing.py    # Pricing endpoints
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database connection
│   │   └── redis_client.py
│   ├── models/           # SQLAlchemy models
│   │   ├── price.py
│   │   └── crop.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── price_schema.py
│   │   └── quality_schema.py
│   ├── services/         # Business logic
│   └── main.py           # FastAPI application
├── ai_models/            # AI/ML models
│   ├── yolo_inference.py
│   └── price_forecast/
└── tests/                # Tests
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   ├── pages/            # Page components
│   │   ├── Dashboard.jsx
│   │   ├── QualityPage.jsx
│   │   └── PricingPage.jsx
│   ├── services/         # API clients
│   │   ├── api.js
│   │   ├── qualityApi.js
│   │   └── pricingApi.js
│   ├── App.jsx           # Main app component
│   └── main.jsx          # Entry point
└── public/
```

## Adding New Features

### 1. Add New API Endpoint

**Step 1: Create Schema** (`backend/app/schemas/`)
```python
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    field1: str
    field2: int

class NewFeatureResponse(BaseModel):
    result: str
```

**Step 2: Create Endpoint** (`backend/app/api/`)
```python
from fastapi import APIRouter
from ..schemas.new_feature_schema import NewFeatureRequest, NewFeatureResponse

router = APIRouter(prefix="/api/new-feature", tags=["new-feature"])

@router.post("/", response_model=NewFeatureResponse)
async def new_feature(request: NewFeatureRequest):
    # Your logic here
    return NewFeatureResponse(result="success")
```

**Step 3: Register Router** (`backend/app/main.py`)
```python
from .api import new_feature

app.include_router(new_feature.router)
```

### 2. Add New Frontend Page

**Step 1: Create Page Component** (`frontend/src/pages/`)
```jsx
import React from 'react';

const NewPage = () => {
  return (
    <div>
      <h1>New Feature</h1>
    </div>
  );
};

export default NewPage;
```

**Step 2: Add Route** (`frontend/src/App.jsx`)
```jsx
import NewPage from './pages/NewPage';

// In Routes:
<Route path="/new-feature" element={<NewPage />} />
```

**Step 3: Create API Service** (`frontend/src/services/`)
```javascript
import api from './api';

export const newFeatureApi = {
  doSomething: async (data) => {
    const response = await api.post('/api/new-feature', data);
    return response.data;
  },
};
```

## Database Migrations

### Create New Model

```python
# backend/app/models/new_model.py
from sqlalchemy import Column, Integer, String
from ..core.database import Base

class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
```

### Apply Changes

```bash
# Access database container
docker-compose exec db psql -U agriuser -d agridb

# Or use Python
docker-compose exec backend python
>>> from app.core.database import init_db
>>> init_db()
```

## Testing

### Backend Tests

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_api.py::test_root
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Manual API Testing

Use the interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Or use curl:
```bash
curl -X POST http://localhost:8000/api/pricing/current \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}'
```

## Debugging

### Backend Debugging

**VS Code:**
1. Set breakpoint in code
2. Press F5 or use "Python: FastAPI" launch configuration
3. Make API request

**Print Debugging:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Debug info: {variable}")
```

### Frontend Debugging

**Browser DevTools:**
- Console: `console.log()`
- Network tab: Check API requests
- React DevTools: Inspect components

**VS Code:**
```javascript
debugger; // Add this line to pause execution
```

## Code Style

### Python (Backend)

Follow PEP 8:
```bash
# Format code
black backend/app

# Check style
flake8 backend/app

# Type checking
mypy backend/app
```

### JavaScript (Frontend)

```bash
# Format code
npm run format

# Lint
npm run lint
```

## Common Tasks

### Add New Dependency

**Backend:**
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild container
docker-compose up -d --build backend
```

**Frontend:**
```bash
# Install package
docker-compose exec frontend npm install new-package

# Or rebuild
docker-compose up -d --build frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec db psql -U agriuser -d agridb

# Backup database
docker-compose exec db pg_dump -U agriuser agridb > backup.sql

# Restore database
docker-compose exec -T db psql -U agriuser agridb < backup.sql

# Reset database
docker-compose down -v
docker-compose up -d
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# View all keys
KEYS *

# Get value
GET key_name

# Clear all
FLUSHALL
```

## Performance Optimization

### Backend
- Use Redis caching for frequently accessed data
- Add database indexes
- Use async/await for I/O operations
- Implement pagination for large datasets

### Frontend
- Lazy load components
- Memoize expensive computations
- Optimize images
- Use React.memo for pure components

## Security Best Practices

- Never commit `.env` files
- Use environment variables for secrets
- Validate all user inputs
- Implement rate limiting
- Use HTTPS in production
- Keep dependencies updated

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

### Module Not Found
```bash
# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database Connection Error
```bash
# Check database is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)

## Getting Help

- Check existing issues on GitHub
- Read the documentation
- Ask in discussions
- Contact maintainers

Happy coding! 🚀
