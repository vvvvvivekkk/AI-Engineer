"""
app.py - a small web chat UI built with Gradio (pip install gradio).

    python app.py          # then open http://127.0.0.1:7860 in your browser
In Colab, set share=True below (or run with GRADIO_SHARE=true) to get a public link.
"""
import os

import gradio as gr

from src import config
from src.chat import RAGChatbot
from src.index import get_index

docs = config.DOCS
bot = RAGChatbot(get_index(docs=docs, folder=config.INDEX_DIR / (docs if docs in ("repo", "sample") else "custom")))


def respond(message: str, history: list) -> str:
    """Gradio calls this for every message. Our bot keeps its own short memory."""
    if not history:          # a fresh conversation in the UI -> clear the bot's memory too
        bot.reset()
    ans = bot.ask(message)
    note = f"\n\n_(searched for: {ans.standalone})_" if ans.standalone != message else ""
    return ans.formatted() + note


demo = gr.ChatInterface(
    respond,
    title="Course notes chatbot (RAG)",
    description="Answers questions about the AI Engineer curriculum and cites file > heading.",
    examples=["What is RAG?", "How do I evaluate it?", "What is overfitting?", "Where should I keep my API key?"],
)

if __name__ == "__main__":
    demo.launch(share=os.getenv("GRADIO_SHARE", "false").lower() == "true")
