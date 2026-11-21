# Module 09 - Retrieval-augmented generation (RAG)

## What RAG is
**Retrieval-augmented generation** (RAG) answers a question in two stages: first **retrieve** the most relevant passages from your own documents, then **generate** an answer with an LLM that is told to use only those passages. It is like an open-book exam: the model looks things up instead of relying on memory.

## Chunking
Documents are cut into **chunks** before indexing. Small chunks (around 100-200 words) give precise matches but can lose context; large chunks (400+ words) keep context but dilute the match. Splitting on headings and adding a small **overlap** between chunks helps keep ideas together.

## Vector stores
Each chunk is turned into an embedding and stored in a **vector store** such as FAISS or Chroma. At question time the question is embedded too, and the store returns the chunks whose vectors are closest. FAISS is a fast library; Chroma is a small database that also stores the text and metadata.

## Reranking
A **reranker** is a second, slower model (a cross-encoder) that reads the question and each candidate chunk together and gives a more accurate relevance score. Retrieve 20 candidates quickly, then rerank and keep the best 3-5.

## Evaluating RAG
Measure retrieval with **hit rate @ k** (is the right source in the top k results?) and **MRR** (mean reciprocal rank: 1 if the right source is first, 1/2 if second, and so on). Measure answers for faithfulness to the sources and correctness against reference answers.

## Conversation memory
In a chat, follow-up questions like "and how do I evaluate it?" mention earlier topics only indirectly. **Query rewriting** turns a follow-up into a standalone question using the recent conversation before retrieval.
