# Arsitektur OCR

## Tujuan
Layanan untuk ekstraksi teks dari foto struk dan parsing transaksi otomatis.

## Komponen
- **OCR Service**: container terpisah (Tesseract/PaddleOCR); endpoint HTTP internal `POST /ocr`.
- **Parser**: modul di backend/worker yang memproses teks mentah → tanggal, total, merchant, item (opsional).
- **Storage**: file struk disimpan di S3/MinIO; path dicatat di tabel `receipts`.
- **Worker**: job async untuk antrean OCR jika volume tinggi.

## Alur
1) User upload struk via API → file ke storage → buat record `receipts (pending_ocr)`.
2) Backend/worker panggil OCR service dengan signed URL/file.
3) OCR service kembalikan teks + posisi/konfiden (jika tersedia).
4) Parser ekstrak field, buat transaksi (source=ocr), panggil classifier kategori.
5) Update status receipt (`parsed/failed`) + simpan payload OCR/parsed untuk audit.

## Non-Fungsional
- **SLA**: target <10 detik per struk; batch via worker jika antrean.
- **Validasi**: batas ukuran/format file (jpg/png/pdf kecil), reject file berbahaya.
- **Keamanan**: service internal; tidak expose publik; signed URL jika perlu.
- **Monitoring**: metrik latency OCR, success/error rate, queue depth.
- **Fallback**: jika OCR gagal → tawarkan input manual; tampilkan alasan gagal.

## Teknologi
- OCR engine: Tesseract (ringan) atau PaddleOCR (lebih akurat).
- Service wrapper: FastAPI/Flask ringan; autoscale kontainer jika beban tinggi.
- Parser: regex + heuristik; bisa digabung NLP ringan jika butuh akurasi lebih.
