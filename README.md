# News Sentiment API (Ubuntu, CPU only)

## Setup
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip build-essential
cd /opt
sudo mkdir -p /opt/news-sentiment/app
sudo chown -R $USER:$USER /opt/news-sentiment
cd /opt/news-sentiment
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
# salin semua file repo ini ke /opt/news-sentiment lalu:
pip install -r requirements.txt
```

## Run dev
```bash
source /opt/news-sentiment/venv/bin/activate
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

## Test
```bash
curl -s http://127.0.0.1:8000/healthz
curl -s -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query":"inflasi Indonesia","max_results":5}' | jq .
```

## Systemd service
Create file `/etc/systemd/system/news-sentiment.service`:
```ini
[Unit]
Description=News Sentiment REST API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/news-sentiment
Environment="PATH=/opt/news-sentiment/venv/bin"
ExecStart=/opt/news-sentiment/venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo chown -R www-data:www-data /opt/news-sentiment
sudo systemctl daemon-reload
sudo systemctl enable --now news-sentiment
sudo systemctl status news-sentiment --no-pager
```

## Notes
- CPU only. No CUDA needed.
- Tokenizer uses `use_fast=False` to avoid `tiktoken` dependency.
