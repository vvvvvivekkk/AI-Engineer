<!-- nav:start -->
> [🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 05 Deep Learning](../05-deep-learning/README.md) · [07 LLMs & GenAI ➡️](../07-llms-and-genai/README.md)  
> **💬 Module 06 · NLP & Transformers**  
> [📖 Lesson](concepts.md) · [📄 PDF handout](pdf/06-nlp-and-transformers-handout.pdf) · [🎞️ Slides](slides/06-nlp-and-transformers.pptx) · [📓 Notebooks](notebooks/) · [✍️ Exercises](exercises.md) · [✅ Solutions](solutions/) · [🧑‍🏫 Trainer notes](trainer-notes.md) · [🔗 Resources](resources.md)
<!-- nav:end -->

# Module 06 - NLP and Transformers

**Weeks 11-12 of the course.** How computers read text: tokens, embeddings, attention and the transformer, then real models from Hugging Face running on a laptop.

## Learning goals

After this module a learner can:

1. Explain what a **token** (a small chunk of text a model treats as one unit) is, and show real tokenizer output from a Hugging Face tokenizer and from `tiktoken`.
2. Explain why sub-word tokenisation (BPE / WordPiece) is used, and why token counts matter for cost and limits.
3. Create **sentence embeddings** (lists of numbers that represent meaning) and compare them with **cosine similarity**.
4. Compute **self-attention** by hand in NumPy for a 3-word sentence and read the attention heatmap.
5. Draw and explain a transformer block (attention, feed-forward, residual connections, layer norm, positional encoding, causal mask).
6. Use Hugging Face at three levels: `pipeline`, tokenizer + model, raw outputs; read a model card on the Hub.
7. Run sentiment analysis and tiny text generation on a CPU.

## Prerequisites

- Module 02 (NumPy arrays, pandas basics) and Module 03 (vectors, dot product).
- Module 05 helps (neural networks, PyTorch tensors), but is not strictly needed to run the notebooks.

## Time estimate

| Part | Time |
|---|---|
| Read `concepts.md` | 60-90 min |
| Notebooks 01-03 | 2-3 hours |
| Exercises | 2-3 hours |
| Taught session (see `trainer-notes.md`) | 2 hours |

## Which tool to use, and why

- **Google Colab** — easiest. Click the badge at the top of each notebook. Nothing to install, and model downloads are fast. A GPU is not needed.
- **Jupyter / VS Code locally** — fine on any laptop with about 4 GB free RAM and 1 GB free disk for the models. Install with `pip install transformers torch sentence-transformers tiktoken matplotlib pandas`.
- **VS Code** for the `code/` scripts: run them from the terminal with `python code/<script>.py`.

Models are downloaded once from the Hugging Face Hub and cached (usually in `~/.cache/huggingface`). The largest one used here is about 270 MB.

## File map

| Path | What it is |
|---|---|
| `concepts.md` | The main lesson. Start here. |
| `notebooks/01-tokens-and-embeddings.ipynb` | Real tokenizers (GPT-2, BERT, SmolLM2, tiktoken), tokens per word, MiniLM embeddings, cosine similarity, tiny semantic search |
| `notebooks/02-attention-by-hand.ipynb` | Self-attention in NumPy on "the cat sat", heatmaps, causal mask, multi-head shapes, real DistilBERT attention |
| `notebooks/03-hugging-face-pipelines.ipynb` | `pipeline`, tokenizer + model by hand, model internals, sentiment, text generation, chat templates |
| `code/tokenize_demo.py` | Compare tokenizers on any sentence from the command line |
| `code/embeddings_similarity.py` | Embed sentences, print a similarity grid, run a search |
| `code/attention_numpy.py` | Self-attention by hand; saves a heatmap |
| `code/sentiment_pipeline.py` | Sentiment two ways (pipeline and by hand) |
| `code/generate_text.py` | Text generation and chat format with SmolLM2-135M-Instruct |
| `images/` | Diagrams used in the lesson and slides (`.mmd` files are the editable Mermaid sources) |
| `slides/06-nlp-and-transformers.pptx` | Teaching deck with speaker notes |
| `pdf/06-nlp-and-transformers-handout.pdf` | Printable version of `concepts.md` |
| `excel/06-nlp-cheatsheet.xlsx` | Glossary, tokens-per-word table (live formula), models used |
| `exercises.md` / `solutions/` | 10 exercises, easy to hard, with full solutions |
| `trainer-notes.md` | How to teach this module, with a timed session plan |
| `resources.md` | The best external links, each with a reason |
| `build.py` | Regenerates images, notebooks, slides, PDF and Excel |

## Rebuild the generated files

```bash
python 06-nlp-and-transformers/build.py
python tools/check_module.py 06-nlp-and-transformers --run
```

<!-- nav:start -->
---
[🏠 Course home](../README.md) · [🗺️ Roadmap](../ROADMAP.md) · [⬅️ 05 Deep Learning](../05-deep-learning/README.md) · [07 LLMs & GenAI ➡️](../07-llms-and-genai/README.md)
<!-- nav:end -->
