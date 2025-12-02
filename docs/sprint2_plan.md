# Sprint 2 Plan (Dashboard Dasar & Hardening)

Durasi: 2 minggu. Fokus pada summary dashboard, hardening transaksi (pagination/filter), error handling seragam, dan CI lint/test.

## Goals
- Insight awal: income vs expense, balance, top kategori.
- Pagination + filter/search transaksi stabil.
- Error handling seragam di backend.
- Lint/test berjalan di pipeline (backend & frontend).

## User Stories
1. Sebagai user, saya melihat ringkasan income, expense, dan balance periode berjalan.
2. Sebagai user, saya melihat kategori teratas pengeluaran.
3. Sebagai user, saya bisa memfilter/paginate transaksi agar cepat ditemukan.
4. Sebagai tim dev, saya mendapat error response seragam dan lint/test hijau di CI.

## Task Teknis (Backend)
- Endpoint dashboard summary: income, expense, balance, top N kategori (periode bulanan default; support query start/end).
- Tambah pagination + filter (search deskripsi, kategori, tipe, tanggal) pada `/transactions`.
- Error handling seragam (schema Error) untuk 4xx/5xx di router utama.
- Indexing tambahan untuk agregasi dan filter transaksi (`user_id, occurred_at`, `user_id, category_id, occurred_at`).
- OpenAPI update untuk summary + pagination params + error response.
- Alembic migrasi untuk indeks baru.
- Aktifkan lint/test di Jenkins (pytest; optional ruff/black jika siap).

## Task Teknis (Frontend)
- Halaman Dashboard: kartu income/expense/balance + chart kategori/top spend.
- Integrasi endpoint summary (periode selector).
- Pagination + filter/search di tabel transaksi.
- Tampilkan error response seragam (toast/inline).
- Pastikan env frontend (`VITE_API_BASE_URL`) terdokumentasi.

## Acceptance Criteria (Exit Checklist)
- Endpoint `/dashboard/summary` mengembalikan income, expense, balance, top kategori akurat untuk periode yang diminta.
- `/transactions` mendukung pagination + filter (tanggal, kategori, tipe, search) dan stabil.
- Error response konsisten (schema Error) untuk kasus umum (401/403/404/400/500).
- Indeks agregasi terpasang via migrasi; query summary tidak menjadi bottleneck pada data contoh.
- CI lint/test backend & frontend hijau.
- Halaman dashboard menampilkan ringkasan + top kategori; tabel transaksi dapat dipaginate/filter/search.

## Risks/Notes
- Kinerja agregasi: pastikan indeks tepat; batasi periode default (mis. bulan berjalan).
- Konsistensi error: pastikan middleware/exception handler tidak bocor stacktrace.
- FE chart: pilih lib ringan (mis. Recharts/ECharts) sesuai footprint.
- Data seed: gunakan data demo (demo@example.com) untuk verifikasi cepat.
