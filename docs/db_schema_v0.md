# Skema Database v0 (Konseptual)

Gunakan PostgreSQL. Tipe data referensial, gunakan UUID untuk id.

## Tabel Inti
- `users`: `id (uuid)`, `email`, `password_hash`, `name`, `role`, `created_at`, `updated_at`, `deleted_at?`.
- `accounts`: `id`, `user_id -> users`, `name`, `type` (cash/bank/e-wallet), `currency`, `balance_snapshot?`, `created_at`, `updated_at`.
- `categories`: `id`, `user_id (nullable untuk global)`, `name`, `type` (income/expense/transfer), `parent_id?`, `created_at`.
- `transactions`: `id`, `user_id`, `account_id`, `category_id?`, `type` (income/expense/transfer), `amount (decimal)`, `currency`, `description`, `occurred_at (timestamptz)`, `source` (manual/import/ocr), `status` (predicted/confirmed), `ai_confidence?`, `receipt_id?`, `import_job_id?`, `created_at`, `updated_at`.
- `budgets`: `id`, `user_id`, `category_id`, `period` (month), `amount_limit`, `currency`, `created_at`.
- `financial_goals`: `id`, `user_id`, `name`, `target_amount`, `current_amount`, `deadline?`, `priority?`, `created_at`.
- `advisor_insights`: `id`, `user_id`, `period_start`, `period_end`, `type` (overspend/ratio/goal/etc), `payload JSONB`, `severity`, `generated_by` (rule/llm), `created_at`.
- `import_jobs`: `id`, `user_id`, `source` (csv/excel), `file_path`, `status` (pending/running/completed/failed), `summary JSONB`, `created_at`, `updated_at`.
- `receipts`: `id`, `user_id`, `file_path`, `status` (pending_ocr/parsed/failed), `ocr_text?`, `parsed_payload JSONB`, `created_at`, `updated_at`.

## Indeks & Integritas
- Gunakan `created_at` + `user_id` indeks untuk query per user.
- `transactions (user_id, occurred_at)` indeks untuk laporan per periode.
- `categories (user_id, type, name)` unique (user_id null untuk global).
- FK dengan `ON DELETE RESTRICT` untuk akun/kategori; pertimbangkan soft delete untuk data sensitif.

## Migrasi & Praktik
- Kelola migrasi dengan Alembic (FastAPI) atau Prisma/Knex (Node) sesuai stack.
- Simpan `created_at/updated_at` via trigger atau aplikasi.
- Pertimbangkan `currency` kolom konsisten, default mis. `IDR`.

