import streamlit as st
import pandas as pd
import io
import time
import random

from utils.constants import COUNTRY_CITIES, DEFAULT_EMAIL_BLACKLIST, DEFAULT_CHAIN_KEYWORDS
from utils.text_helpers import normalize_country_name, is_chain, is_blacklisted_email
from core.scraper import selenium_scrape_single
from core.api_scraper import rapidapi_scrape

# Inisialisasi blacklists di session state jika belum ada
if "email_blacklist" not in st.session_state:
    st.session_state.email_blacklist = DEFAULT_EMAIL_BLACKLIST.copy()

if "chain_blacklist" not in st.session_state:
    st.session_state.chain_blacklist = list(DEFAULT_CHAIN_KEYWORDS)

# --- UI SETUP ---
st.set_page_config(page_title="MScrape Lead Scraper", layout="wide")

st.title("Google Maps Lead Scraper")

st.markdown("""
Aplikasi ini memungkinkan Anda untuk mengekstrak data bisnis (leads) dari Google Maps secara otomatis.
Anda dapat mencari target spesifik (misal: "software house") di satu kota atau di banyak kota sekaligus untuk mendapatkan prospek bisnis.
""")

with st.expander("Penjelasan Fitur & Bagaimana Cara Kerjanya?"):
    st.markdown("""
    **Penjelasan Fitur Utama:**
    * **Kata Kunci / Niche**: Jenis bisnis yang dicari (contoh: *cafe, coffee shop, restoran*).
    * **Mode Scraping**: 
        * **Satu Kota**: Mencari bisnis hanya di satu kota spesifik dengan batasan jumlah tertentu.
        * **Target Total**: Mencari bisnis di daftar kota secara otomatis sampai jumlah target total tercapai.
    * **Cari Email di Website**: Jika diaktifkan, bot akan mencoba mengunjungi website bisnis untuk menemukan kontak email.
    * **Filter Settings (Blacklist)**: Berfungsi untuk mengabaikan email generik (info@, admin@) dan mengabaikan bisnis franchise besar (KFC, McDonald's) agar prospek lebih relevan.

    **Bagaimana Cara Scraping Berjalan?**
    1. **Pencarian Otomatis**: Bot (menggunakan Selenium) membuka browser tersembunyi, lalu mencari kata kunci di Google Maps sesuai kota target.
    2. **Pengumpulan Profil**: Bot akan melakukan *scroll* otomatis pada panel hasil pencarian untuk memuat dan mengumpulkan link profil bisnis.
    3. **Ekstraksi Data**: Bot membuka profil setiap bisnis satu per satu untuk mengambil data (Nama, Alamat, Telepon, Website, Rating, dll).
    4. **Pencarian Email**: Jika opsi email diaktifkan, bot membuka *tab* baru menuju website bisnis tersebut dan memindai teks untuk mencari format alamat email.
    5. **Pembersihan & Ekspor**: Data difilter dari duplikat dan *blacklist*, lalu ditampilkan dalam tabel yang siap diunduh (Excel).
    """)
    st.info("**Catatan:** Scraping Google Maps memakan waktu sekitar beberapa detik per data. Mengaktifkan fitur Cari Email akan membuat proses lebih lama karena bot harus memuat halaman website dari masing-masing bisnis.")


with st.sidebar:
    st.header("Konfigurasi Pencarian")
    
    # Tab untuk konfigurasi utama dan filter
    tab1, tab2 = st.tabs(["Pengaturan Utama", "🚫 Pengaturan Filter"])
    
    with tab1:
        st.markdown("### Target Bisnis")
        keyword_input = st.text_area(
            "Kata Kunci / Niche (Satu per baris)",
            value="cafe\ncoffee shop",
            help="Masukkan variasi kata kunci jenis bisnis yang dicari. Contoh: cafe, restoran, coffee shop. Lebih banyak variasi = lebih banyak hasil."
        )
        country = st.text_input("Negara", "United States", help="Negara tempat pencarian dilakukan.")
        
        st.markdown("### Engine Scraping")
        scrape_engine = st.radio(
            "Pilih Engine", 
            ["Manual (Browser / Selenium)", "API (Lebih Cepat, Butuh Key)"],
            help="Manual: Gratis tapi lambat. API: Sangat cepat, stabil, namun membutuhkan API Key sendiri (Data Aman & Pribadi)."
        )
        
        rapidapi_key = ""
        if scrape_engine == "API (Lebih Cepat, Butuh Key)":
            st.info("**Catatan:** Scraping API lebih disarankan untuk stabilitas. Pastikan Anda memiliki langganan di `maps-data.p.rapidapi.com`.")
            
            # Membaca dari file .env lokal jika ada
            default_key = ""
            import os
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    for line in f:
                        if line.startswith("RAPIDAPI_KEY="):
                            default_key = line.split("=", 1)[1].strip()
            
            rapidapi_key = st.text_input(
                "Masukkan RapidAPI Key Anda",
                value=default_key,
                type="password",
                help="Key API Anda tidak akan tersimpan atau terekspose. Dapatkan key Anda di: https://rapidapi.com/letscrape-6bRBa3QG1q/api/maps-data"
            )
            st.caption("Belum punya key? [Dapatkan API Key di sini](https://rapidapi.com/letscrape-6bRBa3QG1q/api/maps-data)")
        
        st.markdown("### Mode Scraping")
        scrape_mode = st.radio(
            "Pilih Mode", 
            ["Satu Kota", "Target Total (Banyak Kota)"],
            help="Pilih 'Satu Kota' untuk pencarian spesifik, atau 'Target Total' jika Anda butuh data dalam jumlah besar dari berbagai kota."
        )
        
        if scrape_mode == "Satu Kota":
            location = st.text_input("Nama Kota", "New York", help="Masukkan nama kota target.")
            max_res_per_city = st.number_input(
                "Maksimal Data per Kata Kunci",
                min_value=1,
                max_value=200,
                value=20,
                step=10,
                help="Batas data yang diambil per kata kunci. Google Maps biasanya hanya menampilkan maksimal 60-80 hasil per pencarian."
            )
        else:
            total_target = st.number_input(
                "Target Total Data Keseluruhan",
                min_value=10,
                value=100,
                step=50,
                help="Bot akan terus mencari dari satu kota ke kota lain sampai jumlah ini tercapai."
            )
            max_per_city = st.number_input(
                "Maksimal Data per Kota",
                min_value=10,
                max_value=100,
                value=60,
                step=10,
                help="Batas pencarian di satu kota sebelum pindah ke kota berikutnya. Disarankan 60-80."
            )
            
            use_builtin = st.checkbox("Gunakan daftar kota bawaan", value=True, help="Otomatis menggunakan daftar kota besar di negara yang dipilih.")
            if not use_builtin:
                cities_input = st.text_area(
                    "Daftar Kota Manual (Satu per baris)",
                    value="New York\nLos Angeles\nChicago\nHouston\nPhoenix",
                    height=150,
                    help="Masukkan daftar kota secara manual jika Anda menonaktifkan kota bawaan."
                )

        st.markdown("### Fitur Tambahan")
        extract_email = st.checkbox(
            "Cari Email di Website Bisnis",
            value=False,
            help="Akan mencari email di website setiap bisnis. (Membuat proses scraping menjadi lebih lama)."
        )
    
    with tab2:
        st.subheader("Email Blacklist")
        st.caption("Jika fitur pencarian email aktif, email yang mengandung kata-kata berikut akan diabaikan (cocok untuk membuang email support).")
        email_blacklist_input = st.text_area(
            "Kata Blacklist Email (Satu per baris)",
            value="\n".join(DEFAULT_EMAIL_BLACKLIST),
            height=150,
            help="Contoh: info@, contact@, support@"
        )
        
        st.subheader("Chain/Franchise Blacklist")
        st.caption("Bisnis yang namanya mengandung kata-kata berikut akan langsung dilewati (cocok untuk membuang franchise besar).")
        chain_blacklist_input = st.text_area(
            "Kata Blacklist Bisnis (Satu per baris)",
            value="\n".join(sorted(DEFAULT_CHAIN_KEYWORDS)),
            height=200,
            help="Contoh: mcdonald, starbucks, kfc"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset ke Default", use_container_width=True):
                st.session_state.email_blacklist = DEFAULT_EMAIL_BLACKLIST.copy()
                st.session_state.chain_blacklist = list(DEFAULT_CHAIN_KEYWORDS)
                st.success("Filter direset ke default!")
                st.rerun()
        
        with col2:
            if st.button("Simpan Filter", use_container_width=True):
                email_patterns = [p.strip() for p in email_blacklist_input.split("\n") if p.strip()]
                chain_keywords = [k.strip() for k in chain_blacklist_input.split("\n") if k.strip()]
                
                st.session_state.email_blacklist = email_patterns
                st.session_state.chain_blacklist = chain_keywords
                st.success("Filter disimpan!")
                st.rerun()

    st.divider()
    
    btn_run = st.button("Mulai Scraping Sekarang!", type="primary", use_container_width=True)

    if st.button("Bersihkan Cache Lokasi", use_container_width=True):
        st.session_state.geocode_cache = {}
        st.success("Cache dibersihkan!")

# --- RUN SCRAPE ---
if btn_run:
    email_blacklist = st.session_state.email_blacklist
    chain_blacklist = st.session_state.chain_blacklist
    
    st.sidebar.success(f"Filter aktif: {len(email_blacklist)} email patterns, {len(chain_blacklist)} chain keywords")
    
    keywords = [k.strip() for k in keyword_input.split("\n") if k.strip()]
    if not keywords or not country.strip():
        st.warning("Isi minimal satu niche dan negara!")
    else:
        normalized_country = normalize_country_name(country)
        all_results = []

        if scrape_mode == "Satu Kota":
            if not location.strip():
                st.warning("Isi City!")
            else:
                with st.spinner(f"Scraping di {location}, {country}..."):
                    for kw in keywords:
                        if len(all_results) >= 1000:
                            break
                            
                        limit_val = max_res_per_city // len(keywords) or 1
                        
                        if scrape_engine == "API (Lebih Cepat, Butuh Key)":
                            if not rapidapi_key:
                                st.error("Masukkan RapidAPI Key terlebih dahulu di menu samping!")
                                st.stop()
                            final_data = rapidapi_scrape(kw, location, country, limit_val, rapidapi_key)
                        else:
                            final_data = selenium_scrape_single(kw, location, country, limit_val, extract_email, email_blacklist, chain_blacklist)
                            
                        all_results.extend(final_data)
        else:
            if use_builtin:
                cities = COUNTRY_CITIES.get(normalized_country)
                if not cities:
                    st.error(f"Negara '{country}' belum didukung untuk daftar bawaan.")
                    st.info("Saat ini mendukung: Indonesia, United States, India, Brazil, France, Germany, United Kingdom.")
                    st.stop()
            else:
                cities = [c.strip() for c in cities_input.split("\n") if c.strip()]
                if not cities:
                    st.error("Daftar kota kosong!")
                    st.stop()

            st.info(f"Akan scrape {len(cities)} kota di {country} sampai target {total_target} data tercapai.")
            st.info(f"Filter aktif: {len(email_blacklist)} pola email, {len(chain_blacklist)} keyword chain")
            if extract_email:
                st.warning("Email extraction aktif — proses akan lebih lama & hasil email tergantung website.")
            
            all_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for city in cities:
                if len(all_results) >= total_target:
                    break
                for kw in keywords:
                    if len(all_results) >= total_target:
                        break
                    needed = total_target - len(all_results)
                    limit = min(max_per_city, needed, 50)

                    status_text.write(f"{city} | {kw} (butuh {needed} lagi)...")
                    
                    if scrape_engine == "API (Lebih Cepat, Butuh Key)":
                        if not rapidapi_key:
                            st.error("Masukkan RapidAPI Key terlebih dahulu di menu samping!")
                            st.stop()
                        city_data = rapidapi_scrape(kw, city, country, limit, rapidapi_key)
                    else:
                        city_data = selenium_scrape_single(kw, city, country, limit, extract_email, email_blacklist, chain_blacklist)
                        
                    all_results.extend(city_data)

                    progress_pct = min(len(all_results) / total_target, 1.0)
                    progress_bar.progress(progress_pct)
                    time.sleep(random.uniform(1, 2))

            status_text.write("Target tercapai atau semua kota selesai!")

        if all_results:
            df = pd.DataFrame(all_results)
            df.drop_duplicates(subset=["Business Name", "Full Address"], keep="first", inplace=True)
            df = df.head(total_target if scrape_mode == "Target Total" else len(df))
            df.reset_index(drop=True, inplace=True)

            chain_filtered_count = sum(1 for name in df["Business Name"] if is_chain(name, chain_blacklist))
            email_filtered_count = sum(1 for email in df["Emails"] if is_blacklisted_email(email, email_blacklist))
            
            st.success(f"Total {len(df)} data unik siap cair!")
            st.info(f"Statistik Filter: {chain_filtered_count} chain diabaikan, {email_filtered_count} email di-blacklist")
            
            st.dataframe(df, use_container_width=True)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)

            filename_prefix = f"Leads_{country.replace(' ', '_')}"
            st.download_button(
                label="Download Excel",
                data=output.getvalue(),
                file_name=f"{filename_prefix}_{len(df)}_leads.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Tidak ada data ditemukan.")
