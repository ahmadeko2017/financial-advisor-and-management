# Runbook Operasional (Ringkas)

## Health Check
- API: `GET /health` harus 200.
- Worker: cek queue length Redis, pastikan worker process aktif.
- OCR/AI service: ping endpoint status.

## Start/Restart Service
- Docker Compose: `docker compose up -d api worker redis db minio`.
- Restart komponen bermasalah: `docker compose restart <service>`.
- Setelah restart API, pastikan migrasi sudah jalan.

## Migrasi DB
- Jalankan migrasi sebelum deploy baru.
- Jika gagal, rollback migrasi terakhir dan cek log error.

## Incident Cepat
- API error rate naik: cek log, periksa DB latency, cek service AI/OCR upstream.
- Queue menumpuk: tambahkan worker instance, periksa job gagal berulang.
- Storage penuh: bersihkan file test, tambah kapasitas, pastikan lifecycle policy.

## Backup/Restore
- Backup DB harian; uji restore berkala di environment terpisah.
- Backup bucket storage (snapshot atau replicate).

## Kredensial & Secret
- Rotasi berkala; simpan di secret manager atau `.env` terenkripsi.
- Jangan commit `.env`.

## Kontak
- Tentukan on-call list dan kanal eskalasi (chat/phone) di dokumen terpisah.
