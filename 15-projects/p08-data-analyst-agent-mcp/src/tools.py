"""
tools.py - the functions the agent (and the MCP server) are allowed to call.

A **tool** is a normal Python function plus a description and a **JSON schema**
(a precise description of the arguments: names, types, which are required).
The model never runs code itself; it *asks* for a tool by name with arguments,
our code runs it and sends the result back. Like a manager (the model) who can
only send requests to specialists (the tools) through a form.

Tools:
  get_schema()                         tables and columns in the database
  sql_query(query)                     run ONE read-only SELECT on data/sales.db
  python_calc(expression)              evaluate a pandas expression on `df` (= the last SQL result)
  make_chart(query, x, y, kind, title) run a SELECT and save a PNG chart
  search_notes(query)                  keyword search in the ops notes (data/notes/*.md)

Safety ("guard rails"):
  * SQL: only one statement, must start with SELECT or WITH, a block-list of
    write/admin keywords, the database is opened read-only (mode=ro) AND an
    sqlite "authorizer" refuses any non-read action. Three independent layers.
  * python_calc: a single expression (no statements), checked with Python's
    `ast` module: no imports, no dunder (__x__) names, only whitelisted names,
    no builtins. This is a teaching sandbox, NOT a security boundary - never
    expose it to untrusted users without a real sandbox (container / separate process).
"""
from __future__ import annotations

import ast
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "sales.db"
NOTES_DIR = ROOT / "data" / "notes"
CHART_DIR = ROOT / "outputs" / "charts"
MAX_ROWS = 200

_STATE: dict = {"last_df": None}       # python_calc works on the result of the previous sql_query


class ToolError(Exception):
    """A problem the model can fix (bad SQL, blocked keyword...). Sent back as an observation."""


# --------------------------------------------------------------------------- SQL guard
BLOCKED = re.compile(r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|"
                     r"truncate|grant|load_extension)\b", re.I)


def check_read_only(query: str) -> str:
    """Raise ToolError unless `query` is a single SELECT/WITH statement. Returns the cleaned query."""
    q = query.strip().rstrip(";").strip()
    if not q:
        raise ToolError("Empty query.")
    if ";" in q:
        raise ToolError("Only one SQL statement is allowed (found ';').")
    if not re.match(r"^(select|with)\b", q, re.I):
        raise ToolError("Only SELECT (or WITH ... SELECT) queries are allowed.")
    if BLOCKED.search(q):
        raise ToolError(f"Blocked keyword in query: {BLOCKED.search(q).group(0).upper()}")
    return q


def _authorizer(action, *args):
    """sqlite calls this for every operation; we allow only reading."""
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def _connect(guarded: bool = True) -> sqlite3.Connection:
    """Open the database read-only. guarded=False is used only by our own trusted get_schema code."""
    if not DB_PATH.exists():
        raise ToolError("Database not found. Run `python -m src.make_db` first.")
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)    # read-only at the file level
    if guarded:
        con.set_authorizer(_authorizer)                            # read-only at the statement level
    return con


def run_select(query: str) -> pd.DataFrame:
    q = check_read_only(query)
    with _connect() as con:
        try:
            return pd.read_sql_query(q, con)
        except Exception as e:                                     # bad column name, syntax error...
            raise ToolError(f"SQL error: {e}") from e


# --------------------------------------------------------------------------- tools
def get_schema() -> dict:
    """List every table with its columns and types (our fixed SQL, so no model input reaches it)."""
    with _connect(guarded=False) as con:
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {t: [f"{c[1]} {c[2]}" for c in con.execute(f"SELECT * FROM pragma_table_info('{t}')")]
                for t in tables}


def sql_query(query: str) -> dict:
    """Run one read-only SELECT. Returns columns, up to 200 rows and the total row count."""
    df = run_select(query)
    _STATE["last_df"] = df
    return {"columns": list(df.columns), "rows": df.head(MAX_ROWS).round(2).values.tolist(),
            "row_count": int(len(df)), "truncated": len(df) > MAX_ROWS}


SAFE_NAMES = {"df", "pd", "np", "len", "round", "abs", "min", "max", "sum", "sorted", "list", "dict", "float",
              "int", "str", "True", "False", "None"}


def python_calc(expression: str) -> dict:
    """Evaluate one pandas expression, e.g. "(df.q4 - df.q3) / df.q3", on the last SQL result `df`."""
    df = _STATE["last_df"]
    if df is None:
        raise ToolError("No data yet: call sql_query first, then python_calc works on its result as `df`.")
    try:
        tree = ast.parse(expression, mode="eval")                  # mode="eval" = a single expression only
    except SyntaxError as e:
        raise ToolError(f"Not a valid single expression: {e.msg}") from e
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in SAFE_NAMES:
            raise ToolError(f"Name '{node.id}' is not allowed. Use df, pd, np and basic functions.")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise ToolError("Private or dunder attributes are not allowed.")
        if isinstance(node, (ast.Lambda, ast.NamedExpr)):
            raise ToolError("Lambdas and := are not allowed.")
    env = {"df": df.copy(), "pd": pd, "np": np, "len": len, "round": round, "abs": abs, "min": min, "max": max,
           "sum": sum, "sorted": sorted, "list": list, "dict": dict, "float": float, "int": int, "str": str}
    try:
        value = eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, env)   # noqa: S307 (guarded above)
    except Exception as e:
        raise ToolError(f"Calculation error: {e}") from e
    if isinstance(value, pd.DataFrame):
        return {"type": "table", "columns": [str(c) for c in value.columns],
                "rows": value.head(MAX_ROWS).round(4).values.tolist()}
    if isinstance(value, pd.Series):
        return {"type": "series", "values": {str(k): (round(float(v), 4) if isinstance(v, (int, float, np.number)) else str(v))
                                             for k, v in value.head(MAX_ROWS).items()}}
    if isinstance(value, (np.generic,)):
        value = value.item()
    return {"type": "value", "value": value if isinstance(value, (int, float, str, bool)) else str(value)}


def make_chart(query: str, x: str, y: str, kind: str = "line", title: str = "") -> dict:
    """Run a SELECT and save a line or bar chart of column y against column x as a PNG."""
    import matplotlib
    matplotlib.use("Agg")                                          # draw to files, no window
    import matplotlib.pyplot as plt
    df = run_select(query)
    if x not in df or y not in df:
        raise ToolError(f"Columns {x!r}/{y!r} not in result columns {list(df.columns)}")
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    (ax.bar if kind == "bar" else ax.plot)(df[x].astype(str), df[y])
    ax.set_title(title or f"{y} by {x}")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    name = re.sub(r"[^a-z0-9]+", "-", (title or f"{y}-by-{x}").lower()).strip("-") + ".png"
    fig.savefig(CHART_DIR / name, dpi=110)
    plt.close(fig)
    return {"path": f"outputs/charts/{name}", "points": int(len(df))}


def search_notes(query: str, k: int = 2) -> dict:
    """Return the k notes that share the most words with the query."""
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    scored = []
    for f in sorted(NOTES_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        score = sum(text.lower().count(w) for w in words)
        if score:
            scored.append((score, f.name, text))
    scored.sort(key=lambda t: -t[0])
    return {"matches": [{"file": n, "text": t.strip()} for _, n, t in scored[:k]]}


# --------------------------------------------------------------------------- registry
TOOLS = {
    "get_schema": {"fn": get_schema, "description": "List the database tables and their columns.",
                   "parameters": {"type": "object", "properties": {}, "required": []}},
    "sql_query": {"fn": sql_query,
                  "description": "Run ONE read-only SQLite SELECT on the sales database (tables: regions, products, "
                                 "orders). Returns columns and rows. Dates are TEXT 'YYYY-MM-DD'.",
                  "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    "python_calc": {"fn": python_calc,
                    "description": "Evaluate one pandas expression on `df`, the result of the previous sql_query. "
                                   "Example: (df['q4'] - df['q3']) / df['q3']",
                    "parameters": {"type": "object", "properties": {"expression": {"type": "string"}},
                                   "required": ["expression"]}},
    "make_chart": {"fn": make_chart, "description": "Run a SELECT and save a line or bar chart PNG of y against x.",
                   "parameters": {"type": "object", "properties": {
                       "query": {"type": "string"}, "x": {"type": "string"}, "y": {"type": "string"},
                       "kind": {"type": "string", "enum": ["line", "bar"]}, "title": {"type": "string"}},
                       "required": ["query", "x", "y"]}},
    "search_notes": {"fn": search_notes, "description": "Keyword search in internal ops/marketing/IT notes "
                                                        "that explain business events.",
                     "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                                    "required": ["query"]}},
}


def call_tool(name: str, args: dict) -> dict:
    """Run a tool by name. Errors come back as {"error": ...} so the agent can recover."""
    if name not in TOOLS:
        return {"error": f"Unknown tool {name!r}. Available: {', '.join(TOOLS)}"}
    try:
        return TOOLS[name]["fn"](**(args or {}))
    except ToolError as e:
        return {"error": str(e)}
    except TypeError as e:                                         # wrong/missing arguments
        return {"error": f"Bad arguments for {name}: {e}"}
