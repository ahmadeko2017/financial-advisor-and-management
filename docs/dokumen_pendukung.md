# Dokumen Pendukung & Rekomendasi Tahap Awal

Dokumen ini melengkapi `arsitektur_solusi_ai_financial_tracker.md` dengan daftar dokumentasi pendukung yang perlu disiapkan agar pengembangan awal berjalan lancar.

## Prioritas Tinggi (sebelum sprint 1 dimulai)
- **Project Brief & Scope**: tujuan, non-goals, tipe user (personal/UMKM), KPI awal.
- **Glosarium & Asumsi Domain**: definisi income/expense, akun, kategori, budget, goal; asumsi mata uang, timezone, dan periodisasi laporan.
- **Architecture Decisions (ADR)**: catat keputusan teknologi utama (backend, DB, storage, gateway, worker, OCR/AI approach).
- **Backlog Awal & Roadmap**: epik/sprint awal (auth, akun/kategori, transaksi manual, dashboard dasar); definisi “done”.
- **Desain Data & Skema Database** (v0): tabel inti (`users`, `accounts`, `categories`, `transactions`, `budgets`, `financial_goals`, `advisor_insights`), indeks kunci, relasi, strategi soft delete.
- **Kontrak API Draft (OpenAPI)**: endpoint inti (auth, akun, kategori, transaksi CRUD, import, dashboard summary); format error & pagination.
- **Standar Kategori & Aturan Bisnis**: daftar kategori default, aturan validasi transaksi (mis. amount > 0), aturan budget/goal.
- **Security & Privacy Checklist**: JWT, enkripsi at-rest/ in-transit, kebijakan password, PII yang disimpan, retensi data.
- **Konfigurasi Lingkungan**: contoh `.env.example`, dependency minimum (Python/Node), cara menjalankan dev server + worker.
- **Contribution Guide Ringkas**: gaya commit, branching, lint/format, cara menambah migrasi, cara menambah/ubah ADR.

## Prioritas Menengah (setelah sprint 1, sebelum fitur AI penuh)
- **Desain Pipeline Import & OCR**: format CSV/Excel yang didukung, validasi, error handling, SLA proses batch, contoh payload receipt.
- **Spesifikasi Layanan AI Kategorisasi**: input/output JSON, skema label kategori, baseline model (mis. TF-IDF + LR), metrik evaluasi (accuracy, F1 macro).
- **Dataset & Labeling Guide**: sumber data, cara labeling transaksi, kebijakan privasi data latih, split train/val/test.
- **Plan MLOps**: penyimpanan artefak model, versi model, jadwal retrain, threshold confidence & fallback.
- **Background Jobs & Scheduler**: daftar job (import, OCR, insight), SLA, retry policy, observability per job.
- **Monitoring & Observability**: metric yang dipantau (latency API, error rate, job duration), log format, trace context.
- **Operasional & Runbook**: prosedur incident, rollback, backup/restore DB + storage, rotasi kredensial.
- **Rencana Rilis**: versioning API, migration checklist, strategi backward compatibility.

## Prioritas Lanjutan (saat fitur advisor & LLM ditambahkan)
- **Rule Engine Advisor Spec**: daftar rule, kondisi, output insight terstruktur; prioritas dan severity.
- **LLM Adapter & NLG Guide**: prompt template, guardrail, batasan biaya, caching, safe completion (no PII leakage).
- **Anomaly & Forecasting Spec** (opsional): definisi anomali, metrik deteksi, skema output alert.
- **UX Copy & Tone of Voice**: panduan bahasa untuk insight/rekomendasi, konteks lokal (ID).

## Saran Struktur Folder & Nama Berkas
- `docs/adr/ADR-0001-backend-stack.md`
- `docs/backlog_roadmap.md`
- `docs/db_schema_v0.md`
- `docs/api/openapi_draft.yaml`
- `docs/domain_glossary.md`
- `docs/security_privacy_checklist.md`
- `docs/pipeline_import_ocr.md`
- `docs/ai/category_classifier_spec.md`
- `docs/mlops_plan.md`
- `docs/monitoring_observability.md`
- `docs/runbook_operasional.md`
- `docs/contributing.md`
- `docs/env.example` (atau ditempatkan di root sebagai `.env.example`)

## Langkah Berikutnya
1) Kunci scope sprint 1 dan buat backlog + definition of done.  
2) Finalisasi skema DB v0 dan draft OpenAPI untuk endpoint inti.  
3) Tulis ADR untuk keputusan stack (backend, DB, storage, worker, OCR/AI approach).  
4) Siapkan `.env.example` + panduan run dev, lalu tambahkan checklist security dasar.  
5) Jika siap ke AI, buat spesifikasi service kategori + dataset/labeling guide.  
