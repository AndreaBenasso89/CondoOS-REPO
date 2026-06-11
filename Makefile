# CondominioOS developer Makefile
.DEFAULT_GOAL := help
COMPOSE := docker compose -f infra/docker/docker-compose.yml

.PHONY: help up down logs migrate seed dev test lint fmt typecheck eval walkthrough

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Start local infra (postgres, redis, nats, minio, qdrant, temporal)
	$(COMPOSE) up -d

down: ## Stop local infra
	$(COMPOSE) down

logs: ## Tail infra logs
	$(COMPOSE) logs -f

migrate: ## Run Alembic migrations
	cd services && uv run alembic upgrade head

seed: ## Seed a demo condominium + tenant
	cd services && uv run python -m condominioos.scripts.seed_demo

dev: ## Run API gateway + agent runtime (hot reload)
	cd services && uv run uvicorn condominioos.gateway.main:app --reload --port 8080

test: ## Run all backend tests
	cd services && uv run pytest -q

lint: ## Lint (ruff)
	cd services && uv run ruff check .

fmt: ## Format (ruff format)
	cd services && uv run ruff format .

typecheck: ## Static typecheck (mypy)
	cd services && uv run mypy condominioos

eval: ## Run the agent evaluation suite
	cd services && uv run python -m condominioos.evals.run_suite

walkthrough: ## Guided end-to-end user-test walkthrough + maturity/gap report (offline, no infra)
	cd services && uv run python -m condominioos.scripts.walkthrough
