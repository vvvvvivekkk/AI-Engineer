"""
check_env.py - a friendly health check for your Python setup.

What it reports:
  1. Which Python you are running (version and location on disk)
  2. Whether you are inside a virtual environment (a "venv")
  3. Which of the course's key packages are installed, and their versions
  4. Whether each API key is set - WITHOUT ever printing the key itself
  5. Whether a GPU is visible (only if PyTorch is installed)

How to run it (from the 00-setup folder, with your venv activated):
    python code/check_env.py          # normal report
    python code/check_env.py --all    # also list every installed package

It only uses Python's standard library, so it works even on a brand-new install.
If python-dotenv is installed, it also reads a .env file first.
"""

# --- Imports: tools that come with Python itself (the "standard library") ---
import argparse                     # reads options typed after the script name, like --all
import importlib.metadata as meta   # asks Python which packages are installed and their versions
import os                           # gives access to environment variables
import platform                     # tells us the operating system (Windows / macOS / Linux)
import sys                          # information about the running Python itself

# The oldest Python version this course supports, written as (major, minor).
MIN_PYTHON = (3, 10)

# Packages the course uses. The left side is the name you pip-install,
# the right side is a short plain-English reason we need it.
KEY_PACKAGES = {
    "pip": "installs other packages",
    "python-dotenv": "loads API keys from a .env file",
    "jupyterlab": "local notebooks in the browser",
    "notebook": "classic Jupyter notebook interface",
    "ipykernel": "lets Jupyter / VS Code run Python cells",
    "numpy": "fast number arrays (module 02)",
    "pandas": "tables of data (module 02)",
    "matplotlib": "charts (module 02)",
    "scikit-learn": "classic machine learning (module 04)",
    "torch": "deep learning (module 05)",
    "transformers": "Hugging Face models (module 06)",
}

# Environment variable names for API keys used later in the course.
KEY_NAMES = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "HF_TOKEN"]

# Text that means "someone left the template value in place" (see .env.example).
PLACEHOLDER_HINTS = ("your-key-here", "your-token-here", "paste", "changeme", "xxx")


def heading(text):
    """Print a section title with a line under it, so the report is easy to scan."""
    print()                         # blank line before each section
    print(text)                     # the title itself
    print("-" * len(text))          # a row of dashes as long as the title


def try_load_dotenv():
    """Load a .env file if python-dotenv is installed. Returns a short status message."""
    try:
        from dotenv import find_dotenv, load_dotenv   # only works if the package is installed
    except ImportError:                                # the package is missing
        return "python-dotenv not installed - skipped reading .env"
    path = find_dotenv(usecwd=True)                   # look for .env from the current folder upwards
    if not path:                                       # an empty string means no file was found
        return "no .env file found (that is fine if you set keys another way)"
    load_dotenv(path)                                  # copy NAME=value lines into the environment
    return f"loaded variables from {path}"


def check_python():
    """Report the Python version and whether it is new enough."""
    heading("1. Python")
    version = sys.version_info                         # e.g. (3, 12, 4, 'final', 0)
    print(f"Version     : {version.major}.{version.minor}.{version.micro}")
    print(f"Executable  : {sys.executable}")           # the exact python program running this file
    print(f"OS          : {platform.system()} {platform.release()}")
    ok = (version.major, version.minor) >= MIN_PYTHON  # compare as tuples: (3, 12) >= (3, 10)
    if ok:
        print("Status      : OK")
    else:
        print(f"Status      : TOO OLD - please install Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer")
    return ok


def check_venv():
    """Report whether we are inside a virtual environment."""
    heading("2. Virtual environment")
    # Inside a venv, sys.prefix points at the venv folder,
    # while sys.base_prefix still points at the original Python install.
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print(f"Active venv : {sys.prefix}")
    else:
        print("Active venv : none (packages go into your main Python install)")
        print("Tip         : create one with  python -m venv .venv  and activate it")
    if "google.colab" in sys.modules or os.getenv("COLAB_RELEASE_TAG"):
        print("Note        : running in Google Colab - venvs are not needed there")
    return in_venv


def check_packages(show_all):
    """Report which key packages are installed."""
    heading("3. Packages")
    missing = []                                       # we collect missing names here
    for name, why in KEY_PACKAGES.items():             # loop over every (name, reason) pair
        try:
            version = meta.version(name)               # raises an error if not installed
            print(f"  [ok]      {name:<15} {version:<12} {why}")
        except meta.PackageNotFoundError:
            print(f"  [missing] {name:<15} {'-':<12} {why}")
            missing.append(name)
    # Count every installed package (distribution) in this environment.
    installed = sorted({d.metadata["Name"] for d in meta.distributions() if d.metadata["Name"]},
                       key=str.lower)
    print(f"\nTotal packages installed in this environment: {len(installed)}")
    if missing:
        print("Install missing ones with:  python -m pip install " + " ".join(missing))
    if show_all:                                       # only when the user typed --all
        print("\nAll installed packages:")
        for pkg in installed:
            print(f"  {pkg}=={meta.version(pkg)}")
    return missing


def describe_key(value):
    """Return a SAFE description of a key's value. Never returns the value itself."""
    if value is None:                                  # variable does not exist at all
        return "NOT SET"
    if value.strip() == "":                            # exists but is empty
        return "EMPTY"
    if any(hint in value.lower() for hint in PLACEHOLDER_HINTS):
        return "PLACEHOLDER (still the template text - paste your real key)"
    return "set"                                       # we deliberately say nothing more


def check_keys():
    """Report whether each API key is set, without printing it."""
    heading("4. API keys (values are never shown)")
    print(f"  {try_load_dotenv()}")
    results = {}
    for name in KEY_NAMES:
        status = describe_key(os.getenv(name))         # os.getenv returns None if missing
        results[name] = status
        print(f"  {name:<18} {status}")
    print("  Missing keys are fine for now: course notebooks fall back to offline stand-ins.")
    return results


def check_gpu():
    """Report whether PyTorch can see a GPU (skipped if PyTorch is not installed)."""
    heading("5. GPU")
    try:
        import torch                                   # only works if PyTorch is installed
    except ImportError:
        print("  PyTorch not installed - skipped")
        return None
    if torch.cuda.is_available():                      # an NVIDIA GPU with working drivers
        print(f"  CUDA GPU    : {torch.cuda.get_device_name(0)}")
        return True
    mps = getattr(torch.backends, "mps", None)         # Apple Silicon GPU support
    if mps is not None and mps.is_available():
        print("  Apple GPU (MPS) available")
        return True
    print("  No GPU found - CPU only (fine for most modules; use Colab for GPU work)")
    return False


def main():
    """Run every check in order and print a one-line summary at the end."""
    parser = argparse.ArgumentParser(description="Check your Python setup for the course.")
    parser.add_argument("--all", action="store_true", help="list every installed package")
    args = parser.parse_args()                         # read what the user typed

    print("AI Engineer course - environment check")
    py_ok = check_python()
    check_venv()
    missing = check_packages(args.all)
    check_keys()
    check_gpu()

    heading("Summary")
    if py_ok and not missing:
        print("Everything needed is installed. You are ready to go!")
    elif py_ok:
        print(f"Python is fine. {len(missing)} package(s) missing - see section 3.")
    else:
        print("Please upgrade Python first - see section 1.")


# This line means: only run main() when the file is run directly,
# not when another file imports it.
if __name__ == "__main__":
    main()
