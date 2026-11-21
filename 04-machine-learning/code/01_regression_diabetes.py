"""
01_regression_diabetes.py
Train a linear regression on scikit-learn's built-in diabetes data and report its errors.
Run:  python 01_regression_diabetes.py      (takes about 2 seconds, no internet needed)
"""
# numpy gives us maths on whole arrays of numbers at once
import numpy as np
# load_diabetes returns a small medical dataset that ships with scikit-learn
from sklearn.datasets import load_diabetes
# train_test_split randomly divides rows into a training part and a test part
from sklearn.model_selection import train_test_split
# DummyRegressor is a "no skill" baseline that always predicts the average
from sklearn.dummy import DummyRegressor
# LinearRegression fits the best straight line (flat surface) through the data
from sklearn.linear_model import LinearRegression
# these functions turn predictions + true answers into a single error number
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# X = table of 10 features per patient, y = disease progression number we want to predict
X, y = load_diabetes(return_X_y=True, as_frame=True)
# print the size: (rows, columns)
print("data shape:", X.shape)

# keep 20% of patients hidden as the test set; random_state makes the split repeatable
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# build the baseline and let it "learn" the training average
baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)
# build the real model and train it on the training rows only
model = LinearRegression().fit(X_train, y_train)

# loop over both models so we print the same report for each
for name, m in [("baseline (always the mean)", baseline), ("linear regression", model)]:
    # predict the label for every test patient
    pred = m.predict(X_test)
    # MAE: average size of the mistakes
    mae = mean_absolute_error(y_test, pred)
    # RMSE: square root of the average squared mistake (punishes big misses)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    # R2: 1 is perfect, 0 is no better than predicting the average
    r2 = r2_score(y_test, pred)
    # print the three numbers neatly, rounded
    print(f"{name:28s} MAE={mae:6.2f}  RMSE={rmse:6.2f}  R2={r2:6.3f}")

# show the learned weight of each feature, biggest positive first
print("\nlearned weights:")
# zip pairs each column name with its weight; sorted orders them by weight
for col, w in sorted(zip(X.columns, model.coef_), key=lambda t: -t[1]):
    print(f"  {col:4s} {w:8.1f}")
