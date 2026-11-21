"""
resume_matcher.py - compare a resume with a job description (JD), fully offline.

It reports:
  1. which known AI/tech skills the JD asks for, and which of them your resume mentions
  2. a TF-IDF similarity score (how much the two texts use the same important words)
  3. frequent JD phrases missing from your resume

Usage (from the 16-careers folder):
    python code/resume_matcher.py data/sample_resume.txt data/sample_job_description.txt
Honest-use rule: only add a missing keyword to your resume if you really have that skill.
"""
import re
import sys
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer  # scikit-learn tools
from sklearn.metrics.pairwise import cosine_similarity

# A skill vocabulary: canonical name -> list of ways people write it (all lower-case).
SKILLS = {
    "python": ["python"], "sql": ["sql", "postgres", "postgresql", "mysql"], "git": ["git", "github", "gitlab"],
    "pytest / testing": ["pytest", "unit test", "unit testing", "tests"],
    "machine learning": ["machine learning", "scikit-learn", "sklearn"], "pytorch": ["pytorch", "torch"],
    "transformers / hugging face": ["hugging face", "transformers", "distilbert", "bert"],
    "llm apis": ["openai api", "anthropic", "llm api", "llm apis", "gemini api", "claude"],
    "prompt engineering": ["prompt engineering", "prompting", "prompt design"],
    "structured outputs": ["structured output", "structured outputs", "json mode", "json schema"],
    "rag": ["rag", "retrieval-augmented", "retrieval augmented"],
    "embeddings": ["embedding", "embeddings", "sentence-transformers", "minilm"],
    "vector database": ["vector database", "vector db", "faiss", "qdrant", "pgvector", "chroma", "pinecone", "weaviate"],
    "hybrid search / reranking": ["hybrid search", "bm25", "rerank", "reranking", "reranker"],
    "agents / tool calling": ["agent", "agents", "tool calling", "function calling"],
    "langgraph": ["langgraph"], "langchain": ["langchain"], "mcp": ["mcp", "model context protocol"],
    "fastapi / rest apis": ["fastapi", "rest api", "rest apis", "flask"],
    "docker": ["docker", "container", "containers"], "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "github actions", "continuous integration"],
    "cloud": ["aws", "gcp", "azure", "cloud"],
    "evaluation / evals": ["evaluation", "evals", "eval", "evaluated", "hit rate", "llm-as-judge"],
    "observability": ["observability", "langfuse", "langsmith", "monitoring", "tracing"],
    "guardrails / security": ["guardrails", "pii", "prompt injection", "red-teaming", "red teaming"],
    "fine-tuning": ["fine-tuning", "fine-tuned", "fine tuning", "lora", "qlora"],
    "streamlit / gradio": ["streamlit", "gradio"],
    "rubrics / annotation": ["rubric", "rubrics", "annotation", "rank and compare", "rated and ranked"],
    "communication": ["communication", "documentation", "written english", "justifications"],
}


def normalise(text: str) -> str:
    """Lower-case and collapse whitespace so matching is simpler."""
    return re.sub(r"\s+", " ", text.lower())


def find_skills(text: str) -> set[str]:
    """Return the canonical skill names whose spellings appear in the text (whole-word matches)."""
    t = normalise(text)
    found = set()
    for name, variants in SKILLS.items():
        for v in variants:
            if re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", t):
                found.add(name)
                break
    return found


def tfidf_similarity(a: str, b: str) -> float:
    """Cosine similarity of TF-IDF vectors: 0 = no shared important words, 1 = identical word use."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    m = vec.fit_transform([a, b])
    return float(cosine_similarity(m[0], m[1])[0, 0])


def missing_phrases(resume: str, jd: str, top: int = 12) -> list[tuple[str, int]]:
    """Most frequent 1-2 word JD phrases (without stop words) that never appear in the resume."""
    words = [w for w in re.findall(r"[a-z][a-z+/.-]*[a-z]", normalise(jd)) if w not in ENGLISH_STOP_WORDS]
    grams = words + [" ".join(p) for p in zip(words, words[1:])]
    counts = Counter(grams)
    r = normalise(resume)
    return [(g, c) for g, c in counts.most_common() if g not in r][:top]


def report(resume: str, jd: str) -> dict:
    jd_skills, cv_skills = find_skills(jd), find_skills(resume)
    matched, missing = sorted(jd_skills & cv_skills), sorted(jd_skills - cv_skills)
    coverage = len(matched) / len(jd_skills) if jd_skills else 0.0
    return {"coverage": coverage, "matched": matched, "missing": missing,
            "tfidf": tfidf_similarity(resume, jd), "missing_phrases": missing_phrases(resume, jd)}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python resume_matcher.py RESUME.txt JOB_DESCRIPTION.txt")
    resume_text = open(sys.argv[1], encoding="utf-8").read()
    jd_text = open(sys.argv[2], encoding="utf-8").read()
    r = report(resume_text, jd_text)
    print(f"Skill coverage: {r['coverage']:.0%} of the skills this JD mentions")
    print("Matched :", ", ".join(r["matched"]))
    print("Missing :", ", ".join(r["missing"]))
    print(f"TF-IDF similarity: {r['tfidf']:.2f}  (no absolute meaning: use it to compare versions of your resume against the same JD)")
    print("Frequent JD phrases not in your resume:")
    for phrase, n in r["missing_phrases"]:
        print(f"  {n}x  {phrase}")
