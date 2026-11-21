"""
numpy_basics.py - a tour of the NumPy ideas from Module 02, as one script you can run.

Run it from anywhere:   python 02-python-for-data/code/numpy_basics.py
Every line or small group of lines has a plain-English comment.
"""
import numpy as np                     # load NumPy and call it "np" (the usual nickname)

# --- 1. Making an array -------------------------------------------------------------
prices = np.array([799, 2499, 1199, 249])          # turn a Python list into a NumPy array
print("prices:", prices)                            # show the array
print("prices * 2:", prices * 2)                    # maths on an array touches every item

# --- 2. Shape, number of dimensions, data type --------------------------------------
scores = np.array([[80, 72, 65],                    # a 2-D array: each inner list is one row
                   [65, 90, 70],                    # rows = students
                   [70, 88, 92],                    # columns = maths, science, english
                   [95, 60, 75]])
print("shape:", scores.shape)                       # (4, 3) -> 4 rows, 3 columns
print("ndim:", scores.ndim)                         # 2 -> it is a table
print("dtype:", scores.dtype)                       # int64 -> whole numbers

# --- 3. Picking items out (indexing and slicing) -------------------------------------
print("row 0:", scores[0])                          # the first student's three scores
print("row 2, col 1:", scores[2, 1])                # one single number
print("column 0:", scores[:, 0])                    # ":" = every row; so this is all maths scores

# --- 4. Vectorised maths: no loops needed ---------------------------------------------
quantity = np.array([2, 1, 3, 6])                   # how many of each item was bought
discount = np.array([0.0, 0.10, 0.05, 0.0])         # discount as a fraction (0.10 = 10 %)
bill = quantity * prices * (1 - discount)           # item-by-item multiplication, all at once
print("bill per order:", bill)
print("total bill:", bill.sum())                    # add every number in the array

# --- 5. Aggregations along an axis -----------------------------------------------------
print("mean per subject (axis=0):", scores.mean(axis=0))   # collapse rows -> one value per column
print("mean per student (axis=1):", scores.mean(axis=1))   # collapse columns -> one value per row

# --- 6. Boolean masks (True/False filters) -------------------------------------------
expensive = prices > 1000                           # compare every price with 1000 -> True/False array
print("mask:", expensive)
print("expensive prices:", prices[expensive])        # keep only the positions marked True

# --- 7. Broadcasting -------------------------------------------------------------------
bonus = np.array([0, 5, 0])                         # +5 marks for science only
print("scores with bonus:\n", scores + bonus)        # the 1-row bonus is added to every row

# --- 8. Reshape ----------------------------------------------------------------------
a = np.arange(12)                                   # the numbers 0..11 in one row
print("as 3x4:\n", a.reshape(3, 4))                  # same 12 numbers, now 3 rows of 4

# --- 9. Reproducible random numbers --------------------------------------------------
rng = np.random.default_rng(42)                     # a random generator with seed 42
print("dice:", rng.integers(1, 7, 10))               # 10 dice rolls; same every run thanks to the seed
