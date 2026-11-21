"""
llm_judge.py - grade an answer against a rubric with an LLM, with an offline fallback.

* If ANTHROPIC_API_KEY is set (in your environment or a .env file), it calls Claude.
* Otherwise it uses a clearly-labelled OFFLINE stand-in made of simple rules.

Run:  python code/llm_judge.py
"""
import json                                          # build and parse JSON
import os                                            # read environment variables
import re                                            # find the JSON block in the reply

try:
    from dotenv import load_dotenv                   # optional: read keys from a .env file
    load_dotenv()
except ImportError:
    pass

RUBRIC = {                                           # binary criteria: easier to agree on
    "correct": "Contains the key fact from the reference and nothing false.",
    "answers_question": "Directly addresses what was asked.",
    "concise": "No padding or repetition.",
}


def offline_judge(question, reference, answer):
    """OFFLINE STAND-IN - keyword rules, not intelligence. Used only when no API key exists."""
    words = answer.lower().split()
    return {
        "correct": reference.lower() in answer.lower(),       # does it mention the key fact?
        "answers_question": len(words) >= 2,                  # at least a real sentence
        "concise": len(words) <= 25,                          # short enough
    }


def claude_judge(question, reference, answer, model="claude-sonnet-4-5"):
    """Real LLM-as-judge call. The model name is an example - check Anthropic's docs."""
    import anthropic                                 # pip install anthropic
    client = anthropic.Anthropic()                   # reads ANTHROPIC_API_KEY automatically
    prompt = (
        "You are a strict grader. Use the rubric. Reply with JSON only, "
        f"keys {list(RUBRIC)} and true/false values.\n"
        f"Rubric: {json.dumps(RUBRIC)}\nQuestion: {question}\n"
        f"Reference answer: {reference}\nAnswer to grade: {answer}"
    )
    msg = client.messages.create(model=model, max_tokens=200,
                                 messages=[{"role": "user", "content": prompt}])
    text = msg.content[0].text                       # the judge's reply as text
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))  # pull out the JSON part


def judge(question, reference, answer):
    """Pick the real judge if a key exists, otherwise the offline stand-in."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return claude_judge(question, reference, answer)
    return offline_judge(question, reference, answer)


if __name__ == "__main__":
    print("judge:", "Claude" if os.getenv("ANTHROPIC_API_KEY") else "OFFLINE stand-in")
    print(judge("Name the largest planet.", "Jupiter", "Saturn is the largest planet."))
    print(judge("What does CPU stand for?", "central processing unit", "Central Processing Unit."))
