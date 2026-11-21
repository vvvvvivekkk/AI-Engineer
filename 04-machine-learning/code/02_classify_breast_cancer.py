"""
02_classify_breast_cancer.py
Classify tumours as malignant or benign and print every metric from the confusion matrix.
Run:  python 02_classify_breast_cancer.py
"""
# the built-in breast cancer dataset: 569 tumours, 30 measurements each
from sklearn.datasets import load_breast_cancer
# splitter for train/test
from sklearn.model_selection import train_test_split
# make_pipeline chains several steps into one model object
from sklearn.pipeline import make_pipeline
# StandardScaler rescales every feature to mean 0 and spread 1
from sklearn.preprocessing import StandardScaler
# LogisticRegression is a simple, strong classifier that outputs probabilities
from sklearn.linear_model import LogisticRegression
# metric helpers
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score

# load features (X) and labels; in the raw data 0 = malignant, 1 = benign
data = load_breast_cancer()
X = data.data
# flip the labels so 1 = malignant: the "positive" class is the thing we hunt for
y = (data.target == 0).astype(int)

# 25% test set; stratify keeps the same share of malignant cases in both parts
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

# scaler then classifier, wrapped as one object so scaling only learns from training data
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
# train both steps on the training rows
clf.fit(X_train, y_train)

# hard 0/1 predictions using the default 0.5 threshold
pred = clf.predict(X_test)
# probability of class 1 (malignant) for each test tumour
proba = clf.predict_proba(X_test)[:, 1]

# confusion_matrix returns [[TN, FP], [FN, TP]]; ravel flattens it into four numbers
tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
print(f"TP={tp}  FN={fn}  FP={fp}  TN={tn}")

# compute each metric directly from the four boxes
accuracy = (tp + tn) / (tp + tn + fp + fn)       # share of all answers that were right
precision = tp / (tp + fp)                        # when we said malignant, how often right
recall = tp / (tp + fn)                           # of real malignant tumours, how many found
f1 = 2 * precision * recall / (precision + recall)  # balance of precision and recall
print(f"accuracy={accuracy:.3f} precision={precision:.3f} recall={recall:.3f} f1={f1:.3f}")

# AUC uses probabilities, not hard predictions: 1.0 perfect, 0.5 coin flip
print(f"ROC-AUC={roc_auc_score(y_test, proba):.4f}")
# scikit-learn's full per-class report for comparison
print(classification_report(y_test, pred, target_names=["benign", "malignant"]))

# try a stricter and a looser threshold to see the precision/recall trade-off
for t in (0.2, 0.5, 0.8):
    # turn probabilities into 0/1 using threshold t
    p = (proba >= t).astype(int)
    # recount the boxes for this threshold
    tn_, fp_, fn_, tp_ = confusion_matrix(y_test, p).ravel()
    print(f"threshold {t}: missed cancers (FN)={fn_}, false alarms (FP)={fp_}")
