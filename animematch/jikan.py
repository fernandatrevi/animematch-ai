"""Jikan API integration for live anime metadata and poster images."""
import requests
import pandas as pd

BASE_URL = "https://api.jikan.moe/v4"
HEADERS = {"User-Agent": "AnimeMatchAI/0.2 (educational project)"}


def parse_anime(item):
    """Map a Jikan anime response to the recommender schema."""
    if not isinstance(item, dict):
        return None
    title = item.get("title_english") or item.get("title")
    synopsis = item.get("synopsis") or ""
    if not title or not synopsis.strip():
        return None
    genres = [g.get("name", "") for key in ("genres", "themes", "demographics")
              for g in (item.get(key) or []) if isinstance(g, dict)]
    images = item.get("images") or {}
    jpg = images.get("jpg") or {}
    webp = images.get("webp") or {}
    return {
        "title": title,
        "genres": " ".join(genres) or "Anime",
        "synopsis": synopsis,
        "score": item.get("score"),
        "episodes": item.get("episodes"),
        "image_url": webp.get("large_image_url") or jpg.get("large_image_url")
                     or jpg.get("image_url"),
        "mal_id": item.get("mal_id"),
        "url": item.get("url"),
    }


def fetch_anime_catalog(pages=3, timeout=12, session=None):
    """Fetch up to 25 titles per page from Jikan's top-anime endpoint.

    Raise a RuntimeError on request failures so the UI can use offline fallback.
    """
    if not 1 <= pages <= 5:
        raise ValueError("pages must be between 1 and 5")
    client = session or requests
    items = []
    for page in range(1, pages + 1):
        try:
            response = client.get(
                f"{BASE_URL}/top/anime",
                params={"page": page, "limit": 25, "filter": "bypopularity"},
                headers=HEADERS,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            if items:
                break  # Keep successful pages if a later request is rate-limited.
            raise RuntimeError("Could not retrieve anime data from Jikan.") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise RuntimeError("Jikan returned an unexpected response.")
        items.extend(parsed for item in payload["data"]
                     if (parsed := parse_anime(item)) is not None)
    if not items:
        raise RuntimeError("Jikan returned no usable anime entries.")
    data = pd.DataFrame(items)
    return data.drop_duplicates(subset=["mal_id"]).reset_index(drop=True)

def fetch_anime_poster(title, timeout=8, session=None):
    """Look up a single anime poster; return None if unavailable."""
    client = session or requests
    try:
        response = client.get(
            f"{BASE_URL}/anime",
            params={"q": title, "limit": 1},
            headers=HEADERS,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        if data:
            images = data[0].get("images") or {}
            jpg = images.get("jpg") or {}
            webp = images.get("webp") or {}
            return webp.get("large_image_url") or jpg.get("large_image_url") or jpg.get("image_url")
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        pass
    return None
