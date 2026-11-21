"""
analyse_prompt_patterns.py - count design patterns in real AI-tool system prompts, WITHOUT copying any text.

Source: https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools
  (GPL-3.0 repo of system prompts claimed to come from commercial products; the
  prompt texts belong to those companies and their authenticity is unverified).

What it does:
  For each product folder it opens the prompt .txt/.yaml files, measures them
  (word count) and checks with keyword rules whether each pattern appears
  (e.g. XML-style section tags, few-shot examples, an explicit agent loop).
  It writes ONLY numbers and yes/no flags to a CSV. No sentence from any prompt
  is stored or printed, so the output is our own data, not their text.

Keyword rules are rough: a "yes" means "keyword found", not "a human confirmed it".
We spot-checked the main products by reading them; see system-prompt-analysis.md.

Run it (needs a local clone of the repo):
  git clone --depth 1 https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools /tmp/sp
  python code/analyse_prompt_patterns.py /tmp/sp
"""
import csv
import re
import sys
from pathlib import Path

# Pattern name -> regular expression that suggests the pattern is present.
PATTERNS = {
    "identity_line": r"^\s*(you are|i am)\b",                                  # opens by naming who the assistant is
    "xml_sections": r"^\s*<[a-z_]{3,40}>\s*$",                                 # sections wrapped in <tag> ... </tag>
    "markdown_sections": r"^#{1,3} \S",                                        # sections with # headings
    "tool_rules": r"\b(tool call|tool_call|function call|tools? available|use the \w+ tool)\b",
    "examples": r"(<example>|\bexample[s]?:|good example|bad example)",         # few-shot / good-vs-bad examples
    "step_by_step_workflow": r"(step 1|1\.\s+\w+.*\n\s*2\.\s+\w+|workflow|agent loop)",
    "planning_or_todo": r"\b(plan|todo|to-do|task list)\b",
    "think_scratchpad": r"(<think>|think step|reasoning|scratchpad)",
    "output_format_rules": r"\b(markdown|format(ting)?|bullet|json)\b",
    "emphasis_caps": r"\b(NEVER|ALWAYS|MUST|IMPORTANT|CRITICAL)\b",           # shouting important rules
    "safety_refusals": r"\b(refus\w*|harmful|malicious|decline)\b",
    "environment_context": r"\b(current date|today's date|operating system|working directory|cwd|os version)\b",
    "memory_or_context_mgmt": r"\b(memor(y|ies)|context window|summari[sz]e)\b",
    "citations": r"\b(cite|citation|sources?)\b",
    "confidentiality": r"(do not|don't|never) (reveal|share|disclose).{0,40}(prompt|instructions)",
}

PRODUCTS = ["Cursor Prompts", "Devin AI", "Lovable", "Manus Agent Tools & Prompt", "Perplexity",
            "v0 Prompts and Tools", "Windsurf", "Replit", "NotionAi", "Kiro", "Cluely", "Junie",
            "Same.dev", "Trae", "VSCode Agent", "Warp.dev", "Anthropic", "Augment Code", "Comet Assistant"]


def analyse(repo: Path) -> list[dict]:
    rows = []
    for prod in PRODUCTS:
        folder = repo / prod
        if not folder.exists():
            continue
        files = [f for f in folder.rglob("*") if f.suffix in {".txt", ".yaml", ".md"} and f.name != "README.md"]
        text = "\n".join(f.read_text(encoding="utf-8", errors="ignore") for f in files)
        tool_files = [f for f in folder.rglob("*") if f.suffix in {".json"} or "tool" in f.name.lower()]
        row = {"product": prod, "prompt_files": len(files), "words": len(text.split()),
               "has_tool_schema_file": "yes" if tool_files else "no"}
        for name, rx in PATTERNS.items():
            hits = len(re.findall(rx, text, flags=re.IGNORECASE | re.MULTILINE))
            if name == "emphasis_caps":                                 # this one must stay case-sensitive
                hits = len(re.findall(rx, text, flags=re.MULTILINE))
            row[name] = hits
        rows.append(row)
    return rows


if __name__ == "__main__":
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/src/x1xhlol_system-prompts-and-models-of-ai-tools")
    rows = analyse(repo)
    out = Path(__file__).resolve().parents[1] / "excel" / "prompt_pattern_counts.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"{r['product']:<28} {r['words']:>7} words  tools-file={r['has_tool_schema_file']}")
    print("Saved", out)
