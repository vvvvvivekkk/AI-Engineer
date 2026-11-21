"""
Solution to exercise 10: check_env_plus.py

Adds three things to code/check_env.py:
  1. warns if .env exists here but .gitignore does not list it
  2. checks GROQ_API_KEY too
  3. a --json option that prints machine-readable results (never key values)

Run from the 00-setup folder:
    python solutions/check_env_plus.py
    python solutions/check_env_plus.py --json
"""
import argparse                                    # reads --json from the command line
import importlib.metadata as meta                  # installed package versions
import json                                        # turns a Python dict into JSON text
import os                                          # environment variables
import sys                                         # Python version and venv info
from pathlib import Path                           # file paths

KEY_NAMES = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "HF_TOKEN",
             "GROQ_API_KEY"]                       # change 2: the new key name
PACKAGES = ["pip", "python-dotenv", "numpy", "pandas"]


def key_status(value):
    """Describe a key without revealing it."""
    if value is None:
        return "NOT SET"
    if value.strip() == "" or "your-key-here" in value:
        return "EMPTY_OR_PLACEHOLDER"
    return "set"


def gitignore_protects_env(folder):
    """Change 1: True if .gitignore in `folder` lists .env (simple line match)."""
    gi = folder / ".gitignore"
    if not gi.exists():                            # no .gitignore at all = not protected
        return False
    lines = [l.strip() for l in gi.read_text(encoding="utf-8").splitlines()]
    return any(l in (".env", "*.env", ".env*") for l in lines)


def collect():
    """Gather every result into one dictionary."""
    try:
        from dotenv import load_dotenv             # load .env if the package exists
        load_dotenv(Path.cwd() / ".env")
    except ImportError:
        pass
    here = Path.cwd()
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = meta.version(name)
        except meta.PackageNotFoundError:
            packages[name] = None                  # JSON will show null for missing
    env_exists = (here / ".env").exists()
    return {
        "python": ".".join(map(str, sys.version_info[:3])),
        "in_venv": sys.prefix != sys.base_prefix,
        "packages": packages,
        "keys": {k: key_status(os.getenv(k)) for k in KEY_NAMES},
        "env_file_exists": env_exists,
        "env_file_unprotected": env_exists and not gitignore_protects_env(here),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print results as JSON")  # change 3
    args = parser.parse_args()
    results = collect()
    if args.json:
        print(json.dumps(results, indent=2))       # values of keys are never in `results`
        return
    print(f"Python {results['python']}  (venv active: {results['in_venv']})")
    for name, version in results["packages"].items():
        print(f"  {name:<14} {version or 'missing'}")
    for name, status in results["keys"].items():
        print(f"  {name:<18} {status}")
    if results["env_file_unprotected"]:
        print("WARNING: .env exists here but .gitignore does not list it. Add '.env' to .gitignore now!")


if __name__ == "__main__":
    main()
