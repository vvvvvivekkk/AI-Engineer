# [Project name]

[One sentence: what it does and for whom.] **[Live demo](link)** · **[2-minute video](link)**

![Screenshot or GIF of the app](https://your-site.example/screenshot.png)  <!-- replace with docs/screenshot.png in your repo -->

## Why
[The problem in 2-3 sentences. Who has it? What do they do today?]

## How it works
![Architecture diagram](https://your-site.example/architecture.png)  <!-- replace with docs/architecture.png in your repo -->

1. [Step 1, e.g. documents are chunked by heading and embedded with MiniLM]
2. [Step 2, e.g. hybrid search: BM25 + FAISS, reranked with a cross-encoder]
3. [Step 3, e.g. answer generated with citations; guardrails check input and output]

## Results
| Version | [Metric 1, e.g. hit rate@5] | [Metric 2, e.g. faithfulness] | p95 latency | Cost / 100 questions |
|---|---|---|---|---|
| Baseline | [ ] | [ ] | [ ] | [ ] |
| + [change] | [ ] | [ ] | [ ] | [ ] |

Evaluation set: [N questions, how they were written, where they are in the repo].

## Run it
```bash
git clone [repo-url] && cd [repo]
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your own keys; never commit .env
python -m pytest -q         # tests
uvicorn app.main:app --reload   # or: streamlit run app.py
```

## Design decisions and trade-offs
- [Why X instead of Y]
- [What you measured to decide]

## Limitations and next steps
- [Honest limitation]
- [What you would build next]

## Tech stack
[Python, FastAPI, FAISS, ...]

## Licence
[MIT / Apache-2.0 / ...]
