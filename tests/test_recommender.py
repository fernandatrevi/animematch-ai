import pytest
from animematch.catalog import sample_catalog
from animematch.recommender import recommend
from animematch.agent import answer_request

def test_excludes_favorite():
    assert "Death Note" not in recommend(sample_catalog(),favorites=["Death Note"])["title"].tolist()

def test_episode_limit():
    assert (recommend(sample_catalog(),description="mystery",max_episodes=13)["episodes"]<=13).all()

def test_requires_preferences():
    with pytest.raises(ValueError):
        recommend(sample_catalog())

def test_agent_explains_results():
    assert all("reason" in item for item in answer_request(sample_catalog(),["Erased"]))
