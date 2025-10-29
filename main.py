# main.py
from scraper import scrape_news
from sentiment import analyze_sentiment_batch
import pandas as pd
import re

def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip()
    return re.sub(r"\s+", "_", name)

def main():
    query = input("Masukkan query pencarian: ").strip()
    max_results = int(input("Berapa banyak berita yang ingin diambil? (cth: 10): ").strip() or "10")

    print(f"\n🔎 Mengambil berita untuk: '{query}' ...")
    df = scrape_news(query, max_results=max_results)

    if df.empty:
        print("❌ Tidak ada berita ditemukan. Coba query lain atau periksa koneksi.")
        return

    print("🧠 Menganalisis sentimen...")
    df["combined"] = (df["title"].fillna("") + ". " + df["summary"].fillna("")).str.strip()
    df["sentiment"] = analyze_sentiment_batch(df["combined"].tolist())

    df_result = df[["title", "summary", "url", "sentiment"]]
    print("\n✅ Hasil Analisis:")
    try:
        with pd.option_context("display.max_colwidth", 100):
            print(df_result.to_string(index=False))
    except Exception:
        print(df_result)

    file_name = f"hasil_sentimen_{sanitize_filename(query)}.csv"
    df_result.to_csv(file_name, index=False, encoding="utf-8")
    print(f"\n📁 Data disimpan di: {file_name}")

if __name__ == "__main__":
    main()
