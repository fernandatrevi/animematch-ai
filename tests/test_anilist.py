"""Tests for the AniList fallback integration."""
import pytest
import requests
from animematch.anilist import parse_anilist, fetch_anilist_catalog, fetch_anilist_poster

ENTRY = {
    "id": 42,
    "title": {"english": "Example", "romaji": "Example Anime"},
    "description": "A <b>mysterious</b> adventure.",
    "genres": ["Mystery", "Adventure"],
    "episodes": 12,
    "averageScore": 83,
    "coverImage": {"extraLarge": "https://example.org/poster.jpg"},
    "siteUrl": "https://anilist.co/anime/42",
}

class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {"data": {"Page": {"media": [ENTRY]}}}

class FakeSession:
    def post(self, *args, **kwargs):
        return FakeResponse()

class OfflineSession:
    def post(self, *args, **kwargs):
        raise requests.Timeout("offline")


def test_anilist_maps_poster_and_score():
    item = parse_anilist(ENTRY)
    assert item["image_url"] == "https://example.org/poster.jpg"
    assert item["score"] == 8.3
    assert "<b>" not in item["synopsis"]


def test_anilist_catalog_deduplicates_titles():
    assert len(fetch_anilist_catalog(pages=2, session=FakeSession())) == 1


def test_anilist_handles_network_failure():
    with pytest.raises(RuntimeError):
        fetch_anilist_catalog(session=OfflineSession())


def test_anilist_poster_handles_network_failure():
    assert fetch_anilist_poster("Example", session=OfflineSession()) is None
