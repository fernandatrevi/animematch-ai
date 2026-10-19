"""Content-based anime recommendation engine."""
import re
import unicodedata

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .catalog import normalize_catalog


def franchise_key(title):
    """Conservatively group sequels under the same franchise title.

    Only explicit sequel markers and well-known punctuation variants are stripped.
    Distinct spin-offs with different names may still appear separately.
    """
    text = unicodedata.normalize("NFKC", str(title)).casefold().strip()
    text = re.sub(r"[’']", "'", text)
    text = re.sub(r"\s+", " ", text)
    # Tokyo Ghoul √A / Tokyo Ghoul VA are sequel titles of Tokyo Ghoul.
    if re.match(r"^tokyo ghoul(?:$|\s|:|√)", text):
        return "tokyo ghoul"
    text = re.sub(r"\s*[:\-]\s*(?:season\s*\d+|part\s*\d+|\d+(?:st|nd|rd|th)\s+season)\b.*$", "", text)
    text = re.sub(r"\s+(?:season\s*\d+|\d+(?:st|nd|rd|th)\s+season|part\s*\d+)\b.*$", "", text)
    text = re.sub(r"\s+\d+(?:nd|rd|th)\s+season\b.*$", "", text)
    return text.strip()


def recommend(catalog, favorites=(), description="", max_episodes=None, limit=5,
              genre=None, min_score=None):
    data = normalize_catalog(catalog)
    if data.empty:
        return data.assign(similarity=[])
    favorites = [str(f).strip() for f in favorites if str(f).strip()]
    documents = (data["genres"] + " " + data["genres"] + " " + data["synopsis"]).tolist()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents)
    selected = data["title"].str.casefold().isin([f.casefold() for f in favorites]).to_numpy()
    if not selected.any() and not description.strip():
        raise ValueError("Choose a favorite anime or enter a description.")
    vectors = []
    if selected.any():
        vectors.append(np.asarray(matrix[selected].mean(axis=0)).reshape(1, -1))
    if description.strip():
        vectors.append(vectorizer.transform([description]).toarray())
    query = np.mean(np.vstack(vectors), axis=0).reshape(1, -1)
    scores = cosine_similarity(matrix, query).ravel()
    result = data.assign(similarity=scores).loc[~selected]
    excluded_franchises = {franchise_key(title) for title in favorites}
    result = result.loc[~result["title"].map(franchise_key).isin(excluded_franchises)]
    if max_episodes is not None:
        result = result.loc[result["episodes"].notna() & (result["episodes"] <= max_episodes)]
    if genre:
        result = result.loc[result["genres"].str.contains(re.escape(genre), case=False, regex=True)]
    if min_score is not None:
        result = result.loc[result["score"].notna() & (result["score"] >= min_score)]
    result = result.sort_values(["similarity", "score"], ascending=[False, False], kind="stable")
    # Show one entry per franchise to prevent season-heavy results.
    result = result.assign(_franchise=result["title"].map(franchise_key))
    result = result.drop_duplicates(subset=["_franchise"]).drop(columns=["_franchise"])
    return result.head(limit).reset_index(drop=True)
