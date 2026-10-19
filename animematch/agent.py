"""Deterministic tool-routing assistant for the MVP."""
from .recommender import recommend

def answer_request(catalog,favorites=(),description="",max_episodes=None):
    results=recommend(catalog,favorites,description,max_episodes)
    return [{"title":row.title,"score":row.score,"episodes":row.episodes,
             "genres":row.genres,"synopsis":row.synopsis,
             "similarity":float(row.similarity),
             "image_url":getattr(row,"image_url",None),
             "url":getattr(row,"url",None),
             "reason":f"Matches the themes in your request ({row.genres})."}
            for row in results.itertuples()]
