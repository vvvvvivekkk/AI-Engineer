"""
kappa.py - measure agreement between annotators.

Contains:
  * cohens_kappa(a, b)        two annotators, written from scratch
  * fleiss_kappa(table)       many annotators, written from scratch
  * a check against scikit-learn's cohen_kappa_score

Run:  python code/kappa.py
"""
import numpy as np                                   # fast maths on arrays
from sklearn.metrics import cohen_kappa_score        # the trusted reference implementation


def cohens_kappa(a, b):
    """Cohen's kappa for two equal-length lists of labels."""
    a, b = np.asarray(a), np.asarray(b)              # turn lists into numpy arrays
    if a.shape != b.shape:                           # both annotators must label the same items
        raise ValueError("a and b must have the same length")
    cats = np.union1d(a, b)                          # every label that either annotator used
    p_o = np.mean(a == b)                            # observed agreement: fraction of matches
    # chance agreement: for each label, P(A uses it) * P(B uses it), then add them up
    p_e = sum(np.mean(a == c) * np.mean(b == c) for c in cats)
    if p_e == 1:                                     # both used one single label for everything
        return 1.0                                   # (avoid dividing by zero)
    return (p_o - p_e) / (1 - p_e)                   # the kappa formula


def fleiss_kappa(table):
    """Fleiss' kappa for many annotators.

    table[i][j] = how many annotators put item i into category j.
    Every row must add up to the same number of annotators.
    """
    t = np.asarray(table, dtype=float)               # rows = items, columns = categories
    n_items, _ = t.shape
    n_raters = t[0].sum()                            # annotators per item
    p_j = t.sum(axis=0) / (n_items * n_raters)       # how often each category is used overall
    # agreement within each item: share of annotator pairs that agree
    p_i = (np.sum(t * t, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    p_bar = p_i.mean()                               # average observed agreement
    p_e = np.sum(p_j ** 2)                           # chance agreement
    return (p_bar - p_e) / (1 - p_e)


if __name__ == "__main__":
    # The worked example from concepts.md (10 reviews, two annotators).
    a = ["POS", "POS", "NEG", "POS", "NEG", "POS", "POS", "NEG", "POS", "POS"]
    b = ["POS", "NEG", "NEG", "POS", "NEG", "POS", "POS", "POS", "POS", "POS"]
    print("our Cohen's kappa :", round(cohens_kappa(a, b), 3))
    print("scikit-learn      :", round(cohen_kappa_score(a, b), 3))

    # Fleiss example: 5 items, 3 annotators each, categories [POS, NEG, NEU].
    table = [[3, 0, 0],   # all three said POS
             [0, 3, 0],   # all three said NEG
             [2, 1, 0],   # two POS, one NEG
             [0, 1, 2],
             [1, 1, 1]]   # total disagreement
    print("Fleiss' kappa     :", round(fleiss_kappa(table), 3))
