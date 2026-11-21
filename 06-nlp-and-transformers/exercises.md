# Module 06 - Exercises

Ten exercises, easy to hard. Do them in a notebook (Colab or Jupyter). Full worked solutions are in [`solutions/solutions.md`](solutions/solutions.md) and runnable code in [`solutions/solutions.py`](solutions/solutions.py). Try each one for at least 15 minutes before looking.

---

## Easy

### 1. Count tokens three ways
Take the sentence `"Hyderabad's biryani is world-famous!"`.
Print its tokens and token count using (a) the `gpt2` tokenizer, (b) the `bert-base-uncased` tokenizer, (c) tiktoken `o200k_base`.
Which gives the fewest tokens? Why might that be?

### 2. Round trip
Using tiktoken `cl100k_base`, encode the text `"Tokens are not words."`, print the IDs, then decode the IDs back. Check that you get the same text. Then decode each ID on its own and print the pieces with `repr()` so you can see the spaces.

### 3. Cosine similarity by hand
Without any library except NumPy, write `cosine(a, b)`. Test it on:
- `a = [1, 2, 3]`, `b = [2, 4, 6]` (expect 1.0 — same direction, different length)
- `a = [1, 0]`, `b = [0, 1]` (expect 0.0)
- `a = [1, 1]`, `b = [-1, -1]` (expect -1.0)

---

## Medium

### 4. Tokens per word in your languages
Write a function `tokens_per_word(text, encoding="o200k_base")`. Run it on one English sentence and the same sentence translated into two other languages you know (for example Hindi and Telugu). Put the results in a pandas DataFrame and explain in two sentences what this means for the cost of an app used in those languages.

### 5. Odd one out
Use `sentence-transformers/all-MiniLM-L6-v2` to embed these five sentences and find the one that is least similar to the others (lowest average cosine similarity to the rest):
```
"The train to Chennai is delayed."
"My flight to Delhi was cancelled."
"The bus arrived two hours late."
"I baked a chocolate cake yesterday."
"Our metro service stopped due to rain."
```

### 6. Softmax and temperature
Write `softmax(scores)` in NumPy. For `scores = [2.0, 1.0, 0.1]`, compute `softmax(scores / T)` for `T = 0.5, 1, 2`. Describe what happens to the biggest probability as T grows. (This "temperature" idea returns in Module 07.)

### 7. Sentiment stress test
Use the `distilbert-base-uncased-finetuned-sst-2-english` pipeline on eight sentences you write yourself: two clearly positive, two clearly negative, two sarcastic, two with negation ("not bad", "not great"). Make a table of text, expected label, model label, score. How many did it get wrong, and what pattern do you see?

---

## Hard

### 8. Attention by hand, fully
For three words with embeddings
```
X = [[1, 0], [0, 1], [1, 1]]
```
and `W_q = W_k = W_v = identity (2x2)`:
(a) compute Q, K, V; (b) compute the scaled scores `Q Kᵀ / √2`; (c) apply softmax row by row; (d) compute the output. Do (b)-(d) first with pencil for row 0, then verify all rows in NumPy. Finally apply a causal mask and recompute.

### 9. Mini semantic FAQ bot
Build a function `answer(question)` over this FAQ (question → answer pairs). Embed the FAQ questions once with MiniLM. For a user question, return the answer of the most similar FAQ question — but if the best cosine similarity is below 0.4, return `"Sorry, I don't know. A human will reply soon."`.
```python
faq = {
  "How do I reset my password?": "Click 'Forgot password' on the login page.",
  "What are your opening hours?": "We are open 9am to 6pm, Monday to Saturday.",
  "Do you deliver to Secunderabad?": "Yes, delivery to Secunderabad takes 1-2 days.",
  "How can I cancel my order?": "Go to My Orders and click Cancel within 1 hour.",
}
```
Test with at least five questions, including two unrelated ones.

### 10. Greedy next-token loop
Using `HuggingFaceTB/SmolLM2-135M-Instruct` with `AutoModelForCausalLM` (not `generate`), write your own loop that:
1. tokenizes `"The capital of France is"`,
2. runs the model, takes the logits of the last position, picks the highest one (`argmax`),
3. appends that token ID and repeats 10 times,
4. prints the text after each step.

Then compare your output with `model.generate(..., max_new_tokens=10, do_sample=False)`. They should match. Explain in your own words why.
