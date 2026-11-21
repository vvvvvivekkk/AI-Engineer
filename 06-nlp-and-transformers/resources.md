# Module 06 - Resources

Links chosen from the course link catalogue (built from the nine source lists; see the root `SOURCES.md`) plus a few well-known official pages. Each has one line on why it is worth your time. Start with the "first" group.

## Start here (first)

| Resource | Type | Why |
|---|---|---|
| [Hugging Face Learn](https://huggingface.co/learn) | Free course | The standard hands-on route through tokenizers, `transformers`, datasets and fine-tuning; matches the tools in this module. |
| [Transformers course, chapter 1](https://huggingface.co/course/chapter1) | Free course | The direct entry point: what transformers are and how `pipeline()` works. Good follow-up to notebook 03. |
| [Hugging Face model hub](https://huggingface.co/models) | Tool | Browse and filter models by task; read model cards and licences before use. |
| [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/) | Article | Picture-by-picture walk through attention and the transformer block; the best visual companion to section 5-6 of `concepts.md`. |

## Official documentation

| Resource | Type | Why |
|---|---|---|
| [huggingface/transformers](https://github.com/huggingface/transformers) | Repo | The library itself; its examples show the real, current API. |
| [Hugging Face course source](https://github.com/huggingface/course) | Repo | The course as notebooks you can run offline. |
| [Sentence Transformers documentation](https://www.sbert.net/) | Docs | How `SentenceTransformer`, `encode` and `util.cos_sim` work, and which embedding model to choose. |
| [tiktoken](https://github.com/openai/tiktoken) | Repo | OpenAI's tokenizer library used in notebook 01 and Module 07. |
| [Attention Is All You Need (2017 paper)](https://arxiv.org/abs/1706.03762) | Paper | The original transformer paper. Read the figures and section 3 after this module; skip the maths you don't need. |

## Go deeper (video and books)

| Resource | Type | Why |
|---|---|---|
| [Neural Networks: Zero to Hero (Andrej Karpathy)](https://www.youtube.com/watch?v=VMj-3S1tku0&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ) | Free video series | Later videos build a small GPT from scratch: the clearest view of attention in code. |
| [A Hacker's Guide to Language Models (Jeremy Howard)](https://www.youtube.com/watch?v=jkrNMKz9pWU) | Free video | Practical, code-first tour of how language models work and how to use them. |
| [Build a Large Language Model (From Scratch)](https://www.manning.com/books/build-a-large-language-model-from-scratch) | Paid book | Builds tokenizer, attention and GPT training step by step in PyTorch. |
| [Stanford CS25 - Transformers United](https://web.stanford.edu/class/cs25/) | Free lectures | Advanced guest lectures on where transformer research is going. |
| [Cohere LLM University](https://academy.cohere.com/) | Free course | Short lessons on embeddings, semantic search and generation; a good bridge to RAG. |
| [Mastering LLMs (AssemblyAI)](https://www.youtube.com/watch?v=zjkBMFhNj_g) | Free video | One-video overview of how LLMs are built and used. |

## Reference lists and paper explainers

| Resource | Type | Why |
|---|---|---|
| [ML Papers Explained (dair-ai)](https://github.com/dair-ai/ML-Papers-Explained) | Repo | Plain-language summaries of landmark papers (BERT, GPT, T5 ...). |
| [Treasure of Transformers](https://github.com/ashishpatel26/Treasure-of-Transformers) | Repo | Catalogue of transformer model families, useful for orientation. |
| [awesome-sentence-embedding](https://github.com/Separius/awesome-sentence-embedding) | Repo | Background on embedding methods; leads into semantic search and RAG. |
| [awesome-nlp](https://github.com/keon/awesome-nlp) | Repo | Broad map of NLP courses, libraries and datasets. |

## Practice projects

| Resource | Type | Why |
|---|---|---|
| [NLP beginner projects](https://github.com/positivepeng/nlp-beginner-projects) | Repo | Small classic exercises (text classification, NER) with reference code. |
| [The Super Duper NLP Repo](https://notebooks.quantumstat.com/) | Index | Searchable list of Colab notebooks for many NLP tasks. |
| [6 sentiment analysis projects](https://amankharwal.medium.com/6-sentiment-analysis-projects-with-python-1fdd3d43d90f) | Article (Medium limits) | Ready-made scenarios for practising sentiment analysis. |
| [20 NLP projects with Python](https://medium.com/coders-camp/20-machine-learning-projects-on-nlp-582effe73b9c) | Article (Medium limits) | More project ideas, from summarisation to keyword extraction. |

## Models used in this module (model cards)

- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) — sentence embeddings
- [distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english) — sentiment
- [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct) — tiny text generation
- [gpt2](https://huggingface.co/gpt2) and [bert-base-uncased](https://huggingface.co/bert-base-uncased) — tokenizer comparisons

Licence note: all links point to the original authors. Nothing from these resources is copied into this module; descriptions are our own.
