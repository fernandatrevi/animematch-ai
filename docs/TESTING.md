# Testing guide

Run `pytest -q` from the repository root after installing dependencies.

Current automated checks cover catalog schema validation, duplicate removal, exclusion of already-selected favorites, episode filtering, missing-preference errors, structured explanation output, sentiment training, and invalid sentiment labels.

## Manual smoke test
1. Run `streamlit run app.py`.
2. Select Death Note and submit the default form.
3. Confirm a ranked list appears and Death Note is not recommended.
4. Change maximum episodes to 13 and confirm displayed results respect it.
5. Clear favorites and text and confirm a friendly error appears.
