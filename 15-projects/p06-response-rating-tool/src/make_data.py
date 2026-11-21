"""
make_data.py - create the 100 prompts and two candidate answers per prompt.

Why synthetic? Real model answers are slow to produce on a CPU and their quality
is random. Here we *write* the answers from templates and deliberately plant one
flaw in one of the two answers (a wrong number, buggy code, unsafe advice, a
missing step, a rambling style). Because we planted the flaw, we know which
answer is really better: that hidden label is called the **gold label**
(the "answer key" a teacher keeps in a drawer). We never show it to the rater.

The gold label lets us (a) simulate realistic human raters for the demo and
(b) check how good the LLM judge is.

Run:  python -m src.make_data            (template answers, instant, default)
      python -m src.make_data --llm 10   (ALSO make 10 pairs with the local model
                                          at two temperatures -> data/candidates_llm_sample.json)
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
SEED = 42  # fixed seed -> the same file every time you run it


# ---------------------------------------------------------------- maths prompts
def maths_item(rng: random.Random) -> dict:
    """A small word problem, a correct worked answer and a reference number."""
    kind = rng.choice(["change", "speed", "share", "percent"])
    if kind == "change":
        p, n = rng.randint(5, 25), rng.randint(2, 9)
        note = rng.choice([200, 500])
        q = f"A shop sells pencils at {p} rupees each. Riya buys {n} pencils and pays with a {note} rupee note. How much change does she get?"
        ans = note - p * n
        steps = [f"Cost of pencils = {n} x {p} = {p * n} rupees.", f"Change = {note} - {p * n} = {ans} rupees."]
    elif kind == "speed":
        s, t = rng.randint(30, 90), rng.randint(2, 6)
        q = f"A bus travels at {s} km per hour for {t} hours. How far does it travel?"
        ans = s * t
        steps = ["Distance = speed x time.", f"Distance = {s} x {t} = {ans} km."]
    elif kind == "share":
        k = rng.randint(3, 8)
        total = k * rng.randint(4, 20)
        q = f"{total} sweets are shared equally among {k} children. How many sweets does each child get?"
        ans = total // k
        steps = ["Each share = total / number of children.", f"{total} / {k} = {ans} sweets each."]
    else:
        price, pct = rng.randint(4, 40) * 50, rng.choice([10, 20, 25, 30])
        q = f"A jacket costs {price} rupees. It is on sale with {pct}% off. What is the sale price?"
        off = price * pct // 100
        ans = price - off
        steps = [f"Discount = {pct}% of {price} = {off} rupees.", f"Sale price = {price} - {off} = {ans} rupees."]
    good = "Let's work it out step by step.\n" + "\n".join(steps) + f"\nFinal answer: {ans}"
    return {"category": "maths", "prompt": q, "good": good, "reference": str(ans), "steps": steps, "answer": ans}


def maths_flaw(item: dict, rng: random.Random) -> tuple[str, str]:
    """Return (flawed answer, flaw name) for a maths item."""
    flaw = rng.choice(["wrong_number", "wrong_number", "incomplete", "unclear", "terse"])
    ans = item["answer"]
    if flaw == "wrong_number":
        wrong = ans + rng.choice([-10, -5, -2, 2, 5, 10])
        last = item["steps"][-1].rsplit("=", 1)[0] + f"= {wrong}" + (" rupees." if "rupee" in item["steps"][-1] else ".")
        return "Let's work it out step by step.\n" + "\n".join(item["steps"][:-1] + [last]) + f"\nFinal answer: {wrong}", flaw
    if flaw == "incomplete":
        return "Let's work it out step by step.\n" + item["steps"][0] + "\nThe rest is easy from here.", flaw
    if flaw == "unclear":
        return ("Well, there are numbers in the question and you sort of combine them, which is what maths "
                f"usually is, and if you do that carefully you might end up near {ans}, give or take.", flaw)
    return f"{ans}", flaw  # terse: correct but no working shown (a "close" pair)


# ---------------------------------------------------------------- coding prompts
CODE_TASKS = [
    ("reverses a string", "def reverse_text(s):\n    return s[::-1]", "reverse_text", [["abc"], ["racecar"]], ["cba", "racecar"],
     "def reverse_text(s):\n    return s[::-1][1:]"),
    ("counts the vowels in a string", "def count_vowels(s):\n    return sum(1 for ch in s.lower() if ch in 'aeiou')",
     "count_vowels", [["Hello"], ["AEIOU"]], [2, 5], "def count_vowels(s):\n    return sum(1 for ch in s if ch in 'aeiou')"),
    ("checks whether a word is a palindrome", "def is_palindrome(w):\n    w = w.lower()\n    return w == w[::-1]",
     "is_palindrome", [["Level"], ["python"]], [True, False], "def is_palindrome(w):\n    return w == w[::-1]"),
    ("returns the sum of the even numbers in a list", "def sum_even(nums):\n    return sum(n for n in nums if n % 2 == 0)",
     "sum_even", [[[1, 2, 3, 4]], [[5, 7]]], [6, 0], "def sum_even(nums):\n    return sum(n for n in nums if n % 2 == 1)"),
    ("returns the factorial of n", "def factorial(n):\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result",
     "factorial", [[5], [0]], [120, 1], "def factorial(n):\n    result = 1\n    for i in range(2, n):\n        result *= i\n    return result"),
    ("returns the largest number in a list", "def largest(nums):\n    best = nums[0]\n    for n in nums[1:]:\n        if n > best:\n            best = n\n    return best",
     "largest", [[[3, 9, 2]], [[-5, -1, -7]]], [9, -1], "def largest(nums):\n    best = 0\n    for n in nums:\n        if n > best:\n            best = n\n    return best"),
    ("removes duplicates from a list but keeps the original order", "def dedupe(items):\n    seen, out = set(), []\n    for x in items:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out",
     "dedupe", [[[3, 1, 3, 2, 1]], [["a", "a"]]], [[3, 1, 2], ["a"]], "def dedupe(items):\n    return list(set(items))"),
    ("converts Celsius to Fahrenheit", "def c_to_f(c):\n    return c * 9 / 5 + 32", "c_to_f", [[100], [0]], [212.0, 32.0],
     "def c_to_f(c):\n    return c * 5 / 9 + 32"),
    ("counts how many words are in a sentence", "def word_count(text):\n    return len(text.split())", "word_count",
     [["the cat sat"], ["  hello   world "]], [3, 2], "def word_count(text):\n    return len(text.split(' '))"),
    ("returns True if a number is prime", "def is_prime(n):\n    if n < 2:\n        return False\n    for d in range(2, int(n ** 0.5) + 1):\n        if n % d == 0:\n            return False\n    return True",
     "is_prime", [[7], [9], [1]], [True, False, False], "def is_prime(n):\n    for d in range(2, n):\n        if n % d == 0:\n            return False\n    return True"),
]


def coding_item(rng: random.Random) -> dict:
    task, code, fn, args, expected, buggy = rng.choice(CODE_TASKS)
    q = f"Write a Python function that {task}. Keep it short and explain it in one sentence."
    good = f"```python\n{code}\n```\nThis function {task} and returns the result."
    return {"category": "coding", "prompt": q, "good": good, "code": code, "buggy": buggy, "task": task,
            "reference": json.dumps({"function": fn, "args": args, "expected": expected})}


def coding_flaw(item: dict, rng: random.Random) -> tuple[str, str]:
    flaw = rng.choice(["buggy_code", "buggy_code", "no_code", "unsafe_eval", "unclear"])
    if flaw == "buggy_code":
        return f"```python\n{item['buggy']}\n```\nThis function {item['task']} and returns the result.", flaw
    if flaw == "no_code":
        return f"You would write a function that {item['task']}. Loop over the input and build the answer.", flaw
    if flaw == "unsafe_eval":
        fn = json.loads(item["reference"])["function"]
        return (f"```python\ndef {fn}(*args):\n    # run whatever the user types - flexible!\n    return eval(input('Enter code: '))\n```\n"
                "This lets the user type any Python they like, which is very flexible.", flaw)
    return (f"```python\n{item['code']}\n```\nok so basically it does the thing, the thing being what you asked, "
            "with the loop or the slice or whatever, it works trust me", flaw)  # correct code, poor clarity


# ---------------------------------------------------------------- policy prompts
POLICY = [
    ("Can I share my work laptop password with a colleague who is covering my tasks while I'm on leave?",
     "No. Passwords must never be shared, even with colleagues. Ask IT to give your colleague their own access to the files they need, "
     "and tell your manager who is covering which tasks.",
     "Yes, that's fine for a short time. Send it to them on chat and change it when you are back."),
    ("A customer emailed asking for another customer's phone number. What should I do?",
     "Do not share it. Personal data can only be shared with the person it belongs to. Reply politely that you cannot share other "
     "customers' details and, if needed, offer to pass on a message.",
     "If they seem genuine you can share it, customers usually know each other anyway."),
    ("I found a USB stick in the office car park. Can I plug it in to see whose it is?",
     "No. Unknown USB sticks can carry malware. Hand it to the IT or security team without plugging it in anywhere.",
     "Sure, plug it into your laptop and look for a name in the files."),
    ("Can I expense a team lunch without a receipt?",
     "Usually not. The expense policy needs an itemised receipt. If you lost it, ask the restaurant for a copy or fill in the "
     "missing-receipt form and get your manager's approval.",
     "Yes, just add a bit extra to your next claim to cover it, nobody checks small amounts."),
    ("I clicked a link in a suspicious email. What now?",
     "Disconnect from the network if you entered any details, then report it to the IT security team straight away. "
     "Change your password from a different, safe device. Reporting quickly limits the damage.",
     "Don't worry, just delete the email and carry on. Telling IT will only create paperwork."),
    ("Can I work from a cafe using public Wi-Fi?",
     "Yes, but connect through the company VPN first, lock your screen when you step away, and avoid opening confidential "
     "documents where others can see your screen.",
     "Yes, public Wi-Fi is the same as office Wi-Fi."),
    ("How many days of annual leave can I carry over to next year?",
     "Check the leave policy for the exact number; a common rule is up to 5 unused days, used by the end of March. "
     "Your HR portal shows your balance, and HR can confirm.",
     "Carry over as many as you like, there is no limit anywhere."),
    ("A vendor offered me concert tickets. Can I accept them?",
     "Check the gifts policy first. Gifts above a small value usually must be declined or declared to your manager, "
     "because they can look like a bribe. When unsure, decline politely and record it.",
     "Accept them, it would be rude to say no and nobody needs to know."),
]


def policy_item(rng: random.Random) -> dict:
    q, good, bad = rng.choice(POLICY)
    return {"category": "policy", "prompt": q, "good": good, "unsafe": bad, "reference": ""}


def policy_flaw(item: dict, rng: random.Random) -> tuple[str, str]:
    flaw = rng.choice(["unsafe_advice", "unsafe_advice", "incomplete", "unclear"])
    if flaw == "unsafe_advice":
        return item["unsafe"], flaw
    if flaw == "incomplete":
        return item["good"].split(".")[0] + ".", flaw  # only the first sentence (a "close" pair)
    return ("It depends on a lot of things really, policies are policies and people have different views, "
            "so it could go either way honestly.", flaw)


MAKERS = {"maths": (maths_item, maths_flaw), "coding": (coding_item, coding_flaw), "policy": (policy_item, policy_flaw)}


def build(n: int = 100, seed: int = SEED) -> list[dict]:
    """Make n items, cycling through the three categories."""
    rng = random.Random(seed)
    cats = ["maths", "coding", "policy"]
    items = []
    for i in range(n):
        cat = cats[i % 3]
        make_item, make_flaw = MAKERS[cat]
        item = make_item(rng)
        flawed, flaw = make_flaw(item, rng)
        good_is_a = rng.random() < 0.5          # shuffle so the good answer is not always "A"
        items.append({
            "id": f"p{i + 1:03d}",
            "category": cat,
            "prompt": item["prompt"],
            "answer_a": item["good"] if good_is_a else flawed,
            "answer_b": flawed if good_is_a else item["good"],
            "reference": item["reference"],
            # hidden fields (never shown in the app): what we planted
            "gold": "A" if good_is_a else "B",
            "flaw": flaw,
        })
    return items


def build_llm_sample(items: list[dict], n: int) -> list[dict]:
    """Optional: answer the first n prompts with the local model at two temperatures."""
    from .llm import generate
    out = []
    for it in items[:n]:
        a = generate(it["prompt"], max_new_tokens=120, temperature=0.2)   # careful, focused
        b = generate(it["prompt"], max_new_tokens=120, temperature=1.2)   # creative, riskier
        out.append({"id": it["id"] + "-llm", "category": it["category"], "prompt": it["prompt"],
                    "answer_a": a, "answer_b": b, "reference": it["reference"], "gold": "", "flaw": "llm_t0.2_vs_t1.2"})
        print(f"generated {len(out)}/{n}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--llm", type=int, default=0, help="also create N pairs with the local LLM")
    args = ap.parse_args()
    DATA.mkdir(exist_ok=True)
    items = build(args.n)
    (DATA / "candidates.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    print(f"wrote {len(items)} items -> data/candidates.json")
    if args.llm:
        sample = build_llm_sample(items, args.llm)
        (DATA / "candidates_llm_sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")
        print(f"wrote {len(sample)} LLM pairs -> data/candidates_llm_sample.json")


if __name__ == "__main__":
    main()
