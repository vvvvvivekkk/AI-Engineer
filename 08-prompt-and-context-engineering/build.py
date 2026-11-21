"""
build.py - regenerate this module's images, notebooks, slides, Excel tracker and PDF handout.

    python 08-prompt-and-context-engineering/build.py
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
sys.path.insert(0, str(HERE))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook  # noqa: E402

import csv  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

IMG = HERE / "images"
NAME = HERE.name

# ---------------------------------------------------------------- diagrams
MERMAID = {
    "prompt_anatomy": """
flowchart LR
  R[Role / identity] --> T[Task: one clear verb]
  T --> C[Context: facts it lacks]
  C --> E[Examples: input to output]
  E --> F[Output format]
  F --> K[Constraints and fallbacks]
  K --> I[Input, inside delimiters]
  I --> M((Model))
""",
    "injection_defences": """
flowchart LR
  U[Untrusted text: web page, email, tool result] --> L1[1 Tag as data]
  L1 --> L2[2 Scan for attack phrases]
  L2 --> M((Model with least-privilege tools))
  M --> L4[4 Check output]
  L4 --> L5{5 Risky action?}
  L5 -- no --> OK[Show to user]
  L5 -- yes --> H[Human approves]
""",
    "prompt_eval_loop": """
flowchart LR
  W[Write or change prompt] --> V[Save as new version]
  V --> R[Run fixed test set]
  R --> S[Score: exact, rules, judge]
  S --> F[Read the failures]
  F --> D{Good enough?}
  D -- no --> W
  D -- yes --> P[Ship and log fingerprint]
""",
    "system_prompt_layers": """
flowchart TD
  A[Identity and scope] --> B[Environment facts injected at run time]
  B --> C[Tools: when to use, when not to]
  C --> D[Work loop and planning]
  D --> E[Output format for the screen]
  E --> F[Grounding and citations]
  F --> G[Safety: trusted vs untrusted]
  G --> H[Tone for the user]
  H --> I[Good and bad examples]
""",
}


def context_chart():
    """Stacked bar showing how a context window budget is typically split."""
    parts = [("System prompt", 1200, "#1B263B"), ("Memory", 300, "#5A6370"), ("Retrieved docs", 3000, "#0F9D9A"),
             ("Chat history (summarised + recent)", 1800, "#7FB7BE"), ("Tool results (trimmed)", 1200, "#E0A458"),
             ("Question", 100, "#C84C09"), ("Room for the answer", 1000, "#D9D9D9")]
    fig, ax = plt.subplots(figsize=(10, 2.6))
    left = 0
    for label, v, c in parts:
        ax.barh(0, v, left=left, color=c, edgecolor="white")
        ax.text(left + v / 2, 0, f"{label}\n{v}", ha="center", va="center", fontsize=7.5,
                color="white" if c not in ("#D9D9D9", "#7FB7BE") else "black")
        left += v
    ax.set_xlim(0, left); ax.set_yticks([]); ax.set_xlabel("tokens (example 8,600-token budget)")
    ax.set_title("Context engineering: every call is a packed suitcase with a weight limit")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    plt.tight_layout(); fig.savefig(IMG / "context_window_layout.png", dpi=150); plt.close(fig)


def pattern_charts():
    """Charts from our own keyword counts of real system prompts (no prompt text involved)."""
    path = HERE / "excel" / "prompt_pattern_counts.csv"
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    rows.sort(key=lambda r: int(r["words"]))
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.barh([r["product"] for r in rows], [int(r["words"]) for r in rows], color="#0F9D9A")
    ax.set_xscale("log"); ax.set_xlabel("words in all prompt files of the folder (log scale)")
    ax.set_title("How long are real system prompts? (our count, per repo folder)")
    plt.tight_layout(); fig.savefig(IMG / "prompt_sizes.png", dpi=150); plt.close(fig)

    pats = ["xml_sections", "markdown_sections", "tool_rules", "examples", "step_by_step_workflow",
            "planning_or_todo", "output_format_rules", "emphasis_caps", "safety_refusals",
            "environment_context", "memory_or_context_mgmt", "citations"]
    rows.sort(key=lambda r: r["product"].lower())
    data = np.array([[int(r[p]) / int(r["words"]) * 1000 for p in pats] for r in rows])
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(np.minimum(data, 15), cmap="GnBu", aspect="auto")
    ax.set_xticks(range(len(pats)), [p.replace("_", " ") for p in pats], rotation=40, ha="right")
    ax.set_yticks(range(len(rows)), [r["product"] for r in rows])
    for i in range(len(rows)):
        for j in range(len(pats)):
            ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if data[i, j] > 8 else "black")
    fig.colorbar(im, label="keyword hits per 1,000 words (capped at 15)")
    ax.set_title("Pattern keywords in real AI-tool system prompts (rough keyword count, not a human rating)")
    plt.tight_layout(); fig.savefig(IMG / "pattern_heatmap.png", dpi=150); plt.close(fig)


# ---------------------------------------------------------------- slides
def deck():
    I = lambda n: str(IMG / f"{n}.png")
    return {
        "title": "Module 08 - Prompt and Context Engineering",
        "subtitle": "Python to Pro AI Engineer curriculum",
        "slides": [
            {"title": "Why this module matters",
             "bullets": ["A model only knows what is in front of it on THIS call",
                         "Prompt engineering: how to phrase instructions and examples",
                         "Context engineering: what goes in the window, in what order, within a budget",
                         "Both are code: version them, test them, defend them"],
             "notes": "Open with the idea that the model has no memory between calls. Every API call is a fresh start, so the words we send are everything. Today we learn to choose those words well and to test our choice like code."},
            {"title": "Analogy: briefing a temp worker",
             "bullets": ["Very well read, knows nothing about your company", "Forgets everything when they leave",
                         "Cannot ask questions mid-task", "Eager to please - will guess rather than stop",
                         "Your prompt = the briefing note at the door"],
             "notes": "Tell the story: each morning the agency sends a new, very smart temp. You hand them a note. A vague note gets vague work. Ask the class what they would put in a good briefing note - they will reinvent the anatomy on the next slide."},
            {"title": "Messages and roles",
             "bullets": ["system: standing rules from the developer", "user: the request for this turn",
                         "assistant: the model's replies (you can write fake ones as examples)",
                         "The chat template joins them into one text stream"],
             "code": 'messages = [\n {"role": "system", "content": "You sort tickets..."},\n {"role": "user", "content": "Ticket: charged twice"},\n]',
             "notes": "Show that roles are only labels in one long text. In notebook 01 we print the joined text with its special marker tokens so students see there is no magic. The Anthropic API takes the system prompt as a separate argument; OpenAI takes it as the first message. Same idea."},
            {"title": "Anatomy of a good prompt", "image": I("prompt_anatomy"),
             "bullets": ["Role", "Task (one verb)", "Context", "Examples", "Format", "Constraints + fallback", "Input in delimiters"],
             "notes": "Walk through each block with the ticket-classifier example. Stress the fallback: tell the model what to say when it cannot answer, otherwise it will guess. Delimiters such as XML tags separate instructions from input."},
            {"title": "Zero-shot vs few-shot",
             "bullets": ["Zero-shot: rules only", "Few-shot: rules + 2-8 worked examples",
                         "Examples fix FORMAT better than rules", "Cover every label, vary them, watch order",
                         "Our tiny model: 0% format obeyed zero-shot, ~75% few-shot"],
             "notes": "Analogy: describing the till versus showing three customers being served. Share the measured result from notebook 01: the tiny local model mostly repeated the ticket text zero-shot, and mostly answered with a single label when examples were sent as chat turns. Strong API models score higher on both."},
            {"title": "Reasoning prompts",
             "bullets": ["Chain-of-thought: think in <thinking>, answer in <answer>",
                         "Your code reads only the answer", "Reasoning models: set a thinking budget instead",
                         "Costs tokens; nice reasoning can still be wrong", "Self-consistency: sample 5, take the majority"],
             "notes": "Analogy: showing your working in a maths exam. Each written step becomes context for the next. Warn that reasoning text is not proof - always test the final answers."},
            {"title": "Structured output",
             "bullets": ["Programs need data, not prose", "Schema = a paper form with boxes (Pydantic)",
                         "Validate -> on error, send the error back -> retry -> give up safely",
                         "APIs can enforce a JSON schema; still validate in code"],
             "code": 'class TicketInfo(BaseModel):\n    category: Literal["billing","delivery",\n                      "product","account"]\n    urgency: int = Field(ge=1, le=5)\n    order_id: Optional[str] = None',
             "notes": "Show the Pydantic class. Literal means only these values. Optional lets the model say 'no order id' instead of inventing one. Never pass unvalidated model output to the rest of your program."},
            {"title": "System prompts and templates",
             "bullets": ["System prompt = job description pinned above the desk",
                         "Not a secret vault, not a security wall", "Templates with {blanks} filled by code",
                         "Version every change + note + fingerprint", "Keep old versions (recipe-card box)"],
             "notes": "Two warnings: users can often extract a system prompt, so never put secrets in it; and 'never do X' lowers the chance of X but does not make it impossible. Then show the recipe card analogy for versioning."},
            {"title": "Context engineering", "image": I("context_window_layout"),
             "bullets": ["Window = budget (cost, speed, attention)", "Essentials first, question last",
                         "Summarise old history", "Trim tool output (head + tail)", "Recall only relevant memory"],
             "notes": "Suitcase analogy: weight limit, essentials first, vacuum-pack bulky clothes, leave the hair dryer at home. Mention the lost-in-the-middle effect: models use the start and end of long inputs more reliably than the middle."},
            {"title": "Prompt injection",
             "bullets": ["Untrusted text that tries to give new instructions",
                         "Direct: the user types it", "Indirect: hidden in web pages, emails, PDFs, tool results",
                         "Works because the model sees one text stream", "No complete fix yet - defend in layers"],
             "notes": "Receptionist analogy: a letter that says the manager wants you to hand over the master key is a letter to read, not an order. Show the hidden HTML comment attack from notebook 04."},
            {"title": "Defence in depth", "image": I("injection_defences"),
             "bullets": ["Tag untrusted text as data", "Scan inputs (smoke alarm)", "Least privilege (strongest)",
                         "Check outputs", "Human approval for risky actions"],
             "notes": "Emphasise least privilege: if the summariser has no email tool, a hijack cannot send email. Show how a simple letter-swap beats the regex scanner - that is why one layer is never enough."},
            {"title": "Evaluate prompts like code", "image": I("prompt_eval_loop"),
             "bullets": ["10-30 cases: typical, edge, attack", "Score: exact match, rules, LLM-as-judge",
                         "Read the failures", "Change ONE thing, new version, rerun", "Record runs in the tracker"],
             "notes": "Driving-test route analogy: same route and checklist for every candidate. Show the Excel tracker. Insist on temperature 0 for repeatable tests and testing on the model you will ship."},
            {"title": "What real products' prompts look like", "image": I("prompt_sizes"),
             "bullets": ["Thousands of words: operations manuals", "Same building blocks, different mix",
                         "Treat as unverified case studies", "We copy no text - patterns only"],
             "notes": "Introduce the public repository of collected system prompts. Stress the two rules: authenticity is unverified, and the text belongs to the companies, so we only discuss patterns and link to folders."},
            {"title": "Recurring building blocks", "image": I("system_prompt_layers"),
             "bullets": ["Identity + scope", "Run-time environment facts", "Tools with when-NOT-to rules",
                         "Work loop + to-do list", "Format for the screen", "Citations", "Trusted vs untrusted", "Good/bad examples"],
             "notes": "Go through the blocks with one example product each: Cursor for tool rules, Manus for the agent loop, Perplexity for citations and format, Lovable for consent-first workflow, browser agents for injection rules, Kiro for routing."},
            {"title": "Write your own system prompt",
             "bullets": ["Start from templates/system-prompt-template.md", "Fill identity, environment, tools, workflow",
                         "Format, grounding, safety, tone, examples", "Test with 10-20 cases", "Add rules only to fix failing tests"],
             "notes": "Show the filled-in Brightleaf example in the template. Students will write their own in exercises 9 to 12."},
            {"title": "Common mistakes",
             "bullets": ["One vague sentence as the prompt", "No output format, no validation",
                         "All examples look the same", "Stuffing everything into the context",
                         "Secrets in the system prompt", "Editing prompts in production without tests"],
             "notes": "Ask students which of these they have already done. Every one of them is fixed by something in today's session."},
            {"title": "Recap and exercises",
             "bullets": ["Anatomy -> examples -> format -> versioning", "Context = budget: pack, order, compress",
                         "Injection: layers + least privilege", "Test sets + tracker", "Exercises 1-12 in exercises.md"],
             "notes": "Recap in one breath, then assign exercises 1 to 4 in class and the rest as homework. Point to the four notebooks."},
        ],
    }


# ---------------------------------------------------------------- excel
def tracker():
    header = ["test_id", "prompt_name", "prompt_version", "fingerprint", "model", "case_type", "input",
              "expected", "actual_reply", "pass (1/0)", "failure_reason", "notes", "run_date"]
    rows = [header]
    res = HERE / "code" / "prompt_eval_results.csv"
    if res.exists():
        for r in csv.DictReader(open(res, encoding="utf-8")):
            rows.append([r["id"], "classify_ticket", r["version"], r["fingerprint"], "SmolLM2-135M-Instruct (local)",
                         "typical", r["input"], r["expected"], r["reply"], 1 if r["correct"] == "True" else 0,
                         "" if r["correct"] == "True" else ("format" if r["format_ok"] == "False" else "wrong label"),
                         "from code/prompt_eval.py", ""])
    n = len(rows)
    summary = [["prompt_version", "cases", "passed", "pass_rate"]]
    for v in ["v1", "v2", "v3", "v4"]:
        summary.append([v, f'=COUNTIF(Tests!C:C,"{v}")', f'=COUNTIFS(Tests!C:C,"{v}",Tests!J:J,1)',
                        f'=IF(B{len(summary)+1}=0,"",C{len(summary)+1}/B{len(summary)+1})'])
    blank = [["(your case id)", "(prompt name)", "(v1)", "", "", "typical / edge / attack", "", "", "", "", "", "", ""]
             for _ in range(5)]
    guide = [["column", "what to write"],
             ["test_id", "Stable id, e.g. T01 typical, E01 edge, A01 attack"],
             ["prompt_version", "The version you ran (v1, v2...). Never reuse a version name for a different text"],
             ["fingerprint", "First 8 characters of the SHA-256 hash of the prompt text"],
             ["case_type", "typical / edge / attack"],
             ["expected", "The exact label, or the rule a good answer must follow"],
             ["pass (1/0)", "1 if it passed, 0 if not. The Summary sheet counts these"],
             ["failure_reason", "format / wrong label / hallucination / followed injection / too long ..."],
             ["Tip", "Change ONE thing per version, rerun every case, read every failure"]]
    pattern_rows = [list(r.keys()) for r in [next(csv.DictReader(open(HERE / "excel" / "prompt_pattern_counts.csv")))]]
    pattern_rows += [list(r.values()) for r in csv.DictReader(open(HERE / "excel" / "prompt_pattern_counts.csv"))]
    workbook({"Tests": rows + blank, "Summary": summary, "How to use": guide,
              "Real prompt patterns": pattern_rows},
             HERE / "excel" / "prompt-test-tracker.xlsx",
             col_widths={"Tests": [8, 16, 10, 11, 22, 12, 40, 12, 30, 9, 16, 22, 11], "How to use": [18, 80]})
    return n


def main():
    for name, src in MERMAID.items():
        mermaid(src, IMG / f"{name}.png")
    context_chart()
    pattern_charts()
    from build_notebooks import NB01, NB02, NB03, NB04
    nbdir = HERE / "notebooks"
    notebook(NB01, nbdir / "01-prompt-anatomy-and-few-shot.ipynb")
    notebook(NB02, nbdir / "02-structured-output-and-reasoning.ipynb")
    notebook(NB03, nbdir / "03-context-engineering.ipynb")
    notebook(NB04, nbdir / "04-injection-and-prompt-evaluation.ipynb")
    slides(deck(), HERE / "slides" / f"{NAME}.pptx")
    tracker()
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{NAME}-handout.pdf",
                      title="Module 08 - Prompt and Context Engineering")
    pdf_from_markdown(HERE / "system-prompt-analysis.md", HERE / "pdf" / "system-prompt-analysis.pdf",
                      title="What real AI products' system prompts teach us")
    print("built", NAME)


if __name__ == "__main__":
    main()
