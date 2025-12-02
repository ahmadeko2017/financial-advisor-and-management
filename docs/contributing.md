# Panduan Kontribusi (Ringkas)

## Alur Kerja
- Gunakan branch feature: `feature/<deskripsi-singkat>`.
- PR kecil, terfokus; cantumkan issue/epik terkait.
- Wajib lint + test lokal sebelum PR.

## Commit & Format
- Format commit: `type(scope): message` (contoh: `feat(api): add transactions endpoint`).
- Gunakan formatter/linter sesuai stack (Python: black/isort/ruff; JS: prettier/eslint).

## Migrasi & DB
- Tambah migrasi untuk perubahan skema; pastikan idempotent.
- Update dokumen terkait (OpenAPI, schema doc) jika ada perubahan.

## Dokumentasi
- Perbarui `docs/adr` jika ada keputusan arsitektur.
- Jaga sinkron antara OpenAPI draft dan implementasi.

## Testing
- Unit test untuk business logic, minimal coverage kritikal.
- Smoke test endpoint utama (auth, transaksi) di CI.

## Review
- Deskripsikan perubahan, langkah uji, dan impact backward compatibility di PR.
- Tangani feedback reviewer dengan commit terpisah.
