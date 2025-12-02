# Backlog & Roadmap Awal

## Phase 1 – Core Non-AI (Sprint 1-2)
- Auth (register/login), JWT, refresh token.
- CRUD akun + kategori default.
- CRUD transaksi manual.
- Dashboard dasar: income vs expense, kategori top.
- Infrastruktur dev: Docker compose, lint/format, CI basic, monitoring healthcheck.

## Phase 2 – AI Kategori & UX (Sprint 3-4)
- Integrasi Category Classifier baseline.
- Status transaksi: predicted vs confirmed.
- Edit/override kategori oleh user; feedback loop simpan label.
- Filter/pencarian transaksi, eksport CSV.

## Phase 3 – Import & OCR (Sprint 5-6)
- Upload CSV/Excel + job async import.
- Upload struk → OCR → parsing → transaksi otomatis.
- Error handling + notifikasi job selesai/gagal.

## Phase 4 – Advisor Rule-Based (Sprint 7-8)
- Budget & goals CRUD.
- Rule engine insight: overspend, ratio income/expense, progress goals.
- Insight list + timeline.

## Phase 5 – LLM Advisor & Optimalisasi (Sprint 9+)
- LLM adapter untuk narasi insight (opsional).
- Anomali/forecasting dasar.
- Optimasi performa, caching, observability penuh.

## Definition of Done (ringkas)
- Kode terlinting, test utama lulus.
- Endpoint ter-dokumen (OpenAPI).
- DB migration tersedia.
- Monitoring dasar (health, error rate).
- UAT singkat/QA checklist terpenuhi.

