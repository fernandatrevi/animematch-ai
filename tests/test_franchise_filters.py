"""Tests for franchise-aware recommendations and optional filters."""
import pandas as pd

from animematch.recommender import franchise_key, recommend


def catalog():
    return pd.DataFrame([
        {"title": "Tokyo Ghoul", "genres": "Action Horror", "synopsis": "A dark ghoul story", "score": 8.0, "episodes": 12},
        {"title": "Tokyo Ghoul √A", "genres": "Action Horror", "synopsis": "Another ghoul story", "score": 7.0, "episodes": 12},
        {"title": "Tokyo Ghoul:re", "genres": "Action Horror", "synopsis": "More ghoul drama", "score": 7.1, "episodes": 12},
        {"title": "Parasyte", "genres": "Action Horror", "synopsis": "Parasites and survival", "score": 8.5, "episodes": 24},
        {"title": "Haikyuu", "genres": "Sports", "synopsis": "A volleyball team", "score": 9.0, "episodes": 25},
        {"title": "Haikyuu Season 2", "genres": "Sports", "synopsis": "More volleyball", "score": 8.8, "episodes": 25},
    ])


def test_tokyo_ghoul_franchise():
    assert franchise_key("Tokyo Ghoul") == franchise_key("Tokyo Ghoul √A")
    assert franchise_key("Tokyo Ghoul") == franchise_key("Tokyo Ghoul:re")


def test_favorite_sequels_excluded():
    results = recommend(catalog(), favorites=["Tokyo Ghoul"], limit=10)
    assert all("Tokyo Ghoul" not in title for title in results["title"])


def test_only_one_season_per_franchise():
    results = recommend(catalog(), description="volleyball team", limit=10)
    assert len([title for title in results["title"] if title.startswith("Haikyuu")]) == 1


def test_genre_rating_and_episode_filters():
    results = recommend(catalog(), description="dark survival", genre="Horror", min_score=8, max_episodes=24)
    assert results["title"].tolist() == ["Parasyte", "Tokyo Ghoul"]
