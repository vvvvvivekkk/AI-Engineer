"""
embeddings_similarity.py - turn sentences into vectors and compare them by meaning.

Run:  python embeddings_similarity.py
Needs: sentence-transformers, numpy  (first run downloads all-MiniLM-L6-v2, about 90 MB)
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# A small, fast model that maps any sentence to 384 numbers
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "How do I reset my password?",
    "I forgot my login details.",
    "The cat is sleeping on the sofa.",
    "A kitten naps on the couch.",
    "What is the price of the premium plan?",
    "How much does the subscription cost?",
]

vectors = model.encode(sentences)            # shape (6 sentences, 384 numbers)
print("Embedding shape:", vectors.shape)
print("First 5 numbers of sentence 0:", np.round(vectors[0][:5], 3))


def cosine(a, b):
    """Cosine similarity: dot product divided by the product of the lengths."""
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


# Compare every sentence with every other sentence
print("\nCosine similarity grid (1 = same meaning, 0 = unrelated):")
for i, s in enumerate(sentences):
    row = [f"{cosine(vectors[i], vectors[j]):.2f}" for j in range(len(sentences))]
    print(f"{s[:32]:<34}", " ".join(row))

# Tiny semantic search: which stored sentence best matches a new question?
query = "I can't remember my password"
q = model.encode(query)                                        # embed the question the same way
scores = [cosine(q, v) for v in vectors]                       # score every stored sentence
best = int(np.argmax(scores))                                  # index of the highest score
print(f"\nQuery: {query!r}\nBest match: {sentences[best]!r} (score {scores[best]:.2f})")
