from animematch.catalog import sample_catalog
from animematch.recommender import recommend


def test_case_insensitive_favorite_exclusion():
    result = recommend(sample_catalog(), favorites=["death note"])
    assert "Death Note" not in result["title"].tolist()


def test_result_limit():
    assert len(recommend(sample_catalog(), description="action", limit=2)) <= 2


def test_empty_episode_result():
    assert recommend(sample_catalog(), description="mystery", max_episodes=1).empty
