# Sentiment Scraper

Scraping berita berdasarkan query dan analisis sentimen menggunakan TextBlob.

## 📦 Setup

1. Clone / download repo
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   python -m textblob.download_corpora
   ```

## 🚀 Jalankan

```bash
python main.py
```

Masukkan query seperti `Elon Musk`, `Krisis Ekonomi`, dll.

## 📝 Output

File CSV berisi:
- Judul berita
- Ringkasan
- URL
- Hasil sentimen (`positive`, `negative`, `neutral`)

pip install --upgrade transformers torch sentencepiece protobuf