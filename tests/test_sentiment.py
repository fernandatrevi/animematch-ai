import pytest
from animematch.sentiment import train_sentiment

def test_classifier_fits_small_fixture():
    model=train_sentiment(["amazing story","great animation","boring plot","terrible pacing"],[1,1,0,0])
    assert model.predict(["amazing animation"])[0] in (0,1)

def test_classifier_rejects_one_class():
    with pytest.raises(ValueError):
        train_sentiment(["good","great"],[1,1])
