# 📝 Useful Commands

## Quick Start

```bash
# Setup and start
./scripts/setup.sh
./scripts/start.sh

# Check system health
./scripts/check_system.sh

# Run demo
./scripts/demo.sh

# Test API
./scripts/test_api.sh

# Stop
./scripts/stop.sh
```

## Docker Commands

### Basic Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild and start
docker-compose up -d --build

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Container Management
```bash
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh

# View container stats
docker stats

# Remove stopped containers
docker-compose rm
```

## Backend Commands

### Development
```bash
# Run backend locally
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing
```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_root

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Database
```bash
# Access PostgreSQL
docker-compose exec db psql -U agriuser -d agridb

# Run SQL file
docker-compose exec -T db psql -U agriuser -d agridb < script.sql

# Backup database
docker-compose exec db pg_dump -U agriuser agridb > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U agriuser agridb < backup.sql

# Initialize database with sample data
docker-compose exec backend python scripts/init_db.py
```

### Redis
```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Common Redis commands
KEYS *              # List all keys
GET key_name        # Get value
SET key value       # Set value
DEL key             # Delete key
FLUSHALL            # Clear all data
INFO                # Server info
```

## Frontend Commands

### Development
```bash
# Run frontend locally
cd frontend
npm install
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Package Management
```bash
# Install new package
npm install package-name

# Install dev dependency
npm install -D package-name

# Update packages
npm update

# Check outdated packages
npm outdated

# Remove package
npm uninstall package-name
```

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get current price
curl -X POST http://localhost:8000/api/pricing/current \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","quality_grade":"grade_1"}'

# Price forecast
curl -X POST http://localhost:8000/api/pricing/forecast \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Cà chua","region":"Hà Nội","days":7}'

# Price history
curl "http://localhost:8000/api/pricing/history/Cà%20chua/Hà%20Nội?days=30"

# Compare regions
curl "http://localhost:8000/api/pricing/compare-regions/Cà%20chua"

# Quality grades
curl http://localhost:8000/api/quality/grades

# Upload image for quality check
curl -X POST http://localhost:8000/api/quality/check \
  -F "file=@/path/to/image.jpg"
```

### Using httpie (if installed)

```bash
# Install httpie
pip install httpie

# GET request
http GET http://localhost:8000/health

# POST request
http POST http://localhost:8000/api/pricing/current \
  crop_name="Cà chua" \
  region="Hà Nội" \
  quality_grade="grade_1"
```

## Git Commands

```bash
# Clone repository
git clone <repo-url>
cd agri-ai

# Create new branch
git checkout -b feature/new-feature

# Stage changes
git add .

# Commit changes
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Pull latest changes
git pull origin main

# View status
git status

# View commit history
git log --oneline

# Discard local changes
git checkout -- .
```

## Debugging

### View Logs
```bash
# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend

# Follow logs with timestamps
docker-compose logs -f -t backend
```

### Inspect Containers
```bash
# Container details
docker inspect <container_id>

# Container processes
docker-compose top

# Container resource usage
docker stats

# Network inspection
docker network ls
docker network inspect agri-ai_default
```

### Debug Backend
```bash
# Python shell in container
docker-compose exec backend python

# IPython shell (if installed)
docker-compose exec backend ipython

# Check Python path
docker-compose exec backend python -c "import sys; print(sys.path)"
```

## Maintenance

### Clean Up
```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a

# Clean up project
make clean
```

### Update Dependencies
```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade package-name

# Frontend
cd frontend
npm outdated
npm update
```

### Backup
```bash
# Backup database
docker-compose exec db pg_dump -U agriuser agridb > backup.sql

# Backup uploads
tar -czf uploads_backup.tar.gz backend/uploads/

# Backup everything
tar -czf agri-ai-backup.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  .
```

## Performance

### Monitor Resources
```bash
# Container stats
docker stats

# System resources
docker system df

# Detailed container info
docker-compose top
```

### Optimize
```bash
# Rebuild with no cache
docker-compose build --no-cache

# Remove unused data
docker system prune -a --volumes

# Optimize images
docker image prune -a
```

## Production

### Deploy
```bash
# Build for production
docker-compose -f docker-compose.prod.yml build

# Start production
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Checks
```bash
# Check all services
./scripts/check_system.sh

# Test API endpoints
./scripts/test_api.sh

# Monitor logs
docker-compose logs -f --tail=100
```

## Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'

# AgriAI specific
alias agri-start='cd ~/agri-ai && docker-compose up -d'
alias agri-stop='cd ~/agri-ai && docker-compose down'
alias agri-logs='cd ~/agri-ai && docker-compose logs -f'
alias agri-test='cd ~/agri-ai && ./scripts/test_api.sh'
```

## Help

```bash
# Docker help
docker --help
docker-compose --help

# Make help
make help

# View documentation
cat README.md
cat GETTING_STARTED.md
cat API_DOCUMENTATION.md
```
