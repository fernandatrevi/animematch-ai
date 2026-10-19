"""Explain recommendations using the same TF-IDF features as the ranking model."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .catalog import normalize_catalog


def explain_recommendations(catalog, recommendations, favorites=(), description=""):
    """Return model-grounded shared terms and genres for each recommended title.

    Contributions are the elementwise product of TF-IDF candidate and query vectors,
    which add up to the cosine similarity for normalized vectors.
    """
    data = normalize_catalog(catalog)
    if data.empty or recommendations.empty:
        return []
    docs = (data["genres"] + " " + data["genres"] + " " + data["synopsis"]).tolist()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(docs)
    selected = data["title"].str.casefold().isin(
        [str(f).strip().casefold() for f in favorites]
    ).to_numpy()
    vectors = []
    if selected.any():
        vectors.append(np.asarray(matrix[selected].mean(axis=0)).reshape(1, -1))
    if description.strip():
        vectors.append(vectorizer.transform([description]).toarray())
    if not vectors:
        return [{} for _ in range(len(recommendations))]
    query = np.mean(np.vstack(vectors), axis=0).reshape(1, -1)
    norm = np.linalg.norm(query)
    if norm:
        query = query / norm
    terms = vectorizer.get_feature_names_out()
    by_title = {title.casefold(): index for index, title in enumerate(data["title"])}
    output = []
    for row in recommendations.itertuples():
        idx = by_title.get(str(row.title).casefold())
        if idx is None:
            output.append({})
            continue
        contributions = matrix[idx].multiply(query).toarray().ravel()
        top_indices = np.argsort(-contributions, kind="stable")
        keywords = [str(terms[i]) for i in top_indices if contributions[i] > 0][:4]
        genres = [
            genre for genre in (
                "Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror",
                "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life",
                "Sports", "Supernatural", "Thriller"
            )
            if genre.casefold() in str(row.genres).casefold()
        ][:3]
        output.append({
            "keywords": keywords,
            "genres": genres,
            "similarity": round(float(row.similarity), 4),
            "method": "TF-IDF cosine similarity",
        })
    return output
