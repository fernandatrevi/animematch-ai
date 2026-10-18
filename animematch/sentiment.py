"""Optional sentiment classifier for labeled review datasets."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

def train_sentiment(reviews,labels):
    if len(reviews)!=len(labels) or len(set(labels))!=2:
        raise ValueError("Provide aligned reviews and exactly two sentiment classes.")
    model=make_pipeline(TfidfVectorizer(ngram_range=(1,2)),LogisticRegression(max_iter=1000))
    model.fit(reviews,labels)
    return model
