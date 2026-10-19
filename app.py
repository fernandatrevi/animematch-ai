"""AnimeMatch AI Streamlit interface."""
import streamlit as st
from animematch.catalog import sample_catalog
from animematch.agent import answer_request

st.set_page_config(page_title="AnimeMatch AI",page_icon="🎌",layout="wide")
st.title("🎌 AnimeMatch AI")
st.caption("Find your next anime with an explainable content-based recommendation engine.")
st.info("Demo: 18 curated titles. Some scores are illustrative or unavailable; no live ratings, external API, or LLM are used.")
catalog=sample_catalog()
with st.form("recommendation"):
    favorites=st.multiselect("Anime you already enjoy",catalog["title"].tolist(),default=["Death Note"])
    description=st.text_input("Describe what you want to watch",placeholder="dark mystery with psychological tension")
    restrict=st.checkbox("Limit episode count",value=True)
    max_episodes=st.number_input("Maximum episodes",min_value=1,max_value=500,value=30,disabled=not restrict)
    submitted=st.form_submit_button("Find recommendations",type="primary")
if submitted:
    try:
        results=answer_request(catalog,favorites,description,int(max_episodes) if restrict else None)
        if not results:
            st.warning("No titles match your filters. Try increasing the episode limit.")
        for index,anime in enumerate(results,1):
            with st.container(border=True):
                st.subheader(f"{index}. {anime['title']}")
                score = "Not available" if anime["score"] != anime["score"] else str(anime["score"])
                st.write(f"**Genres:** {anime['genres']} · **Episodes:** {int(anime['episodes'])} · **Catalog score:** {score}")
                st.write(anime["synopsis"])
                st.caption(anime["reason"])
    except ValueError as exc:
        st.error(str(exc))
with st.expander("How does it work?"):
    st.write("Genres and synopsis are transformed into TF-IDF vectors. Favorites and the search description are combined and ranked with cosine similarity. Similarity is not a probability of enjoyment.")
