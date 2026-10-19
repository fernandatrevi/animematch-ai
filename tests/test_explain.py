"""Validate explanations are grounded in shared TF-IDF features."""
import pandas as pd

from animematch.explain import explain_recommendations
from animematch.recommender import recommend


def test_explanation_has_matching_features():
    catalog = pd.DataFrame([
        {"title": "Favorite", "genres": "Horror Mystery", "synopsis": "Dark mystery horror", "score": 8, "episodes": 12},
        {"title": "Similar", "genres": "Horror Mystery", "synopsis": "Dark horror mystery", "score": 8, "episodes": 12},
        {"title": "Different", "genres": "Sports Comedy", "synopsis": "Happy volleyball team", "score": 8, "episodes": 12},
    ])
    results = recommend(catalog, favorites=["Favorite"], limit=2)
    explanations = explain_recommendations(catalog, results, favorites=["Favorite"])
    assert len(explanations) == len(results)
    assert explanations[0]["method"] == "TF-IDF cosine similarity"
    assert explanations[0]["keywords"]
    assert explanations[0]["similarity"] == round(float(results.iloc[0]["similarity"]), 4)


def test_empty_results():
    catalog = pd.DataFrame(columns=["title", "genres", "synopsis", "score", "episodes"])
    assert explain_recommendations(catalog, catalog) == []
