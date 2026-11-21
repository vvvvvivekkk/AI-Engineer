"""
Solution to exercise 8: load a key from .env safely.
Run from the project folder that holds your .env:   python app.py
"""
import os                                  # reads environment variables

from dotenv import load_dotenv             # reads NAME=value lines from .env

load_dotenv()                              # find .env (next to this script or above) and load it
key = os.getenv("MY_SERVICE_KEY")          # None if the variable is missing

print("Key loaded:", key is not None)      # True / False only - never the key itself
if key is None:                            # friendly help instead of a crash
    print("MY_SERVICE_KEY is missing. Add a line MY_SERVICE_KEY=... to your .env file.")
else:
    print("Key length:", len(key))         # the length reveals almost nothing; the value would
