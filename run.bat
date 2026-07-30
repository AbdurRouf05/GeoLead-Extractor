@echo off
echo ==============================================
echo 🚀 Memulai MScrape: Google Maps Scraper...
echo ==============================================

echo [1/2] Memeriksa dan menginstal library yang dibutuhkan...
pip install -r requirements.txt

echo.
echo [2/2] Menjalankan Aplikasi Web...
cd GoogleMaps-Lead-Scraper
streamlit run app.py
pause
