#!/bin/bash

echo "🔍 AgriAI System Health Check"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        if [ "$2" = "version" ]; then
            echo "  Version: $($1 --version | head -n1)"
        fi
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an 2>/dev/null | grep ":$1 " | grep LISTEN >/dev/null; then
        echo -e "${GREEN}✓${NC} Port $1 is in use"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Port $1 is free"
        return 1
    fi
}

echo "1. Checking required tools..."
echo "------------------------------"
check_command "docker" "version"
check_command "docker-compose" "version"
check_command "git" "version"
echo ""

echo "2. Checking Docker status..."
echo "------------------------------"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running"
    echo "  Please start Docker Desktop"
fi
echo ""

echo "3. Checking Docker containers..."
echo "------------------------------"
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Containers are running:"
    docker-compose ps
else
    echo -e "${YELLOW}⚠${NC} No containers are running"
    echo "  Start with: docker-compose up -d"
fi
echo ""

echo "4. Checking ports..."
echo "------------------------------"
check_port 5432 && echo "  PostgreSQL"
check_port 6379 && echo "  Redis"
check_port 8000 && echo "  Backend API"
check_port 5173 && echo "  Frontend"
echo ""

echo "5. Checking API health..."
echo "------------------------------"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend API is healthy"
    response=$(curl -s http://localhost:8000/health)
    echo "  Response: $response"
else
    echo -e "${RED}✗${NC} Backend API is not responding"
fi
echo ""

echo "6. Checking frontend..."
echo "------------------------------"
if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is accessible"
else
    echo -e "${RED}✗${NC} Frontend is not responding"
fi
echo ""

echo "=============================="
echo "Health check complete!"
echo ""
echo "📝 Quick commands:"
echo "  Start:   docker-compose up -d"
echo "  Stop:    docker-compose down"
echo "  Logs:    docker-compose logs -f"
echo "  Restart: docker-compose restart"
