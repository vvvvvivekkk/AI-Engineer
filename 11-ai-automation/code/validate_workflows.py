"""
validate_workflows.py - checks that the n8n workflow JSON files in ../workflows are well formed.

n8n imports a workflow from a JSON file with (at least):
  name         : the workflow's title
  nodes        : list of steps; each has id, name, type, typeVersion, position [x, y], parameters
  connections  : which node's output goes to which node's input, keyed by the SOURCE node's NAME

This script catches the mistakes that make an import fail or a workflow silently break:
missing keys, duplicate node names, connections pointing at nodes that don't exist,
no trigger node, nodes nobody connects to, and secrets accidentally pasted in.

Run: python validate_workflows.py
"""
import json
import re
import sys
from pathlib import Path

WF_DIR = Path(__file__).resolve().parents[1] / "workflows"
NODE_KEYS = {"id", "name", "type", "typeVersion", "position", "parameters"}
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_\-]{30,})")


def is_trigger(node_type: str) -> bool:
    """n8n trigger node types end in 'Trigger' or are the webhook node."""
    return node_type.endswith("Trigger") or node_type == "n8n-nodes-base.webhook"


def validate(wf: dict) -> list[str]:
    errors = []
    for key in ("name", "nodes", "connections"):
        if key not in wf:
            errors.append(f"missing top-level key '{key}'")
    if errors:
        return errors
    names = [n.get("name") for n in wf["nodes"]]
    if len(names) != len(set(names)):
        errors.append("duplicate node names (connections use names, so they must be unique)")
    for n in wf["nodes"]:
        missing = NODE_KEYS - n.keys()
        if missing:
            errors.append(f"node '{n.get('name')}' missing {sorted(missing)}")
        if not str(n.get("type", "")).startswith(("n8n-nodes-base.", "@n8n/")):
            errors.append(f"node '{n.get('name')}' has unexpected type {n.get('type')}")
    if not any(is_trigger(n["type"]) for n in wf["nodes"]):
        errors.append("no trigger node - the workflow could never start by itself")
    targets = set()
    for src, outputs in wf["connections"].items():
        if src not in names:
            errors.append(f"connection from unknown node '{src}'")
        for branch in outputs.get("main", []):
            for link in branch or []:
                if link["node"] not in names:
                    errors.append(f"connection from '{src}' to unknown node '{link['node']}'")
                targets.add(link["node"])
    for n in wf["nodes"]:
        if not is_trigger(n["type"]) and n["name"] not in targets:
            errors.append(f"node '{n['name']}' is never reached (nothing connects to it)")
    if SECRET_RE.search(json.dumps(wf)):
        errors.append("looks like a real API key/token is inside the file - remove it!")
    return errors


def main() -> int:
    bad = 0
    for path in sorted(WF_DIR.glob("*.json")):
        wf = json.loads(path.read_text(encoding="utf-8"))
        errs = validate(wf)
        status = "OK " if not errs else "BAD"
        print(f"[{status}] {path.name}: {len(wf.get('nodes', []))} nodes")
        for e in errs:
            print("      -", e)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
