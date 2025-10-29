from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.scraper import scrape_news
from app.sentiment import analyze_sentiment_batch
import pandas as pd

app = FastAPI(title="News Sentiment API", version="1.0.0")

# CORS optional: uncomment to allow browsers
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Kata kunci pencarian berita")
    max_results: int = Field(10, ge=1, le=500, description="Jumlah berita")

class ArticleOut(BaseModel):
    title: str
    summary: str
    url: str
    sentiment: str

class AnalyzeResponse(BaseModel):
    query: str
    total: int
    items: List[ArticleOut]

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        df = scrape_news(req.query, max_results=req.max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"scrape error: {e}")

    if df.empty:
        return AnalyzeResponse(query=req.query, total=0, items=[])

    df["combined"] = (df["title"].fillna("") + ". " + df["summary"].fillna("")).str.strip()
    sentiments = analyze_sentiment_batch(df["combined"].tolist())
    df["sentiment"] = sentiments

    items = [
        ArticleOut(title=row["title"], summary=row["summary"], url=row["url"], sentiment=row["sentiment"])
        for _, row in df[["title", "summary", "url", "sentiment"]].iterrows()
    ]
    return AnalyzeResponse(query=req.query, total=len(items), items=items)
