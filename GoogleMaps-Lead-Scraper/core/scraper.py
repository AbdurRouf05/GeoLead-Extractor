import time
import random
import re
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from .geocoder import get_coordinates_cached
from .email_finder import extract_email_from_website_in_new_tab
from utils.text_helpers import clean_text, is_chain, is_blacklisted_email

def selenium_scrape_single(kw, loc, ctr, limit, extract_email=False, email_blacklist=None, chain_blacklist=None):
    """Scrape satu kota."""
    results = []
    full_location = f"{loc}, {ctr}"
    
    coords = get_coordinates_cached(full_location)
    if coords is None:
        st.warning(f"Lewati: {full_location} (koordinat tidak ditemukan)")
        return []

    lat, lng = coords
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Memastikan pencarian lebih spesifik dengan menyertakan nama kota
        search_query = f"{kw} di {loc}".replace(' ', '+')
        zoom = 12
        # Perbaiki spasi berlebih di URL
        url = f"https://www.google.com/maps/search/{search_query}/@{lat},{lng},{zoom}z"
        driver.get(url)
        time.sleep(random.uniform(6, 9) if extract_email else random.uniform(5, 7))

        try:
            panel = driver.find_element(By.XPATH, '//div[contains(@role, "feed")]')
            last_height = driver.execute_script("return arguments[0].scrollHeight", panel)
            scroll_count = 0
            max_scrolls = 8  # cukup untuk 50+ listing
            
            while scroll_count < max_scrolls:
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', panel)
                time.sleep(random.uniform(2.0, 3.0))  # lebih lama saat email aktif
                
                new_height = driver.execute_script("return arguments[0].scrollHeight", panel)
                if new_height == last_height:
                    break  # tidak ada lagi listing baru
                last_height = new_height
                scroll_count += 1
        except Exception as e:
            st.warning(f"Scroll feed gagal: {str(e)}")

        items = driver.find_elements(By.XPATH, '//div[contains(@role, "article")]')
        if not items:
            return []

        # 1. Kumpulkan semua URL terlebih dahulu agar DOM tidak hilang saat klik
        urls = []
        for card in items[:limit]:
            try:
                link_elements = card.find_elements(By.XPATH, './/a[contains(@href, "/maps/place/")]')
                if link_elements:
                    urls.append(link_elements[0].get_attribute("href"))
                else:
                    all_links = card.find_elements(By.TAG_NAME, "a")
                    for lnk in all_links:
                        href = lnk.get_attribute("href")
                        if href and "google.com/maps" in href:
                            urls.append(href)
                            break
            except:
                pass

        # 2. Kunjungi setiap URL satu per satu
        for gmaps_url in urls:
            if not gmaps_url or "google.com/maps" not in gmaps_url:
                continue
                
            try:
                driver.get(gmaps_url)
                time.sleep(random.uniform(4.5, 6.0))

                # Ambil judul bisnis dari Title halaman (Paling Akurat)
                page_title = driver.title
                raw_name = page_title.split(' - Google Maps')[0] if ' - Google Maps' in page_title else "N/A"
                if raw_name == "N/A" or raw_name == "Google Maps":
                    h1_elements = driver.find_elements(By.TAG_NAME, 'h1')
                    raw_name = h1_elements[0].text if h1_elements else "N/A"
                raw_address = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').text if driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id="address"]') else "N/A"
                
                raw_phone = "N/A"
                for tooltip in ["telepon", "phone"]:
                    els = driver.find_elements(By.XPATH, f'//button[contains(@data-tooltip, "{tooltip}")]')
                    if els:
                        raw_phone = els[0].text
                        break

                website_elem = driver.find_elements(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
                website = website_elem[0].get_attribute("href") if website_elem else "N/A"

                name = clean_text(raw_name)
                address = clean_text(raw_address)
                phone = clean_text(raw_phone)

                # Ambil Email di Tab Baru (tidak ganggu halaman utama)
                email = "N/A"
                if extract_email and website != "N/A":
                    email = extract_email_from_website_in_new_tab(driver, website)

                # Rating
                rating = "N/A"
                try:
                    # Mencari elemen dengan aria-label yang mengandung kata "stars" atau "bintang"
                    rating_candidates = driver.find_elements(By.XPATH, '//span[contains(@aria-label, "stars") or contains(@aria-label, "bintang")]')
                    for el in rating_candidates:
                        rating_text = el.get_attribute("aria-label")
                        if rating_text:
                            match = re.search(r'([\d,.]+)', rating_text)
                            if match:
                                rating = match.group(1).replace(',', '.')
                                break
                    
                    if rating == "N/A":
                        rating_el = driver.find_elements(By.CSS_SELECTOR, 'div[role="img"][aria-label*="stars"], div[role="img"][aria-label*="bintang"]')
                        if rating_el:
                            match = re.search(r'([\d,.]+)', rating_el[0].get_attribute("aria-label"))
                            if match:
                                rating = match.group(1).replace(',', '.')
                except:
                    pass
                
                # Review Count
                review_count = "N/A"
                try:
                    candidates = driver.find_elements(By.XPATH, '//span[contains(@aria-label, "review") or contains(@aria-label, "ulasan") or contains(text(), "review") or contains(text(), "ulasan")]')
                    if not candidates:
                         candidates = driver.find_elements(By.TAG_NAME, 'button')
                         
                    for el in candidates:
                        text = el.text or el.get_attribute("aria-label") or ""
                        match = re.search(r'[\(·]?\s*([\d.,]+)\s*[\)]?\s*(?:reviews?|ulasan)', text, re.IGNORECASE)
                        if match:
                            review_count = match.group(1).replace('.', '').replace(',', '')
                            break
                        
                        match2 = re.search(r'([\d.,]+)\s*(?:reviews?|ulasan)', text, re.IGNORECASE)
                        if match2:
                            review_count = match2.group(1).replace('.', '').replace(',', '')
                            break
                except:
                    pass

                # Latitude & Longitude
                lat_detail, lng_detail = "N/A", "N/A"
                try:
                    current_url = driver.current_url
                    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
                    if match:
                        lat_detail, lng_detail = match.group(1), match.group(2)
                except:
                    pass

                # Gunakan blacklist yang ada di session state
                if chain_blacklist and is_chain(name, chain_blacklist):
                    continue  # skip large chains

                if extract_email and email_blacklist and is_blacklisted_email(email, email_blacklist):
                    email = "N/A"  # hide blacklisted emails

                results.append({
                    "Business Name": name,
                    "Full Address": address,
                    "Website": website,
                    "Phone": phone, 
                    "Emails": email,
                    "Category": kw.title(),
                    "Rating": rating,
                    "Review Counts": review_count,
                    "Latitude": lat_detail,
                    "Longitude": lng_detail,
                    "City": loc.title(),
                    "Country": ctr.title(),
                    "Google Maps URL": gmaps_url
                })
            except Exception as e:
                continue
    finally:
        driver.quit()
    return results
