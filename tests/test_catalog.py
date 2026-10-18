import pandas as pd
import pytest
from animematch.catalog import sample_catalog,normalize_catalog

def test_sample_has_expected_columns():
    assert {"title","genres","episodes"}.issubset(sample_catalog().columns)

def test_duplicate_titles_are_removed():
    data=pd.concat([sample_catalog(),sample_catalog().iloc[:1]],ignore_index=True)
    assert len(normalize_catalog(data))==len(sample_catalog())

def test_missing_columns_raise_error():
    with pytest.raises(ValueError):
        normalize_catalog(pd.DataFrame({"title":["Example"]}))
