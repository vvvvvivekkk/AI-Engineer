"""
probability_and_softmax.py - simulation, mean/variance, softmax with temperature,
sampling a "next word", and cross-entropy loss.

Run:   python 03-math-for-ai/code/probability_and_softmax.py
"""
import numpy as np                                      # arrays and random numbers

rng = np.random.default_rng(42)                         # seed 42 -> same results every run

# --- Law of large numbers ---------------------------------------------------------------
for n in [10, 100, 10_000]:                             # more and more coin flips
    heads = (rng.random(n) < 0.5).mean()                # share of numbers below 0.5 = share of heads
    print(f"{n:>6} flips -> share of heads {heads:.3f}")  # gets closer to 0.5 as n grows

# --- Mean, variance, standard deviation by hand -----------------------------------------
data = np.array([4, 8, 6, 5, 7])
mean = data.sum() / len(data)                           # centre
variance = ((data - mean) ** 2).mean()                  # average squared distance from the centre
std = variance ** 0.5                                   # back to the original units
print(f"mean {mean}, variance {variance}, std {std:.3f}")


# --- Softmax -------------------------------------------------------------------------------
def softmax(scores, temperature=1.0):
    """Turn any scores into probabilities that are positive and add up to 1."""
    z = np.asarray(scores, dtype=float) / temperature   # temperature: <1 sharpens, >1 flattens
    z = z - z.max()                                     # subtract the biggest score: avoids overflow, same answer
    e = np.exp(z)                                       # e to the power of each score (all positive)
    return e / e.sum()                                  # divide by the total so they sum to 1


vocab = ["cat", "dog", "car", "tree", "sky"]            # a tiny "vocabulary"
logits = np.array([3.0, 2.2, 1.0, 0.4, -0.5])           # raw scores from an imaginary model
for t in [0.5, 1.0, 2.0]:
    print(f"T={t}:", dict(zip(vocab, softmax(logits, t).round(3).tolist())))

# --- Sampling the next word like an LLM -----------------------------------------------------
probs = softmax(logits, temperature=1.0)
sentence = rng.choice(vocab, size=10, p=probs)          # 10 random picks, weighted by probability
print("ten sampled words:", sentence.tolist())

# --- Cross-entropy -----------------------------------------------------------------------------
for correct in ["cat", "sky"]:
    p = probs[vocab.index(correct)]                     # probability the model gave the right answer
    print(f"if the right word is '{correct}': p={p:.3f}, loss={-np.log(p):.3f}")   # -log(p)
