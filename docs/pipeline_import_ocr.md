# Pipeline Import CSV/Excel & OCR Struk

## Import CSV/Excel
- **Input**: file CSV/Excel dengan kolom minimal: `date`, `description`, `amount`, `type`, `account`, `category?`.
- **Validasi**: ukuran file (mis. <10MB), tipe mime, header wajib, amount numerik, date parsable (YYYY-MM-DD atau DD/MM/YYYY).
- **Proses**:
  1. Simpan file ke storage; buat `import_job` status `pending`.
  2. Worker parse per baris → normalisasi → buat transaksi.
  3. Panggil classifier kategori untuk tiap transaksi (async/batch).
  4. Rekap summary (total baris, sukses, gagal) → update job `completed/failed`.
- **Error Handling**: kumpulkan error per baris; simpan di summary JSONB; berikan endpoint untuk fetch hasil.
- **SLA**: target <5 menit untuk 5k baris; worker dapat diskalakan horizontal.

## OCR Struk
- **Input**: gambar (jpg/png/pdf kecil), batas ukuran mis. 2MB.
- **Proses**:
  1. Simpan file → record `receipts` status `pending_ocr`.
  2. Kirim ke OCR service; terima teks mentah.
  3. Parser ekstrak tanggal, total, merchant (heuristik/regex).
  4. Buat transaksi dengan source `ocr`; panggil classifier kategori.
  5. Update receipt `parsed` + simpan payload OCR/parsed.
- **Error Handling**: fallback manual entry jika OCR gagal; tandai status `failed` + alasan.
- **SLA**: target <10 detik per struk (single), batch via worker jika antrean besar.

## Notifikasi & UX
- Tampilkan status job di UI (pending/running/completed/failed).
- Sediakan file log ringkas atau daftar baris gagal untuk diunduh.
- Beri pilihan mapping kolom ketika format CSV berbeda (preset bank/e-wallet).
