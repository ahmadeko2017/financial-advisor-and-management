# TODO (Codex)

- [ ] Run `alembic upgrade head` against target DB (Postgres) to ensure transaction indexes created.
- [ ] Validate Jenkins pipeline end-to-end (podman build/run, FE lint/build, optional ruff/black).
- [ ] Improve frontend dashboard: add chart for top categories and ensure start/end range selector UX is smooth.
- [ ] Run EXPLAIN/benchmark script (`python scripts/benchmark_summary.py <user_id>`) on sample data and document results.
