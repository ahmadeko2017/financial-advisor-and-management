# Monitoring & Observability (Awal)

## Metrics (API)
- Latency p50/p95/p99 per endpoint.
- Error rate (4xx/5xx), terutama auth dan transaksi.
- Throughput (req/s).

## Metrics (Worker)
- Job throughput/duration per tipe (import, ocr, insight).
- Retry count, dead-letter queue size.
- Queue length (Redis).

## Infra
- DB connections, query duration berat (aggregasi).
- Storage I/O (upload/download), ukuran bucket dev/prod.

## Logs
- Struktur JSON; sertakan trace/span id jika pakai tracing.
- Mask data sensitif.
- Log event penting: login sukses/gagal, import start/finish, OCR fail.

## Tracing
- Gunakan OpenTelemetry jika memungkinkan.
- Trace penting: request → DB query → call AI/OCR → response.

## Alerts (awal)
- API error rate > ambang (mis. 5% selama 5 menit).
- P95 latency > X ms.
- Worker queue length > ambang (mis. >500 job pending).
- OCR/classifier service unreachable.
- DB disk usage > 80%, backup gagal.
