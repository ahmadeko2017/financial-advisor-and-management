# Arsitektur AI/ML

## Tujuan
Layanan/komponen AI untuk klasifikasi kategori transaksi, anomaly detection, forecasting, dan LLM advisor (opsional) dengan jalur MLOps terkontrol.

## Komponen
- **Category Classifier Service**: HTTP internal; model baseline TF-IDF + LR/SVM; batch predict untuk import.
- **Anomaly Detection** (opsional): deteksi overspend/outlier per kategori/periode.
- **Forecasting** (opsional): prediksi pengeluaran per kategori.
- **LLM Adapter** (opsional): menerima summary JSON → narasi insight; bisa lokal (Ollama) atau API eksternal.
- **Artefak Storage**: S3/MinIO path `models/{service}/{version}/`.
- **Metadata/Registry**: manifest model (versi, metrik, tanggal, dataset hash) di DB atau file.

## Data & Training
- Sumber label: transaksi dengan kategori confirmed (opt-in), seed dataset internal.
- Preprocess: text cleaning, handling imbalance (class weights/oversampling).
- Evaluasi: F1 macro utama; top-3 accuracy; log confusion matrix.
- Retrain trigger: jadwal bulanan atau setelah N label baru; simpan N versi untuk rollback.

## Deployment Pola
- **Embedded**: model dimuat di backend API (lebih sederhana, latensi rendah).
- **Service Terpisah**: container sendiri, endpoint `/ai/category/predict`; scale horizontal; gunakan cache model in-memory.
- Health & metrics: expose `/health` + metrik prediksi (count, latency, confidence histogram).

## Integrasi dengan Backend
1) Backend kirim transaksi baru ke classifier → terima `category_id` + `confidence`.
2) Jika confidence < threshold → tandai `uncategorized` dan minta konfirmasi user.
3) Feedback user (override kategori) dicatat untuk dataset retrain.
4) Advisor/LLM: backend kirim summary ke LLM adapter → terima narasi insight.

## Keamanan & Privasi
- Data training bebas PII; masking nomor/kode unik.
- Consent penggunaan data untuk training; audit log perubahan model aktif.
- Batasi akses service AI hanya internal network.
