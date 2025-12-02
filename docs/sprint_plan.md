# Rencana Pengembangan: MVP & Iterasi Sprint

Format sprint 2 minggu. Fokus MVP dulu, lalu perluasan AI/OCR/Advisor.

## MVP Scope (Target: Sprint 1-2)
- Auth (register/login) + JWT.
- Akun & kategori default (CRUD dasar).
- Transaksi manual (CRUD) dengan status `confirmed`.
- Dashboard dasar: income vs expense, top kategori bulanan.
- Infrastruktur dev: Docker Compose, lint/format, migrasi DB awal, OpenAPI dasar, healthcheck.
- DoD MVP: endpoint utama berfungsi, migrasi tersedia, test dasar lulus, OpenAPI sinkron, deploy dev berhasil.

## Sprint Breakdown (Draft)

### Sprint 1: Fondasi & Core CRUD
- Goal: user bisa login, kelola akun/kategori, input transaksi manual.
- Deliverables: auth + JWT, akun/kategori CRUD, transaksi create/read, OpenAPI diperbarui, migrasi DB v0, lint/test basic.
- Risks/Notes: pastikan pagination & validasi amount/date, siapkan seed kategori default.
- Exit checklist: auth + akun/kategori + transaksi create/read berfungsi; OpenAPI sinkron; test hijau via kontainer; tidak ada blocker P1. Detail lihat `docs/sprint1_plan.md`.

### Sprint 2: Dashboard Dasar & Hardening
- Goal: insight awal income vs expense dan kategori top.
- Deliverables: endpoint summary dashboard, grafik sederhana di frontend, pagination/search transaksi, error handling seragam, CI lint+test, env.example final.
- Risks/Notes: cek performa agregasi; tambah indeks sesuai skema.
- Exit checklist: endpoint summary akurat dengan indeks memadai; pagination/search stabil; CI lint/test hijau; tidak ada blocker P1 pada dashboard.

### Sprint 3: AI Kategori Baseline
- Goal: auto-kategori dengan feedback user.
- Deliverables: service/pipeline classifier baseline (TF-IDF + LR), endpoint predict, integrasi transaksi (status predicted/confirmed), simpan feedback label, monitoring metrik dasar (log/metric).
- Risks/Notes: threshold confidence, fallback uncategorized; jaga privasi data latih.
- Exit checklist: model baseline ter-deploy; prediksi terintegrasi di transaksi; threshold bekerja (fallback uncategorized); metrik dasar tercatat; tidak ada blocker P1 pada alur transaksi.

### Sprint 4: Import CSV/Excel (Async)
- Goal: impor massal via job worker.
- Deliverables: upload endpoint, job import via worker, summary hasil, mapping kolom preset, error report per baris, notifikasi status job di UI.
- Risks/Notes: SLA 5k baris <5 menit; retry policy worker.
- Exit checklist: job import berjalan end-to-end; summary error tersedia; SLA tercapai pada dataset uji; tidak ada blocker P1 pada impor.

### Sprint 5: OCR Struk
- Goal: upload struk → OCR → parsing → transaksi otomatis.
- Deliverables: endpoint upload receipt, status receipt, panggil OCR service, parser heuristik, integrasi classifier kategori, UI status/gagal.
- Risks/Notes: batas ukuran/tipe file; fallback manual jika parsing gagal.
- Exit checklist: OCR → parser → transaksi otomatis berjalan untuk sampel; fallback manual tersedia; error handling jelas; tidak ada blocker P1 pada alur OCR.

### Sprint 6: Advisor Rule-Based
- Goal: insight overspend/ratio/goal progress tanpa LLM.
- Deliverables: budget & goals CRUD, rule engine sederhana, endpoint insight, tampilan insight di dashboard.
- Risks/Notes: validasi periode budget, prioritas insight, format payload stabil.
- Exit checklist: rule engine menghasilkan insight konsisten; budget/goals CRUD stabil; endpoint/UI menampilkan insight; tidak ada blocker P1 pada advisor.

### Sprint 7+: LLM Advisor & Optimasi
- Goal: narasi natural + optimasi performa/observability.
- Deliverables: LLM adapter (opsional), caching, anomaly/forecast dasar, alerting/monitoring lengkap, hardening keamanan.
- Risks/Notes: biaya LLM, guardrail PII, fallback jika LLM down.
- Exit checklist: LLM adapter memiliki fallback; observability alerting aktif; tidak ada blocker P1; performa/biaya terukur.

## Ketergantungan & Checklist Per Sprint
- Migrasi DB siap sebelum coding fitur terkait.
- OpenAPI diperbarui setiap perubahan endpoint.
- Lint/test wajib hijau sebelum merge.
- Update dokumentasi (ADR jika keputusan baru).
