# sentiment.py
import re
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import torch

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

# pakai tokenizer "slow" untuk hindari dependency tiktoken
_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
_model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
_device = 0 if torch.cuda.is_available() else -1
_pipeline = TextClassificationPipeline(
    model=_model,
    tokenizer=_tokenizer,
    device=_device,
    top_k=None,
)

_label_map = {
    "negative": "negative",
    "neutral": "neutral",
    "positive": "positive",
    "1 star": "negative", "2 stars": "negative",
    "3 stars": "neutral",
    "4 stars": "positive", "5 stars": "positive",
}

_url_re = re.compile(r"https?://\S+")
_ws_re = re.compile(r"\s+")

def _prep(text: str) -> str:
    if not text:
        return ""
    t = _url_re.sub("", text)
    t = t.replace("\u200b", " ")
    t = _ws_re.sub(" ", t).strip()
    return t

def _label_to_sentiment(label: str) -> str:
    return _label_map.get(label, "neutral")

def analyze_sentiment(text: str) -> str:
    t = _prep(text or "")
    if not t:
        return "neutral"
    out = _pipeline(t, truncation=True)
    label = out[0]["label"] if isinstance(out, list) else out["label"]
    return _label_to_sentiment(label)

def analyze_sentiment_batch(texts: List[str]) -> List[str]:
    prepped = [_prep(x or "") for x in texts]
    results = ["neutral"] * len(prepped)
    idx = [i for i, t in enumerate(prepped) if t]
    if idx:
        outs = _pipeline([prepped[i] for i in idx], truncation=True, batch_size=16)
        for j, out in enumerate(outs):
            label = out[0]["label"]
            results[idx[j]] = _label_to_sentiment(label)
    return results
