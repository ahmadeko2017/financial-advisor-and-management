# ADR-0001: Backend Stack & Service Pattern

- Status: Proposed
- Date: 2024-04-xx
- Deciders: Tech Lead, Backend Lead
- Context: Kita butuh stack backend yang cepat dikembangkan, mudah dioperasikan, dan siap integrasi AI (classifier/OCR) serta worker background.

## Keputusan
- Backend utama menggunakan **FastAPI (Python)**.
- Worker background menggunakan **Celery + Redis**.
- Database utama **PostgreSQL**.
- Storage file **S3-compatible** (MinIO di dev, S3 di prod).
- Reverse proxy **Traefik/Nginx**.
- Format API **REST** dengan dokumentasi **OpenAPI**.

## Alasan
- FastAPI: performa baik, tipe hint, dukungan OpenAPI otomatis, ekosistem AI/data kuat (sklearn/transformers).
- Celery + Redis: battle-tested untuk job import/OCR/insight.
- PostgreSQL: relasional, dukungan JSONB, fitur indexing matang.
- S3-compatible: sederhana untuk receipt/CSV storage lintas environment.
- REST + OpenAPI: mudah untuk frontend dan automation testing.

## Konsekuensi
- Tim perlu standar Python (lint/format, dependency management).
- Perlu containerisasi terpisah untuk API, worker, Redis, PG, storage.
- Monitoring harus mencakup API dan worker metrics.
- Jika skala naik, pertimbangkan pemisahan AI service menjadi container sendiri.

