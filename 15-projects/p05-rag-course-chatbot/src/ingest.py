"""
ingest.py - find markdown files and cut them into chunks.

Why chunk? An embedding of a whole 3,000-word file is a blurry average of many topics. Small
pieces ("chunks") each about one idea give sharper matches and let us cite the exact section.

How we chunk (simple and explainable):
  1. split the file at markdown headings (#, ##, ###) - each section keeps its heading path,
     e.g. "Module 09 - RAG > Chunking", which we show in citations
  2. if a section is longer than CHUNK_WORDS, cut it into word windows with a small overlap
     (the last few words of one chunk are repeated at the start of the next, so ideas
     that cross a boundary are not lost)
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import config

SKIP_PARTS = {".git", ".venv", "venv", "node_modules", ".ipynb_checkpoints", "__pycache__"}
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class Chunk:
    source: str      # file path relative to the docs root, e.g. "09-rag/concepts.md"
    heading: str     # heading path, e.g. "Module 09 - RAG > Chunking"
    text: str        # the chunk's words
    id: int = 0

    def citation(self) -> str:
        return f"{self.source} > {self.heading}" if self.heading else self.source

    def to_dict(self) -> dict:
        return asdict(self)


def docs_root(docs: str | None = None) -> Path:
    """Turn the DOCS setting into a folder."""
    docs = docs or config.DOCS
    if docs == "repo":
        return config.REPO_ROOT
    if docs == "sample":
        return config.SAMPLE_DOCS
    return Path(docs).expanduser().resolve()


def find_markdown(root: Path, pattern: str | None = None) -> list[Path]:
    """All markdown files under root (sorted, so the order is stable). Skips hidden/tool folders
    and this project's own sample copies (they would duplicate real curriculum text)."""
    pattern = pattern or config.DOCS_GLOB
    files = []
    for p in sorted(root.glob(pattern)):
        rel_parts = set(p.relative_to(root).parts)
        if not p.is_file() or rel_parts & SKIP_PARTS:
            continue
        if root != config.SAMPLE_DOCS and config.SAMPLE_DOCS in p.parents:
            continue
        files.append(p)
    return files


def split_sections(text: str) -> list[tuple[str, str]]:
    """Return [(heading path, section text), ...]. Text before any heading gets heading ''."""
    sections, stack, buf = [], [], []
    in_code = False

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((" > ".join(h for _, h in stack), body))
        buf.clear()

    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code          # a "#" inside a code block is a comment, not a heading
        m = None if in_code else HEADING.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2).strip()
            while stack and stack[-1][0] >= level:   # leave deeper/equal headings
                stack.pop()
            stack.append((level, title))
        else:
            buf.append(line)
    flush()
    return sections


def window(words: list[str], size: int, overlap: int) -> list[list[str]]:
    """Cut a list of words into windows of `size` words that overlap by `overlap` words."""
    if len(words) <= size:
        return [words]
    step = max(1, size - overlap)
    out = []
    for start in range(0, len(words), step):
        out.append(words[start:start + size])
        if start + size >= len(words):
            break
    return out


def chunk_markdown(text: str, source: str, size: int | None = None, overlap: int | None = None) -> list[Chunk]:
    size = size or config.CHUNK_WORDS
    overlap = config.CHUNK_OVERLAP if overlap is None else overlap
    chunks = []
    for heading, body in split_sections(text):
        for words in window(body.split(), size, overlap):
            if len(words) >= 5:                       # skip near-empty bits (e.g. a lone badge)
                chunks.append(Chunk(source=source, heading=heading, text=" ".join(words)))
    return chunks


def load_chunks(docs: str | None = None, size: int | None = None, overlap: int | None = None) -> list[Chunk]:
    """Find every markdown file under the docs root and chunk it. Falls back to the sample docs
    if the folder has no markdown (e.g. a fresh clone of only this project)."""
    root = docs_root(docs)
    files = find_markdown(root)
    if not files:
        root, files = config.SAMPLE_DOCS, find_markdown(config.SAMPLE_DOCS)
    chunks = []
    for f in files:
        chunks += chunk_markdown(f.read_text(encoding="utf-8", errors="ignore"),
                                 f.relative_to(root).as_posix(), size, overlap)
    for i, c in enumerate(chunks):
        c.id = i
    return chunks
