"""
tool_formats.py - the SAME tool described for OpenAI and for Anthropic, side by side.

What this script teaches
------------------------
A "tool" (also called a "function") is a normal Python function that we let the
model ask us to run. The model never runs code itself. It only writes a small JSON
message that says "please call get_weather with city='Taipei'". Our code runs the
function and sends the answer back.

To let the model know a tool exists, we describe it with a JSON Schema
(a standard way to describe the shape of JSON data: which fields, which types,
which are required).

OpenAI and Anthropic want almost the same description, wrapped slightly differently.

How to run
----------
    python tool_formats.py                 # offline: prints the formats + a fake round trip
    OPENAI_API_KEY=... python tool_formats.py      # also makes a real OpenAI call
    ANTHROPIC_API_KEY=... python tool_formats.py   # also makes a real Anthropic call

Model names change often. As of late 2026 check the official model pages:
  https://platform.openai.com/docs/models
  https://platform.claude.com/docs/en/about-claude/models/overview
and set OPENAI_MODEL / ANTHROPIC_MODEL in your .env file.
"""
import json  # turns Python dicts into JSON text and back
import os    # lets us read environment variables such as API keys

# ---------------------------------------------------------------------------
# 1. The real Python function (the "tool").
# ---------------------------------------------------------------------------
def get_weather(city: str, unit: str = "celsius") -> dict:
    """Pretend weather service. A real one would call a weather API."""
    fake_data = {"taipei": 24, "hyderabad": 31, "london": 9}   # tiny fake database
    temp_c = fake_data.get(city.lower(), 20)                    # default 20 if unknown city
    temp = temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32)  # convert if asked
    return {"city": city, "temperature": temp, "unit": unit}    # the tool's answer


# A registry: tool name (text the model will send) -> Python function to run.
TOOLS = {"get_weather": get_weather}

# ---------------------------------------------------------------------------
# 2. The JSON Schema for the function's arguments. Shared by both providers.
# ---------------------------------------------------------------------------
WEATHER_PARAMS = {
    "type": "object",                                  # the arguments form one JSON object
    "properties": {                                    # ...with these fields
        "city": {"type": "string", "description": "City name, e.g. Taipei"},
        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"],  # only these 2 values allowed
                 "description": "Temperature unit"},
    },
    "required": ["city"],                              # city must always be given
}

# ---------------------------------------------------------------------------
# 3. The two wrappers.
# ---------------------------------------------------------------------------
# OpenAI Chat Completions API: {"type": "function", "function": {name, description, parameters}}
OPENAI_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current temperature for a city.",
        "parameters": WEATHER_PARAMS,                  # <- the schema lives under "parameters"
    },
}
# (OpenAI's newer Responses API flattens this: {"type": "function", "name": ..., "parameters": ...})

# Anthropic Messages API: {name, description, input_schema}
ANTHROPIC_TOOL = {
    "name": "get_weather",
    "description": "Get the current temperature for a city.",
    "input_schema": WEATHER_PARAMS,                    # <- same schema, called "input_schema"
}


def show_formats() -> None:
    """Print both formats so students can compare them line by line."""
    print("=== OpenAI tool format ===")
    print(json.dumps(OPENAI_TOOL, indent=2))
    print("\n=== Anthropic tool format ===")
    print(json.dumps(ANTHROPIC_TOOL, indent=2))


# ---------------------------------------------------------------------------
# 4. Offline round trip: what the model WOULD send, and what we send back.
# ---------------------------------------------------------------------------
def offline_round_trip() -> None:
    """Simulate both providers' replies so the shapes are visible without a key."""
    # What an OpenAI reply with a tool call looks like (simplified).
    openai_reply = {"role": "assistant", "content": None, "tool_calls": [
        {"id": "call_abc", "type": "function",
         "function": {"name": "get_weather", "arguments": '{"city": "Taipei"}'}}]}  # arguments is a JSON *string*
    call = openai_reply["tool_calls"][0]
    args = json.loads(call["function"]["arguments"])            # OpenAI: must parse the string
    result = TOOLS[call["function"]["name"]](**args)            # run the real function
    openai_tool_msg = {"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)}
    print("\nOpenAI: model asked ->", call["function"]["name"], args)
    print("OpenAI: we send back ->", openai_tool_msg)

    # What an Anthropic reply with a tool call looks like (simplified).
    anthropic_reply = {"role": "assistant", "stop_reason": "tool_use", "content": [
        {"type": "text", "text": "Let me check the weather."},
        {"type": "tool_use", "id": "toolu_123", "name": "get_weather", "input": {"city": "Taipei"}}]}  # input is a dict
    block = [b for b in anthropic_reply["content"] if b["type"] == "tool_use"][0]
    result = TOOLS[block["name"]](**block["input"])              # Anthropic: already a dict
    anthropic_tool_msg = {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": block["id"], "content": json.dumps(result)}]}
    print("\nAnthropic: model asked ->", block["name"], block["input"])
    print("Anthropic: we send back ->", anthropic_tool_msg)


# ---------------------------------------------------------------------------
# 5. Real calls - only run when a key exists.
# ---------------------------------------------------------------------------
def real_openai(question: str) -> None:
    from openai import OpenAI                                    # pip install openai
    client = OpenAI()                                            # reads OPENAI_API_KEY from the environment
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini")              # check the models page for current names
    messages = [{"role": "user", "content": question}]
    first = client.chat.completions.create(model=model, messages=messages, tools=[OPENAI_TOOL])
    msg = first.choices[0].message                               # the assistant's reply
    if not msg.tool_calls:                                       # the model answered directly
        print("OpenAI answered:", msg.content)
        return
    messages.append(msg)                                         # keep the assistant turn in history
    for tc in msg.tool_calls:                                    # there may be several calls
        result = TOOLS[tc.function.name](**json.loads(tc.function.arguments))
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    final = client.chat.completions.create(model=model, messages=messages, tools=[OPENAI_TOOL])
    print("OpenAI final:", final.choices[0].message.content)


def real_anthropic(question: str) -> None:
    import anthropic                                             # pip install anthropic
    client = anthropic.Anthropic()                               # reads ANTHROPIC_API_KEY
    model = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")      # check the models page for current names
    messages = [{"role": "user", "content": question}]
    first = client.messages.create(model=model, max_tokens=500, tools=[ANTHROPIC_TOOL], messages=messages)
    if first.stop_reason != "tool_use":                          # no tool needed
        print("Claude answered:", first.content[0].text)
        return
    messages.append({"role": "assistant", "content": first.content})  # keep the assistant turn
    results = []
    for block in first.content:
        if block.type == "tool_use":                             # one block per requested call
            out = TOOLS[block.name](**block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(out)})
    messages.append({"role": "user", "content": results})        # tool results go in a *user* turn
    final = client.messages.create(model=model, max_tokens=500, tools=[ANTHROPIC_TOOL], messages=messages)
    print("Claude final:", final.content[0].text)


if __name__ == "__main__":
    show_formats()
    offline_round_trip()
    q = "What's the weather in Taipei right now?"
    if os.getenv("OPENAI_API_KEY"):
        real_openai(q)
    else:
        print("\n(no OPENAI_API_KEY - skipped real OpenAI call)")
    if os.getenv("ANTHROPIC_API_KEY"):
        real_anthropic(q)
    else:
        print("(no ANTHROPIC_API_KEY - skipped real Anthropic call)")
