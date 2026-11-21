"""
langfuse_tracing.py - record a "trace" of one LLM request with Langfuse.

Vocabulary:
  trace       = the full story of one user request, start to finish
  span        = one timed step inside the trace (e.g. "retrieve documents", "guardrails")
  generation  = a special span for an LLM call; it also stores model name, tokens and cost
  score       = a number or label attached to a trace (e.g. user thumbs-up, an eval result)

Needs:  pip install langfuse      (tested with langfuse 5.2.0, late 2026 - the SDK changes often,
                                   check https://langfuse.com/docs for the current API)
        and three environment variables:
           LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST
        (LANGFUSE_HOST = https://cloud.langfuse.com for Langfuse Cloud, or your own URL if self-hosted)

If the variables are missing, the script uses a tiny console tracer instead, so it never crashes.
"""
import os
import time
import uuid

HAVE_KEYS = all(os.getenv(k) for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"))


def fake_retrieve(question: str) -> list[str]:
    """Pretend document search (stands in for a RAG retriever)."""
    time.sleep(0.05)
    return ["doc-12: Docker packages an app with its dependencies.", "doc-40: Images are recipes, containers are running copies."]


def fake_llm(question: str, docs: list[str]) -> tuple[str, int, int]:
    """Pretend LLM call: returns (answer, input_tokens, output_tokens)."""
    time.sleep(0.1)
    answer = "Docker bundles your app and everything it needs into an image you can run anywhere."
    return answer, 120, 22


def run_with_langfuse(question: str):
    """Real tracing with the Langfuse SDK (v5 style: context managers)."""
    from langfuse import get_client          # get_client() reads the three env vars
    langfuse = get_client()
    # The outer observation becomes the trace's root span.
    with langfuse.start_as_current_observation(name="answer-question", as_type="span",
                                               input={"question": question}) as root:
        with langfuse.start_as_current_observation(name="retrieve", as_type="retriever") as s:
            docs = fake_retrieve(question)
            s.update(output=docs)
        with langfuse.start_as_current_observation(name="llm-call", as_type="generation",
                                                   model="demo-model", input=question) as gen:
            answer, tin, tout = fake_llm(question, docs)
            gen.update(output=answer,
                       usage_details={"input": tin, "output": tout},       # token counts
                       cost_details={"input": tin * 1e-6, "output": tout * 5e-6})  # USD, if you know it
        root.update(output={"answer": answer})
        root.score_trace(name="user_feedback", value=1, comment="thumbs up")  # attach a score (e.g. an eval)
    langfuse.flush()                         # send everything before the script exits
    print("Trace sent. Open your Langfuse project to see it.")


def run_with_console(question: str):
    """Offline stand-in: prints the same tree of steps with timings."""
    trace_id = uuid.uuid4().hex[:8]
    t0 = time.perf_counter()
    print(f"TRACE {trace_id} answer-question  input={question!r}")
    t = time.perf_counter(); docs = fake_retrieve(question)
    print(f"  SPAN retrieve      {1000*(time.perf_counter()-t):6.1f} ms  -> {len(docs)} docs")
    t = time.perf_counter(); answer, tin, tout = fake_llm(question, docs)
    cost = tin * 1e-6 + tout * 5e-6
    print(f"  GENERATION llm     {1000*(time.perf_counter()-t):6.1f} ms  tokens in/out={tin}/{tout}  cost=${cost:.6f}")
    print(f"  total {1000*(time.perf_counter()-t0):.1f} ms  output={answer!r}")


if __name__ == "__main__":
    q = "What is Docker?"
    if HAVE_KEYS:
        run_with_langfuse(q)
    else:
        print("Langfuse keys not set - using the console tracer.\n")
        run_with_console(q)
