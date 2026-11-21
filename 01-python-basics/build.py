"""
build.py for module 01-python-basics.

Regenerates: images/ (Mermaid diagrams), notebooks/, slides/, excel/, pdf/.
Run from the repo root:   python 01-python-basics/build.py
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

IMG = HERE / "images"
NB = HERE / "notebooks"


def md(text):
    return ("md", text)


def code(text):
    return ("code", text)


# ---------------------------------------------------------------------------
# 1. Diagrams
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "variables-labels": """
flowchart LR
    N1([name]) --> V1["'Asha' (str)"]
    N2([age]) --> V2["21 (int)"]
    N3([score]) -. was .-> V3["10 (int)"]
    N3 -- now --> V4["15 (int)"]
""",
    "collections-chooser": """
flowchart TD
    Q{What do you need?} --> A{Look up by a name/key?}
    A -- Yes --> D[dict<br/>key: value]
    A -- No --> B{Only unique items,<br/>order unimportant?}
    B -- Yes --> S[set<br/>unique items]
    B -- No --> C{Will it change<br/>after creation?}
    C -- Yes --> L[list<br/>ordered, changeable]
    C -- No --> T[tuple<br/>ordered, fixed]
""",
    "for-loop": """
flowchart TD
    S[Start] --> N{Any items left<br/>in the collection?}
    N -- Yes --> T[Take the next item<br/>into the loop variable]
    T --> B[Run the indented block]
    B --> N
    N -- No --> E[Continue after the loop]
""",
    "function-machine": """
flowchart LR
    A[Arguments<br/>e.g. 80, 90, 100] --> F[["def average(numbers):<br/>total = sum(numbers)<br/>return total / len(numbers)"]]
    F --> R[Return value<br/>90.0]
""",
    "try-except": """
flowchart TD
    T[Run the try block] --> Q{Exception raised?}
    Q -- No --> EL[Run else block]
    Q -- Yes --> M{Matches an<br/>except clause?}
    M -- Yes --> EX[Run that except block]
    M -- No --> CR[Program crashes<br/>with a traceback]
    EL --> FI[Run finally block]
    EX --> FI
    FI --> C[Continue the program]
""",
    "traceback-reading": """
flowchart TD
    L4["Read 1st - LAST line<br/>ZeroDivisionError: division by zero<br/>WHAT went wrong"] --> L3
    L3["Read 2nd - frame just above<br/>line 3, in average<br/>WHERE it failed"] --> L2
    L2["Read 3rd - line 6, in report<br/>who called average"] --> L1
    L1["Read 4th - TOP frame: line 9, in module<br/>where the chain started"]
""",
}


def build_images():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
NB1 = [
    md(r"""# 01 · Notebook 1 — Python basics: values, strings, decisions, loops

**Goal:** write and run your first real Python, one small step at a time.

You will learn:
1. `print` and comments
2. Values, **types** (what kind of data something is) and **variables** (names for values)
3. Arithmetic and converting between types
4. Strings and **f-strings** (text with values inserted)
5. Decisions with `if` / `elif` / `else`
6. Loops with `for` and `while`

How to use this notebook: read each explanation, run the cell under it with **Shift + Enter**, then **change something and run it again**. Each section ends with a small "Your turn"."""),
    md(r"""## 1. `print` and comments

`print(...)` is a **function** (a named action) that shows its **argument** (the value inside the brackets) on screen. Text must be inside quotes. A `#` starts a **comment**: a note for humans that Python ignores."""),
    code(r"""# My first Python cell
print("Hello, AI engineer!")
print("2 + 3 =", 2 + 3)     # print can show several things, separated by commas"""),
    md(r"""## 2. Values and types

Every value has a **type**:
- `int` — whole numbers like `42`
- `float` — decimals like `3.14`
- `str` — text like `"hello"` (short for "string")
- `bool` — `True` or `False`
- `None` — "no value yet"

`type(value)` tells you the type."""),
    code(r"""print(type(42))
print(type(3.14))
print(type("hello"))
print(type(True))
print(type(None))"""),
    md(r"""## 3. Variables: name tags

`=` is **assignment**: it attaches a name to a value. Read `age = 21` as "age now refers to 21". You can move the tag later. The right side is worked out first, so `score = score + 5` uses the old value."""),
    code(r"""name = "Asha"
age = 21
score = 10
score = score + 5      # take 10, add 5, attach the tag "score" to 15
print(name, "is", age, "and scored", score)"""),
    md(r"""## 4. Arithmetic

Python is a good calculator. Note that `/` always gives a `float`, `//` keeps only the whole part, and `%` gives the remainder."""),
    code(r"""print(7 + 2, 7 - 2, 7 * 2)
print(7 / 2)     # 3.5
print(7 // 2)    # 3   floor division
print(7 % 2)     # 1   remainder
print(2 ** 10)   # 1024 power

x = 5
x += 3           # same as x = x + 3
print(x)

print(0.1 + 0.2)              # tiny binary rounding error - normal in every language
print(round(0.1 + 0.2, 2))    # round for display"""),
    md(r"""## 5. Converting between types

Text that looks like a number is still text. Adding two strings **joins** them; adding two numbers **adds** them. Convert with `int()`, `float()` and `str()`."""),
    code(r"""typed = "42"                 # data from files and input() is always text
print(typed + typed)         # "4242" - joined, not added
print(int(typed) + int(typed))   # 84
print(float("3.5") * 2)
print(str(100) + " points")
print(int(3.9), round(3.9))  # int() cuts off; round() rounds"""),
    md(r"""**Your turn:** make variables `price = "250"` (text) and `quantity = 3`, then print the total cost as a number."""),
    code(r"""price = "250"
quantity = 3
total = int(price) * quantity
print("Total:", total)"""),
    md(r"""## 6. Strings: indexing and slicing

A string is a sequence of characters. Each has an **index** (position) starting at **0**. Negative indexes count from the end. A **slice** `[start:stop]` takes characters from `start` up to, but **not including**, `stop`."""),
    code(r"""word = "Python"
print(word[0], word[1], word[-1])   # P y n
print(word[0:3])                    # Pyt
print(word[2:])                     # thon
print(word[:2])                     # Py
print(len(word))                    # 6"""),
    md(r"""## 7. String methods

A **method** is a function attached to a value, called with a dot. String methods return a **new** string; the original does not change (strings are **immutable**)."""),
    code(r"""text = "  Large Language Models  "
print(repr(text.strip()))          # repr shows the quotes so you can see the spaces are gone
print(text.lower())
print(text.upper())
print(text.replace("Large", "Small"))
print("cat,dog,bird".split(","))   # cut into a list
print(" | ".join(["a", "b", "c"])) # glue a list together
print("data" in "big data")
print(text)                        # unchanged!"""),
    md(r"""## 8. f-strings

Put `f` before the quote and use `{}` to insert values. After a `:` you can add a **format specification**: `.2f` (2 decimals), `.1%` (percent), `<10` (left-align in 10 characters), `,` (thousands separator)."""),
    code(r"""name = "Asha"
accuracy = 0.91234
tokens = 1234567
print(f"{name}'s model accuracy: {accuracy}")
print(f"{name}'s model accuracy: {accuracy:.2f}")
print(f"{name}'s model accuracy: {accuracy:.1%}")
print(f"Tokens used: {tokens:,}")
print(f"[{'left':<10}] [{'right':>10}]")
print(f"{accuracy=}")             # name=value, great for debugging"""),
    md(r"""f-strings are how you will build prompts for language models. Triple quotes allow several lines."""),
    code(r'''topic = "virtual environments"
level = "beginner"
prompt = f"""You are a patient tutor.
Explain {topic} to a {level} in three short sentences."""
print(prompt)'''),
    md(r"""## 9. Decisions: `if`, `elif`, `else`

Comparisons give `True` or `False`: `==` (equal — two signs!), `!=`, `<`, `>`, `<=`, `>=`, `in`. Combine with `and`, `or`, `not`.

The indented lines (4 spaces) belong to the condition above them, which ends with `:`. Only the **first** true branch runs."""),
    code(r"""score = 78     # change me and re-run

if score >= 90:
    grade = "A"
elif score >= 75:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "F"
print(f"Score {score} -> grade {grade}")"""),
    md(r"""Combining conditions, and **truthiness**: empty things (`""`, `[]`, `0`, `None`) count as `False` in an `if`."""),
    code(r"""age = 20
has_id = True
if age >= 18 and has_id:
    print("Entry allowed")

reviews = []
if not reviews:
    print("No reviews yet")

label = "pass" if score >= 60 else "fail"   # one-line conditional expression
print(label)"""),
    md(r"""## 10. `for` loops

A `for` loop runs its block once per item. `range(n)` gives `0, 1, ..., n-1`. `enumerate` gives position and item; `zip` walks two lists together."""),
    code(r"""fruits = ["apple", "banana", "mango"]
for fruit in fruits:
    print("I like", fruit)

for i in range(3):
    print("Epoch", i)

for position, fruit in enumerate(fruits, start=1):
    print(position, fruit)

for name, mark in zip(["Asha", "Ravi"], [88, 92]):
    print(f"{name}: {mark}")"""),
    md(r"""## 11. The accumulator pattern

Start a result before the loop (a total, a count, an empty list), and update it inside."""),
    code(r"""marks = [72, 88, 95, 60, 81]
total = 0
passed = []
for m in marks:
    total += m
    if m >= 75:
        passed.append(m)
print("Average:", total / len(marks))
print("Passed:", passed)"""),
    md(r"""## 12. `while`, `break` and `continue`

`while` repeats as long as a condition is true. `break` leaves a loop; `continue` jumps to the next round. (If a loop never stops, press the notebook's **stop** button.)"""),
    code(r"""balance = 100
months = 0
while balance < 200:
    balance *= 1.1
    months += 1
print(f"Doubled in {months} months -> {balance:.2f}")

for n in [3, 8, -1, 5, 0, 9]:
    if n < 0:
        continue      # skip negatives
    if n == 0:
        break         # stop at zero
    print(n)"""),
    md(r"""**Your turn:** FizzBuzz, the classic warm-up. For numbers 1 to 15, print "Fizz" for multiples of 3, "Buzz" for multiples of 5, "FizzBuzz" for both, otherwise the number. (Hint: check the "both" case first.)"""),
    code(r"""for n in range(1, 16):
    if n % 15 == 0:
        print("FizzBuzz")
    elif n % 3 == 0:
        print("Fizz")
    elif n % 5 == 0:
        print("Buzz")
    else:
        print(n)"""),
    md(r"""## Summary

- Values have types; variables are name tags; `=` assigns.
- Convert text to numbers with `int()` / `float()` before maths.
- Strings index from 0; slices stop *before* the end index; f-strings insert values.
- `if / elif / else` picks the first true branch; indentation defines blocks.
- `for` visits each item; `while` repeats while a condition holds.

Next: **Notebook 2 — collections** (lists, tuples, dicts, sets)."""),
]

NB2 = [
    md(r"""# 01 · Notebook 2 — Collections: lists, tuples, dicts, sets

**Goal:** store and process groups of values — the shape of almost all real data.

- **list** — ordered, changeable: `[1, 2, 3]`
- **tuple** — ordered, fixed: `(1, 2)`
- **dict** (dictionary) — look up values by key: `{"name": "Asha"}`
- **set** — unique items, no order: `{"nlp", "vision"}`
- **comprehensions** — build a new collection in one line"""),
    md(r"""## 1. Lists: create, index, slice

A list keeps items in order. Indexing and slicing work like strings."""),
    code(r"""scores = [72, 88, 95, 60]
print(scores)
print(scores[0], scores[-1])
print(scores[1:3])
print(len(scores), sum(scores), max(scores), min(scores))"""),
    md(r"""## 2. Changing a list

Lists are **mutable** (changeable). `append` adds to the end, `insert` adds at a position, `remove` deletes by value, `pop` removes and returns an item. `sort()` sorts the list itself; `sorted()` returns a new sorted list."""),
    code(r"""scores.append(81)
scores.insert(0, 50)
print("after append/insert:", scores)
scores.remove(60)
last = scores.pop()
print("removed 60, popped", last, "->", scores)
scores[0] = 55
scores.sort()
print("sorted:", scores)
print("biggest first (new list):", sorted(scores, reverse=True))"""),
    md(r"""## 3. The copy trap

`b = a` does **not** copy. It puts a second name tag on the **same** list. Use `.copy()` for an independent copy."""),
    code(r"""a = [1, 2, 3]
b = a            # same list, two names
c = a.copy()     # a separate copy
b.append(99)
print("a:", a)   # changed too!
print("c:", c)   # unaffected"""),
    md(r"""## 4. Lists of lists

A list can hold lists — like a small table. `grid[row][column]`. In module 02 NumPy arrays do this much faster."""),
    code(r"""grid = [[1, 2, 3],
        [4, 5, 6]]
print(grid[1][0])          # row 1, column 0 -> 4
for row in grid:
    print(row, "row total:", sum(row))"""),
    md(r"""## 5. Tuples and unpacking

A tuple cannot be changed after it is created. Use it for fixed groups (coordinates, image sizes). **Unpacking** puts each item into its own variable."""),
    code(r"""image_size = (28, 28)
height, width = image_size
print(height * width, "pixels")

point = (3, 4)
x, y = point
print(f"x={x}, y={y}")

try:
    point[0] = 10
except TypeError as err:
    print("Tuples are fixed:", err)"""),
    md(r"""## 6. Dictionaries: key → value

Look up by key with `d[key]`. Add or change with `d[key] = value`. `d.get(key, default)` returns a default instead of crashing when the key is missing."""),
    code(r"""student = {"name": "Ravi", "age": 20, "scores": [88, 92]}
print(student["name"])
student["age"] = 21
student["city"] = "Hyderabad"
print(student)
print(student.get("email"))
print(student.get("email", "not given"))
print("age" in student, "email" in student)"""),
    md(r"""## 7. Looping over a dict

`.keys()`, `.values()` and `.items()` give the keys, the values, or (key, value) pairs."""),
    code(r"""for key, value in student.items():
    print(f"{key:<7} -> {value}")

prices = {"apple": 30, "banana": 10, "mango": 60}
print("Total:", sum(prices.values()))
print("Most expensive:", max(prices, key=prices.get))"""),
    md(r"""## 8. Counting with a dict

A very common pattern: count how often each thing appears. `counts.get(word, 0) + 1` starts at 0 for new words."""),
    code(r"""text = "the cat sat on the mat the end"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)

from collections import Counter     # the standard library has a ready-made counter
print(Counter(text.split()).most_common(2))"""),
    md(r"""## 9. Nested data: how AI APIs look

Chat models take a **list of dicts**, each with a `role` and `content`. JSON from web APIs becomes the same kind of nested lists and dicts in Python."""),
    code(r"""conversation = [
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "What is a tuple?"},
    {"role": "assistant", "content": "An ordered collection that cannot change."},
]
conversation.append({"role": "user", "content": "And a set?"})
for message in conversation:
    print(f"{message['role']:>9}: {message['content']}")
print("Messages from the user:", sum(1 for m in conversation if m["role"] == "user"))"""),
    md(r"""## 10. Sets

A set keeps each value once. Checking membership with `in` is very fast. Sets support `&` (in both), `|` (in either), `-` (in first, not second)."""),
    code(r"""labels = ["cat", "dog", "cat", "bird", "dog"]
unique = set(labels)
print(unique, len(unique))

a = {"python", "sql", "git"}
b = {"python", "docker"}
print("both:", a & b)
print("either:", a | b)
print("only a:", a - b)
print(type({}), type(set()))     # {} is an empty dict, not a set!"""),
    md(r"""## 11. List comprehensions

`[expression for item in collection if condition]` builds a new list. Read it as English: "n squared, for each n in numbers, if n is even"."""),
    code(r"""numbers = list(range(1, 11))
squares = [n ** 2 for n in numbers]
evens = [n for n in numbers if n % 2 == 0]
words = ["  Hello ", "WORLD  ", " Python"]
clean = [w.strip().lower() for w in words]
print(squares)
print(evens)
print(clean)"""),
    md(r"""The same `squares` with a normal loop, for comparison. Both are fine; the comprehension is shorter for simple cases."""),
    code(r"""squares_loop = []
for n in numbers:
    squares_loop.append(n ** 2)
print(squares_loop == squares)"""),
    md(r"""## 12. Dict and set comprehensions

Curly braces with `key: value` make a dict; curly braces with one expression make a set."""),
    code(r"""words = ["ai", "data", "model", "token"]
lengths = {w: len(w) for w in words}
long_words = {w for w in words if len(w) > 4}
print(lengths)
print(long_words)

marks = {"Asha": 88, "Ravi": 92, "John": 55}
passed = {name: m for name, m in marks.items() if m >= 60}
print(passed)"""),
    md(r"""**Your turn:** you have a list of model names. Make (a) a list of the names in uppercase, (b) a dict from name to its length, (c) the set of first letters."""),
    code(r"""models = ["bert", "gpt", "llama", "bart", "gemma"]
upper = [m.upper() for m in models]
name_len = {m: len(m) for m in models}
first_letters = {m[0] for m in models}
print(upper, name_len, first_letters, sep="\n")"""),
    md(r"""## Summary

| | Brackets | Ordered | Changeable | Duplicates |
|---|---|---|---|---|
| list | `[ ]` | yes | yes | yes |
| tuple | `( )` | yes | no | yes |
| dict | `{k: v}` | insertion order | yes | keys unique |
| set | `{ }` / `set()` | no | yes | no |

Next: **Notebook 3 — functions, errors, files, modules and classes**."""),
]

NB3 = [
    md(r"""# 01 · Notebook 3 — Functions, errors, tracebacks, files, modules, classes

**Goal:** organise code into reusable pieces, handle things going wrong, and read error messages calmly.

Sections:
1. Functions, parameters, return values, defaults
2. Exceptions and `try` / `except`
3. **Reading tracebacks** (the error report Python prints)
4. Files, `pathlib` and JSON
5. Modules and imports
6. Classes and objects (light)"""),
    md(r"""## 1. Defining a function

`def name(parameters):` starts a **function definition**. The indented block is the function's body. `return` sends a value back. The triple-quoted line is a **docstring** (built-in documentation)."""),
    code(r'''def average(numbers):
    """Return the mean of a list of numbers."""
    total = sum(numbers)
    return total / len(numbers)

print(average([80, 90, 100]))
print(average([1.5, 2.5]))
help(average)'''),
    md(r"""## 2. Defaults and keyword arguments

A **default value** is used when the caller leaves that argument out. **Keyword arguments** (`name=value`) can be given in any order — AI libraries use them everywhere."""),
    code(r"""def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

print(greet("Asha"))
print(greet("Asha", "Namaste"))
print(greet(punctuation="?", name="Ravi"))"""),
    md(r"""## 3. Returning several values, and functions without `return`

Returning `a, b` actually returns one tuple, which you can unpack. A function without `return` gives back `None`."""),
    code(r"""def min_max(values):
    return min(values), max(values)

low, high = min_max([4, 9, 1, 7])
print(low, high)

def say_hi():
    print("hi")

result = say_hi()
print("say_hi returned:", result)"""),
    md(r"""## 4. Scope: variables inside functions are local

A variable created inside a function exists only while it runs. Pass data **in** with parameters and get it **out** with `return`."""),
    code(r"""def make_secret():
    secret = 42
    return secret * 2

print(make_secret())
print("'secret' exists outside?", "secret" in globals())"""),
    md(r"""## 5. Type hints and lambdas (preview)

**Type hints** (`: list[float]`, `-> float`) document expected types; Python does not enforce them, but editors use them. A **lambda** is a tiny one-line function, often used as a `key` for sorting."""),
    code(r"""def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)

students = [("Asha", 88), ("Ravi", 92), ("Meera", 75)]
ranked = sorted(students, key=lambda pair: pair[1], reverse=True)
print(mean([1.0, 2.0, 3.0]), ranked)"""),
    md(r"""**Your turn:** write `letter_grade(score)` returning "A" (90+), "B" (75+), "C" (60+) or "F", and test it on a few scores."""),
    code(r"""def letter_grade(score):
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    return "F"

for s in [95, 80, 61, 30]:
    print(s, letter_grade(s))"""),
    md(r"""## 6. Exceptions and `try` / `except`

An **exception** is an error that happens while code runs. Without handling, the program stops. `try` / `except` catches it so the program can continue. Catch the **specific** exception you expect."""),
    code(r"""for text in ["42", "3.5", "abc"]:
    try:
        value = float(text)
        print(f"{text!r} -> {value}")
    except ValueError:
        print(f"{text!r} is not a number, skipping")"""),
    md(r"""## 7. The full form: `except ... as err`, `else`, `finally`

- `as err` keeps the error object so you can print its message.
- `else` runs only if **no** exception happened.
- `finally` **always** runs (good for clean-up)."""),
    code(r"""def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("  cannot divide by zero")
        return None
    except TypeError as err:
        print("  bad input:", err)
        return None
    else:
        return result
    finally:
        print(f"  finished safe_divide({a!r}, {b!r})")

print(safe_divide(10, 2))
print(safe_divide(10, 0))
print(safe_divide(10, "2"))"""),
    md(r"""## 8. Raising your own exceptions

Use `raise` to reject bad input early, with a clear message. This is better than letting a confusing error appear later."""),
    code(r"""def set_temperature(t):
    if not 0 <= t <= 2:
        raise ValueError(f"temperature must be between 0 and 2, got {t}")
    return t

try:
    set_temperature(5)
except ValueError as err:
    print("Rejected:", err)"""),
    md(r"""## 9. Reading tracebacks

When an exception is not caught, Python prints a **traceback** — the chain of function calls that led to the error. To keep this notebook running top to bottom, we catch each error and print its traceback with the standard `traceback` module. It looks exactly like a real crash.

**Read from the bottom up:**
1. **Last line** = *what* went wrong (exception type and message).
2. **The frame above it** = *where* (file or cell, line number, function).
3. **Further up** = *how* the program got there."""),
    code(r'''import traceback, sys

def show_traceback(func):
    """Run func(); if it fails, print the traceback instead of stopping the notebook."""
    try:
        func()
    except Exception:
        traceback.print_exc(file=sys.stdout)

def average_of(scores):
    total = sum(scores)
    return total / len(scores)

def report(student):
    avg = average_of(student["scores"])
    return f"{student['name']}: {avg:.1f}"

show_traceback(lambda: report({"name": "Ravi", "scores": []}))'''),
    md(r"""Reading the traceback above:
- **Last line:** `ZeroDivisionError: division by zero` — we divided by zero.
- **Frame above:** inside `average_of`, the line `return total / len(scores)`. The `~~~^~~~` markers point at the division.
- **Above that:** `report` called `average_of`, and our `lambda` called `report`. (`show_traceback` is our helper; ignore it.)
- **Why:** the scores list was empty, so `len(scores)` was 0.

Now a `KeyError`. Which line failed, and which key was missing?"""),
    code(r"""show_traceback(lambda: report({"name": "Meera"}))"""),
    md(r"""Answer: the last line says `KeyError: 'scores'`; the frame above points at `student["scores"]` inside `report`. The student dict had no `"scores"` key.

Here are several common errors in a row. For each, read only the **last line** and say in your own words what went wrong. Notice the helpful "Did you mean" suggestion for the typo."""),
    code(r"""examples = {
    "TypeError": lambda: "Score: " + 95,
    "ValueError": lambda: int("ninety"),
    "AttributeError": lambda: "hello".uppr(),
    "IndexError": lambda: [10, 20, 30][3],
    "NameError": lambda: undefined_variable + 1,
}
for name, func in examples.items():
    print(f"--- {name} ---")
    try:
        func()
    except Exception as err:
        # format_exception_only gives exactly the traceback's last line(s), suggestions included
        print("".join(traceback.format_exception_only(err)).strip())"""),
    md(r"""Fixes, in order: convert with `str(95)` or use an f-string; pass a numeric string like `"90"`; spell the method `upper`; the last index of a 3-item list is `2`; define the variable (or run the cell that defines it) first.

**Syntax errors** are different: Python cannot even start. We can see one safely by asking Python to `compile` some broken text. The caret `^` shows where Python got confused."""),
    code(r"""broken_code = 'print("hello"'
try:
    compile(broken_code, "<example>", "exec")
except SyntaxError as err:
    print(f"SyntaxError: {err.msg} (line {err.lineno})")"""),
    md(r"""## 10. Files: write, append, read

Always use `with open(...) as f:` — it closes the file for you. Modes: `"w"` write (replaces), `"a"` append, `"r"` read (the default). Pass `encoding="utf-8"` so every language's characters work. `"\n"` is the newline character."""),
    code(r"""with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")
    f.write("second line\n")

with open("notes.txt", "a", encoding="utf-8") as f:
    f.write("third line\n")

with open("notes.txt", encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):
        print(number, line.strip())"""),
    md(r"""## 11. `pathlib` and a missing file

`pathlib.Path` builds paths that work on Windows, macOS and Linux (`/` joins parts). Opening a file that does not exist raises `FileNotFoundError` — a perfect job for `try` / `except`."""),
    code(r"""from pathlib import Path

data_dir = Path("practice_data")
data_dir.mkdir(exist_ok=True)
path = data_dir / "scores.txt"
path.write_text("88\n92\n75\n", encoding="utf-8")
numbers = [int(line) for line in path.read_text(encoding="utf-8").splitlines()]
print(path, path.exists(), numbers)

try:
    Path("does_not_exist.txt").read_text()
except FileNotFoundError as err:
    print("Missing file:", err.filename)"""),
    md(r"""## 12. JSON files

**JSON** is the text format APIs use. `json.dump` saves dicts/lists to a file; `json.load` reads them back. `json.dumps` / `json.loads` do the same with strings."""),
    code(r"""import json

config = {"model": "tiny-model", "temperature": 0.2, "tags": ["demo", "test"]}
json_path = data_dir / "config.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print(json_path.read_text())
with open(json_path, encoding="utf-8") as f:
    loaded = json.load(f)
print(loaded["tags"][0], type(loaded))"""),
    md(r"""## 13. Modules and imports

A **module** is a `.py` file of reusable code. The **standard library** ships with Python. `import x`, `from x import y`, and `import x as z` (an **alias**, a nickname) are the three common forms."""),
    code(r"""import math
from random import choice, seed
import datetime as dt

print(math.sqrt(16), math.pi)
seed(0)                                   # same "random" results every run
print(choice(["rock", "paper", "scissors"]))
print(dt.date(2026, 1, 1).strftime("%A"))"""),
    md(r"""**Your own module:** we write a small `helpers.py` file into our practice folder, tell Python to look there, and import from it — exactly how real projects split code across files."""),
    code(r"""helpers_code = '''
def shout(text):
    return text.upper() + "!"

def word_count(text):
    return len(text.split())
'''
(data_dir / "helpers.py").write_text(helpers_code, encoding="utf-8")

sys.path.insert(0, str(data_dir.resolve()))   # add the folder to Python's search list
from helpers import shout, word_count

print(shout("modules are neat"), word_count("one two three"))"""),
    md(r"""## 14. Classes and objects

A **class** is a blueprint; an **object** is one thing built from it. `__init__` runs when the object is created and sets its **attributes** (its data). **Methods** are functions inside the class; their first parameter `self` means "this object"."""),
    code(r"""class Student:
    def __init__(self, name):
        self.name = name
        self.scores = []

    def add_score(self, score):
        if not 0 <= score <= 100:
            raise ValueError(f"score must be 0-100, got {score}")
        self.scores.append(score)

    def average(self):
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    def __repr__(self):
        return f"Student({self.name!r}, avg={self.average():.1f})"

asha = Student("Asha")
asha.add_score(88)
asha.add_score(94)
ravi = Student("Ravi")
ravi.add_score(91)
print(asha, ravi)
print(asha.name, asha.scores)"""),
    md(r"""You will mostly **use** objects others designed: in later modules `df.head()` (pandas), `model.train()` (PyTorch) and `client.messages.create(...)` (an AI SDK) are all method calls on objects. `type()` and `dir()` help you explore an unfamiliar object."""),
    code(r"""print(type(asha))
print([name for name in dir(asha) if not name.startswith("_")])"""),
    md(r"""## 15. Clean up

Remove the practice files so the folder stays tidy."""),
    code(r"""import shutil
Path("notes.txt").unlink(missing_ok=True)
sys.path.remove(str(data_dir.resolve()))
shutil.rmtree(data_dir, ignore_errors=True)
print("cleaned up:", not data_dir.exists())"""),
    md(r"""## Summary

- Functions: `def`, parameters, `return`, defaults, keyword arguments; local scope.
- Exceptions: `try` / `except SpecificError as err` / `else` / `finally`; `raise` for bad input.
- Tracebacks: read **bottom up** — what, where, how you got there.
- Files: `with open(..., encoding="utf-8")`, `pathlib.Path`, `json`.
- Modules: `import`, `from ... import`, aliases, your own `.py` files.
- Classes: blueprints with `__init__`, attributes and methods using `self`.

Next: **Notebook 4 — mini-project**."""),
]

NB4 = [
    md(r"""# 01 · Notebook 4 — Mini-project: grade calculator (+ bonus text adventure)

**Goal:** combine everything from this module into a small, useful program.

**The brief:** a teacher has a CSV file (**CSV** = comma-separated values, a simple text table) of marks. Some rows are messy. Build a program that:
1. reads the file,
2. skips bad rows with a clear message instead of crashing,
3. computes each student's average and letter grade,
4. prints a neat ranked report and class statistics,
5. saves the results to JSON.

We build it in small functions and test each one before moving on. That is how professionals work."""),
    md(r"""## Step 1 — Create the data file

In a real project the file would already exist. Here we write it ourselves so the notebook works anywhere (including Colab). Two rows are broken on purpose: `abc` is not a number, and `101` is out of range."""),
    code(r'''from pathlib import Path

raw = """name,maths,science,english
Asha,88,92,79
Ravi,95,89,91
Meera,72,abc,80
John,55,61,48
Priya,101,90,85
Karan,66,74,70
Fatima,91,94,97
"""
csv_path = Path("marks.csv")
csv_path.write_text(raw, encoding="utf-8")
print(csv_path.read_text())'''),
    md(r"""## Step 2 — Read the CSV into dicts

The standard library's `csv.DictReader` turns each row into a dict using the header line as keys. That means we can write `row["maths"]` instead of remembering column positions."""),
    code(r"""import csv

with open(csv_path, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    subjects = [col for col in reader.fieldnames if col != "name"]

print("Subjects:", subjects)
print("First row:", rows[0])
print("Number of rows:", len(rows))"""),
    md(r"""## Step 3 — The grade function

We store the grade boundaries as a list of tuples, highest first, and return the first one the score reaches. Storing rules as data (instead of a long `if` chain) makes them easy to change. We test it right away."""),
    code(r"""GRADE_BOUNDARIES = [(90, "A"), (75, "B"), (60, "C"), (40, "D"), (0, "F")]

def letter_grade(score):
    for lowest, letter in GRADE_BOUNDARIES:
        if score >= lowest:
            return letter
    raise ValueError(f"score cannot be negative: {score}")

for test in [95, 90, 89.9, 75, 60, 45, 10]:
    print(test, "->", letter_grade(test))"""),
    md(r"""## Step 4 — Parse one row safely

`parse_marks` converts the text marks to numbers. It **raises** `ValueError` for anything wrong, with a message saying what. We test it on a good row and a bad row."""),
    code(r"""def parse_marks(row, subjects):
    marks = []
    for subject in subjects:
        mark = float(row[subject].strip())          # ValueError if not a number
        if not 0 <= mark <= 100:
            raise ValueError(f"{subject} mark {mark} is outside 0-100")
        marks.append(mark)
    return marks

print(parse_marks(rows[0], subjects))
try:
    parse_marks(rows[2], subjects)
except ValueError as err:
    print("Bad row:", err)"""),
    md(r"""## Step 5 — Build the report

Loop over the rows. For each, try to parse; on failure, record why and `continue`. On success, store a small dict of results. Finally sort by average, best first, using a `lambda` as the sort key."""),
    code(r"""def build_report(rows, subjects):
    results, skipped = [], []
    for line_number, row in enumerate(rows, start=2):   # line 1 is the header
        try:
            marks = parse_marks(row, subjects)
        except ValueError as err:
            skipped.append(f"line {line_number} ({row['name']}): {err}")
            continue
        avg = sum(marks) / len(marks)
        results.append({
            "name": row["name"],
            "marks": dict(zip(subjects, marks)),
            "average": round(avg, 1),
            "grade": letter_grade(avg),
        })
    results.sort(key=lambda r: r["average"], reverse=True)
    return results, skipped

results, skipped = build_report(rows, subjects)
print(len(results), "students graded,", len(skipped), "skipped")"""),
    md(r"""## Step 6 — Print a neat table

f-string alignment (`<10` left, `>8.1f` right with 1 decimal) lines the columns up."""),
    code(r"""def print_report(results, skipped):
    print(f"{'Rank':<5}{'Name':<10}{'Average':>8}  Grade")
    print("-" * 31)
    for rank, r in enumerate(results, start=1):
        print(f"{rank:<5}{r['name']:<10}{r['average']:>8.1f}  {r['grade']}")
    for message in skipped:
        print("Skipped", message)

print_report(results, skipped)"""),
    md(r"""## Step 7 — Class statistics

Comprehensions and dicts answer questions about the class: average per subject, the grade distribution, and the top student per subject."""),
    code(r"""subject_averages = {
    s: round(sum(r["marks"][s] for r in results) / len(results), 1) for s in subjects
}
print("Subject averages:", subject_averages)

grade_counts = {}
for r in results:
    grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1
print("Grade counts:", dict(sorted(grade_counts.items())))

for s in subjects:
    best = max(results, key=lambda r: r["marks"][s])
    print(f"Top in {s}: {best['name']} ({best['marks'][s]:.0f})")"""),
    md(r"""## Step 8 — Save the results as JSON

Other programs (a web page, a spreadsheet, an AI agent) can read this file. We read it back to prove it worked."""),
    code(r"""import json

out_path = Path("grade_report.json")
out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
reloaded = json.loads(out_path.read_text(encoding="utf-8"))
print("Saved and reloaded", len(reloaded), "records. First:", reloaded[0]["name"], reloaded[0]["grade"])"""),
    md(r"""## Step 9 — Wrap it in a class (optional)

The same logic packaged as a `Gradebook` object. This shows how classes bundle data (the rows) with actions (report, stats). Notice it reuses our functions."""),
    code(r"""class Gradebook:
    def __init__(self, csv_file):
        with open(csv_file, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)
            self.subjects = [c for c in reader.fieldnames if c != "name"]
        self.results, self.skipped = build_report(self.rows, self.subjects)

    def top(self, n=3):
        return [r["name"] for r in self.results[:n]]

    def lookup(self, name):
        for r in self.results:
            if r["name"].lower() == name.lower():
                return r
        return None

book = Gradebook(csv_path)
print("Top 3:", book.top())
print("Ravi:", book.lookup("ravi"))
print("Meera:", book.lookup("Meera"))   # None - her row was skipped"""),
    md(r"""## Bonus — A tiny text adventure

Games are a fun way to practise dicts, loops and functions. The whole map is a dict of rooms. Normally the player types commands with `input()`, but notebooks run automatically here, so we feed a **scripted list of commands** instead. To play for real, run `python code/text_adventure.py` in a terminal."""),
    code(r"""ROOMS = {
    "lab": {"text": "The AI lab. Doors north and east.",
            "exits": {"north": "library", "east": "server room"}},
    "library": {"text": "Books everywhere. A note: 'the key is in the server room'.",
                "exits": {"south": "lab"}},
    "server room": {"text": "Blinking lights. A KEY lies here. Exits: west, locked door north.",
                    "exits": {"west": "lab", "north": "exit"}, "item": "key"},
    "exit": {"text": "You unlock the door and step outside. You win!", "exits": {}},
}

def play(commands):
    room, inventory = "lab", set()
    print(f"[{room}] {ROOMS[room]['text']}")
    for command in commands:
        print(f"> {command}")
        if command == "take":
            item = ROOMS[room].get("item")
            if item:
                inventory.add(item)
                print(f"You take the {item}.")
            else:
                print("Nothing here.")
            continue
        exits = ROOMS[room]["exits"]
        if command not in exits:
            print(f"Can't go {command}. Exits: {', '.join(exits)}")
            continue
        if exits[command] == "exit" and "key" not in inventory:
            print("Locked. You need a key.")
            continue
        room = exits[command]
        print(f"[{room}] {ROOMS[room]['text']}")
        if room == "exit":
            return True
    return False

won = play(["north", "south", "east", "north", "take", "jump", "north"])
print("Won:", won)"""),
    md(r"""## Clean up"""),
    code(r"""for p in [csv_path, out_path]:
    p.unlink(missing_ok=True)
print("Removed practice files.")"""),
    md(r"""## Extend it yourself

1. Add a `history` subject column to the CSV. Does your code need changes? (It should not — that is why we read subjects from the header.)
2. Add **weights**: maths counts double. Compute a weighted average.
3. Write the report to a new CSV with `csv.DictWriter`.
4. In the adventure, add a new room and a second item needed to win.
5. Move the grade functions into `grades.py` and import them in a fresh notebook.

You have used: variables, strings, f-strings, lists, tuples, dicts, sets, comprehensions, conditions, loops, functions, lambdas, exceptions, files, JSON, modules and a class. That is the whole module — well done."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-basics.ipynb")
    notebook(NB2, NB / "02-collections.ipynb")
    notebook(NB3, NB / "03-functions-errors-files.ipynb")
    notebook(NB4, NB / "04-mini-project-grade-calculator.ipynb")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    deck = {
        "title": "Module 01 - Python basics",
        "subtitle": "Zero to confident - Python to Pro AI Engineer curriculum",
        "slides": [
            {"title": "Why Python for AI?",
             "bullets": ["Every major AI library is used from Python",
                         "PyTorch, Hugging Face, OpenAI / Anthropic SDKs, LangGraph",
                         "Reads almost like English",
                         "Today: the core language you will use every day"],
             "notes": "Open by showing one line of a real AI call, like client.messages.create(model=..., messages=[...]). Tell students that by the end of this module they will understand every symbol in it: function call, keyword arguments, a list of dictionaries. That is our target."},
            {"title": "Programs, print and comments",
             "bullets": ["A program is a list of statements run top to bottom",
                         "print(...) shows a value on screen",
                         "# starts a comment - notes for humans",
                         "Analogy: a recipe, one step per line"],
             "code": "# my first program\nprint(\"Hello, AI engineer!\")\nprint(2 + 3)",
             "notes": "Have everyone run this in a notebook or a .py file. Point out that the brackets after print mean 'call this function', and the thing inside is the argument."},
            {"title": "Values, types and variables",
             "bullets": ["Types: int, float, str, bool, None",
                         "type(x) tells you the type",
                         "= means 'now refers to', not 'equals'",
                         "Variables are name tags on values"],
             "image": str(IMG / "variables-labels.png"),
             "notes": "Use the sticky-note analogy: the value is the object, the variable is a tag you can move. Walk through score = score + 5: the right side is worked out first using the old value, then the tag moves. Ask: what is the type of '42'? It is str, not int."},
            {"title": "Numbers and conversion",
             "bullets": ["/ gives a float; // whole part; % remainder; ** power",
                         "Data from files and input() is always text",
                         "Convert: int(), float(), str()",
                         "0.1 + 0.2 is not exactly 0.3 - use round()"],
             "code": "print(7 / 2, 7 // 2, 7 % 2)\nprint(\"42\" + \"42\")      # 4242\nprint(int(\"42\") + 42)    # 84\nprint(round(0.1 + 0.2, 2))",
             "notes": "The '42' + '42' example is the one students remember. Explain that this is the source of many bugs when reading CSV files and forms."},
            {"title": "Strings and f-strings",
             "bullets": ["Index from 0; negative counts from the end",
                         "Slice [a:b] stops BEFORE b",
                         "Methods: strip, lower, split, join, replace",
                         "f\"{value:.2f}\" inserts and formats values"],
             "code": "word = \"Python\"\nprint(word[0], word[-1], word[0:3])\nacc = 0.9123\nprint(f\"Accuracy: {acc:.1%}\")\nprompt = f\"Explain {word} simply.\"",
             "notes": "Draw the word Python on the board with index numbers under each letter. f-strings are how students will build prompts for language models in module 08, so spend time here."},
            {"title": "Collections: which one?",
             "bullets": ["list - ordered, changeable [ ]",
                         "tuple - ordered, fixed ( )",
                         "dict - look up by key {k: v}",
                         "set - unique items { }"],
             "image": str(IMG / "collections-chooser.png"),
             "notes": "Analogies: list = numbered lockers; tuple = a sealed envelope; dict = a real dictionary you look up by word; set = a guest list where each name appears once. Walk through the flowchart with examples: shopping list (list), GPS coordinate (tuple), phone book (dict), unique tags (set)."},
            {"title": "Lists and dicts in practice",
             "bullets": ["append, insert, remove, pop, sort",
                         "b = a is NOT a copy - use a.copy()",
                         "d.get(key, default) avoids KeyError",
                         "An AI chat is a list of dicts"],
             "code": "messages = [\n  {\"role\": \"system\", \"content\": \"Be brief.\"},\n  {\"role\": \"user\", \"content\": \"Hi!\"},\n]\nmessages.append({\"role\": \"user\",\n                 \"content\": \"What is a set?\"})\nprint(messages[-1][\"content\"])",
             "notes": "Show the copy trap live from notebook 2: change b and watch a change. Then show the messages example and point out it is exactly the shape AI APIs expect."},
            {"title": "Decisions: if / elif / else",
             "bullets": ["Comparisons: == != < > <= >= in",
                         "Combine with and, or, not",
                         "Only the FIRST true branch runs",
                         "Indent 4 spaces; line before ends with :"],
             "code": "score = 78\nif score >= 90:\n    grade = \"A\"\nelif score >= 75:\n    grade = \"B\"\nelse:\n    grade = \"C\"\nprint(grade)",
             "notes": "Railway junction analogy: the train takes exactly one track. Ask: what happens if we put score >= 60 first? Every passing student gets the same grade. Order matters."},
            {"title": "Loops",
             "bullets": ["for item in collection: runs once per item",
                         "range(n), enumerate(), zip()",
                         "while condition: repeats while True",
                         "break leaves; continue skips"],
             "image": str(IMG / "for-loop.png"),
             "notes": "Analogy: a teacher calling the register, one name at a time. Do FizzBuzz together on the board before running it. Show Ctrl+C or the stop button for an infinite while loop."},
            {"title": "Comprehensions",
             "bullets": ["[expr for x in items if condition]",
                         "Read it as English",
                         "Also dict {k: v for ...} and set {x for ...}",
                         "If it gets long, use a normal loop"],
             "code": "nums = range(1, 7)\nsquares = [n * n for n in nums]\nevens = [n for n in nums if n % 2 == 0]\nlengths = {w: len(w) for w in [\"ai\", \"data\"]}",
             "notes": "Write the loop version first, then the comprehension, and show they give the same result. Stress readability: clear beats clever."},
            {"title": "Functions",
             "bullets": ["def name(params): ... return value",
                         "Parameters are placeholders; arguments are real values",
                         "Defaults and keyword arguments",
                         "Variables inside are local"],
             "image": str(IMG / "function-machine.png"),
             "notes": "Juice machine analogy: fruit in, juice out, you do not rebuild the machine each time. Show a function without return printing None. Connect keyword arguments to AI SDK calls like max_tokens=200."},
            {"title": "Errors and try / except",
             "bullets": ["SyntaxError: not valid Python",
                         "Exceptions: go wrong while running",
                         "Catch SPECIFIC errors: except ValueError",
                         "else = no error; finally = always",
                         "raise ValueError(...) to reject bad input"],
             "image": str(IMG / "try-except.png"),
             "notes": "Safety-net analogy. Warn against bare except, which hides typos. Show the safe_divide example from notebook 3 with three different inputs."},
            {"title": "Reading a traceback",
             "bullets": ["Read from the BOTTOM up",
                         "Last line: WHAT went wrong",
                         "Frame above: WHERE (file, line, function)",
                         "Further up: HOW you got there",
                         "Find the lowest frame in YOUR code"],
             "image": str(IMG / "traceback-reading.png"),
             "notes": "Run code/traceback_demo.py --crash live and read the output together, bottom up. Ask a student to tell you which line to fix. Emphasise: errors are information, not failure. Python often suggests the fix with 'Did you mean'."},
            {"title": "Files, pathlib and JSON",
             "bullets": ["with open(path, mode, encoding=\"utf-8\") as f:",
                         "Modes: \"r\" read, \"w\" write, \"a\" append",
                         "Path(\"data\") / \"file.txt\" works on every OS",
                         "json.dump / json.load for dicts and lists"],
             "code": "from pathlib import Path\nimport json\np = Path(\"config.json\")\np.write_text(json.dumps({\"t\": 0.2}))\nprint(json.loads(p.read_text()))",
             "notes": "Explain that with closes the file even if an error happens. Mention that JSON is the language of APIs, so json.loads is something they will use in almost every AI project."},
            {"title": "Modules and classes",
             "bullets": ["import math; from random import choice; import numpy as np",
                         "Your own .py file is a module",
                         "if __name__ == \"__main__\": run only when executed",
                         "Class = blueprint; object = one thing built from it",
                         "__init__ sets attributes; methods use self"],
             "code": "class Student:\n    def __init__(self, name):\n        self.name = name\n        self.scores = []\n    def add(self, s):\n        self.scores.append(s)\n\nasha = Student(\"Asha\")\nasha.add(90)",
             "notes": "Cookie cutter analogy for classes. Students will mostly USE objects in this course: DataFrames, models, API clients. Writing big classes is not needed yet."},
            {"title": "Common mistakes",
             "bullets": ["= vs ==  (assign vs compare)",
                         "Forgetting the colon or the indent",
                         "\"5\" + 3 - convert types first",
                         "Off-by-one: last index is len - 1",
                         "Bare except hides real bugs",
                         "Notebook cells run out of order"],
             "notes": "For each mistake, show the error message it produces. This links back to the traceback slide: every mistake on this list has a recognisable last line."},
            {"title": "Mini-project: grade calculator",
             "bullets": ["Read a messy CSV of marks",
                         "Skip bad rows with clear messages",
                         "Average + letter grade per student",
                         "Ranked report, class stats, save JSON"],
             "notes": "Walk through notebook 4 step by step. Make the point that each function was tested before moving on. Then let students try the 'extend it yourself' tasks in pairs."},
            {"title": "Recap and exercises",
             "bullets": ["Types, strings, collections, conditions, loops",
                         "Functions, exceptions, tracebacks, files, modules, classes",
                         "Exercises 1-5 in class; 6-14 as homework",
                         "Cheat sheet: excel/python-cheatsheet.xlsx"],
             "notes": "Ask three quick check questions from trainer-notes.md. Hand out the cheat sheet. Remind students that the only way to learn Python is to type it, break it and fix it."},
        ],
    }
    slides(deck, HERE / "slides" / "01-python-basics.pptx")


# ---------------------------------------------------------------------------
# 4. Excel cheat sheet
# ---------------------------------------------------------------------------
CHEATSHEET = [
    ("Basics", "Print", 'print(value, ...)', 'print("Total:", 42)', "Forgetting quotes around text: print(Hello)"),
    ("Basics", "Comment", "# note", "x = 5  # five apples", "Using // or /* */ from other languages"),
    ("Basics", "Variable", "name = value", 'model_name = "bert"', "Using = when you mean == in a condition"),
    ("Basics", "Check type", "type(x)", 'type("3")  # str', "Assuming input/CSV values are numbers"),
    ("Numbers", "Division", "a / b, a // b, a % b", "7 / 2 -> 3.5; 7 // 2 -> 3; 7 % 2 -> 1", "Expecting / to give an int"),
    ("Numbers", "Power", "a ** b", "2 ** 10 -> 1024", "Using ^ (that is bitwise XOR in Python)"),
    ("Numbers", "Update in place", "x += 1", "count += 1", "Writing x++ (not valid Python)"),
    ("Numbers", "Round", "round(x, n)", "round(3.14159, 2) -> 3.14", "Comparing floats with == (0.1 + 0.2 != 0.3)"),
    ("Conversion", "Text to number", "int(s), float(s)", 'int("42") -> 42', 'int("3.5") fails - use float first'),
    ("Conversion", "Number to text", "str(x)", 'str(7) + " days"', '"Score: " + 95 -> TypeError'),
    ("Strings", "Index", "s[i]", '"Python"[0] -> "P"', "Starting to count at 1"),
    ("Strings", "Slice", "s[start:stop]", '"Python"[0:3] -> "Pyt"', "Expecting stop to be included"),
    ("Strings", "Length", "len(s)", 'len("data") -> 4', "Writing s.len() or s.length"),
    ("Strings", "Clean up", "s.strip(), s.lower()", '"  Hi ".strip().lower() -> "hi"', "Not saving the result (strings are immutable)"),
    ("Strings", "Split / join", 's.split(","), ",".join(list)', '"a,b".split(",") -> ["a","b"]', "Calling list.join(sep) instead of sep.join(list)"),
    ("Strings", "Contains", "sub in s", '"ai" in "brain" -> True', "Case matters: 'AI' in 'brain' is False"),
    ("Strings", "f-string", 'f"{value:.2f}"', 'f"Acc: {0.912:.1%}" -> Acc: 91.2%', "Forgetting the f prefix: braces print literally"),
    ("Strings", "Multi-line", '"""text"""', 'prompt = """Line 1\\nLine 2"""', "Mixing quote types inside without escaping"),
    ("Lists", "Create", "[a, b, c]", "scores = [72, 88, 95]", "Using () when you need to change it later"),
    ("Lists", "Add", "lst.append(x), lst.insert(i, x)", "scores.append(81)", "lst = lst.append(x) sets lst to None"),
    ("Lists", "Remove", "lst.remove(x), lst.pop(i)", "scores.pop() -> last item", "remove() deletes only the first match"),
    ("Lists", "Sort", "lst.sort(), sorted(lst)", "sorted(scores, reverse=True)", "x = lst.sort() gives None; use sorted()"),
    ("Lists", "Copy", "lst.copy()", "backup = scores.copy()", "b = a makes two names for ONE list"),
    ("Lists", "Last item", "lst[-1]", "scores[-1]", "lst[len(lst)] -> IndexError (last is len-1)"),
    ("Tuples", "Create / unpack", "t = (a, b); x, y = t", "h, w = (28, 28)", "One-item tuple needs a comma: (5,)"),
    ("Dicts", "Create", "{key: value}", '{"name": "Ravi", "age": 20}', "Duplicate keys - the last one wins"),
    ("Dicts", "Get value", "d[key], d.get(key, default)", 'd.get("email", "n/a")', "d[missing] -> KeyError"),
    ("Dicts", "Add / change", "d[key] = value", 'd["city"] = "Pune"', "Using a list as a key (must be immutable)"),
    ("Dicts", "Loop", "for k, v in d.items():", "for name, mark in marks.items():", "Looping over d gives only keys"),
    ("Dicts", "Count things", "d[k] = d.get(k, 0) + 1", "counts[word] = counts.get(word, 0) + 1", "d[k] += 1 on a new key -> KeyError"),
    ("Sets", "Create", "{a, b}, set(list)", 'set(["a", "a", "b"]) -> {"a","b"}', "{} is an empty DICT; use set()"),
    ("Sets", "Combine", "a & b, a | b, a - b", '{"py","sql"} & {"py"} -> {"py"}', "Expecting sets to keep order"),
    ("Conditions", "if / elif / else", "if c:\\n    ...\\nelif d:\\n    ...\\nelse:\\n    ...", "if score >= 90: grade = 'A'", "Missing colon or indentation"),
    ("Conditions", "Combine", "and, or, not", "if age >= 18 and has_id:", "Writing && or || from other languages"),
    ("Conditions", "One-line", "a if cond else b", 'label = "pass" if s >= 60 else "fail"', "Putting else before if"),
    ("Loops", "for", "for item in items:", "for review in reviews:", "Changing a list while looping over it"),
    ("Loops", "range", "range(start, stop, step)", "range(1, 6) -> 1..5", "Expecting stop to be included"),
    ("Loops", "Index + item", "enumerate(items, start=1)", "for i, name in enumerate(names):", "Using range(len(x)) everywhere"),
    ("Loops", "Two lists", "zip(a, b)", "for n, m in zip(names, marks):", "zip stops at the shorter list silently"),
    ("Loops", "while", "while condition:", "while balance < 200:", "Forgetting to change the condition -> infinite loop"),
    ("Loops", "break / continue", "break, continue", "if n < 0: continue", "break only leaves the innermost loop"),
    ("Comprehensions", "List", "[expr for x in xs if cond]", "[n*n for n in nums if n % 2 == 0]", "Cramming too much logic into one line"),
    ("Comprehensions", "Dict / set", "{k: v for ...}, {x for ...}", "{w: len(w) for w in words}", "Forgetting the colon makes a set, not a dict"),
    ("Functions", "Define", "def name(params):\\n    return value", "def average(xs): return sum(xs)/len(xs)", "Forgetting return -> function gives None"),
    ("Functions", "Default argument", "def f(x, y=10):", 'def greet(name, greeting="Hello"):', "Using a mutable default like y=[]"),
    ("Functions", "Keyword call", "f(y=1, x=2)", "create(model=m, max_tokens=200)", "Positional argument after a keyword one"),
    ("Functions", "Multiple returns", "return a, b", "low, high = min_max(xs)", "Unpacking into the wrong number of names"),
    ("Functions", "Lambda", "lambda args: expr", "sorted(pairs, key=lambda p: p[1])", "Using lambdas for long logic - use def"),
    ("Errors", "try / except", "try:\\n    ...\\nexcept ValueError as err:\\n    ...", 'try: int("x")\\nexcept ValueError: ...', "Bare except: hides typos and real bugs"),
    ("Errors", "else / finally", "else: (no error)  finally: (always)", "finally: print('done')", "Putting too much code inside try"),
    ("Errors", "Raise", "raise ValueError(msg)", 'raise ValueError("temp must be 0-2")', "Returning an error string instead of raising"),
    ("Errors", "Read traceback", "Read bottom up", "Last line = what; frame above = where", "Reading from the top and panicking"),
    ("Files", "Read", 'with open(p, encoding="utf-8") as f:', "text = f.read()", "Forgetting encoding -> garbled characters on Windows"),
    ("Files", "Write / append", 'open(p, "w") / open(p, "a")', 'f.write("line\\n")', '"w" erases the existing file'),
    ("Files", "Paths", "from pathlib import Path", 'Path("data") / "scores.csv"', "Hard-coding C:\\\\ paths that break on Mac/Linux"),
    ("Files", "JSON", "json.dump(obj, f) / json.load(f)", "cfg = json.load(f)", "json.dump needs a file; json.dumps returns a string"),
    ("Modules", "Import", "import m; from m import x; import m as a", "import numpy as np", "Naming your file the same as a library (e.g. json.py)"),
    ("Modules", "Main guard", 'if __name__ == "__main__":', "    main()", "Putting test code at top level so it runs on import"),
    ("Classes", "Define", "class Name:\\n    def __init__(self, ...):", "class Student: ...", "Forgetting self as the first method parameter"),
    ("Classes", "Create / use", "obj = Name(args); obj.method()", 'asha = Student("Asha"); asha.add_score(90)', "Calling Student.add_score(90) on the class, not an object"),
]


def build_excel():
    rows = [["#", "Topic", "Concept", "Syntax", "Example", "Common mistake"]]
    for i, (topic, concept, syntax, example, mistake) in enumerate(CHEATSHEET, start=1):
        rows.append([i, topic, concept, syntax.replace("\\n", "\n"), example.replace("\\n", "\n"), mistake])
    errors = [["Exception (last line of traceback)", "Plain-English meaning", "Typical cause", "Typical fix"],
        ["SyntaxError", "Not valid Python", "Missing bracket, quote or colon", "Look at the caret ^ and the line before it"],
        ["IndentationError", "Spaces at line start are wrong", "No indent after a line ending in :", "Indent the block 4 spaces; do not mix tabs and spaces"],
        ["NameError", "Name is not defined", "Typo, or the defining cell was not run", "Check spelling; run cells from the top"],
        ["TypeError", "Wrong type for this operation", '"5" + 3; calling with wrong number of arguments', "Convert types; check the function's parameters"],
        ["ValueError", "Right type, bad value", 'int("abc")', "Validate or clean the data; use try/except"],
        ["IndexError", "Position past the end", "lst[len(lst)]", "Last index is len - 1; check the list is not empty"],
        ["KeyError", "Key not in dict", 'd["missing"]', 'Use d.get(key, default) or check "key in d"'],
        ["AttributeError", "No such method/attribute", '"abc".uppr(); calling a method on None', "Check spelling (read 'Did you mean'); check the value is not None"],
        ["ZeroDivisionError", "Divided by zero", "Average of an empty list", "Check the length first"],
        ["FileNotFoundError", "Path does not exist", "Wrong folder or file name", "print(Path.cwd()); use pathlib; check spelling"],
        ["ModuleNotFoundError", "Package not installed here", "Wrong venv / kernel; typo", "python -m pip install pkg in the right environment"],
        ["RecursionError", "Function called itself too many times", "Missing stop condition", "Add a base case"],
    ]
    workbook({"Cheat sheet": rows, "Error guide": errors},
             HERE / "excel" / "python-cheatsheet.xlsx",
             col_widths={"Cheat sheet": [5, 15, 18, 38, 42, 48],
                         "Error guide": [30, 32, 42, 55]})


def build_pdf():
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / "01-python-basics-handout.pdf",
                      title="Module 01 - Python basics")


if __name__ == "__main__":
    build_images()
    build_notebooks()
    build_slides()
    build_excel()
    build_pdf()
    print("01-python-basics built.")
