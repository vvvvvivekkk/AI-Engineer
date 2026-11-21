"""
react_agent.py - a ReAct agent loop written from scratch in plain Python.

ReAct = "Reason + Act". The model alternates:
    Thought:      what it thinks it should do next
    Action:       which tool to call, with which input
    Observation:  what the tool returned (written by OUR code, not the model)
...until it writes "Final Answer: ...".

So that this runs with no internet and no API key, the "LLM" here is a
ScriptedLLM: it returns pre-written replies one by one. The LOOP is real -
swap ScriptedLLM for a real model and nothing else has to change.

Run:  python react_agent.py
"""
import re  # regular expressions: used to pull "Action: tool[input]" out of text

# ---------------------------------------------------------------------------
# Tools: plain Python functions the agent may use.
# ---------------------------------------------------------------------------
def calculator(expression: str) -> str:
    """Evaluate simple arithmetic like '17 * 23'. Only digits and + - * / ( ) . allowed."""
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):   # refuse anything that is not arithmetic
        return "Error: only arithmetic is allowed"
    return str(eval(expression))                           # safe here because we filtered the input


def search_notes(query: str) -> str:
    """Look things up in a tiny fake knowledge base."""
    kb = {
        "taipei 101 height": "Taipei 101 is 508 metres tall.",
        "eiffel tower height": "The Eiffel Tower is about 330 metres tall.",
    }
    for key, value in kb.items():                          # very simple keyword match
        if all(word in key for word in query.lower().split()):
            return value
    return "No result found."


TOOLS = {"calculator": calculator, "search_notes": search_notes}  # name -> function

SYSTEM_PROMPT = """You are a helpful agent. Use this format:
Thought: <your reasoning>
Action: <tool name>[<tool input>]
...you will then receive...
Observation: <tool result>
Repeat as needed. When done, write:
Final Answer: <answer>
Tools: calculator[expression], search_notes[query]"""


# ---------------------------------------------------------------------------
# The fake LLM. A real LLM would read the whole transcript and write the next step.
# ---------------------------------------------------------------------------
class ScriptedLLM:
    def __init__(self, replies):
        self.replies = list(replies)                       # copy so we can pop from it

    def __call__(self, transcript: str) -> str:            # same "text in, text out" shape as a real LLM
        return self.replies.pop(0) if self.replies else "Final Answer: I am out of ideas."


# ---------------------------------------------------------------------------
# The loop itself - this is the important part.
# ---------------------------------------------------------------------------
ACTION_RE = re.compile(r"Action:\s*(\w+)\[(.*)\]")         # matches e.g. Action: calculator[2+2]


def run_agent(question: str, llm, max_steps: int = 6, verbose: bool = True) -> str:
    transcript = f"{SYSTEM_PROMPT}\n\nQuestion: {question}\n"  # everything the model has seen so far
    for step in range(1, max_steps + 1):                   # hard limit stops endless loops
        reply = llm(transcript)                            # 1. ask the model for the next step
        transcript += reply + "\n"                         # remember what it said
        if verbose:
            print(f"--- step {step} ---\n{reply}")
        if "Final Answer:" in reply:                       # 2. finished?
            return reply.split("Final Answer:", 1)[1].strip()
        match = ACTION_RE.search(reply)                    # 3. find the requested action
        if not match:
            observation = "Error: I could not find an Action. Use Action: tool[input]."
        else:
            name, arg = match.group(1), match.group(2)
            tool = TOOLS.get(name)                         # 4. look the tool up
            observation = tool(arg) if tool else f"Error: unknown tool '{name}'"
        transcript += f"Observation: {observation}\n"      # 5. feed the result back
        if verbose:
            print(f"Observation: {observation}")
    return "Stopped: reached max_steps without a final answer."


if __name__ == "__main__":
    script = [
        "Thought: I need the height of Taipei 101 first.\nAction: search_notes[taipei 101 height]",
        "Thought: It is 508 m. The Eiffel Tower height is next.\nAction: search_notes[eiffel tower height]",
        "Thought: Now I subtract.\nAction: calculator[508 - 330]",
        "Thought: The difference is 178 m.\nFinal Answer: Taipei 101 is about 178 metres taller than the Eiffel Tower.",
    ]
    answer = run_agent("How much taller is Taipei 101 than the Eiffel Tower?", ScriptedLLM(script))
    print("\nANSWER:", answer)
