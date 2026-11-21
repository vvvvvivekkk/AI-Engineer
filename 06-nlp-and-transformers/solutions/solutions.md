# Module 06 - Solutions

Runnable code for every exercise is in [`solutions.py`](solutions.py) (`python solutions.py 5` runs exercise 5 only). The outputs below were produced by that file. Tokenizer outputs never change; model scores can differ in the last decimal place between library versions.

---

## 1. Count tokens three ways

```
gpt2               12 ['Hy', 'der', 'abad', "'s", 'Ġb', 'iry', 'ani', 'Ġis', 'Ġworld', '-', 'famous', '!']
bert-base-uncased  11 ['hyderabad', "'", 's', 'bi', '##rya', '##ni', 'is', 'world', '-', 'famous', '!']
o200k_base         10 ['Hy', 'derabad', "'s", ' bir', 'y', 'ani', ' is', ' world', '-famous', '!']
```

`o200k_base` wins because its vocabulary is about four times bigger than GPT-2's (about 200,000 vs 50,000 tokens), so more pieces are available as single tokens (`-famous`). BERT knows "hyderabad" as a whole word (it is lower-case and its vocab includes many place names) but splits "biryani". Lesson: token counts depend on the tokenizer; always count with the one that matches your model.

## 2. Round trip

```
IDs: [30400, 527, 539, 4339, 13]
Decoded: Tokens are not words. | same: True
Pieces: ["'Tokens'", "' are'", "' not'", "' words'", "'.'"]
```

The space before each word is part of the token (`' are'`). Decoding the full list gives back exactly the original text — tokenisation loses nothing.

## 3. Cosine similarity by hand

```python
def cosine(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Results: `1.0`, `0.0`, `-0.9999999999999998`. The last one is -1 with a tiny rounding error, which is normal for computer arithmetic. `[1,2,3]` and `[2,4,6]` score 1.0 even though one is twice as long: cosine only cares about direction.

## 4. Tokens per word in your languages

```
  language                                     text  tokens_per_word
0  English    Where is the nearest railway station?             1.17
1    Hindi       सबसे नज़दीकी रेलवे स्टेशन कहाँ है?             1.83
2   Telugu  దగ్గరలో ఉన్న రైల్వే స్టేషన్ ఎక్కడ ఉంది?             2.50
```

The same meaning costs about 1.6x more tokens in Hindi and about 2.1x more in Telugu with this tokenizer. Since APIs charge per token and limits are in tokens, an app used in Telugu pays more per message and fits less text in the context window. Measure with your real users' text before estimating costs.

## 5. Odd one out

```
0.223  The train to Chennai is delayed.
0.297  My flight to Delhi was cancelled.
0.257  The bus arrived two hours late.
0.084  I baked a chocolate cake yesterday.
0.241  Our metro service stopped due to rain.
Odd one out: I baked a chocolate cake yesterday.
```

Trick used: with `normalize_embeddings=True`, every vector has length 1, so the dot product equals cosine similarity, and `v @ v.T` gives the whole grid at once. Subtract the diagonal (each sentence vs itself = 1) before averaging.

## 6. Softmax and temperature

```
T=0.5: [0.864 0.117 0.019]
T=1:   [0.659 0.242 0.099]
T=2:   [0.502 0.304 0.194]
```

Dividing scores by a small T stretches the gaps, so the top choice takes almost everything (more predictable). A big T shrinks the gaps, so probabilities become more even (more random). Module 07 uses exactly this to explain the `temperature` setting of LLMs.

## 7. Sentiment stress test

With the eight sentences in `solutions.py` the model got all eight right, including two sarcastic ones and two with negation. That is a useful surprise: newer students expect it to fail. Point out:

- Sentences with an obvious negative event ("parcel is lost", "deleted all my notes") are easy even when sarcastic; subtler sarcasm ("Great, it broke on the first day." from the notebook) fooled it.
- Neutral sentences ("It was okay") are always forced into POSITIVE or NEGATIVE because the model has only two labels.
- Your own sentences may give different results. Any wrong answer with a score above 0.9 shows that **score = confidence, not correctness**.

## 8. Attention by hand

Pencil work for row 0 (the word with embedding [1, 0]):

- Q = K = V = X because the weight matrices are identity.
- Scores row 0: q0·k0 = 1, q0·k1 = 0, q0·k2 = 1. Divide by √2 ≈ 1.414 → [0.707, 0, 0.707].
- Softmax: e^0.707 ≈ 2.028, e^0 = 1. Total = 2.028 + 1 + 2.028 = 5.056 → [0.401, 0.198, 0.401].
- Output row 0 = 0.401·[1,0] + 0.198·[0,1] + 0.401·[1,1] = [0.802, 0.599].

NumPy output:

```
weights:                 output:
[[0.401 0.198 0.401]     [[0.802 0.599]
 [0.198 0.401 0.401]      [0.599 0.802]
 [0.248 0.248 0.503]]     [0.752 0.752]]
causal weights:          causal output:
[[1.    0.    0.   ]     [[1.    0.   ]
 [0.33  0.67  0.   ]      [0.33  0.67 ]
 [0.248 0.248 0.503]]     [0.752 0.752]]
```

With the causal mask, word 0 can only see itself (weight 1.0); the last word can see everything, so its row is unchanged.

## 9. Mini semantic FAQ bot

Key ideas: embed the FAQ questions once (not on every call), normalise, take the dot product with the user question, and use a **threshold** so the bot says "I don't know" instead of returning a bad match.

```
I forgot my password -> Click 'Forgot password' on the login page. (score 0.78)
when do you open? -> We are open 9am to 6pm, Monday to Saturday. (score 0.73)
can I stop my order? -> Go to My Orders and click Cancel within 1 hour. (score 0.77)
do you ship to Secunderabad -> Yes, delivery to Secunderabad takes 1-2 days. (score 0.88)
what is the capital of Peru? -> Sorry, I don't know. A human will reply soon. (best score 0.22)
tell me a joke -> Sorry, I don't know. A human will reply soon. (best score 0.13)
```

The threshold of 0.4 is a starting guess. In a real project, collect 30-50 real questions, look at the scores of right and wrong matches, and pick the value that separates them. This is a baby version of RAG (Module 09).

## 10. Greedy next-token loop

```
1 'The capital of France is Paris'
2 'The capital of France is Paris.'
...
10 'The capital of France is Paris. Paris is the largest city in France and'
Matches generate(): True
```

They match because `generate(..., do_sample=False)` does exactly the same thing internally: run the model, take the last position's logits, pick the argmax, append, repeat. Greedy decoding has no randomness, so the same input always gives the same output. (`generate` is faster because it caches earlier computations — the **KV cache** — instead of re-reading the whole sentence every step.)
