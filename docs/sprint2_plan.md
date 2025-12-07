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

## Detail Tambahan (Resolusi Gap)
### Detail API `/dashboard/summary`
- `GET /dashboard/summary` (Bearer required, scope user). Timezone: Asia/Jakarta untuk interpretasi tanggal, disimpan UTC.
- Query params:
  - `start_date` (YYYY-MM-DD, optional): default hari pertama bulan berjalan pukul 00:00 lokal.
  - `end_date` (YYYY-MM-DD, optional): default sekarang lokal, diekspansi ke 23:59:59.
  - `top_limit` (int, optional): default 5, max 10.
  - Validasi: `start_date <= end_date`; jika tidak, 400 `VALIDATION_ERROR`.
- Response 200 schema:
  ```json
  {
    "period": { "start_date": "2025-02-01", "end_date": "2025-02-28" },
    "totals": { "income": "12000000.00", "expense": "3500000.00", "balance": "8500000.00" },
    "top_categories": [
      { "category_id": 3, "name": "Makan", "amount": "1500000.00", "type": "expense" }
    ],
    "currency": "IDR"
  }
  ```
  - `totals.*` dan `top_categories.amount` sebagai string desimal.
  - `top_categories` diurutkan desc by amount; kosong bila tidak ada data.
- Error schema seragam `{ "code": "VALIDATION_ERROR", "message": "start_date must be before end_date" }`, dll untuk 401/403/404/500.

### Edge Case Transaksi & Filter
- Timezone: semua perhitungan tanggal di backend di-parse sebagai lokal Asia/Jakarta, disimpan UTC; FE mengirim tanggal tanpa jam dianggap 00:00 lokal.
- Filter tanggal inklusif untuk `start_date` dan `end_date` (end diluaskan ke 23:59:59).
- Zero state: jika tidak ada data, totals bernilai "0.00" dan `top_categories`/list transaksi kosong; FE menampilkan empty state, bukan error.
- Kombinasi filter tanpa hasil: kembalikan 200 dengan list kosong, meta pagination tetap valid.

### Pagination, Sorting, dan Fallback
- Default `page=1`, `page_size=20`, `max_page_size=100`; `total_pages=0` jika tidak ada data.
- Default sort transaksi: `occurred_at` desc; sorting lain nanti disusulkan via white-list (desc/asc).
- Query invalid (page < 1, page_size < 1 atau > max): auto-fallback (reset/cap) dan kembalikan warning ringan di `pagination.warnings` untuk transparansi ke FE.

### Hardening/Keamanan
- Semua endpoint (kecuali `/health`) wajib Authorization Bearer; scoping berdasarkan `user_id` di token.
- Sanitasi input search: trim, limit 100 karakter, hindari wildcard tak terbatas; gunakan query terparameter.
- Rate limiting ringan untuk transaksi/summary (mis. 60 req/menit per user; implementasi via middleware sederhana atau gateway).

### Kinerja
- Target p95 latency summary < 300ms pada dataset contoh (50k transaksi/user). Pastikan indeks `user_id, occurred_at` dan `user_id, category_id, occurred_at`.
- Hindari full scan: gunakan batas periode default; dukung cache ringan in-memory 5 menit per user+periode jika query identik.
- Verifikasi indeks dengan EXPLAIN pada sample data; dokumentasikan hasil di PR.

### Error Handling & Observability
- Gunakan global exception handler FastAPI dengan schema `{ code, message, trace_id? }`; mapping: 400 VALIDATION_ERROR, 401 UNAUTHORIZED, 403 FORBIDDEN, 404 NOT_FOUND, 422 VALIDATION_ERROR, 500 INTERNAL_ERROR.
- Tambahkan trace_id/log_id di log dan response (jika tersedia) tanpa membocorkan stacktrace.
- Konsistensi FE: toast/inline membaca `message`; untuk debug gunakan trace_id bila ada.

### CI (Jenkins)
- Backend: `pip install -r requirements-dev.txt && python -m pytest`; opsi lint: `ruff check .` dan `black --check .` (aktifkan jika lingkungan siap).
- Frontend: `npm ci && npm run lint && npm run build`.
- Artifact/report: simpan coverage pytest (xml) dan log lint/build; set env `DATABASE_URL` dummy untuk test (mis. sqlite memori jika didukung) atau gunakan service postgres container.

### Frontend Detail
- Chart lib: Recharts (ringan) untuk top kategori; format angka/mata uang: locale `id-ID` dan currency `IDR`.
- State: loading skeleton untuk kartu/chart/tabel; empty state jelas; error state baca `message`.
- Env contract: `VITE_API_BASE_URL` wajib; contoh `.env.example` di repo frontend.

### Data Seed & Verifikasi
- Gunakan user demo (`demo@example.com`) dengan data transaksi terkontrol (income/expense beberapa kategori) agar nilai dashboard dapat diprediksi.
- Siapkan skenario uji: (1) ada data dalam periode, (2) periode tanpa data, (3) filter kombinasi tipe/kategori/tanggal menghasilkan kosong.

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
