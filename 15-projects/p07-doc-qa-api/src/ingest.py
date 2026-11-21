"""
ingest.py - turn PDF files into small, searchable text chunks that remember their page.

Words used here:
  **parse** - read a file format (PDF) and pull out the plain text.
  **chunk** - a short piece of a document (here about 60 words). We search chunks,
      not whole documents, because a short piece that exactly matches the question
      is easier to find and to quote. Like cutting a book into index cards.
  **overlap** - the last few words of one chunk are repeated at the start of the
      next, so a sentence cut in half still appears whole in one of them.

**pypdf** is a pure-Python library that reads PDF files page by page.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class Chunk:
    """One searchable piece of text plus where it came from (for citations)."""
    chunk_id: str
    doc: str
    page: int          # 1-based page number, as a person would say it
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def read_pdf_pages(path: Path) -> list[str]:
    """Return the text of every page in a PDF (index 0 = page 1)."""
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        lines = [ln.strip() for ln in (page.extract_text() or "").splitlines() if ln.strip()]
        kept = []
        for ln in lines:
            if ln.startswith("Northwind Labs - "):        # repeated page header: carries no facts
                continue
            if len(ln.split()) <= 5 and not ln.endswith((".", "!", "?", ":")):
                ln += "."                                   # a short heading -> its own "sentence"
            kept.append(ln)
        pages.append(re.sub(r"\s+", " ", " ".join(kept)).strip())   # one clean line of text per page
    return pages


def chunk_text(text: str, size: int = 60, overlap: int = 15) -> list[str]:
    """Split text into windows of `size` words that overlap by `overlap` words."""
    words = text.split()
    if not words:
        return []
    step = max(1, size - overlap)
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):                  # last window reached the end
            break
    return chunks


def ingest_folder(folder: Path, size: int = 60, overlap: int = 15) -> list[Chunk]:
    """Parse every PDF in a folder into page-aware chunks."""
    chunks: list[Chunk] = []
    for pdf in sorted(Path(folder).glob("*.pdf")):
        chunks += ingest_file(pdf, size, overlap)
    return chunks


def ingest_file(pdf: Path, size: int = 60, overlap: int = 15) -> list[Chunk]:
    """Parse one PDF into chunks. Chunks never cross a page boundary, so each has one page number."""
    out = []
    for page_no, text in enumerate(read_pdf_pages(pdf), start=1):
        for j, piece in enumerate(chunk_text(text, size, overlap)):
            out.append(Chunk(chunk_id=f"{pdf.stem}-p{page_no}-c{j}", doc=pdf.name, page=page_no, text=piece))
    return out
