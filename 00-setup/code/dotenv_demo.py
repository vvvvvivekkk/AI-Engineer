"""
dotenv_demo.py - the safe pattern for using an API key in any Python script.

Run it from the 00-setup folder:
    python code/dotenv_demo.py

It works with or without a real key:
  * with a key in .env  -> it says the key was found (and shows nothing of it)
  * without a key       -> it explains what to do and uses an offline stand-in
"""

import os                                   # os.getenv reads environment variables

try:
    from dotenv import load_dotenv          # python-dotenv: reads NAME=value lines from .env
except ImportError:                         # if the package is not installed...
    load_dotenv = None                      # ...remember that, and carry on without it

KEY_NAME = "OPENAI_API_KEY"                 # the variable we want; change it for other providers


def get_api_key(name):
    """Return the key's value, or None if it is missing or still a placeholder."""
    if load_dotenv is not None:             # only if python-dotenv is installed
        load_dotenv()                       # look for .env from this script's folder upwards
    value = os.getenv(name)                 # None when the variable does not exist
    if value is None or value.strip() == "" or "your-key-here" in value:
        return None                         # treat empty or template values as "no key"
    return value                            # a real-looking key


def ask_model(question, api_key):
    """Pretend to ask an AI model. Real API calls come in module 07."""
    if api_key:                             # we have a key: this is where a real call would go
        # Example of what module 07 will do (not run here):
        #   from openai import OpenAI
        #   client = OpenAI(api_key=api_key)
        #   reply = client.chat.completions.create(model=..., messages=[...])
        return "(a real key is set - in module 07 we will make the real API call here)"
    # No key: return a clearly-labelled offline stand-in, so the program still runs.
    return f"[OFFLINE STAND-IN] You asked: {question!r}. Set {KEY_NAME} in .env for a real answer."


def main():
    key = get_api_key(KEY_NAME)             # try to read the key
    if key:
        print(f"{KEY_NAME} found (length hidden, value hidden).")   # never print the key
    else:
        print(f"{KEY_NAME} not found.")
        print("To fix: copy .env.example to .env and paste your key after the = sign.")
    print(ask_model("What is a virtual environment?", key))


if __name__ == "__main__":                  # run main() only when this file is run directly
    main()
