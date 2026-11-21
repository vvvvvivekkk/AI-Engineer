"""Tests: SQL guard, sandboxed calc, the 5 agent tasks (exact tool sequences), loop safety, MCP server."""
import asyncio
import json
from pathlib import Path

import pytest

from src.agent import run_agent
from src.planners import ScriptedPlanner
from src.run_tasks import check
from src.tools import ToolError, call_tool, check_read_only

ROOT = Path(__file__).resolve().parents[1]
TASKS = json.loads((ROOT / "data" / "tasks.json").read_text())


@pytest.mark.parametrize("q", ["DELETE FROM orders", "SELECT 1; DROP TABLE orders", "PRAGMA table_info(orders)",
                               "UPDATE orders SET revenue = 0", "ATTACH DATABASE 'x.db' AS x",
                               "WITH t AS (SELECT 1) INSERT INTO orders VALUES (1)"])
def test_guard_blocks_writes(q):
    with pytest.raises(ToolError):
        check_read_only(q)


def test_guard_allows_reads():
    assert check_read_only("  select * from regions ; ") == "select * from regions"
    assert call_tool("sql_query", {"query": "SELECT COUNT(*) AS n FROM regions"})["rows"] == [[4]]


def test_database_is_really_read_only():
    # even if the text guard were bypassed, the authorizer refuses writes
    from src.tools import _connect
    with pytest.raises(Exception):
        _connect().execute("DELETE FROM regions")


def test_python_calc_sandbox():
    call_tool("sql_query", {"query": "SELECT name FROM regions"})
    assert call_tool("python_calc", {"expression": "len(df)"})["value"] == 4
    assert "error" in call_tool("python_calc", {"expression": "__import__('os').system('echo hi')"})
    assert "error" in call_tool("python_calc", {"expression": "df.__class__.__bases__"})
    assert "error" in call_tool("python_calc", {"expression": "x = 1"})          # statements not allowed


@pytest.mark.parametrize("task", TASKS, ids=[t["id"] for t in TASKS])
def test_five_tasks_expected_tool_sequences(task):
    rec = run_agent(task["question"], ScriptedPlanner(), log=False)
    res = check(task, rec, strict=True)
    assert res["tools_ok"], rec["tools"]
    assert res["answer_ok"], rec["answer"]


def test_loop_stops_at_max_steps_and_survives_tool_errors():
    class Stubborn:                                   # a planner that keeps calling a broken tool
        name = "stubborn"
        def next_action(self, q, h):
            return {"tool": "sql_query", "args": {"query": "DROP TABLE orders"}}
    rec = run_agent("anything", Stubborn(), max_steps=3, log=False)
    assert len(rec["steps"]) == 3 and "Stopped after 3 steps" in rec["answer"]
    assert all("error" in s["result"] for s in rec["steps"])


def test_invalid_model_replies_give_up_cleanly():
    class Confused:
        name = "confused"
        def next_action(self, q, h):
            return {"invalid": "I think the answer is maybe"}
    rec = run_agent("anything", Confused(), log=False)
    assert "did not return a valid action" in rec["answer"]


def test_mcp_server_lists_and_calls_tools():
    from mcp import Client
    from src.mcp_server import mcp

    async def go():
        async with Client(mcp) as c:
            names = {t.name for t in (await c.list_tools()).tools}
            ok = await c.call_tool("sql_query", {"query": "SELECT COUNT(*) AS n FROM products"})
            bad = await c.call_tool("sql_query", {"query": "DELETE FROM products"})
            return names, ok, bad
    names, ok, bad = asyncio.run(go())
    assert names == {"get_schema", "sql_query", "python_calc", "make_chart", "search_notes"}
    assert not ok.is_error and "10" in ok.content[0].text
    assert bad.is_error and "Only SELECT" in bad.content[0].text
