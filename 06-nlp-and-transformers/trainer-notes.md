# Module 06 - Trainer notes

These notes assume you have read `concepts.md` once and run the three notebooks yourself. You do not need to be an expert: if you can explain the library analogy for attention and run the notebooks, you can teach this session.

## 1. What students should be able to do after the session

1. Say what a token is and show that different tokenizers cut the same text differently.
2. Explain why APIs charge per token and why non-English text often costs more.
3. Embed sentences with MiniLM and use cosine similarity to find the most similar one.
4. Explain Query, Key and Value with an analogy, and read an attention heatmap ("row X attends most to column Y").
5. Name the parts of a transformer block and the three families (encoder, decoder, encoder-decoder).
6. Run a Hugging Face `pipeline` for sentiment and for text generation, and explain what the score means.

## 2. Session plan (2 hours)

Before the session: open all three notebooks in Colab and run them once, so model downloads are cached and you have seen every output. Have the slides open.

| Time | Activity | Materials | Notes |
|---|---|---|---|
| 0:00-0:10 | **Hook**: "How does a calculator read the word 'cat'?" Collect guesses on the board. | Slide 1-2 | Lead to: text must become numbers that keep meaning. |
| 0:10-0:30 | **Tokens**: LEGO analogy, BPE in words, live demo of four tokenizers | Slides 3-5, notebook 01 sections 1-4 | Let students suggest sentences (their names, a Hindi/Telugu phrase, code). |
| 0:30-0:50 | **Embeddings + cosine**: fruit sliders on the board, then the similarity heatmap and tiny search | Slides 6-7, notebook 01 sections 5-8 | Ask students to propose two sentences with the same meaning and no shared words. |
| 0:50-1:00 | Break | | |
| 1:00-1:25 | **Attention**: whisper game vs meeting room, library analogy for Q/K/V, then notebook 02 step by step | Slides 8-11, notebook 02 sections 1-6 | Do row "sat" by hand on the board before running the cell. |
| 1:25-1:35 | **Transformer block + families** | Slides 12-13 | Keep it visual; no formulas beyond the one-liner. |
| 1:35-1:55 | **Hugging Face hands-on**: pipeline, by-hand logits, SmolLM2 chat | Slides 14-15, notebook 03 | Students run it themselves in Colab. |
| 1:55-2:00 | **Recap + exercises** | Slides 16-17 | Assign exercises 1-4 in class (or start), 5-10 as homework. |

For a **1-hour** version: hook (5), tokens (15), embeddings (15), attention with the heatmap only (15), pipeline demo (10). Skip notebook 02 sections 7-8 and notebook 03 sections 3, 5, 6.

## 3. Common student mistakes and fixes

| Mistake | What it looks like | Fix |
|---|---|---|
| Using one model's tokenizer with another model | Garbage predictions, no error message | Always load tokenizer and model with the **same name**. Show that ID 1000 means different tokens in GPT-2 and BERT. |
| Thinking tokens = words | Cost estimates off by 30-200% | Run notebook 01 section 4. Rule of thumb: ~0.75 English words per token; measure other languages. |
| Reading cosine 0.5 as "50% the same" | Over-interpreting scores | Scores are only meaningful **relative to each other** for the same model. Compare with known similar/dissimilar pairs. |
| Believing a high score means correct | "The model is 99.9% sure, so it's right" | Show the sarcasm example and the support-ticket example in notebook 03. Score = confidence. |
| Forgetting softmax rows sum to 1 | Confusion when reading heatmaps | Have students add up a row out loud. |
| Thinking attention "understands" | Over-humanising heads | Attention is a weighted average. Heads learn useful patterns from data; many heads look at boring things (punctuation, neighbours). Notebook 02 shows this. |
| Running out of memory / slow downloads | Colab crashes or long waits | Use the tiny models listed; restart the runtime; run download cells once before class. |
| Ignoring warnings like "unauthenticated requests to the HF Hub" | Panic | Explain it is harmless for small downloads; a free HF token (env var `HF_TOKEN`) raises rate limits. Never paste the token into a notebook. |
| Mixing up encoder and decoder | Trying to generate text with BERT | Encoders read (classification, embeddings); decoders write (generation). |

## 4. Questions to check understanding (with answers)

1. **Why don't modern models use one token per word?** The vocabulary would need every word, name and typo; unknown words would be lost. Sub-words keep the vocab manageable and never meet an unknown word.
2. **Why might the same message cost more in Telugu than in English?** Tokenizers are trained mostly on English text, so other scripts are split into more, smaller pieces. More tokens = more cost.
3. **Two vectors are [1, 2] and [3, 6]. What is their cosine similarity, and why?** 1.0. They point the same way; cosine ignores length.
4. **In the attention heatmap, what does a row represent?** How one word (the query) spreads its attention across all words. Each row sums to 1.
5. **What are Q, K and V, in one sentence each?** Query: what this token is looking for. Key: the label it offers others. Value: the information it passes on when picked.
6. **Why divide by √d?** To stop scores getting so large that softmax becomes all-or-nothing, which makes training unstable.
7. **What would go wrong without positional encoding?** The model could not tell "dog bites man" from "man bites dog".
8. **Why does a text generator use a causal mask?** So while learning to predict the next token it cannot look at that token (or later ones).
9. **What is the difference between `pipeline` and AutoTokenizer + AutoModel?** Same result; the pipeline hides the steps, the manual way shows IDs, logits and probabilities so you can customise.
10. **The sentiment model calls "It was okay" NEGATIVE with 0.98. Is it broken?** No — it only has two labels and was trained on movie reviews. Choose a model with a neutral label if you need one.

## 5. Adapting the session

**Faster groups**
- Do exercise 8 (attention by hand on paper) in class, then exercise 10 (greedy loop).
- Show `output_hidden_states=True` and plot how the vector for "bank" differs in "river bank" vs "bank account" (contextual embeddings).
- Discuss the **KV cache** and why generation gets slower with longer outputs without it.

**Slower groups**
- Skip notebook 02 sections 7-8 and the multi-head maths; keep the library analogy and the heatmap.
- Use only `pipeline` in notebook 03; leave by-hand logits for later.
- Spend more time on tokens and costs — it is the most practical takeaway for Module 07.
- Pair students: one drives the notebook, one explains each cell out loud; swap halfway.
