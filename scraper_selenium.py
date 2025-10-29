#scraper_selenium.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# === Selenium-based Scraper ===
def scrape_google_news_selenium(query, max_results=10):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print("📡 Membuka Google News ...")
    driver.get(f'https://news.google.com/search?q={query}&hl=id&gl=ID&ceid=ID:id')

    # Tunggu artikel muncul
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'article'))
    )

    # Scroll sekali untuk load tambahan
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    print("📌 Mengambil hasil berita ...")
    articles = driver.find_elements(By.TAG_NAME, 'article')
    print(f"🧪 Ditemukan {len(articles)} artikel.")

    results = []
    added = 0

    for art in articles:
        if added >= max_results:
            break

        # 1) Cari anchor yang valid
        anchors = art.find_elements(By.TAG_NAME, 'a')
        link = None
        for a in anchors:
            href = a.get_attribute('href') or ""
            # Link Google News artikel biasanya mengandung '/articles/' atau '/topics/'
            if "news.google.com" in href and ("/articles/" in href or "/topics/" in href):
                link = href
                title_candidate = (a.get_attribute('aria-label') or a.text or "").strip()
                break
        if not link:
            continue  # skip jika tak ada link artikel

        # 2) Judul: prioritas h3, fallback h4, lalu fallback dari anchor
        title = ""
        try:
            title = art.find_element(By.TAG_NAME, 'h3').text.strip()
        except:
            try:
                title = art.find_element(By.TAG_NAME, 'h4').text.strip()
            except:
                pass
        if not title:
            title = title_candidate

        if not title:
            continue  # masih tidak ada judul, skip

        # 3) Summary: ambil beberapa span lalu gabungkan (agar tidak kosong)
        spans = art.find_elements(By.TAG_NAME, 'span')
        summary = ""
        if spans:
            # ambil 1-3 span terakhir yang berisi teks
            texts = [s.text.strip() for s in spans if s.text.strip()]
            if texts:
                summary = " • ".join(texts[-3:])

        results.append({"title": title, "summary": summary, "url": link})
        added += 1

    driver.quit()
    return pd.DataFrame(results)
# === Backup Requests-based Scraper ===
INDONESIAN_SITES = [
    "site:detik.com",
    "site:kompas.com",
    "site:cnnindonesia.com",
    "site:tempo.co",
    "site:liputan6.com",
    "site:merdeka.com",
    "site:tribunnews.com"
]

def scrape_indonesian_news(query, max_results=10):
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = []

    for site in INDONESIAN_SITES:
        full_query = quote(f"{query} {site}")
        url = f"https://news.google.com/search?q={full_query}&hl=id&gl=ID&ceid=ID:id"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('article')
        for article in articles:
            if len(data) >= max_results:
                break

            title_tag = article.find('h3') or article.find('h4')
            if not title_tag:
                continue

            try:
                title = title_tag.text.strip()
                link = 'https://news.google.com' + title_tag.find('a')['href'][1:]
                snippet = article.find('span')
                summary = snippet.text.strip() if snippet else ""
                data.append({'title': title, 'summary': summary, 'url': link})
            except Exception as e:
                print("❌ Gagal parsing artikel:", e)
                continue

            time.sleep(0.5)

        if len(data) >= max_results:
            break

    return pd.DataFrame(data)