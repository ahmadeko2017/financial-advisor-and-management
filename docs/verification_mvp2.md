# MVP 2 Verification Checklist (backend + frontend)

## Backend pipeline (local equivalent of Jenkins stages)
- [ ] `cd backend && pip install -r requirements-dev.txt`
- [ ] `cd backend && python -m pytest`
- [ ] `cd backend && python -m compileall app`
- [ ] (optional) `cd backend && RUN_PY_CODE_STYLE=true podman run ...` or run locally if `ruff`/`black` installed:
  - `ruff check .`
  - `black --check .`

## Frontend pipeline
- [ ] `cd frontend && npm ci`
- [ ] `cd frontend && npm run lint`
- [ ] `cd frontend && npm run build`

## Smoke via Compose
- [ ] `docker compose down -v` (optional reset)
- [ ] `docker compose up --build`
- Confirm:
  - API reachable: `curl http://localhost:8000/health`
  - Frontend reachable: `http://localhost:5173`
  - Alembic migration ran without errors in API logs.

## Performance / EXPLAIN
- [ ] Populate sample data (e.g., demo@example.com) then run:
  - `cd backend && DATABASE_URL=... python scripts/benchmark_summary.py <user_id> [start_date] [end_date]`
- [ ] Capture EXPLAIN output and p95 latency notes in PR/issue.
