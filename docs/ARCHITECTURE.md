# Architecture

```text
User browser
    |
Streamlit app (app.py)
    |
Request router (animematch/agent.py)
    |
TF-IDF recommender (animematch/recommender.py)
    |
Validated catalog (animematch/catalog.py)
```

The sentiment module is currently independent. The MVP runs locally without an API key, remote database, or generative model. The term 'agent' refers to simple tool routing in this release.
