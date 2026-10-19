"""FastAPI backend serving the AnimeMatch HTML frontend and recommendation API."""
from functools import lru_cache
from pathlib import Path
from time import monotonic
import math
import threading

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from animematch.catalog import sample_catalog
from animematch.jikan import fetch_anime_catalog
from animematch.anilist import fetch_anilist_catalog
from animematch.recommender import recommend

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="AnimeMatch", version="0.3")
app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
_cache_lock = threading.Lock()
_cache = {"expires": 0.0, "data": None, "source": None}


def get_catalog():
    with _cache_lock:
        if _cache["data"] is not None and monotonic() < _cache["expires"]:
            return _cache["data"], _cache["source"]
    try:
        data, source = fetch_anime_catalog(pages=1, timeout=6), "Jikan"
    except RuntimeError:
        try:
            data, source = fetch_anilist_catalog(pages=2, timeout=8), "AniList"
        except RuntimeError:
            data, source = sample_catalog(), "Offline demo"
    with _cache_lock:
        _cache.update(data=data, source=source, expires=monotonic() + (3600 if source != "Offline demo" else 180))
    return data, source


def safe_number(value):
    if value is None:
        return None
    try:
        return None if math.isnan(float(value)) else float(value)
    except (TypeError, ValueError):
        return None


def serialize_row(row):
    return {
        "title": str(row.title),
        "genres": str(row.genres),
        "synopsis": str(row.synopsis),
        "score": safe_number(row.score),
        "episodes": safe_number(row.episodes),
        "image_url": getattr(row, "image_url", None) if isinstance(getattr(row, "image_url", None), str) else None,
        "url": getattr(row, "url", None) if isinstance(getattr(row, "url", None), str) else None,
    }


class RecommendationRequest(BaseModel):
    favorites: list[str] = Field(default_factory=list, max_length=10)
    description: str = Field(default="", max_length=500)
    max_episodes: int | None = Field(default=None, ge=1, le=1000)
    limit: int = Field(default=9, ge=1, le=24)


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/catalog")
def catalog():
    data, source = get_catalog()
    return {"source": source, "count": len(data), "items": [serialize_row(row) for row in data.itertuples()]}


@app.post("/api/recommend")
def recommendations(payload: RecommendationRequest):
    data, source = get_catalog()
    try:
        results = recommend(data, payload.favorites, payload.description, payload.max_episodes, payload.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"source": source, "items": [
        {**serialize_row(row), "similarity": round(float(row.similarity), 4)}
        for row in results.itertuples()
    ]}
