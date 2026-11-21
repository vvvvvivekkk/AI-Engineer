# Module 06 - NLP and transformers

## Tokenisation
Models cannot read letters directly. **Tokenisation** cuts text into pieces called tokens and maps each to a number. Modern models use **sub-word** tokens (for example BPE), so rare words are split into common pieces like "un", "believ", "able".

## Embeddings
An **embedding** is a list of numbers that represents the meaning of a word or sentence. Texts with similar meaning get vectors that point in similar directions, which we measure with **cosine similarity**. The model `all-MiniLM-L6-v2` turns a sentence into 384 numbers.

## Attention and transformers
**Self-attention** lets every token look at every other token and decide which ones matter for its meaning, like a reader glancing back at earlier words. A **transformer** stacks attention layers with small feed-forward networks. Multi-head attention runs several attention patterns in parallel.

## Hugging Face pipelines
The Hugging Face `pipeline` function loads a pretrained model and its tokenizer in one line, for tasks such as `sentiment-analysis`, `zero-shot-classification` or `text-generation`.
