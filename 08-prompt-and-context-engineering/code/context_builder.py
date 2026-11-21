"""
context_builder.py - decide what goes into the model's context window, in what order, within a token budget.

Analogy: packing a carry-on suitcase with a strict weight limit. Essentials
(system rules, the current question) go in first. Then the most useful extras
(relevant documents, recent chat turns). Old chat turns get "vacuum-packed"
(summarised). Huge items (a 5,000-line tool output) get trimmed. Anything that
still does not fit stays at home.

Run it:  python code/context_builder.py
"""
from dataclasses import dataclass

try:
    import tiktoken                                       # OpenAI's tokenizer library: counts tokens the way GPT models do
    _ENC = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(_ENC.encode(text))
except Exception:                                         # if tiktoken is missing or offline, use a rough rule
    def count_tokens(text: str) -> int:
        return max(1, len(text) // 4)                     # about 4 characters per token in English


@dataclass
class Piece:
    """One candidate item for the context window."""
    kind: str          # "system", "memory", "doc", "history", "tool", "question"
    text: str
    priority: int      # lower number = more important = packed first


def truncate_middle(text: str, max_tokens: int) -> str:
    """Keep the start and end of a long text, cut the middle. Good for logs and tool outputs,
    where the first lines (the command) and last lines (the error) matter most."""
    if count_tokens(text) <= max_tokens:
        return text
    lines = text.splitlines()
    head, tail = lines[: len(lines) // 4 or 1], lines[-(len(lines) // 4 or 1):]
    while count_tokens("\n".join(head + tail)) > max_tokens and (len(head) > 1 or len(tail) > 1):
        head, tail = head[:-1] or head, tail[1:] or tail    # shave one line from each side until it fits
    cut = len(lines) - len(head) - len(tail)
    return "\n".join(head + [f"... [{cut} lines removed to save space] ..."] + tail)


def summarise_history(turns: list[str], keep_last: int = 4) -> list[str]:
    """Keep the last few turns word-for-word; squash older turns into one summary line.
    Here the 'summary' is a cheap rule (first 12 words of each turn). In production you
    would ask an LLM to write the summary."""
    if len(turns) <= keep_last:
        return turns
    old, recent = turns[:-keep_last], turns[-keep_last:]
    gist = " | ".join(" ".join(t.split()[:12]) for t in old)
    return [f"[Summary of {len(old)} earlier turns: {gist}]"] + recent


def build_context(pieces: list[Piece], budget: int) -> tuple[str, list[str]]:
    """Pack pieces by priority until the token budget is used. Then re-order the kept pieces
    so the layout is: system -> memory -> docs -> history -> tool results -> question.
    Putting the question LAST means it is the freshest thing the model reads."""
    layout = ["system", "memory", "doc", "history", "tool", "question"]
    kept, log, used = [], [], 0
    for p in sorted(pieces, key=lambda p: p.priority):    # most important first
        cost = count_tokens(p.text)
        if used + cost <= budget:
            kept.append(p); used += cost
            log.append(f"KEEP  {p.kind:<8} {cost:>5} tok (total {used})")
        else:
            log.append(f"DROP  {p.kind:<8} {cost:>5} tok (would exceed {budget})")
    kept.sort(key=lambda p: layout.index(p.kind))        # final reading order
    blocks = [f"<{p.kind}>\n{p.text}\n</{p.kind}>" for p in kept]   # tags make section edges clear to the model
    return "\n\n".join(blocks), log


if __name__ == "__main__":
    history = [f"turn {i}: user asked about order #{100+i} and the bot answered politely" for i in range(10)]
    tool_output = "\n".join(f"log line {i}: ok" for i in range(300)) + "\nERROR: payment gateway timeout"
    pieces = [
        Piece("system", "You are a support assistant for Brightleaf. Be brief and cite sources.", 0),
        Piece("question", "Why did my payment fail?", 0),
        Piece("memory", "Customer prefers email. Customer is on the Gold plan.", 1),
        Piece("tool", truncate_middle(tool_output, 80), 2),
        Piece("doc", "Payments policy: failed payments are retried once after 10 minutes.", 2),
        Piece("history", "\n".join(summarise_history(history)), 3),
        Piece("doc", "Unrelated doc about returns. " * 40, 5),
    ]
    context, log = build_context(pieces, budget=300)
    print(*log, sep="\n")
    print("\n===== FINAL CONTEXT =====\n" + context)
