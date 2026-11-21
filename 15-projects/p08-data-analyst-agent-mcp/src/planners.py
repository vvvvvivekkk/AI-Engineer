"""
planners.py - the "brain" that decides the agent's next step.

A **planner** looks at the question and everything that has happened so far
(the **trajectory**: which tools were called, with what, and what came back)
and returns ONE next action:
    {"tool": "sql_query", "args": {"query": "SELECT ..."}}      or
    {"final": "North fell most because ..."}

Planners in this file:
  ScriptedPlanner   deterministic rules for 5 known question types. No model,
                    always the same steps - perfect for tests and demos. Honest
                    note: it cannot handle new kinds of questions.
  JsonPlanner       asks any text LLM (local SmolLM2 or Ollama) to reply with JSON.
                    The 135M local model usually fails at this - try it to see why
                    agents need bigger models.
  AnthropicPlanner  Claude with native tool calling (needs ANTHROPIC_API_KEY).
  OpenAIPlanner     GPT with native tool calling (needs OPENAI_API_KEY).
  OllamaPlanner     Ollama's native tool calling (e.g. qwen2.5:1.5b or llama3.2:3b).
"""
from __future__ import annotations

import json
import os
import re

from .tools import TOOLS

SYSTEM = ("You are a careful data analyst. Answer business questions about a SQLite sales database "
          "(tables: regions, products, orders; dates are 'YYYY-MM-DD' text; year 2025). Use the tools: look at "
          "the schema, query with read-only SQL, calculate with python_calc, explain with search_notes. "
          "When you have enough evidence, give a short final answer with the key numbers.")

Q3 = "substr(o.order_date,6,2) IN ('07','08','09')"
Q4 = "substr(o.order_date,6,2) IN ('10','11','12')"


def _last(history: list[dict], tool: str) -> dict | None:
    """Most recent result of a given tool."""
    return next((h["result"] for h in reversed(history) if h["tool"] == tool), None)


# =========================================================================== scripted
class ScriptedPlanner:
    """Rule-based planner: classify the question, then follow a fixed playbook."""

    name = "scripted"

    @staticmethod
    def intent(question: str) -> str:
        q = question.lower()
        if any(w in q for w in ["duplicate", "twice", "double"]):
            return "duplicates"
        if "discount" in q:
            return "discounts"
        if any(w in q for w in ["plot", "chart", "graph", "trend"]):
            return "trend_chart"
        if any(w in q for w in ["fell", "drop", "decline", "decrease"]) and "region" in q:
            return "region_drop"
        if "top" in q and "product" in q:
            return "top_products"
        return "unknown"

    def next_action(self, question: str, history: list[dict]) -> dict:
        plan = getattr(self, "_" + self.intent(question))
        return plan(question, history, len(history))

    # -- playbooks: step = how many tool calls have happened so far --------------------
    def _region_drop(self, q, h, step):
        if step == 0:
            return {"tool": "get_schema", "args": {}}
        if step == 1:
            return {"tool": "sql_query", "args": {"query":
                    f"SELECT r.name AS region, SUM(CASE WHEN {Q3} THEN o.revenue END) AS q3, "
                    f"SUM(CASE WHEN {Q4} THEN o.revenue END) AS q4 FROM orders o JOIN regions r "
                    f"USING(region_id) GROUP BY r.name"}}
        if step == 2:
            return {"tool": "python_calc", "args": {"expression":
                    "df.assign(change_pct=(df.q4 - df.q3) / df.q3 * 100).sort_values('change_pct')[['region', 'change_pct']]"}}
        region = _last(h, "python_calc")["rows"][0][0]                       # the worst region
        if step == 3:
            return {"tool": "sql_query", "args": {"query":
                    f"SELECT p.name AS product, SUM(CASE WHEN {Q3} THEN o.revenue ELSE 0 END) AS q3, "
                    f"SUM(CASE WHEN {Q4} THEN o.revenue ELSE 0 END) AS q4, "
                    f"SUM(CASE WHEN {Q4} THEN o.revenue ELSE 0 END) - SUM(CASE WHEN {Q3} THEN o.revenue ELSE 0 END) AS diff "
                    f"FROM orders o JOIN products p USING(product_id) JOIN regions r USING(region_id) "
                    f"WHERE r.name = '{region}' GROUP BY p.name ORDER BY diff ASC LIMIT 3"}}
        products = [r[0] for r in _last(h, "sql_query")["rows"]]
        if step == 4:
            return {"tool": "search_notes", "args": {"query": f"{region} {products[0]} October Q4"}}
        change = _last(h, "python_calc")["rows"][0][1]
        note = (_last(h, "search_notes")["matches"] or [{"file": "none", "text": ""}])[0]
        return {"final": f"{region} had the biggest revenue fall from Q3 to Q4 2025 ({change:.1f}%). "
                         f"The largest product drops were {', '.join(products)}. Likely reason (from {note['file']}): "
                         f"{note['text'].splitlines()[-1][:400]}"}

    def _top_products(self, q, h, step):
        n = int(m.group(1)) if (m := re.search(r"top\s+(\d+)", q.lower())) else 3
        if step == 0:
            return {"tool": "sql_query", "args": {"query":
                    "SELECT p.name AS product, ROUND(SUM(o.revenue), 2) AS revenue FROM orders o "
                    f"JOIN products p USING(product_id) GROUP BY p.name ORDER BY revenue DESC LIMIT {n}"}}
        rows = _last(h, "sql_query")["rows"]
        return {"final": f"Top {n} products by 2025 revenue: " +
                         "; ".join(f"{i}. {r[0]} (${r[1]:,.0f})" for i, r in enumerate(rows, 1))}

    def _trend_chart(self, q, h, step):
        query = ("SELECT substr(order_date,1,7) AS month, ROUND(SUM(revenue), 2) AS revenue FROM orders "
                 "GROUP BY month ORDER BY month")
        if step == 0:
            return {"tool": "make_chart", "args": {"query": query, "x": "month", "y": "revenue", "kind": "line",
                                                   "title": "Monthly revenue 2025"}}
        if step == 1:
            return {"tool": "sql_query", "args": {"query": query}}
        rows = _last(h, "sql_query")["rows"]
        lo, hi = min(rows, key=lambda r: r[1]), max(rows, key=lambda r: r[1])
        return {"final": f"Chart saved to {_last(h, 'make_chart')['path']}. Highest month {hi[0]} (${hi[1]:,.0f}), "
                         f"lowest {lo[0]} (${lo[1]:,.0f})."}

    def _discounts(self, q, h, step):
        if step == 0:
            return {"tool": "sql_query", "args": {"query":
                    "SELECT r.name AS region, substr(o.order_date,1,7) AS month, AVG(o.discount) AS avg_discount "
                    "FROM orders o JOIN regions r USING(region_id) GROUP BY region, month"}}
        if step == 1:
            return {"tool": "python_calc", "args": {"expression":
                    "df.assign(z=(df.avg_discount - df.avg_discount.mean()) / df.avg_discount.std())"
                    ".sort_values('z', ascending=False).head(3)"}}
        top = _last(h, "python_calc")["rows"][0]                             # region, month, avg, z
        if step == 2:
            return {"tool": "search_notes", "args": {"query": f"{top[0]} discount promo {top[1]}"}}
        note = (_last(h, "search_notes")["matches"] or [{"file": "none", "text": ""}])[0]
        return {"final": f"{top[0]} in {top[1]} stands out: average discount {top[2]:.0%} "
                         f"(z-score {top[3]:.1f}, normal is about 4%). Explanation from {note['file']}: "
                         f"{note['text'].splitlines()[-1][:400]}"}

    def _duplicates(self, q, h, step):
        if step == 0:
            return {"tool": "sql_query", "args": {"query":
                    "SELECT o.order_date, r.name AS region, COUNT(*) - COUNT(DISTINCT o.product_id || '-' || o.quantity "
                    "|| '-' || o.discount) AS extra_rows FROM orders o JOIN regions r USING(region_id) "
                    "GROUP BY o.order_date, r.name HAVING extra_rows > 3 ORDER BY extra_rows DESC LIMIT 5"}}
        rows = _last(h, "sql_query")["rows"]
        if not rows:
            return {"final": "No clear duplicate orders found."}
        if step == 1:
            return {"tool": "search_notes", "args": {"query": f"duplicate orders {rows[0][1]} {rows[0][0]}"}}
        note = (_last(h, "search_notes")["matches"] or [{"file": "none", "text": ""}])[0]
        return {"final": f"Yes: {rows[0][0]} in the {rows[0][1]} region has about {rows[0][2]} more rows than distinct "
                         f"orders. Explanation from {note['file']}: {note['text'].splitlines()[-1][:400]}"}

    def _unknown(self, q, h, step):
        return {"final": "The scripted planner only knows 5 question types (region drop, top products, monthly "
                         "chart, discounts, duplicates). Set LLM_PROVIDER to ollama/anthropic/openai for open questions."}


# =========================================================================== LLM planners
def tool_specs() -> list[dict]:
    return [{"name": n, "description": t["description"], "parameters": t["parameters"]} for n, t in TOOLS.items()]


def _short(result: dict, limit: int = 1500) -> str:
    """Tool results can be long; models only need the start."""
    text = json.dumps(result, default=str)
    return text if len(text) <= limit else text[:limit] + " ...(truncated)"


class JsonPlanner:
    """Works with ANY text model: we describe the tools and ask for one JSON object back."""

    name = "json"

    def next_action(self, question: str, history: list[dict]) -> dict:
        from .llm import generate
        tools = "\n".join(f"- {t['name']}({', '.join(t['parameters']['properties'])}): {t['description']}"
                          for t in tool_specs())
        past = "\n".join(f"Step {i}: called {h['tool']}({json.dumps(h['args'])}) -> {_short(h['result'], 600)}"
                         for i, h in enumerate(history, 1)) or "(nothing yet)"
        prompt = (f"Tools:\n{tools}\n\nQuestion: {question}\n\nSo far:\n{past}\n\n"
                  'Reply with ONE JSON object only: {"tool": "<name>", "args": {...}} to call a tool, '
                  'or {"final": "<answer>"} when done.')
        reply = generate(prompt, system=SYSTEM, max_new_tokens=200)
        m = re.search(r"\{.*\}", reply, re.S)
        try:
            action = json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            action = None
        if not isinstance(action, dict) or not ("final" in action or "tool" in action):
            return {"invalid": reply[:300]}              # the loop records this and lets the model retry
        action.setdefault("args", {})
        return action


class AnthropicPlanner:
    """Claude's native tool use: we pass the tool schemas, Claude returns tool_use blocks."""

    name = "anthropic"

    def next_action(self, question: str, history: list[dict]) -> dict:
        from .llm import _real_key
        import anthropic
        client = anthropic.Anthropic(api_key=_real_key("ANTHROPIC_API_KEY"))
        messages = [{"role": "user", "content": question}]
        for i, h in enumerate(history):                  # replay the trajectory in Claude's format
            tid = f"toolu_{i}"
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": tid, "name": h["tool"], "input": h["args"]}]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tid, "content": _short(h["result"])}]})
        resp = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"), max_tokens=800, system=SYSTEM,
            tools=[{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]}
                   for t in tool_specs()],
            messages=messages)
        for block in resp.content:
            if block.type == "tool_use":
                return {"tool": block.name, "args": dict(block.input)}
        return {"final": "".join(b.text for b in resp.content if b.type == "text")}


class OpenAIPlanner:
    """OpenAI's function calling: same idea, slightly different message format."""

    name = "openai"

    def next_action(self, question: str, history: list[dict]) -> dict:
        from .llm import _real_key
        from openai import OpenAI
        client = OpenAI(api_key=_real_key("OPENAI_API_KEY"))
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        for i, h in enumerate(history):
            cid = f"call_{i}"
            messages.append({"role": "assistant", "content": None, "tool_calls": [
                {"id": cid, "type": "function", "function": {"name": h["tool"], "arguments": json.dumps(h["args"])}}]})
            messages.append({"role": "tool", "tool_call_id": cid, "content": _short(h["result"])})
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=messages,
            tools=[{"type": "function", "function": t} for t in tool_specs()])
        msg = resp.choices[0].message
        if msg.tool_calls:
            call = msg.tool_calls[0]
            return {"tool": call.function.name, "args": json.loads(call.function.arguments or "{}")}
        return {"final": msg.content or ""}


class OllamaPlanner:
    """Ollama's /api/chat accepts OpenAI-style tool schemas for models that support tools."""

    name = "ollama"

    def next_action(self, question: str, history: list[dict]) -> dict:
        import httpx
        from .llm import LLMError
        host, model = os.getenv("OLLAMA_HOST", "http://localhost:11434"), os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        for h in history:
            messages.append({"role": "assistant", "content": "",
                             "tool_calls": [{"function": {"name": h["tool"], "arguments": h["args"]}}]})
            messages.append({"role": "tool", "content": _short(h["result"]), "tool_name": h["tool"]})
        try:
            r = httpx.post(f"{host}/api/chat", timeout=180, json={
                "model": model, "messages": messages, "stream": False,
                "tools": [{"type": "function", "function": t} for t in tool_specs()]})
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise LLMError(f"Could not reach Ollama at {host}: {e}") from e
        msg = r.json()["message"]
        if msg.get("tool_calls"):
            fn = msg["tool_calls"][0]["function"]
            args = fn.get("arguments") or {}
            return {"tool": fn["name"], "args": json.loads(args) if isinstance(args, str) else args}
        return {"final": msg.get("content", "")}


def get_planner(name: str | None = None):
    """PLANNER=scripted|llm|auto (default auto: scripted for the local model, native tools otherwise)."""
    from .llm import provider
    name = (name or os.getenv("PLANNER", "auto")).lower()
    prov = provider()
    if name == "scripted" or (name == "auto" and prov == "local"):
        return ScriptedPlanner()
    return {"anthropic": AnthropicPlanner, "openai": OpenAIPlanner, "ollama": OllamaPlanner}.get(prov, JsonPlanner)()
