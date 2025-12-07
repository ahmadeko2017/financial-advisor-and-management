# Spesifikasi Category Classifier (Draft)

## Tujuan
Prediksi kategori transaksi otomatis untuk mempercepat input dan memberi insight awal, dengan confidence threshold dan opsi override oleh user.

## Input
- `description`: string
- `amount`: float
- `type`: enum `income/expense/transfer`
- `merchant?`, `account_type?`, `timestamp?` (opsional, jika tersedia)

## Output
- `category_id`: string
- `confidence`: float 0-1
- `labels`: optional distribusi skor per kategori untuk UI/analitik

## Model Baseline
- Pipeline: text preprocess (lowercase, punctuation strip) → TF-IDF → Logistic Regression / Linear SVM.
- Fallback rule: jika confidence < threshold, tag sebagai `uncategorized` dan minta konfirmasi user.
- Persist artefak: vectorizer + model disimpan di storage S3-compatible.

## Endpoint/Interface
- HTTP (internal): `POST /ai/category/predict`
  - Request: `{ description, amount, type, metadata? }`
  - Response: `{ category_id, confidence, labels? }`
- Batch mode optional: terima array transaksi untuk import job.

## Training Data
- Sumber: transaksi user yang sudah dikonfirmasi (opt-in), seed dataset publik/bootstrapped kategori.
- Label set: selaraskan dengan tabel `categories` (global).
- Split: train/val/test, stratified per kategori.
- Class imbalance: gunakan class weights atau oversampling jika perlu.

## Evaluasi
- Metrik: F1 macro (utama), accuracy, top-3 accuracy.
- Monitoring drift: distribusi prediksi per kategori, confidence histogram, akurasi sampel berkala.

## Retraining & Deployment
- Frekuensi awal: bulanan atau setelah N label baru (mis. 1k).
- Versioning: `model_version` disimpan di DB dan response.
- Rollback: simpan N versi terakhir; bisa pilih versi aktif via config.

## Keamanan & Privasi
- Hindari menyimpan PII dalam teks training; masking jika ada nomor unik.
- Data user dipakai training hanya jika diizinkan; dokumentasikan opt-in.

## Rencana Implementasi (Backend Inline)
- Modul: `backend/app/ai/category_classifier.py`
  - `train(df)` → simpan artefak (vectorizer + model) ke `ml_artifacts/category_model.pkl` + `meta.json` (model_version, created_at, threshold).
  - `load_model()` → lazy load artefak; fallback ke None jika belum ada.
  - `predict(payload)` → return `{category_id|None, confidence, top_k: [{label, score}]?, model_version}` dengan fallback `None` jika confidence < threshold atau model belum tersedia.
  - Threshold default: 0.5 (konfigurabel via env).
- Integrasi transaksi:
  - Field baru di `transactions`: `predicted_category_id`, `predicted_confidence`, `status` (`predicted`/`confirmed`).
  - Pada `POST /transactions`: jika `category_id` kosong dan model tersedia, panggil predict; simpan hasil sebagai predicted* dan set status `predicted`. Jika user mengirim kategori, status `confirmed` dan jadi data label.
  - Endpoint khusus: `POST /ai/predict_category` (input deskripsi/amount/type) untuk UI/QA.
- Logging/monitoring:
  - Log prediksi: user_id hashed, category_predicted, confidence, threshold_hit (bool), fallback flag.
  - Expose metrik sederhana (counter prediksi, hit/miss threshold) via log; opsi Prometheus nanti.

## Checkpoint Pengembangan
1. Schema & migration
   - [ ] Tambah kolom `predicted_category_id`, `predicted_confidence`, `status` di `transactions`.
   - [ ] Alembic migration dibuat dan dijalankan.
2. Model utilities
   - [ ] Modul classifier dengan load/predict; artefak dummy (baseline kosong) untuk runtime.
   - [ ] Config threshold via env.
3. API & integrasi
   - [ ] Endpoint `POST /ai/predict_category` (auth).
   - [ ] Hook di `POST /transactions` untuk auto-predict saat kategori kosong.
   - [ ] OpenAPI/schemas diperbarui (field predicted* dan status).
4. Logging/monitoring
   - [ ] Log prediksi (confidence, threshold hit, fallback).
5. Testing
   - [ ] Unit test model wrapper: predict returns None when no model, respects threshold, returns label when above threshold.
   - [ ] API test: `/ai/predict_category` tanpa model → 200 dengan kategori null; dengan mock model → kategori terisi.
   - [ ] Transactions flow: create tanpa kategori memanggil predict (mock), status `predicted`; update/confirm menyimpan kategori dan status `confirmed`.

## Catatan Pengujian
- Gunakan fixture/mock untuk model agar test tidak bergantung pada artefak berat.
- Tambah sample data kecil untuk e2e predict (fit sederhana) bila perlu.
