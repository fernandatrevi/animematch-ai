"""Jikan API mapping and network error handling tests."""
import pytest
import requests

from animematch.jikan import fetch_anime_catalog, parse_anime


def example():
    return {
        "mal_id": 1,
        "title": "Example",
        "title_english": "Example English",
        "synopsis": "An adventurous story about friendship.",
        "genres": [{"name": "Adventure"}],
        "themes": [{"name": "Teamwork"}],
        "episodes": 12,
        "score": 8.2,
        "images": {"jpg": {"image_url": "https://example.com/cover.jpg"}},
        "url": "https://myanimelist.net/anime/1",
    }


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"data": [example()]}


class FakeSession:
    def get(self, *args, **kwargs):
        return FakeResponse()


class BrokenSession:
    def get(self, *args, **kwargs):
        raise requests.Timeout("request timed out")


def test_parse_anime_metadata_and_image():
    item = parse_anime(example())
    assert item["title"] == "Example English"
    assert "Adventure" in item["genres"]
    assert item["image_url"] == "https://example.com/cover.jpg"


def test_fetch_catalog_deduplicates_across_pages():
    data = fetch_anime_catalog(pages=2, session=FakeSession())
    assert len(data) == 1
    assert data.iloc[0]["episodes"] == 12


def test_fetch_catalog_handles_network_failure():
    with pytest.raises(RuntimeError, match="Could not retrieve"):
        fetch_anime_catalog(session=BrokenSession())


def test_fetch_catalog_rejects_excessive_pages():
    with pytest.raises(ValueError):
        fetch_anime_catalog(pages=10)


def test_parse_anime_skips_missing_synopsis():
    assert parse_anime({"title": "Example", "synopsis": None}) is None
