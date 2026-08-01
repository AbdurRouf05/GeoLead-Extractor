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
    
    while len(results) < limit:
        params = {
            "query": search_query, 
            "limit": "20", 
            "country": "id", # Bisa disesuaikan dengan negara
            "lang": "id", 
            "offset": str(offset)
        }
        
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 200:
                retry_count = 0 # Reset retry on success
                data = r.json().get("data", [])
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
                
                offset += 20
                if len(data) < 20:
                    break # Data sudah habis di halaman ini
                    
                time.sleep(1) # Delay wajar antar request API
                
            elif r.status_code == 403 or r.status_code == 401:
                st.error("API Key tidak valid atau tidak memiliki akses ke endpoint ini.")
                break
            elif r.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    st.error("Rate limit (batas kuota API) Anda mungkin sudah habis atau terblokir. Proses dihentikan.")
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
