.PHONY: build up down logs migrate test lint format clean

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	docker-compose exec api alembic revision --autogenerate -m "$(m)"

test:
	docker-compose exec api pytest tests/ -v --cov=src --cov-report=html

lint:
	docker-compose exec api flake8 src/ tests/
	docker-compose exec api mypy src/

format:
	docker-compose exec api black src/ tests/
	docker-compose exec api isort src/ tests/

clean:
	docker-compose down -v
	docker system prune -f

seed:
	docker-compose exec api python scripts/seed_data.py

backup:
	docker-compose exec postgres pg_dump -U ai_engineer ai_smart_engineer > backup_$$(date +%Y%m%d_%H%M%S).sql

restore:
	docker-compose exec -T postgres psql -U ai_engineer ai_smart_engineer < $(file)
