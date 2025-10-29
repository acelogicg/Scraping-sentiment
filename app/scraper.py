from typing import List, Dict
from urllib.parse import urlparse, parse_qs, quote_plus
import html as htmllib
import requests
import pandas as pd
from bs4 import BeautifulSoup

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

def _extract_canonical_url(google_news_link: str) -> str:
    try:
        parsed = urlparse(google_news_link)
        qs = parse_qs(parsed.query)
        if "url" in qs and qs["url"]:
            return qs["url"][0]
        return google_news_link
    except Exception:
        return google_news_link

def _clean_summary(summary_html: str) -> str:
    if not summary_html:
        return ""
    try:
        text = htmllib.unescape(summary_html)
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    except Exception:
        return summary_html

def scrape_news(query: str, max_results: int = 10) -> pd.DataFrame:
    url = GOOGLE_NEWS_RSS.format(q=quote_plus(query))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Gagal unduh RSS: {e}")
        return pd.DataFrame(columns=["title", "summary", "url"])

    soup = BeautifulSoup(resp.content, "xml")
    rows: List[Dict[str, str]] = []
    for it in soup.find_all("item")[:max_results]:
        title_tag = it.find("title")
        link_tag = it.find("link")
        desc_tag = it.find("description")
        title = title_tag.get_text(strip=True) if title_tag else ""
        link_raw = link_tag.get_text(strip=True) if link_tag else ""
        summary_raw = desc_tag.get_text() if desc_tag else ""
        if not title or not link_raw:
            continue
        url_final = _extract_canonical_url(link_raw)
        summary = _clean_summary(summary_raw)
        rows.append({"title": title, "summary": summary, "url": url_final})
    return pd.DataFrame(rows, columns=["title", "summary", "url"])
