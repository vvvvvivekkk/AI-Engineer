"""Tests for Project 5 - deterministic: they use the committed sample docs and extractive answers.
The first run downloads all-MiniLM-L6-v2 (~90 MB) from Hugging Face. Run:  python -m pytest -q"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import llm
from src.chat import NOT_FOUND, RAGChatbot
from src.evaluate import load_faq, token_f1
from src.index import VectorIndex
from src.ingest import chunk_markdown, load_chunks, split_sections, window
from src.retriever import retrieve
from src.rewrite import looks_like_follow_up, rewrite_rules


@pytest.fixture(scope="module")
def index():
    return VectorIndex.build(load_chunks("sample"))


def test_sections_keep_heading_path_and_ignore_code_comments():
    md = "# Top\nintro words here\n## Sub\nbody text\n```\n# not a heading\n```\n"
    secs = split_sections(md)
    assert secs[0] == ("Top", "intro words here")
    assert secs[1][0] == "Top > Sub" and "# not a heading" in secs[1][1]


def test_window_overlaps():
    words = [str(i) for i in range(10)]
    parts = window(words, size=4, overlap=1)
    assert parts[0] == ["0", "1", "2", "3"] and parts[1][0] == "3"   # word 3 repeated
    assert parts[-1][-1] == "9"


def test_chunks_have_citations():
    chunks = chunk_markdown("# Doc\n## Part\n" + "word " * 50, "doc.md", size=20, overlap=5)
    assert len(chunks) >= 3 and chunks[0].citation() == "doc.md > Doc > Part"
    sample = load_chunks("sample")
    assert len({c.source for c in sample}) == 8


def test_follow_up_rewriting_rules():
    assert looks_like_follow_up("how do I evaluate it?")
    assert not looks_like_follow_up("What is the difference between precision and recall?")
    assert rewrite_rules("how do I evaluate it?", [("What is RAG?", "...")]) == "how do I evaluate it (RAG)?"
    assert rewrite_rules("What is MCP?", []) == "What is MCP?"


@pytest.mark.parametrize("question,section", [
    ("What does a reranker do?", "Reranking"),
    ("Where should I keep my API key?", "API keys and .env files"),
    ("What is overfitting?", "Overfitting"),
])
def test_retrieval_finds_the_right_section(index, question, section):
    top_chunk, score = retrieve(index, question, k=3, rerank=False)[0]
    assert top_chunk.heading.endswith(section) and score > 0.3


def test_chatbot_cites_refuses_and_remembers(index):
    bot = RAGChatbot(index, answer_mode="extractive", rewrite_mode="rules")
    a1 = bot.ask("What is RAG?")
    assert a1.found and "[1]" in a1.text and a1.sources[0].startswith("09-rag.md")
    a2 = bot.ask("how do I evaluate it?")
    assert "RAG" in a2.standalone and any("Evaluating RAG" in s for s in a2.sources)
    a3 = bot.ask("What is the capital of France?")
    assert not a3.found and a3.text == NOT_FOUND


def test_faq_and_token_f1():
    faq = load_faq()
    assert len(faq) >= 30 and {"question", "answer", "source", "section"} <= set(faq[0])
    assert token_f1("the cat sat [1]", "cat sat") == 1.0 and token_f1("dog", "cat") == 0.0


def test_missing_key_message(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(llm.LLMConfigError, match="OPENAI_API_KEY"):
        llm.generate("hi")
