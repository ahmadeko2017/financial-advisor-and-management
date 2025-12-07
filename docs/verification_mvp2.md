# MVP 2 Verification Checklist (backend + frontend)

## Backend pipeline (local equivalent of Jenkins stages)
- [ ] `cd backend && pip install -r requirements-dev.txt` _(blocked: psycopg2 build needs pg_config/libpq; not available in current env)_
- [ ] `cd backend && python -m pytest` _(pending; awaits deps install)_
- [ ] `cd backend && python -m compileall app` _(pending)_
- [ ] (optional) `cd backend && RUN_PY_CODE_STYLE=true podman run ...` or run locally if `ruff`/`black` installed:
  - `ruff check .` _(pending)_
  - `black --check .` _(pending)_

## Frontend pipeline
- [ ] `cd frontend && npm ci` _(pending on target; install succeeded locally with npm install)_
- [x] `cd frontend && npm run lint`
- [x] `cd frontend && npm run build`

## Smoke via Compose
- [ ] `docker compose down -v` (optional reset) _(pending)_
- [ ] `docker compose up --build` _(pending; run to verify after compose fix)_
- Confirm:
  - API reachable: `curl http://localhost:8000/health`
  - Frontend reachable: `http://localhost:5173`
  - Alembic migration ran without errors in API logs.

## Performance / EXPLAIN
- [ ] Populate sample data (e.g., demo@example.com) then run:
  - `cd backend && DATABASE_URL=... python scripts/benchmark_summary.py <user_id> [start_date] [end_date]`
- [ ] Capture EXPLAIN output and p95 latency notes in PR/issue. _(pending; not executed yet)_
