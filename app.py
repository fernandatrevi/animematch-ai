"""AnimeMatch AI: image-rich anime discovery powered by Jikan and TF-IDF."""
import pandas as pd
import streamlit as st

from animematch.agent import answer_request
from animematch.catalog import sample_catalog
from animematch.jikan import fetch_anime_catalog, fetch_anime_poster

st.set_page_config(page_title="AnimeMatch AI", page_icon="🎌", layout="wide")
st.title("🎌 AnimeMatch AI")
st.caption("Discover anime with personalized recommendations and real cover art.")


@st.cache_data(ttl=3600, show_spinner=False)
def load_live_catalog():
    return fetch_anime_catalog(pages=1)


@st.cache_data(ttl=86400, show_spinner=False)
def lookup_poster(title):
    return fetch_anime_poster(title)


with st.spinner("Loading anime catalog and posters..."):
    try:
        catalog = load_live_catalog()
        source = "Jikan API"
    except RuntimeError:
        catalog = sample_catalog()
        source = "offline demo"

if source == "Jikan API":
    st.success(f"Explore {len(catalog)} anime with live metadata and cover art from Jikan (MyAnimeList unofficial API).")
else:
    st.warning("Jikan catalog is temporarily unavailable. Using the 18-title offline catalog; poster lookup will be attempted separately.")

with st.form("recommendation"):
    favorites = st.multiselect(
        "Anime you already enjoy",
        catalog["title"].tolist(),
        default=["Death Note"] if "Death Note" in catalog["title"].values else [],
    )
    description = st.text_input(
        "Describe what you want to watch",
        placeholder="dark mystery with psychological tension",
    )
    restrict = st.checkbox("Limit episode count", value=False)
    max_episodes = st.number_input(
        "Maximum episodes", min_value=1, max_value=500,
        value=30, disabled=not restrict,
    )
    submitted = st.form_submit_button("Find recommendations", type="primary")

if submitted:
    try:
        results = answer_request(
            catalog, favorites, description,
            int(max_episodes) if restrict else None,
        )
        if not results:
            st.warning("No titles match your filters. Try another description or episode limit.")
        for index, anime in enumerate(results, 1):
            with st.container(border=True):
                poster, details = st.columns([1, 4], gap="large")
                with poster:
                    image_url = anime.get("image_url")
                    if not isinstance(image_url, str) or not image_url.startswith("https://"):
                        image_url = lookup_poster(anime["title"])
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.caption("Poster unavailable")
                with details:
                    st.subheader(f"{index}. {anime['title']}")
                    episodes = anime["episodes"]
                    episodes_text = "Unknown" if pd.isna(episodes) else str(int(episodes))
                    score = anime["score"]
                    score_text = "N/A" if pd.isna(score) else f"{score:.1f}/10"
                    st.write(f"**Genres:** {anime['genres']}")
                    st.write(f"**Episodes:** {episodes_text} · **Score:** {score_text}")
                    st.write(anime["synopsis"])
                    st.caption(anime["reason"])
                    if isinstance(anime.get("url"), str) and anime["url"].startswith("https://"):
                        st.markdown(f"[View anime details]({anime['url']})")
    except ValueError as exc:
        st.error(str(exc))

with st.expander("How does it work?"):
    st.write(
        "Jikan provides public anime metadata and poster URLs. "
        "TF-IDF converts genres and synopses into vectors; cosine similarity ranks "
        "anime based on your favorites and description. Results exclude selected favorites. "
        "The catalog is cached for one hour to reduce API requests. "
        "Similarity is not a probability of enjoyment. "
        "This is a content-based recommendation assistant, not a generative LLM agent."
    )
st.caption("Anime metadata and artwork: Jikan API / MyAnimeList. Images remain hosted by their providers.")
