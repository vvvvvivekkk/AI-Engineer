"""
course_meta.py - one place that describes the course structure.

Used by tools/build_readme.py (root README + module navigation bars) and
tools/build_pdfs.py (course book + handouts), so names, order and icons
stay the same everywhere.
"""

REPO = "vvvvvivekkk/AI-Engineer"

# Four phases (= "Parts" in the course book PDF)
PHASES = [
    ("I", "Foundations", "🧱", "Get set up, learn Python, handle data and build maths intuition."),
    ("II", "Machine Learning, Deep Learning & NLP", "🧠", "Train models, build neural networks and understand how machines read text."),
    ("III", "LLM & GenAI Engineering", "🤖", "Use LLMs well: prompts, RAG, agents and automation."),
    ("IV", "Data, Fine-tuning, Production & Careers", "🚀", "Make models better, ship them safely and get hired."),
]

# folder, icon, short title, phase index, weeks, plain-English summary, everyday analogy
MODULES = [
    ("00-setup", "🛠️", "Setup", 0, "1",
     "Install the tools every AI engineer uses: Python, VS Code, Jupyter, Google Colab, Git/GitHub, virtual environments, pip and safe API keys.",
     "Setting up a kitchen before you cook: stove, knives, fridge, and a locked drawer for the house keys."),
    ("01-python-basics", "🐍", "Python Basics", 0, "2–3",
     "Write real programs: variables, strings, lists, dictionaries, if/else, loops, functions, errors, files and classes.",
     "Learning the alphabet and grammar of a new language before writing essays."),
    ("02-python-for-data", "📊", "Python for Data", 0, "4–5",
     "Load, clean, summarise and chart data with NumPy, pandas and matplotlib, and read and write CSV and Excel files.",
     "Turning a messy pile of receipts into a tidy spreadsheet with charts."),
    ("03-math-for-ai", "📐", "Math for AI", 0, "6",
     "Intuition (no proofs) for vectors, dot products, matrices, probability, softmax, derivatives and gradient descent.",
     "Gradient descent is walking downhill in fog: feel the slope, take a small step, repeat."),
    ("04-machine-learning", "🎯", "Machine Learning", 1, "7–8",
     "Teach computers from examples with scikit-learn: regression, classification, trees, clustering, metrics and cross-validation.",
     "A new employee learning used-car prices by studying 500 past sales."),
    ("05-deep-learning", "🧬", "Deep Learning", 1, "9–10",
     "Build neural networks in PyTorch: neurons, layers, loss, backpropagation, the training loop and CNNs for images.",
     "Each neuron is a tiny weighted vote; stack many layers and simple votes become smart decisions."),
    ("06-nlp-and-transformers", "💬", "NLP & Transformers", 1, "11–12",
     "How machines read text: tokens, embeddings, attention, the transformer, and Hugging Face models.",
     "Attention is a reader deciding which earlier words to look back at to understand the current one."),
    ("07-llms-and-genai", "✨", "LLMs & GenAI", 2, "13",
     "What LLMs really do (next-token prediction), sampling, context windows, calling OpenAI/Anthropic/Gemini APIs, cost, and local models with Ollama.",
     "An extremely well-read autocomplete that predicts the next word, one word at a time."),
    ("08-prompt-and-context-engineering", "📝", "Prompt & Context Engineering", 2, "14",
     "Write prompts that work and prove it: structure, examples, structured output, system prompts, context design, injection defence and lessons from real AI products.",
     "Briefing a smart new intern: clear role, task, examples and the format you want back."),
    ("09-rag", "🔎", "RAG (Retrieval-Augmented Generation)", 2, "15–16",
     "Let an LLM answer from your own documents: chunking, embeddings, vector databases, hybrid search, reranking, citations and evaluation.",
     "An open-book exam: a librarian finds the right pages, then the student writes the answer and cites them."),
    ("10-agentic-ai", "🦾", "Agentic AI", 2, "17–18",
     "LLMs that take actions: tool calling, the ReAct loop, LangGraph, CrewAI, multi-agent teams, memory and the Model Context Protocol (MCP).",
     "An intern at a desk who decides each next step and asks the receptionist (your code) to make the calls."),
    ("11-ai-automation", "⚙️", "AI Automation", 2, "19",
     "Automate business workflows with n8n, webhooks and Python, and learn when browser and computer-use agents are worth it.",
     "A factory conveyor belt: fixed, reliable steps, with an AI worker at the stations that need judgement."),
    ("12-data-annotation-and-rlhf", "🏷️", "Data Annotation & RLHF", 3, "20",
     "Create high-quality labelled data, measure agreement, understand RLHF and DPO, run evals, and get AI-trainer work.",
     "Marking exam papers with a shared answer key so every marker grades the same way."),
    ("13-fine-tuning", "🎛️", "Fine-tuning (LoRA / QLoRA)", 3, "21",
     "When and how to fine-tune: SFT datasets, LoRA, quantisation, QLoRA and evaluating the result.",
     "LoRA is sticky notes on a textbook: you add small notes instead of reprinting the whole book."),
    ("14-deployment-and-llmops", "🚢", "Deployment & LLMOps", 3, "22–23",
     "Ship AI apps: FastAPI, Docker, Streamlit/Gradio, vLLM, Langfuse tracing, monitoring, guardrails, CI/CD and secrets.",
     "Opening a restaurant: a menu (API), a kitchen in a box (Docker), a doorman (guardrails) and a manager watching the numbers (monitoring)."),
    ("15-projects", "🏗️", "Projects", 3, "throughout",
     "Ten portfolio projects from a beginner classifier to a fine-tuned model, each with an architecture diagram and interview guide.",
     "Practice matches: you learn the rules in class, but you become a player on the field."),
    ("16-careers", "💼", "Careers", 3, "24",
     "Pick a role (AI trainer, AI engineer, ML engineer and more), build a portfolio, write a resume, and prepare for interviews.",
     "Packing your bag for the journey: proof of skills, a clear story, and practice answers."),
]

PROJECTS = [
    ("p01-ml-classifier-pipeline", "ML classifier pipeline", "🟢 Beginner", "04"),
    ("p02-regression-and-segmentation", "Regression & customer segmentation", "🟢 Beginner", "04"),
    ("p03-digit-recognizer-cnn", "Digit recogniser (CNN)", "🟢→🟡", "05"),
    ("p04-sentiment-classic-vs-neural", "Sentiment: classic vs neural", "🟡 Intermediate", "06"),
    ("p05-rag-course-chatbot", "RAG chatbot over this course", "🟡 Intermediate", "09"),
    ("p06-response-rating-tool", "Response-rating & eval tool", "🟡 Intermediate", "12"),
    ("p07-doc-qa-api", "Document Q&A API (FastAPI + Docker)", "🟡→🔴", "09 + 14"),
    ("p08-data-analyst-agent-mcp", "Data-analyst agent + MCP server", "🔴 Advanced", "10"),
    ("p09-support-inbox-automation", "Support-inbox automation", "🔴 Advanced", "11"),
    ("p10-finetune-lora-dpo", "Fine-tune: LoRA SFT + DPO", "🔴 Advanced", "13"),
]
