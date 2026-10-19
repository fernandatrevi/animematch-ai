# AnimeMatch 🎌

**Find your next obsession.**

Discover anime tailored to your taste.

[**🌐 Explore the live website**](https://animematch.onrender.com)

AnimeMatch is a personalized anime discovery website that recommends titles based on a viewer's favorite anime, written preferences, and optional filters. It combines a custom web interface with a **content-based recommendation model** built in Python.

The project focuses on **applied data analytics, natural language processing, recommendation systems, and model interpretability**.

## Project overview

Finding something new to watch can be difficult when anime platforms contain hundreds of titles, sequels, and related series. AnimeMatch helps viewers narrow down their choices by comparing the **genres and synopses** of anime with their interests.

Rather than ranking anime only by popularity, the recommendation engine uses **TF-IDF and cosine similarity** to identify titles with related content. It also explains which shared textual features contributed to the recommendation.

**Live website:** https://animematch.onrender.com

## Features

- **Personalized recommendations:** Select favorite anime and/or describe the kind of story you want to watch.
- **Expanded anime catalog:** Fetch up to 500 anime entries through paginated AniList requests when the service is available.
- **Anime metadata:** Display cover art, synopses, genres, episode counts, and ratings where available.
- **Optional filters:** Narrow recommendations by genre, minimum rating, and maximum episode count.
- **Franchise-aware results:** Exclude selected favorites and group some related seasons or sequels to reduce repetitive recommendations (including Tokyo Ghoul and Tokyo Ghoul √A).
- **Why this anime?:** Expand each recommendation to see the textual features that contributed to its ranking.
- **Responsive interface:** Custom dark-themed HTML, CSS, and JavaScript website.
- **Fallback catalog:** Use a smaller local sample catalog if the external APIs are unavailable.

## How the recommendation model works

### 1. Collect viewer preferences

The viewer selects one or more favorite anime, enters a free-text description, or uses both. For example:

- Favorite anime: **Tokyo Ghoul**
- Description: **Dark psychological horror with a mystery**

### 2. Prepare the anime descriptions

For every anime, the model combines the **genres and synopsis** into a text document. Genre text is repeated to give genre matches more influence in the representation.

The website retrieves catalog data from the Jikan API when available and falls back to AniList if Jikan fails. If both are unavailable, the local sample catalog is used.

### 3. Convert text into TF-IDF vectors

The recommendation engine uses scikit-learn's `TfidfVectorizer` with English stop-word removal and **unigrams and bigrams** (`ngram_range=(1, 2)`).

**TF-IDF (Term Frequency–Inverse Document Frequency)** assigns weights to words and phrases based on how informative they are within the catalog. Common words receive less emphasis than terms that help distinguish anime descriptions.

This converts textual information into numeric vectors that can be compared mathematically.

### 4. Construct the viewer's preference vector

The model creates a representation of the selected favorites and/or written description. If both are provided, it combines their vectors by averaging them.

### 5. Rank titles using cosine similarity

The system compares the viewer's preference vector with the vector for each anime using **cosine similarity**:

```text
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

A larger similarity score indicates greater overlap in the TF-IDF representation. **It is not a probability that the viewer will enjoy the anime**, and it should not be confused with the anime's public rating.

### 6. Apply filters and reduce repeated franchises

The system excludes selected favorites and uses title-based franchise rules to remove certain related seasons. It then applies optional genre, minimum-rating, and episode-count filters, sorts by similarity (with public rating as a secondary sorting criterion), and returns the highest-ranked titles.

Franchise detection is heuristic, not a comprehensive anime relationship database. Some spin-offs or alternate titles may still be treated as separate series.

## Explainability: "Why this anime?"

AnimeMatch includes an expandable **Why this anime?** section on recommendation cards.

The explanation module (`animematch/explain.py`) uses the **same TF-IDF vectorizer configuration and viewer preferences** as the recommender. For a recommended title, it computes the element-wise product between the title's TF-IDF vector and the normalized preference vector, then identifies the highest positive term contributions.

These terms are displayed to show **which shared words or phrases helped increase the similarity score**.

For example, when the relevant terms overlap, an explanation may highlight words such as `horror`, `mystery`, or `psychological`.

**Important distinctions:**

- Explanations are derived from model features, not generated by an LLM.
- Displayed genres provide additional context; they are not a separate causal analysis.
- Shared terms help explain textual similarity, **not** whether the viewer will actually like the anime.
- Explanations do not claim to identify the emotional or narrative reasons behind a viewer's preferences.

This feature makes the ranking process more transparent and demonstrates a practical approach to **interpretable machine learning**.

## Technology stack

| Layer | Technologies | Purpose |
| --- | --- | --- |
| Frontend | HTML, CSS, JavaScript | Responsive website, inputs, filters, and recommendation cards |
| Backend | Python, FastAPI, Pydantic | Serve the website and validate API requests |
| Data processing | pandas, NumPy | Prepare anime metadata and model inputs |
| Recommendation model | scikit-learn | TF-IDF vectorization and cosine similarity |
| Anime data | Jikan API, AniList GraphQL API | Retrieve anime metadata and cover image URLs |
| Testing | pytest, FastAPI TestClient | Unit tests and API integration tests |
| Version control | Git, GitHub | Track development and code changes |
| Deployment | Render | Host the Python backend and website |

## Project architecture

```text
animematch-ai/
├── web/
│   ├── index.html             # Website structure
│   ├── styles.css             # Responsive visual design
│   └── app.js                 # Search, filters, and recommendation cards
├── animematch/
│   ├── catalog.py             # Catalog validation and local sample
│   ├── jikan.py               # Jikan API integration
│   ├── anilist.py             # AniList GraphQL integration
│   ├── recommender.py         # TF-IDF ranking and franchise filtering
│   ├── explain.py             # Recommendation feature explanations
│   ├── agent.py               # Deterministic recommendation wrapper
│   └── sentiment.py           # Separate sentiment classifier utility
├── tests/                     # Automated tests
├── server.py                  # FastAPI application and JSON endpoints
├── app.py                     # Original Streamlit prototype
├── render.yaml                # Render deployment configuration
└── requirements.txt           # Python dependencies
```

## Run locally

Clone the repository and install the dependencies:

```bash
git clone https://github.com/fernandatrevi/animematch-ai.git
cd animematch-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment using `.venv\Scripts\activate`.

Start the website:

```bash
uvicorn server:app --reload
```

Open **http://127.0.0.1:8000**.

### API endpoints

- `GET /` — HTML website
- `GET /api/catalog` — Anime catalog and data source
- `POST /api/recommend` — Recommendations and model explanations
- `GET /api/health` — Health check

Example request:

```json
{
  "favorites": ["Tokyo Ghoul"],
  "description": "Dark psychological mystery",
  "genre": "Horror",
  "min_score": 7,
  "max_episodes": 24,
  "limit": 9
}
```

## Run tests

```bash
python -m pytest -q
```

The test suite includes recommender behavior, franchise filtering, API response handling, and explanation logic. Tests should be run after changes; a successful deployment alone does not prove that every test passes.

## Original Streamlit prototype

The original version remains in `app.py` and can be launched separately:

```bash
streamlit run app.py
```

The HTML/FastAPI website is the current public-facing version. The Streamlit prototype is retained as part of the project's development history.

## Data sources and attribution

AnimeMatch uses the [Jikan API](https://docs.api.jikan.moe/) and the [AniList API](https://docs.anilist.co/) to obtain anime metadata and image URLs. The live site may show a different catalog size depending on external API availability and fallback behavior.

Artwork is displayed from source-provided URLs and belongs to its respective rights holders. AnimeMatch is an independent educational project and is not affiliated with AniList, Jikan, MyAnimeList, or the anime rights holders.

## Limitations and next steps

- The catalog is **not the entire anime universe**; current AniList pagination is capped at ten pages (up to 500 entries before filtering).
- The franchise filter relies on title patterns and does not capture every sequel or spin-off.
- Recommendation quality has **not yet been validated against real user preference labels**. Similarity-based ranking alone does not establish recommendation accuracy.
- The system does not currently learn from user ratings or watch history.
- The separate sentiment classifier is not connected to the public interface.
- This is a deterministic content-based recommender, **not a generative AI agent**.

Possible next steps include evaluating Precision@K and Recall@K using collected preference data, adding structured franchise relationships, and expanding the catalog search experience.

## License

MIT.
