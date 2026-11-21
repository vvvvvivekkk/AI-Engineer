"""
build.py - regenerates this project's architecture diagram (images/) and Colab notebook.

Run from anywhere:  python 15-projects/p05-rag-course-chatbot/build.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from build_kit import mermaid, notebook  # noqa: E402

PROJECT = "15-projects/p05-rag-course-chatbot"

DIAGRAM = """
flowchart LR
    MD[curriculum *.md files] --> CH[chunk by heading<br/>+ word windows]
    CH --> EM[embed<br/>all-MiniLM-L6-v2]
    EM --> IX[(FAISS index)]
    U[user question] --> RW[rewrite follow-up<br/>using memory]
    RW --> RT[retrieve top-k]
    IX --> RT
    RT --> RR[optional reranker<br/>cross-encoder]
    RR --> AN[answer: LLM or extractive]
    AN --> OUT[answer + citations<br/>file > heading]
    OUT --> UI[CLI or Gradio UI]
"""

GET_CODE = f'''
import os, subprocess, sys
from pathlib import Path

PROJECT = "{PROJECT}"
if Path("main.py").exists() and Path("requirements.txt").exists():
    print("Already inside the project folder - no clone needed.")
elif Path("../../" + PROJECT).exists():
    os.chdir("../../" + PROJECT)          # repo already on disk two levels up
else:
    if not Path("AI-Engineer").exists():  # first run in Colab: download the repo
        subprocess.run(["git", "clone", "--depth", "1",
                        "https://github.com/vvvvvivekkk/AI-Engineer.git"], check=True)
    os.chdir(Path("AI-Engineer") / PROJECT)
print("Working folder:", Path.cwd())
'''

INSTALL = '''
import sys, subprocess
from pathlib import Path
# Only install in Colab. Locally you already did "pip install -r requirements.txt" in a venv.
# Colab ships its own PyTorch, so we skip the torch line to save a big download.
if "google.colab" in sys.modules:
    reqs = [l for l in Path("requirements.txt").read_text().splitlines()
            if l.strip() and not l.startswith(("#", "torch"))]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *reqs], check=True)
    print("installed", len(reqs), "packages")
else:
    print("Not in Colab - skipping install.")
'''


def build():
    mermaid(DIAGRAM, HERE / "images" / "architecture.png")
    notebook([
        ("md", "# P5 quickstart - RAG chatbot over the course notes\n\n"
               "Indexes the curriculum's markdown files with sentence-transformers + FAISS, answers "
               "questions with citations, rewrites follow-ups, and evaluates retrieval. CPU is enough. "
               "First run downloads small Hugging Face models (~90 MB embedder, ~720 MB SmolLM2-360M)."),
        ("md", "## 1. Get the code\nIn Colab this clones the repo. If the project folder already exists, "
               "the clone is skipped."),
        ("code", GET_CODE),
        ("md", "## 2. Install packages (Colab only)"),
        ("code", INSTALL),
        ("md", "## 3. Build the index over every markdown file in the repo\n"
               "Each file is cut into chunks by heading; each chunk becomes a 384-number embedding in FAISS."),
        ("code", "!{sys.executable} main.py index"),
        ("md", "## 4. Ask questions - extractive mode (no LLM, instant)\n"
               "The answer quotes the best-matching sentences and cites file > heading."),
        ("code", "from src.index import get_index\n"
                 "from src.chat import RAGChatbot\n"
                 "from src import config\n"
                 "vi = get_index(folder=config.INDEX_DIR / 'repo')\n"
                 "bot = RAGChatbot(vi, answer_mode='extractive')\n"
                 "for q in ['What is a virtual environment?', 'Why should I use one?']:\n"
                 "    a = bot.ask(q)\n"
                 "    print('Q:', q, '| searched for:', a.standalone)\n"
                 "    print(a.formatted(), end='\\n\\n')"),
        ("md", "## 5. The same with a local LLM writing the answer\n"
               "SmolLM2-360M runs on CPU (slow-ish, 10 s to a few minutes). Its answers read well but "
               "can add unsupported claims; the sources list is always shown so you can check. "
               "Set LLM_PROVIDER in .env to use Ollama, Claude or OpenAI instead."),
        ("code", "bot_llm = RAGChatbot(vi, answer_mode='llm')\n"
                 "print(bot_llm.ask('What is retrieval-augmented generation?').formatted())"),
        ("md", "## 6. Evaluate: two chunk sizes x reranker off/on\nUses the committed sample docs and FAQ, "
               "so numbers are repeatable."),
        ("code", "!{sys.executable} main.py eval"),
        ("md", "## 7. Run the tests"),
        ("code", "!{sys.executable} -m pytest -q"),
        ("md", "## 8. Web UI (Colab only)\nStarts Gradio with a public share link. Locally run `python app.py` "
               "instead."),
        ("code", "if 'google.colab' in sys.modules:\n"
                 "    os.environ['GRADIO_SHARE'] = 'true'\n"
                 "    !{sys.executable} app.py\n"
                 "else:\n"
                 "    print('Locally: run  python app.py  and open http://127.0.0.1:7860')"),
    ], HERE / "colab_quickstart.ipynb")
    print("built diagram + notebook")


if __name__ == "__main__":
    build()
