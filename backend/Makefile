PODMAN ?= podman
COMPOSE ?= $(PODMAN) compose -f ../docker-compose.yml
IMAGE ?= fintrack-api:dev

.PHONY: build test dev-up dev-down

build:
	$(PODMAN) build -t $(IMAGE) -f Dockerfile .

test: build
	$(PODMAN) run --rm $(IMAGE) pytest

alembic-upgrade:
	DATABASE_URL=${DATABASE_URL} python -m alembic -c alembic.ini upgrade head

dev-up:
	COMPOSE_PROJECT_NAME=fintrack $(COMPOSE) up -d

dev-down:
	COMPOSE_PROJECT_NAME=fintrack $(COMPOSE) down
