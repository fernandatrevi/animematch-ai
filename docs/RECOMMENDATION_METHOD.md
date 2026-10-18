# Recommendation method

1. Validate the catalog.
2. Concatenate genres twice and synopsis once to emphasize themes.
3. Fit TF-IDF with English stop-word removal and unigrams/bigrams.
4. Average favorite-item vectors and optional query-text vector.
5. Compute cosine similarity for all candidates.
6. Exclude selected favorites and apply a hard episode-count filter.
7. Sort by similarity, using demo score only to break ties.

## Important caveat
TF-IDF reflects textual overlap, not personal satisfaction or semantic understanding. Cold-start behavior requires a text query or favorite title.
