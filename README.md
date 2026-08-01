# GeoLead Extractor

Aplikasi otomatis berbasis Python dan Streamlit yang dirancang untuk membantu Anda mencari dan mengumpulkan data calon pelanggan (leads) bisnis dari Google Maps. Aplikasi ini dibuat dengan antarmuka yang bersih dan ramah pengguna, sehingga Anda dapat langsung menggunakannya tanpa perlu memahami pemrograman.

Sangat cocok digunakan untuk kebutuhan marketing B2B (Business-to-Business), agensi pemasaran digital, riset pasar, hingga kampanye penawaran langsung (cold outreach).

## Fitur Utama

- **Pencarian Skala Global dan Lokal**: Cari dan kumpulkan data bisnis di satu kota tertentu atau di banyak kota sekaligus sesuai target bisnis Anda.
- **Sistem Scraping Ganda (Dual Engine)**:
  - **Manual Engine (Selenium)**: Bekerja langsung dari komputer Anda dengan membuka browser secara tersembunyi.
  - **API Engine (RapidAPI)**: Menggunakan koneksi langsung ke penyedia data (maps-data) untuk proses pencarian yang sangat cepat, stabil, dan berskala besar.
- **Pencarian Email Otomatis**: Bot akan mencoba mengunjungi situs web dari masing-masing bisnis untuk memindai dan mencatat alamat email resmi mereka (khusus untuk mode Manual).
- **Penyaringan Data Otomatis**: Dilengkapi dengan fitur Blacklist untuk menyortir dan membuang email umum (seperti info@, admin@) serta bisnis waralaba besar (seperti Starbucks, KFC) agar data yang Anda dapatkan lebih berkualitas dan tepat sasaran.
- **Ekspor Data Rapi**: Hasil pencarian dapat langsung diunduh dalam bentuk file Excel (.xlsx) yang siap digunakan.

## Kebutuhan Sistem

- Python versi 3.8 atau yang lebih baru.
- Browser Google Chrome terinstal di komputer Anda (Diperlukan jika menggunakan metode Manual/Selenium).

## Panduan Instalasi

1. **Unduh Repositori:**
   ```bash
   git clone https://github.com/AbdurRouf05/GeoLead-Extractor.git
   cd GeoLead-Extractor
   ```

2. **Instal Modul yang Dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi:**
   Bagi pengguna Windows, Anda cukup mengklik dua kali pada file:
   **`run.bat`**

   Atau jalankan secara manual melalui terminal dengan perintah:
   ```bash
   cd GoogleMaps-Lead-Scraper
   streamlit run app.py
   ```

## Cara Penggunaan

1. Buka browser Anda dan kunjungi alamat `http://localhost:8501`.
2. Pada panel sebelah kiri, masukkan variasi kata kunci target bisnis Anda (misalnya: `software agency`, `digital marketing`).
3. Pilih metode Scraping (API atau Manual). Khusus untuk metode API, pastikan Anda telah memiliki dan memasukkan API Key dari RapidAPI.
4. Tentukan lokasi pencarian (Nama Kota dan Negara).
5. Centang opsi pencarian email jika Anda membutuhkan kontak email.
6. Klik tombol Mulai dan tunggu hingga proses pencarian data selesai 100%.
7. Setelah selesai, klik tombol Download Excel untuk menyimpan hasil akhirnya.

## Catatan Penting

- **Kecepatan**: Kecepatan pencarian pada mode Manual sangat bergantung pada koneksi internet dan RAM komputer Anda. Jika Anda ingin mencari data dalam jumlah yang masif, kami sangat menyarankan Anda menggunakan mode API.
- **Pembaruan**: Struktur website Google Maps dapat berubah sewaktu-waktu. Pastikan Anda selalu menggunakan versi aplikasi terbaru agar sistem tetap dapat membaca data dengan akurat.

---

### Lisensi
Aplikasi ini bersifat open-source. Kami mengimbau Anda untuk selalu menggunakan perangkat lunak ini secara etis dan mematuhi kebijakan privasi dari website target Anda.
