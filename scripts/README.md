# Scripts - AgriAI

Utility scripts for development and deployment.

## Available Scripts

### Setup & Start

**setup.sh**
- Initialize project
- Create directories
- Setup environment

```bash
./scripts/setup.sh
```

**start.sh**
- Start all services
- Check health
- Display URLs

```bash
./scripts/start.sh
```

**stop.sh**
- Stop all services

```bash
./scripts/stop.sh
```

### Testing & Demo

**demo.sh**
- Run API demos
- Test endpoints
- Show examples

```bash
./scripts/demo.sh
```

**test_api.sh**
- Test all API endpoints
- Check responses
- Verify functionality

```bash
./scripts/test_api.sh
```

**check_system.sh**
- Check system health
- Verify dependencies
- Check ports
- Test services

```bash
./scripts/check_system.sh
```

### Database

**init_db.py**
- Initialize database
- Create tables
- Insert sample data

```bash
docker-compose exec backend python scripts/init_db.py
```

## Usage

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

Run any script:
```bash
./scripts/<script-name>.sh
```

## Requirements

- Bash (Linux/Mac) or Git Bash (Windows)
- Docker & Docker Compose
- curl (for API testing)
- jq (optional, for JSON formatting)
