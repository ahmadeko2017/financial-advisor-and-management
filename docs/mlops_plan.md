# Rencana MLOps (Awal)

## Versioning & Artefak
- Simpan model + vectorizer di storage S3-compatible dengan path `models/category/{version}/`.
- Catat metadata (versi, metrik, tanggal, dataset hash) di DB atau file manifest.

## Training Pipeline (Offline)
- Ambil data label terbaru (transactions dengan status confirmed).
- Clean/preprocess → split train/val/test.
- Train baseline (TF-IDF + LR/SVM) → simpan metrik.
- Simpan artefak + manifest → tandai versi kandidat.

## Deployment
- Mode 1: model embedded di backend (muat saat start).
- Mode 2: service terpisah; gunakan endpoint predict; caching model di memori.
- Rollout: manual switch versi aktif melalui config/env.

## Monitoring
- Koleksi prediksi vs feedback (kategori yang diubah user).
- Hitung akurasi sampel berkala, F1 macro.
- Pantau distribusi input (description length, amount) untuk drift indikasi.

## Retrain
- Trigger terjadwal (bulanan) atau threshold label baru.
- Keep last N model untuk rollback.
- Uji di dataset holdout sebelum dipromosi.

## Governance & Privasi
- Dokumentasikan consent data training.
- Jangan sertakan PII mentah; masking jika diperlukan.
- Audit log untuk perubahan model aktif.
