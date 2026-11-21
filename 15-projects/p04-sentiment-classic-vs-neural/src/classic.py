"""
classic.py - Model 1: TF-IDF + logistic regression (the classic, fast, strong baseline).

TF-IDF turns each review into a long list of numbers, one per word (or word pair) in the vocabulary:
  * TF  (term frequency)         - how often the word appears in THIS review
  * IDF (inverse document freq.) - words that appear in almost every review ("the", "is") get
                                   a small weight; rarer, more telling words get a big weight
ngram_range=(1, 2) also counts word PAIRS ("not bad"), which lets a linear model handle simple negation.
Logistic regression then learns one weight per word/pair: positive weights push toward "positive".
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def build() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=2000, C=4.0)),
    ])


def top_words(model: Pipeline, n: int = 8) -> dict:
    """The words/pairs with the strongest pull in each direction - great for explaining the model."""
    vocab = model.named_steps["tfidf"].get_feature_names_out()
    coefs = model.named_steps["clf"].coef_[0]
    order = coefs.argsort()
    return {"negative": [vocab[i] for i in order[:n]], "positive": [vocab[i] for i in order[-n:][::-1]]}
