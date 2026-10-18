# Sentiment classifier

The optional `train_sentiment` function trains a TF-IDF + logistic regression pipeline on labeled reviews. It is separate from the recommendation UI.

## Data requirements
Use legitimately accessible reviews with clear sentiment labels, consistent language, and no duplicate leakage across train and test sets.

## Evaluation plan
Split reviews into training and held-out test sets. Report confusion matrix, precision, recall, F1 score, class distribution, and errors by category. Do not claim benchmark performance from the four toy samples in the unit test.
