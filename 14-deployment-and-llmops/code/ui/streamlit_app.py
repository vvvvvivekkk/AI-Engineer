"""
streamlit_app.py - a chat web page in about 40 lines, using Streamlit.

Streamlit re-runs this whole script from top to bottom every time the user
does something (types, clicks). st.session_state keeps data between those re-runs.

Run:   pip install -r ../requirements-ui.txt
       streamlit run streamlit_app.py
It calls our FastAPI service at API_URL. If the API is not running,
it falls back to a local offline reply so the page still works in class.
"""
import os
import httpx                 # HTTP client: sends requests to our API
import streamlit as st       # the UI library; "st" is the usual nickname

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")   # where the FastAPI app lives

st.set_page_config(page_title="LLM Chat", page_icon="💬")
st.title("LLM Chat (module 14 demo)")
st.caption(f"Backend: {API_URL}")

if "history" not in st.session_state:          # first run: create an empty chat history
    st.session_state.history = []

for role, text in st.session_state.history:    # redraw earlier messages on every re-run
    with st.chat_message(role):
        st.write(text)


def ask_api(message: str) -> str:
    """Send the message to POST /chat. Return the reply or a friendly error."""
    try:
        r = httpx.post(f"{API_URL}/chat", json={"message": message}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return f"{data['reply']}\n\n_{data['latency_ms']} ms, {data['output_tokens']} output tokens_"
        return f"API error {r.status_code}: {r.json().get('detail')}"
    except httpx.HTTPError:                     # API not running: offline fallback
        return f"(API offline - local echo) {message}"


prompt = st.chat_input("Ask something")        # the text box at the bottom of the page
if prompt:                                     # only true on the re-run right after the user presses Enter
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.write(prompt)
    reply = ask_api(prompt)
    st.session_state.history.append(("assistant", reply))
    with st.chat_message("assistant"):
        st.write(reply)

with st.sidebar:                               # a side panel showing live metrics from the API
    st.header("Metrics")
    if st.button("Refresh"):
        try:
            st.json(httpx.get(f"{API_URL}/metrics", timeout=5).json())
        except httpx.HTTPError:
            st.warning("API not reachable")
