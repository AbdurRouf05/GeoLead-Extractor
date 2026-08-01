import requests
import time
import streamlit as st

def rapidapi_scrape(query, loc, ctr, limit, api_key):
    """
    Scrape data menggunakan RapidAPI (maps-data.p.rapidapi.com).
    """
    results = []
    
    # Format query pencarian, mirip dengan yang diketik di Google Maps
    search_query = f"{query} di {loc}, {ctr}"
    
    url = "https://maps-data.p.rapidapi.com/searchmaps.php"
    headers = {
        "x-rapidapi-host": "maps-data.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    
    # RapidAPI maps-data limit default biasanya 20 per page
    offset = 0
    retry_count = 0
    max_retries = 3
    api_mode = 1 # 1: maps-data, 2: unlimited-google-maps (fallback)
    
    while len(results) < limit:
        if api_mode == 1:
            url = "https://maps-data.p.rapidapi.com/searchmaps.php"
            headers = {
                "x-rapidapi-host": "maps-data.p.rapidapi.com",
                "x-rapidapi-key": api_key
            }
            params = {
                "query": search_query, 
                "limit": "20", 
                "country": "id", 
                "lang": "id", 
                "offset": str(offset)
            }
        else:
            url = "https://unlimited-google-maps.p.rapidapi.com/api/maps/simple-search"
            headers = {
                "x-rapidapi-host": "unlimited-google-maps.p.rapidapi.com",
                "x-rapidapi-key": api_key
            }
            params = {"query": search_query} # API ini tidak menggunakan offset yang sama
            
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 200:
                retry_count = 0 # Reset retry on success
                
                # API 1 menggunakan key "data", API 2 menggunakan key "items"
                json_data = r.json()
                data = json_data.get("data", []) if api_mode == 1 else json_data.get("items", [])
                
                if not data:
                    break # Tidak ada data lagi
                
                for item in data:
                    if len(results) >= limit:
                        break
                        
                    name_val = item.get("name", "")
                    addr_val = item.get("full_address", "")
                    subtypes = item.get("subtypes")
                    category = ", ".join(subtypes) if isinstance(subtypes, list) else (subtypes or query.title())
                    
                    results.append({
                        "Business Name": name_val.replace("\n", " ") if name_val else "N/A",
                        "Full Address": addr_val.replace("\n", " ") if addr_val else "N/A",
                        "Website": item.get("website", "N/A") or "N/A",
                        "Phone": item.get("phone_number", "N/A") or "N/A",
                        "Emails": "N/A", # API ini tidak menyediakan email
                        "Category": category,
                        "Rating": str(item.get("rating", "N/A")),
                        "Review Counts": str(item.get("review_count", "N/A")),
                        "Latitude": str(item.get("latitude", "N/A")),
                        "Longitude": str(item.get("longitude", "N/A")),
                        "City": loc.title(),
                        "Country": ctr.title(),
                        "Google Maps URL": item.get("place_link", "N/A") or "N/A"
                    })
                
                if api_mode == 1:
                    offset += 20
                    if len(data) < 20:
                        break # Data sudah habis di halaman ini
                    time.sleep(1) # Delay wajar antar request API
                else:
                    break # Fallback API tidak mendukung pagination simple, jadi kita ambil 1 halaman saja
                
            elif r.status_code == 403 or r.status_code == 401:
                st.error("API Key tidak valid atau tidak berlangganan ke endpoint ini.")
                break
            elif r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    if api_mode == 1:
                        st.toast("Rate limit API pertama habis. Beralih ke API cadangan (Unlimited Google Maps)...")
                        api_mode = 2 # Switch to fallback API
                        retry_count = 0 # Reset retry for new API
                        continue
                    else:
                        st.error("Kedua API telah mencapai batas kuota (Rate limit). Proses dihentikan.")
                        break
                    
                st.toast(f"Rate limit API tercapai. Menunggu 5 detik (Percobaan {retry_count}/{max_retries})...")
                time.sleep(5)
            else:
                st.error(f"Terjadi kesalahan API: {r.status_code}")
                break
                
        except Exception as e:
            st.error(f"Gagal mengambil data dari API: {e}")
            break
            
    return results
