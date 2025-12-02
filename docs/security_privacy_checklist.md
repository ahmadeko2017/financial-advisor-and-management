# Security & Privacy Checklist (Awal)

## Akses & Auth
- Semua API lewat HTTPS.
- JWT access + refresh; rotasi refresh token; expiry wajar.
- RBAC minimal: user vs admin.

## Data Proteksi
- Password: bcrypt/argon2.
- Pertimbangkan enkripsi kolom sensitif (mis. token akses bank jika ada).
- Jangan simpan nomor rekening lengkap; mask/partial.
- Backup terenkripsi; uji restore berkala.

## API & Input
- Validasi payload (schema-based).
- Rate limiting di gateway.
- Pagination pada list endpoints.
- Uniform error format tanpa bocor stacktrace.

## File & Storage
- Scan ukuran/tipe file upload (CSV/Excel/receipt).
- Pisah bucket per environment; restrict public access.
- Signed URL untuk akses file jika diperlukan.

## Logging & Audit
- Audit log untuk login, impor, perubahan konfigurasi.
- Jangan log data sensitif (password, token, PII penuh).

## Compliance & Retensi
- Definisikan retensi data user (hapus akun = hapus data? soft delete?).
- Kebijakan penggunaan data untuk pelatihan model; opt-in/opt-out.

## DevSecOps
- Secret di `.env`/secret manager, bukan di repo.
- Dependabot atau scanner vulnerability deps.
- Minimal SAST (lint keamanan) + unit test untuk auth/role.
