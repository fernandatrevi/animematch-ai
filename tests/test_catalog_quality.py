import pandas as pd
from animematch.catalog import normalize_catalog, sample_catalog


def test_catalog_has_unique_titles():
    assert sample_catalog()["title"].is_unique


def test_catalog_episodes_are_positive():
    assert (sample_catalog()["episodes"] > 0).all()


def test_catalog_converts_numeric_fields():
    data = sample_catalog().copy()
    data["episodes"] = data["episodes"].astype(str)
    assert pd.api.types.is_numeric_dtype(normalize_catalog(data)["episodes"])
