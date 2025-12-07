#!/usr/bin/env sh
set -euo pipefail

# Stop existing stack
podman compose down

# Build images
podman compose build

# Start in detached mode
podman compose up -d

# Run migrations to ensure tables exist
podman exec -it fintrack-api alembic upgrade head

# Run backend tests in api container
podman exec -it fintrack-api pytest -vv -rA
