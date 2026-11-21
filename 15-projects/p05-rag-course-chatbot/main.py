"""
main.py - command-line interface for the RAG course chatbot.

    python main.py index                 # build the FAISS index from the markdown files
    python main.py ask "What is RAG?"    # one question
    python main.py chat                  # interactive chat with memory (type 'exit' to quit)
    python main.py eval                  # FAQ evaluation: chunk sizes x reranker
Options: --docs repo|sample|<folder>, --mode llm|extractive, --rerank
For the web UI run:  python app.py
"""
import argparse
from pathlib import Path

from src import config
from src.chat import RAGChatbot
from src.index import get_index

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description="RAG chatbot over the course notes")
    ap.add_argument("command", choices=["index", "ask", "chat", "eval"])
    ap.add_argument("question", nargs="?", default="")
    ap.add_argument("--docs", default=None, help="repo (default), sample, or a folder path")
    ap.add_argument("--mode", choices=["llm", "extractive"], default=None, help="how answers are written")
    ap.add_argument("--rerank", action="store_true", help="use the cross-encoder reranker")
    ap.add_argument("--rebuild", action="store_true", help="re-embed even if an index exists")
    args = ap.parse_args()

    if args.command == "eval":
        from src.evaluate import run_experiments
        table = run_experiments()
        out = HERE / "reports"
        out.mkdir(exist_ok=True)
        table.round(3).to_csv(out / "eval.csv", index=False)
        md = "# FAQ evaluation (sample docs)\n\n" + table.round(3).to_markdown(index=False) + "\n"
        (out / "eval.md").write_text(md, encoding="utf-8")
        print(table.round(3).to_string(index=False))
        print(f"\nwritten to {out / 'eval.md'}")
        return

    # A separate index folder per docs choice, so "sample" and "repo" don't overwrite each other
    docs = args.docs or config.DOCS
    folder = config.INDEX_DIR / (docs if docs in ("repo", "sample") else "custom")
    rebuild = args.rebuild or args.command == "index"
    vi = get_index(rebuild=rebuild, docs=docs, folder=folder)
    n_files = len({c.source for c in vi.chunks})
    print(f"index: {len(vi.chunks)} chunks from {n_files} markdown files ({docs})")
    if args.command == "index":
        return

    bot = RAGChatbot(vi, answer_mode=args.mode, rerank=args.rerank or None)
    if args.command == "ask":
        ans = bot.ask(args.question or "What is RAG?")
        print(f"\n{ans.formatted()}\n\n(mode: {ans.mode})")
        return

    print("Ask about the course (type 'exit' to quit, 'reset' to clear memory).")
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit"}:
            break
        if q.lower() == "reset":
            bot.reset()
            print("memory cleared")
            continue
        if q:
            ans = bot.ask(q)
            if ans.standalone != q:
                print(f"(searched for: {ans.standalone})")
            print(f"bot> {ans.formatted()}")


if __name__ == "__main__":
    main()
