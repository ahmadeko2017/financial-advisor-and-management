# Arsitektur Backend

## Tujuan
Layanan API yang mengelola auth, akun, kategori, transaksi, budget/goal, integrasi AI/ML & OCR, serta menyediakan endpoint dashboard/advisor.

## Komponen
- **API Service (FastAPI)**: endpoint REST + OpenAPI, validasi schema, middleware auth.
- **DB (PostgreSQL)**: data relasional (users, accounts, categories, transactions, budgets, goals, advisor_insights, import_jobs, receipts).
- **Cache/Queue (Redis)**: session rate-limit/cache ringan; broker Celery.
- **Worker (Celery)**: job import CSV/Excel, OCR, advisor insight, retraining trigger.
- **Object Storage (MinIO/S3)**: simpan file CSV/Excel, struk, artefak model.
- **Reverse Proxy (Traefik/Nginx)**: TLS termination, routing API, rate limiting dasar.

## Modul Logis (API)
- Auth & Users: JWT access/refresh, RBAC (user/admin).
- Accounts & Categories: CRUD akun, kategori global + custom.
- Transactions: CRUD + integrasi classifier (status predicted/confirmed).
- Import: upload file → buat import_job → worker proses.
- Receipts: upload struk → kirim ke OCR service → parser → transaksi.
- Dashboard: agregasi income/expense, top kategori, saldo.
- Advisor: rule engine + integrasi LLM adapter opsional.
- Admin/Monitoring: health, metrics.

## Integrasi Eksternal
- **AI Service** (kategori/anomali/LLM): HTTP internal.
- **OCR Service**: HTTP internal untuk ekstraksi teks.
- Storage S3: via SDK (boto3/minio).

## Pola & Non-Fungsional
- **Transport**: HTTPS di depan proxy.
- **Auth**: Bearer JWT, refresh token rotasi, blacklist opsional.
- **Error/Log**: format seragam JSON; masking data sensitif.
- **Migration**: Alembic (jika Python); schema versioned.
- **Monitoring**: Prometheus metrics + structured logs; health endpoint.
- **Scalability**: API stateless, scale horizontal; worker scale by queue depth.
- **Resilience**: retry Celery untuk job import/OCR; circuit breaker ke AI/OCR jika perlu.

## Data Flow Singkat
1) Request masuk proxy → API FastAPI.
2) API baca/ tulis ke Postgres; kirim file ke storage jika perlu.
3) Pekerjaan berat/asinkron dikirim ke Celery (Redis broker).
4) API memanggil AI/OCR internal service untuk kategori/OCR; hasil disimpan kembali.

