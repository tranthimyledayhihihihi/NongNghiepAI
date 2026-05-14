.PHONY: help build up down logs test clean

help:
	@echo "AgriAI - Makefile Commands"
	@echo "=========================="
	@echo "make build    - Build Docker images"
	@echo "make up       - Start all services"
	@echo "make down     - Stop all services"
	@echo "make logs     - View logs"
	@echo "make test     - Run tests"
	@echo "make clean    - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Services started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	docker system prune -f
