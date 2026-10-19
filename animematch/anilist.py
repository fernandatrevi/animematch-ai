"""AniList GraphQL API as an alternative anime catalog and poster source."""
import re

import pandas as pd
import requests

ENDPOINT = "https://graphql.anilist.co"
QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: ANIME, sort: POPULARITY_DESC) {
      id
      title { english romaji }
      description(asHtml: false)
      genres
      episodes
      averageScore
      coverImage { extraLarge large }
      siteUrl
    }
  }
}
"""


def clean_description(value):
    """Strip basic markup and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", text).strip()


def parse_anilist(item):
    """Normalize one AniList anime into the app's catalog schema."""
    title = item.get("title") or {}
    name = title.get("english") or title.get("romaji")
    synopsis = clean_description(item.get("description"))
    if not name or not synopsis:
        return None
    cover = item.get("coverImage") or {}
    rating = item.get("averageScore")
    return {
        "title": name,
        "genres": " ".join(item.get("genres") or []) or "Anime",
        "synopsis": synopsis,
        "score": rating / 10 if isinstance(rating, (int, float)) else None,
        "episodes": item.get("episodes"),
        "image_url": cover.get("extraLarge") or cover.get("large"),
        "mal_id": None,
        "url": item.get("siteUrl"),
    }


def fetch_anilist_catalog(pages=2, timeout=12, session=None):
    """Fetch popular anime with cover images from AniList."""
    if not 1 <= pages <= 10:
        raise ValueError("pages must be between 1 and 10")
    client = session or requests
    entries = []
    for page in range(1, pages + 1):
        try:
            response = client.post(
                ENDPOINT,
                json={"query": QUERY, "variables": {"page": page, "perPage": 50}},
                headers={"Content-Type": "application/json"},
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            items = payload["data"]["Page"]["media"]
            if not isinstance(items, list):
                raise ValueError("Unexpected AniList response")
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            if entries:
                break
            raise RuntimeError("Could not retrieve anime data from AniList.") from exc
        entries.extend(entry for item in items if (entry := parse_anilist(item)) is not None)
        if len(items) < 50:
            break
    if not entries:
        raise RuntimeError("AniList returned no usable anime entries.")
    return pd.DataFrame(entries).drop_duplicates(subset=["title"]).reset_index(drop=True)


def fetch_anilist_poster(title, timeout=8, session=None):
    """Look up an anime cover on AniList when the catalog is offline."""
    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) { coverImage { extraLarge large } }
    }
    """
    client = session or requests
    try:
        response = client.post(
            ENDPOINT,
            json={"query": query, "variables": {"search": title}},
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        response.raise_for_status()
        cover = response.json()["data"]["Media"]["coverImage"] or {}
        return cover.get("extraLarge") or cover.get("large")
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None
