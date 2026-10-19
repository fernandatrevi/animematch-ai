# AnimeMatch 🎌

A personalized anime discovery website with a custom **HTML, CSS, and JavaScript** frontend, a **FastAPI** backend, and a content-based recommender built with **scikit-learn**. The original Streamlit prototype is retained.

## Website (HTML + FastAPI)

Run the custom website locally:

```bash
pip install -r requirements.txt
uvicorn server:app --reload
```

Open **http://127.0.0.1:8000** in your browser. The FastAPI server serves the HTML/CSS/JavaScript frontend and the `/api/catalog` and `/api/recommend` endpoints. This website requires a Python backend; it cannot be hosted on GitHub Pages alone.

## Original Streamlit prototype

The previous version remains available and can be deployed through [Streamlit Community Cloud](https://share.streamlit.io/) with `app.py` as the entry point. The Streamlit deployment does **not** automatically switch to the HTML website.

## Features
- Browse an expanded catalog fetched from Jikan's public anime API.
- Display cover images, synopses, genres, episode counts, and ratings when available.
- Select favorite titles or describe what you want to watch.
- Receive explainable TF-IDF + cosine-similarity recommendations.
- Optionally limit results by episode count.
- Fall back to an 18-title offline catalog if the API is unavailable.
- Train a separate, optional review sentiment classifier with labeled reviews.

## Streamlit quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows activation: `.venv\\Scripts\\activate`. The app usually opens at `http://localhost:8501`.

## Tests
```bash
python -m pytest -q
```

## Architecture
- `web/index.html`, `web/styles.css`, `web/app.js`: custom browser interface.
- `server.py`: FastAPI website and JSON endpoints.
- `app.py`: Streamlit interface and one-hour catalog cache.
- `animematch/jikan.py`: Jikan API client and metadata mapping.
- `animematch/catalog.py`: offline catalog and validation.
- `animematch/recommender.py`: TF-IDF vectorization, cosine similarity, and filtering.
- `animematch/agent.py`: recommendation result formatting.
- `animematch/sentiment.py`: independent supervised sentiment-classification utility.
- `tests/`: automated unit tests and mocked API tests.

## Data source and attribution
Anime metadata and image URLs are fetched from the [Jikan API](https://docs.api.jikan.moe/), an unofficial public MyAnimeList API. Poster images are linked from their original providers and are not stored in this repository. Jikan may impose rate limits or become temporarily unavailable. The catalog is cached for one hour to reduce requests. This project is educational and is not affiliated with Jikan or MyAnimeList.

## How recommendations work
The engine represents genres and synopses as TF-IDF vectors. It combines vectors for selected favorites and optional search text, ranks candidate anime by cosine similarity, excludes selected favorites, and applies episode filters. Similarity is not a probability of enjoyment.

## Deployment note

Deploy the HTML website to a Python-capable host using `uvicorn server:app --host 0.0.0.0 --port $PORT` (adapt the port syntax to the host). A public deployment of the new HTML website has not yet been verified.

## Current limitations
The catalog is limited to three pages of Jikan's popularity listing (up to 75 entries before filtering), not the entire MyAnimeList database. Entries without a usable synopsis are omitted; titles with unknown episode counts are excluded when the episode filter is active. API data is external and may change. This version is a deterministic recommendation assistant, **not a generative LLM agent**. The sentiment classifier is not yet connected to the interface.

## Roadmap
Expand catalog search and pagination, measure Precision@K and Recall@K on real preference data, evaluate review sentiment on held-out labeled reviews, and add a tool-using LLM with grounded explanations.

## License
MIT.
