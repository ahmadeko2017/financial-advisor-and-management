#!/usr/bin/env sh

# Stop existing stack
podman compose down -v

# Build images
podman compose build

# Start in detached mode
podman compose up -d

# Ensure tables exist only if missing to avoid enum/type duplication
podman exec -it fintrack-api sh -c "cd /app && python - <<'PY'\nfrom sqlalchemy import inspect\nfrom app.database import Base, engine\nfrom app import models  # register models\ninsp = inspect(engine)\nif not insp.has_table('users'):\n    Base.metadata.create_all(bind=engine)\n    print('tables created via create_all')\nelse:\n    print('tables already exist, skipping create_all')\nPY"

# Run migrations to ensure schema is at head
podman exec -it fintrack-api alembic upgrade head

# Show tables for verification
podman exec -it fintrack-db psql -U finuser -d fintrack -c '\dt'

# Run backend tests in api container
podman exec -it fintrack-api pytest -vv -rA
