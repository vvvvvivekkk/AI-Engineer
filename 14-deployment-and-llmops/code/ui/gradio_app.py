"""
gradio_app.py - the same chat UI built with Gradio.

Gradio builds the web page from a Python function: you say "my function takes
a message and the history, and returns a reply" and Gradio draws the chat box.
It is popular for ML demos and is what Hugging Face Spaces use.

Run:   pip install -r ../requirements-ui.txt
       python gradio_app.py            -> open http://127.0.0.1:7860
Add share=True to demo.launch() to get a temporary public link (careful: anyone with it can use your app).
"""
import os
import httpx
import gradio as gr          # "gr" is the usual nickname

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def respond(message: str, history: list) -> str:
    """Gradio calls this with the new message and the past conversation; we return the reply text."""
    try:
        r = httpx.post(f"{API_URL}/chat", json={"message": message}, timeout=30)
        if r.status_code == 200:
            return r.json()["reply"]
        return f"API error {r.status_code}: {r.json().get('detail')}"
    except httpx.HTTPError:
        return f"(API offline - local echo) {message}"


# ChatInterface = a ready-made chat page around our function.
demo = gr.ChatInterface(
    fn=respond,
    title="LLM Chat (module 14 demo)",
    description=f"Calls the FastAPI backend at {API_URL}",
    examples=["What is Docker?", "Explain an API to a 10-year-old"],
)

if __name__ == "__main__":         # only launch the server when run directly, not when imported
    demo.launch(server_name="127.0.0.1", server_port=7860)
