"""
solutions.py - runnable solutions for module 01 exercises 1-13.
(Exercise 14 is in text_adventure_extended.py.)

Run all of them:   python solutions/solutions.py
Each exerciseN() function prints its own results.
"""

import json                                   # exercise 13: save/load JSON
import tempfile                               # exercises 11 and 13: a scratch folder
from pathlib import Path                      # file paths


# ---------- Exercise 1: receipt line ----------
def exercise1():
    item, price, quantity = "notebook", 45.5, 3            # three assignments in one line
    print(f"{quantity} x {item} @ {price:.2f} = {price * quantity:.2f}")   # .2f = 2 decimals


# ---------- Exercise 2: temperature converter ----------
def c_to_f(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


def exercise2():
    for c in [-10, 0, 37, 100]:                            # each test temperature
        print(f"{c} C = {c_to_f(c):.1f} F")


# ---------- Exercise 3: describe a number ----------
def describe(n):
    """Return 'zero' or '<positive|negative> <even|odd>'."""
    if n == 0:                                             # handle zero first
        return "zero"
    sign = "positive" if n > 0 else "negative"             # one-line conditional
    parity = "even" if n % 2 == 0 else "odd"               # % 2 is 0 for even numbers
    return f"{sign} {parity}"


def exercise3():
    for n in [4, -3, 0, 7, -8]:
        print(n, "->", describe(n))


# ---------- Exercise 4: string surgery ----------
def exercise4():
    s = "  Artificial Intelligence  "
    clean = s.strip()                                      # (a) remove outer spaces
    print(clean.upper())                                   # (b)
    print(clean[:10])                                      # (c) first 10 characters
    print(clean.lower().count("i"))                        # (d) lowercase first so 'I' counts
    print(clean.replace("Intelligence", "Engineering"))    # (e)


# ---------- Exercise 5: list basics ----------
def exercise5():
    nums = [5, 3, 8, 1, 9, 2]
    print("sum", sum(nums), "| average", sum(nums) / len(nums))
    print("max", max(nums), "| min", min(nums))
    print("sorted", sorted(nums))                          # new list; nums unchanged
    print("reversed", nums[::-1])                          # slice with step -1 reverses
    print("greater than 4", [n for n in nums if n > 4])    # comprehension with a filter


# ---------- Exercise 6: word frequency ----------
def word_counts(text):
    """Count lowercase words, ignoring . , ! ?"""
    for mark in ".,!?":                                    # remove each punctuation mark
        text = text.replace(mark, "")
    counts = {}
    for word in text.lower().split():                      # split on spaces
        counts[word] = counts.get(word, 0) + 1             # start at 0 for new words
    return counts


def exercise6():
    counts = word_counts("The cat sat. The cat ran! A dog sat?")
    top3 = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:3]
    print(", ".join(f"{w}: {c}" for w, c in top3))         # the: 2, cat: 2, sat: 2


# ---------- Exercise 7: FizzBuzz as a list ----------
def fizzbuzz(n):
    """Return the FizzBuzz values for 1..n as a list."""
    result = []
    for i in range(1, n + 1):                              # n + 1 because range stops before it
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(i)
    return result


def exercise7():
    print(fizzbuzz(5))
    print(fizzbuzz(15)[-1])


# ---------- Exercise 8: safe number parser ----------
def parse_numbers(items):
    """Split strings into (floats that parsed, strings that did not)."""
    numbers, bad = [], []
    for item in items:
        try:
            numbers.append(float(item))                    # float("") also raises ValueError
        except ValueError:
            bad.append(item)
    return numbers, bad


def exercise8():
    print(parse_numbers(["4", "x", "2.5", "", "-1"]))      # ([4.0, 2.5, -1.0], ['x', ''])


# ---------- Exercise 9: merge and invert ----------
def merge_stock(a, b):
    """Add counts from two dicts; keys in only one dict are kept as-is."""
    merged = dict(a)                                       # copy a so we do not change it
    for fruit, count in b.items():
        merged[fruit] = merged.get(fruit, 0) + count
    return merged


def exercise9():
    shop_a = {"apple": 5, "pear": 2}
    shop_b = {"apple": 3, "kiwi": 7}
    merged = merge_stock(shop_a, shop_b)
    print(merged)                                          # {'apple': 8, 'pear': 2, 'kiwi': 7}
    print([fruit for fruit, n in merged.items() if n < 5]) # ['pear']
    print(set(shop_a) & set(shop_b))                       # {'apple'}


# ---------- Exercise 10: read the traceback ----------
def exercise10():
    print("(a) KeyError - a dict key was missing: 'mango'")
    print("(b) item_price, line 4: return PRICES[name] * qty")
    print("(c) total_price called it (line 9), from the top level (line 14)")
    print("(d) add 'mango' to PRICES, or use PRICES.get(name) and handle unknown items")


# ---------- Exercise 11: grade statistics from a file ----------
def exercise11(folder):
    path = Path(folder) / "scores.txt"
    path.write_text("Asha: 88, 92, 79\nRavi: 95, 89, 91\nMeera: 72, x, 80\nJohn 55, 61, 48\n",
                    encoding="utf-8")
    averages = {}
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if ":" not in line:                            # malformed: no colon
                print(f"Skipping line {line_no}: no ':' in {line!r}")
                continue
            name, marks_text = line.split(":", 1)          # split only at the first colon
            try:
                marks = [float(m) for m in marks_text.split(",")]
            except ValueError as err:
                print(f"Skipping line {line_no} ({name}): {err}")
                continue
            averages[name.strip()] = sum(marks) / len(marks)
    for name, avg in averages.items():
        print(f"{name}: {avg:.1f}")
    best = max(averages, key=averages.get)                 # key with the biggest value
    print("Best student:", best)


# ---------- Exercise 12: BankAccount class ----------
class BankAccount:
    def __init__(self, owner, balance=0.0):
        self.owner = owner
        self.balance = balance
        self.history = []                                  # list of (action, amount) tuples

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def __repr__(self):
        return f"BankAccount({self.owner!r}, balance={self.balance:.2f})"


def exercise12():
    acct = BankAccount("Asha")
    acct.deposit(100)
    acct.withdraw(30)
    for bad in [lambda: acct.withdraw(500), lambda: acct.deposit(-5)]:
        try:
            bad()
        except ValueError as err:
            print("Rejected:", err)
    print(acct, acct.history)


# ---------- Exercise 13: prompt builder ----------
def build_prompt(task, examples, question):
    """Return a few-shot prompt string."""
    if not examples:
        raise ValueError("need at least one example")
    parts = [f"Task: {task}", ""]                          # task line, then a blank line
    for given, expected in examples:                       # unpack each (input, output) tuple
        parts += [f"Input: {given}", f"Output: {expected}", ""]
    parts += [f"Input: {question}", "Output:"]
    return "\n".join(parts)                                # glue lines with newlines


def exercise13(folder):
    prompt = build_prompt("Classify the sentiment as positive or negative.",
                          [("I loved it", "positive"), ("Terrible service", "negative")],
                          "The food was great")
    print(prompt)
    path = Path(folder) / "prompt.json"
    record = {"task": "sentiment", "n_examples": 2, "prompt": prompt}
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    print("Reloaded n_examples:", loaded["n_examples"])
    try:
        build_prompt("x", [], "y")
    except ValueError as err:
        print("Rejected:", err)


def main():
    with tempfile.TemporaryDirectory() as folder:          # deleted automatically afterwards
        simple = [exercise1, exercise2, exercise3, exercise4, exercise5, exercise6,
                  exercise7, exercise8, exercise9, exercise10]
        for number, func in enumerate(simple, start=1):
            print(f"\n=== Exercise {number} ===")
            func()
        print("\n=== Exercise 11 ===")
        exercise11(folder)
        print("\n=== Exercise 12 ===")
        exercise12()
        print("\n=== Exercise 13 ===")
        exercise13(folder)


if __name__ == "__main__":
    main()
