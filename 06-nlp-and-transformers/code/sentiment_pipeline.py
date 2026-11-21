"""
sentiment_pipeline.py - sentiment analysis two ways: the one-line pipeline, and tokenizer + model by hand.

Run:  python sentiment_pipeline.py
Needs: transformers, torch  (first run downloads the model, about 270 MB)
"""
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

NAME = "distilbert-base-uncased-finetuned-sst-2-english"   # DistilBERT fine-tuned on movie-review sentences
reviews = [
    "I love this course, the examples are so clear!",
    "The battery died after one hour. Terrible.",
    "It was okay, nothing special.",              # no 'neutral' label exists, so watch what happens
    "Great, it broke on the first day.",          # sarcasm often fools small models
]

# --- Way 1: pipeline (does tokenizing, the model and softmax for you) ---------
clf = pipeline("sentiment-analysis", model=NAME)
for text, result in zip(reviews, clf(reviews)):          # the pipeline accepts a list of texts
    print(f"{result['label']:<8} {result['score']:.3f}  {text}")

# --- Way 2: the same thing by hand, so you can see each step ------------------
tok = AutoTokenizer.from_pretrained(NAME)                          # matching tokenizer
model = AutoModelForSequenceClassification.from_pretrained(NAME)   # model with a 2-label classification head
inputs = tok(reviews, padding=True, return_tensors="pt")           # pad shorter texts so all rows have equal length
with torch.no_grad():                                              # we are not training, so skip gradient bookkeeping
    logits = model(**inputs).logits                                # raw scores, shape (4 reviews, 2 labels)
probs = torch.softmax(logits, dim=-1)                              # scores -> probabilities per row
labels = model.config.id2label                                     # {0: 'NEGATIVE', 1: 'POSITIVE'}
print("\nBy hand:")
for text, p in zip(reviews, probs):
    best = int(p.argmax())                                         # index of the bigger probability
    print(f"{labels[best]:<8} {p[best]:.3f}  {text}")
