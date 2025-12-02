# Sprint 1 Plan (Fondasi)

Durasi: 2 minggu. Fokus MVP dasar (auth, akun/kategori, transaksi manual, healthcheck) dengan pipeline container berbasis Podman.

## Goals
- User dapat registrasi/login (JWT).
- CRUD akun & kategori default tersedia.
- Input transaksi manual (create/read).
- Healthcheck endpoint siap untuk monitoring.
- Lingkungan dev kontainer berjalan via Podman/compose; unit test dasar berjalan di kontainer.

## User Stories (Sprint 1)
1. Sebagai user, saya bisa registrasi & login agar data saya privat.
2. Sebagai user, saya bisa membuat dan mengelola akun (cash/bank/e-wallet).
3. Sebagai user, saya bisa melihat dan mengelola kategori default.
4. Sebagai user, saya bisa menambahkan transaksi manual dan melihat daftar transaksi.
5. Sebagai tim dev, saya bisa menjalankan layanan dan test via Podman container.

## Task Teknis
- Setup struktur project + FastAPI skeleton + health endpoint.
- Skema DB awal + migrasi pertama (users, accounts, categories, transactions).
- Implement auth (register/login), akun CRUD, kategori listing/CRUD, transaksi create/read.
- Seed kategori default (via migrasi/seed script).
- Lengkapi OpenAPI draft sesuai endpoint Sprint 1.
- Lint/test basic (pytest) dan jalankan dalam kontainer.
- Dockerfile, docker-compose (db, redis, api), Makefile helper, env.example.
- Jenkinsfile pipeline dengan Podman build/test/smoke.
- FE shell (Vite + React + Tailwind) dengan layar auth/akun/kategori/transaksi (UI siap dihubungkan ke API).
  - FE container build & dev (podman compose).
  - Backend container + migration tooling (Alembic) + .env.example di backend.

## Acceptance Criteria (Exit Checklist Sprint 1)
- `/health` 200.
- Register + login mengembalikan JWT, akses endpoint protected berhasil.
- CRUD akun dan transaksi create/read berjalan dengan validasi amount/date.
- Kategori default muncul minimal view/list.
- OpenAPI sesuai implementasi Sprint 1.
- Test dasar hijau via `podman run IMAGE pytest`.
- `podman compose up` berfungsi (api + db + redis), API dapat diakses di `http://localhost:8000`.
- Tidak ada blocker kritis (P1) terbuka; P2 punya workaround.

## Testing dengan Podman
```bash
# Build image dan jalankan unit test
podman build -t fintrack-api:dev .
podman run --rm fintrack-api:dev pytest

# Jalankan stack dev (api + db + redis)
COMPOSE_PROJECT_NAME=fintrack podman compose -f docker-compose.yml up -d

# Smoke test health endpoint
curl http://localhost:8000/health

# Matikan stack
COMPOSE_PROJECT_NAME=fintrack podman compose -f docker-compose.yml down
```

## Deliverables Sprint 1
- API dasar berjalan (auth, akun, kategori, transaksi create/read).
- OpenAPI diperbarui.
- Migrasi DB pertama.
- CI Jenkins tahap build + test + smoke via Podman.
- Dokumentasi cara jalanin lokal (README singkat atau update docs).
