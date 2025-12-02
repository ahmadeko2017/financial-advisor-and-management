# Glosarium & Asumsi Domain

- **Akun**: sumber dana (bank, e-wallet, cash) yang menampung transaksi.
- **Kategori**: klasifikasi transaksi (income/expense/transfer); ada global dan custom per user.
- **Transaksi**: peristiwa finansial dengan `amount`, `type`, `occurred_at`, `source`.
- **Budget**: batas pengeluaran per kategori/period (bulanan).
- **Goal/Financial Goal**: target tabungan/investasi user dengan `target_amount` dan deadline opsional.
- **Income vs Expense Ratio**: metrik untuk insight advisor.
- **Overspending**: kondisi expense > budget atau > ambang historis.
- **Source**: asal transaksi (`manual`, `import`, `ocr`).
- **Predicted vs Confirmed**: status kategori hasil AI vs yang sudah dikonfirmasi user.
- **Periodisasi**: default bulanan, timezone `Asia/Jakarta`, currency default `IDR`.
- **PII**: data identitas seperti email, nama, nomor rekening (hindari simpan nomor penuh).
