"""Content-based anime recommendation engine."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .catalog import normalize_catalog

def recommend(catalog,favorites=(),description="",max_episodes=None,limit=5):
    data=normalize_catalog(catalog)
    if data.empty:
        return data.assign(similarity=[])
    favorites=[str(f).strip() for f in favorites if str(f).strip()]
    documents=(data["genres"]+" "+data["genres"]+" "+data["synopsis"]).tolist()
    vectorizer=TfidfVectorizer(stop_words="english",ngram_range=(1,2))
    matrix=vectorizer.fit_transform(documents)
    selected=data["title"].str.casefold().isin([f.casefold() for f in favorites]).to_numpy()
    if not selected.any() and not description.strip():
        raise ValueError("Choose a favorite anime or enter a description.")
    vectors=[]
    if selected.any():
        vectors.append(np.asarray(matrix[selected].mean(axis=0)).reshape(1,-1))
    if description.strip():
        vectors.append(vectorizer.transform([description]).toarray())
    query=np.mean(np.vstack(vectors),axis=0).reshape(1,-1)
    scores=cosine_similarity(matrix,query).ravel()
    result=data.assign(similarity=scores).loc[~selected]
    if max_episodes is not None:
        result=result.loc[result["episodes"].notna() & (result["episodes"]<=max_episodes)]
    return result.sort_values(["similarity","score"],ascending=[False,False],kind="stable").head(limit).reset_index(drop=True)
