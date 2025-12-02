# Arsitektur Solusi AI Financial Tracker + Dashboard + Financial Advisor

## 1. Gambaran Umum
Solusi ini adalah sistem **personal/UMKM financial tracking** yang dilengkapi dengan:

- Pencatatan transaksi multi-sumber (manual, impor CSV/Excel, foto struk/OCR)
- Otomatisasi kategori transaksi berbasis AI
- Dashboard keuangan interaktif (cashflow, kategori, akun)
- Modul **AI Financial Advisor** (insight, rekomendasi, budget & goal tracking)

Sistem dirancang modular agar dapat dikembangkan bertahap, dengan pemisahan yang jelas antara:

- **Presentation Layer (Dashboard/Web App)**
- **API & Business Logic Layer (Backend Service)**
- **AI/ML Layer (Model Service/Module)**
- **Data Layer (Database & Storage)**
- **Background Jobs & Scheduler**

---

## 2. Use Case Utama

1. **User Management & Akun**
   - Registrasi & login user
   - Manajemen akun keuangan (bank, e-wallet, cash)

2. **Transaksi & Data Input**
   - Input manual transaksi
   - Import mutasi via CSV/Excel
   - Upload foto struk → OCR → parsing → transaksi

3. **AI Kategorisasi Transaksi**
   - Prediksi kategori berdasarkan deskripsi, amount, pola historis
   - Menandai confidence & meminta konfirmasi user

4. **Dashboard & Laporan**
   - Cashflow bulanan
   - Breakdown kategori
   - Perbandingan income vs expense
   - Laporan periodik

5. **Financial Advisor**
   - Analisis pengeluaran vs income & budget
   - Deteksi overspending
   - Progress goals (dana darurat, tabungan, dsb.)
   - Insight & rekomendasi dalam bahasa natural

6. **Background Processing**
   - Re-kalkulasi metrik periodik
   - Training/refresh model AI
   - Pembuatan insight bulanan/mingguan otomatis

---

## 3. Arsitektur Logis (Logical Architecture)

### 3.1. Lapisan Presentasi (Frontend)

- **Web Dashboard (SPA)**
  - Dibangun dengan React/Next.js (atau framework serupa)
  - Modul UI:
    - Halaman Overview (summary & insight)
    - Halaman Transaksi (tabel, filter, edit kategori)
    - Halaman Budget & Goals
    - Halaman Import & OCR
    - Halaman Insight & Laporan
  - Berkomunikasi dengan Backend via REST/GraphQL API (HTTPS)

### 3.2. API & Business Logic Layer (Backend Service)

- Contoh teknologi: **FastAPI (Python)** atau **Node.js (NestJS)**
- Modul utama:

  1. **Auth & User Management Module**
     - JWT-based authentication
     - Session & refresh token

  2. **Accounts & Categories Module**
     - CRUD akun finansial
     - Global categories + custom categories per user

  3. **Transactions Module**
     - CRUD transaksi
     - Integrasi dengan AI Category Service
     - Integrasi dengan OCR Service

  4. **Import & OCR Module**
     - Endpoint upload CSV/Excel
     - Endpoint upload image struk
     - Pengiriman file ke OCR Service

  5. **Dashboard & Reports Module**
     - Aggregation query ke database
     - Endpoint untuk summary, charts, dan laporan

  6. **Advisor Module (Business Rules)**
     - Hitung metrik: income/expense ratio, kategori overspend, dsb.
     - Rule engine untuk menghasilkan insight terstruktur
     - Integrasi ke LLM Adapter (opsional) untuk natural language

  7. **Admin & Monitoring Module** (opsional)
     - Health check
     - Metrics endpoint (Prometheus)

### 3.3. AI/ML Layer

Dapat berupa:
- Library/module terintegrasi di backend, atau
- Service terpisah (microservice) jika skalanya besar.

Komponen:

1. **Category Classifier Service**
   - Input: teks deskripsi, amount, metadata
   - Output: `category_id`, `confidence`
   - Model: TF-IDF + Logistic Regression / Transformer + classifier

2. **Anomaly Detection Service**
   - Input: historis pengeluaran per kategori/periode
   - Output: flag anomali (boolean/probabilitas)

3. **Forecasting Service** (optional, tahap lanjut)
   - Input: time-series pengeluaran
   - Output: prediksi pengeluaran per kategori/periode

4. **LLM Advisor/NLG Service** (opsional)
   - Input: summary JSON (metrik finansial user)
   - Output: teks insight/rekomendasi natural
   - Bisa menggunakan LLM lokal (Ollama) atau API eksternal

### 3.4. Data Layer

1. **Relational Database (PostgreSQL)**
   - Tabel:
     - `users`
     - `accounts`
     - `categories`
     - `transactions`
     - `budgets`
     - `financial_goals`
     - `advisor_insights`
     - `import_jobs` (opsional)

2. **Object Storage**
   - Menyimpan file:
     - Gambar struk
     - File CSV/Excel
   - Contoh: MinIO (self-hosted S3-compatible), AWS S3, dsb.

3. **ML Artifacts Storage**
   - Menyimpan model terlatih, scaler, encoder, dsb.
   - Dapat berupa:
     - Folder di object storage
     - Model registry (MLflow) jika ingin lebih advance

### 3.5. Background Jobs & Scheduler

- Contoh teknologi: Celery + Redis, RQ, atau cronjob kustom.
- Tugas:
  - Proses import file besar secara asynchronous
  - Jalankan OCR batch
  - Hitung insight periodik (harian/mingguan/bulanan)
  - Re-train/refresh model secara berkala

---

## 4. Arsitektur Fisik (High-Level Deployment)

### Komponen Utama

1. **Client**
   - Browser user → mengakses web dashboard melalui HTTPS

2. **API Gateway / Reverse Proxy**
   - Nginx / Traefik
   - Menangani routing ke Backend Service

3. **Backend Service Container**
   - Menjalankan aplikasi FastAPI/Node.js
   - Mengakses DB, AI Service, dan Storage

4. **AI Service Container** (opsional terpisah)
   - Category classifier
   - Anomaly detection
   - LLM adapter (jika LLM lokal)

5. **OCR Service Container**
   - Tesseract/PaddleOCR yang dikemas dalam service
   - Menerima image, mengembalikan teks

6. **Database Server (PostgreSQL)**
   - Single instance atau cluster

7. **Object Storage Service**
   - MinIO / S3

8. **Background Worker Container**
   - Menjalankan Celery/RQ jobs

9. **Monitoring & Logging Stack** (opsional tapi direkomendasikan)
   - Prometheus + Grafana
   - Loki/ELK untuk log

---

## 5. Alur Data Utama

### 5.1. Input Transaksi Manual

1. User membuka form input di dashboard.
2. Frontend mengirim `POST /transactions` ke Backend.
3. Backend menyimpan transaksi (status: `pending_category`).
4. Backend memanggil Category Classifier Service.
5. Classifier mengembalikan prediksi kategori + confidence.
6. Backend update transaksi dengan `category_id` + `confidence`.
7. Frontend menampilkan transaksi dengan status "prediksi AI" dan user dapat mengubah jika perlu.

### 5.2. Import CSV/Excel

1. User upload file → `POST /imports`.
2. Backend menyimpan file ke Object Storage dan membuat record `import_jobs`.
3. Background worker memproses file:
   - Parse baris → buat transaksi satu per satu
   - Panggil Category Classifier untuk tiap transaksi
4. Setelah selesai, status job berubah menjadi `completed`.
5. User melihat hasil di halaman Transaksi.

### 5.3. Upload Foto Struk (OCR)

1. User upload gambar struk → `POST /receipts`.
2. Backend simpan file ke Object Storage dan membuat record `receipts` (status: `pending_ocr`).
3. Background job atau synchronous call memanggil OCR Service.
4. OCR Service mengembalikan teks dan struktur dasar.
5. Backend melakukan parsing (total amount, tanggal, merchant) → buat transaksi.
6. Backend memanggil Category Classifier untuk transaksi tersebut.

### 5.4. Generasi Insight Advisor

1. Scheduler (harian/mingguan/bulanan) menjalankan job Advisor.
2. Advisor Module mengambil data:
   - income & expense per kategori & periode
   - budget & goals
3. Rule Engine meng-evaluasi kondisi dan menghasilkan list insight terstruktur.
4. Opsional: summary insight diberikan ke LLM Adapter untuk dibuatkan narasi natural.
5. Insight disimpan di tabel `advisor_insights`.
6. Frontend menampilkan insight di dashboard.

---

## 6. Security & Compliance (High-Level)

- **Transport Security**: semua komunikasi via HTTPS.
- **Authentication & Authorization**:
  - JWT token
  - Role-based access control (user/admin)
- **Data Protection**:
  - Hashing password (bcrypt/argon2)
  - Pertimbangkan enkripsi field sensitif (mis. akun/rek. bank jika disimpan eksplisit)
- **Logging & Auditing**:
  - Access log API
  - Event log penting (login, impor data, perubahan konfigurasi)

---

## 7. Tahapan Implementasi Bertahap

1. **Phase 1 – Core System (Non-AI)**
   - Auth, akun, transaksi, kategori.
   - Dashboard dasar (income vs expense, kategori).

2. **Phase 2 – AI Kategori & Dashboard Lanjutan**
   - Implementasi Category Classifier.
   - Tambah filter AI-predicted vs user-confirmed.

3. **Phase 3 – OCR & Import Pipeline**
   - Upload CSV/Excel + pipeline asynchronous.
   - OCR struk & otomatisasi parsing.

4. **Phase 4 – Advisor Engine (Rule-Based)**
   - Budget & goals.
   - Rule-engine untuk insight (tanpa LLM dulu).

5. **Phase 5 – LLM Advisor & Optimasi**
   - Tambah LLM untuk menghasilkan rekomendasi natural.
   - Optimasi performa, caching, dan monitoring.

---

Dokumen ini dapat dijadikan dasar untuk:
- Desain detail API (OpenAPI/Swagger)
- Desain skema database
- Perencanaan sprint/iterasi pengembangan
- Penyusunan portofolio teknis (arsitektur + implementasi)

Lihat juga arsitektur terpisah per komponen:
- `docs/arsitektur_backend.md`
- `docs/arsitektur_frontend.md`
- `docs/arsitektur_ml.md`
- `docs/arsitektur_ocr.md`
