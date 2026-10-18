# AnimeMatch AI 🎌

A browser-based, explainable anime recommendation prototype built with **Python, scikit-learn, and Streamlit**.

## Features
- Select favorite anime and describe what you want to watch.
- Filter recommendations by maximum episode count.
- Rank titles with TF-IDF and cosine similarity.
- Read synopsis and explanations for each recommendation.
- Train an optional review sentiment classifier with labeled examples.

> **MVP scope:** Uses a small, offline, manually curated demo catalog of 15 titles. Ratings are illustrative, not live. The assistant routes requests to a deterministic recommendation tool; it is **not yet an LLM agent**. The sentiment classifier is implemented but not integrated into the UI because no licensed labeled review dataset has been added.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows activation: `.venv\Scripts\activate`. Streamlit normally opens `http://localhost:8501`.

## Tests

```bash
pytest -q
```

## Architecture
- `app.py` — Streamlit interface.
- `animematch/catalog.py` — catalog and validation.
- `animematch/recommender.py` — TF-IDF ranking and filtering.
- `animematch/agent.py` — request routing and explanations.
- `animematch/sentiment.py` — optional supervised sentiment classifier.
- `tests/` — automated tests.

## How it works
The engine converts genre tags and synopsis into TF-IDF vectors, combining chosen favorites and a text query. Cosine similarity ranks unseen anime. Episode limits are strict filters. Similarity is **not** a calibrated probability of enjoyment.

## Limitations and next steps
The small catalog does not support credible recommendation benchmarks. No live API, LLM, or review ingestion is implemented. Future work: integrate a licensed larger catalog, evaluate Precision@K / Recall@K on held-out preferences, train and validate sentiment on labeled reviews, add retrieval-augmented agent tools, and deploy the application.

## License
MIT.
