import time
import random
import re
from selenium.webdriver.common.by import By

def extract_email_from_website_in_new_tab(driver, url):
    if url == "N/A":
        return "N/A"
    try:
        # Buka tab baru
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        # Coba halaman utama dulu
        driver.get(url)
        time.sleep(random.uniform(2.5, 3.5))
        
        # 1. Cari di body text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        emails_found = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body_text)
        if emails_found:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return emails_found[0]

        # 2. Cari di tag mailto
        mailto_links = driver.find_elements(By.XPATH, '//a[contains(@href, "mailto:")]')
        for link in mailto_links:
            href = link.get_attribute("href")
            if href and "mailto:" in href:
                email = href.split("mailto:")[-1].split("?")[0].strip()
                if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    return email

        # 3. Coba halaman /contact (opsional)
        try:
            contact_url = url.rstrip("/") + "/contact"
            driver.get(contact_url)
            time.sleep(random.uniform(2.0, 3.0))
            body_text_contact = driver.find_element(By.TAG_NAME, "body").text
            emails_contact = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body_text_contact)
            if emails_contact:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return emails_contact[0]
        except:
            pass

        # Tidak ditemukan
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return "N/A"
    except Exception:
        # Pastikan kembali ke tab utama jika error
        try:
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return "N/A"
