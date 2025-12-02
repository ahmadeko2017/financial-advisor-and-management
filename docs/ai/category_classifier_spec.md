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
