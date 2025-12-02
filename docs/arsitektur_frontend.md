# Arsitektur Frontend

## Tujuan
Web dashboard interaktif untuk input transaksi, monitoring cashflow, mengelola budget/goal, import/OCR, dan menampilkan insight/advisor.

## Stack & Struktur
- **Framework**: React/Next.js (SPA/SSR hybrid).
- **State**: React Query/RTK Query untuk data fetching; konteks auth.
- **UI**: komponen tabel/form, chart (mis. Recharts/ECharts), notifikasi/toast.
- **Routing**: halaman modular: Overview, Transaksi, Import/OCR, Budget & Goals, Insight/Advisor, Settings.
- **Theming**: design system ringan + tokens (spacing, warna, typography).

## Integrasi API
- Gunakan klien HTTP dengan interceptor JWT (refresh otomatis).
- Typing berdasarkan OpenAPI (generator opsional).
- Error handling seragam (toast + inline form errors).

## Fitur Utama
- **Overview**: ringkasan income/expense, saldo, insight singkat.
- **Transaksi**: tabel dengan filter (tanggal, kategori, akun, tipe), edit kategori, label predicted/confirmed.
- **Import/OCR**: upload CSV/Excel, pantau status job; upload struk, tampilkan hasil parsing + edit.
- **Budget & Goals**: form CRUD, progress bar.
- **Insight/Advisor**: daftar insight, severity, narasi (jika LLM).
- **Settings**: akun finansial, kategori custom, profil.

## Non-Fungsional
- **Performance**: caching fetch (React Query), pagination server-side, lazy load chart.
- **Security**: simpan token di memory atau httpOnly cookie (sesuai backend), CSRF jika pakai cookie, sanitasi input user.
- **Accessibility**: keyboard nav, ARIA untuk tabel/form.
- **i18n**: siapkan struktur jika perlu multi bahasa (id/en).
- **Observability**: frontend logging ringan + error boundary + tracing header (propagate traceparent).

## Build & Deploy
- Build Next.js → output statis/hybrid; served via CDN + edge cache untuk assets.
- Konfigurasi base URL API via env runtime.
