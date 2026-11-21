"""
solutions.py - runnable solutions for module 12 exercises 3, 6, 7, 8, 10 and 11.

Run from the module folder:  python solutions/solutions.py
"""
import json                                          # read/write JSON
import pathlib                                       # file paths
import tempfile                                      # a temporary file for exercise 7
import numpy as np                                   # arrays
import torch                                         # tensors
import torch.nn.functional as F                      # logsigmoid
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import cohen_kappa_score

HERE = pathlib.Path(__file__).resolve().parent.parent


def ex3():
    """Exercise 3: kappa by hand and with sklearn."""
    a, b = list("SHHHSHHHHS"), list("SHHSSHSHHH")
    p_o = np.mean(np.array(a) == np.array(b))
    p_e = sum((a.count(c) / len(a)) * (b.count(c) / len(b)) for c in "SH")
    print(f"Ex3: p_o={p_o:.2f} p_e={p_e:.2f} kappa={(p_o - p_e) / (1 - p_e):.3f} sklearn={cohen_kappa_score(a, b):.3f}")


def ex6():
    """Exercise 6: compare the sample labels with a simulated partner."""
    mine = ["POS", "NEG", "NEU", "NEG", "POS", "NEU", "POS", "NEG", "NEU", "NEG",
            "NEG", "POS", "NEU", "NEG", "NEU", "POS", "POS", "NEG", "NEU", "NEU"]
    partner = list(mine)
    partner[3] = "POS"      # took sarcasm literally
    partner[9] = "NEU"      # 'Returned for a refund.' seen as neutral
    partner[14] = "POS"     # 'Decent.' seen as positive
    k = cohen_kappa_score(mine, partner)
    diffs = [i for i, (x, y) in enumerate(zip(mine, partner)) if x != y]
    print(f"Ex6: kappa={k:.2f}, disagreements on items {diffs}")


def validate_preferences(path):
    """Exercise 7: check a preference JSONL file. Returns a list of problems (empty = valid)."""
    problems = []
    for n, line in enumerate(pathlib.Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue                                  # skip blank lines
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            problems.append(f"line {n}: not valid JSON ({e})")
            continue
        if set(row) != {"prompt", "chosen", "rejected"}:
            problems.append(f"line {n}: keys are {sorted(row)}")
            continue
        if not all(isinstance(v, str) and v.strip() for v in row.values()):
            problems.append(f"line {n}: empty or non-string value")
        if row["chosen"].strip() == row["rejected"].strip():
            problems.append(f"line {n}: chosen and rejected are identical")
    return problems


def ex7():
    rows = [
        {"prompt": "How long should I boil an egg for a soft yolk?",
         "chosen": "About 6 minutes in boiling water, then cool it in cold water to stop cooking.",
         "rejected": "About 6 minutes."},
        {"prompt": "Bad row", "chosen": "same", "rejected": "same"},
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("Ex7 problems found:", validate_preferences(f.name))
    print("Ex7 sample file problems:", validate_preferences(HERE / "data" / "preference_pairs_sample.jsonl"))


def ex8():
    """Exercise 8: DPO loss with beta = 0.2."""
    beta = 0.2
    cr, rr = beta * (-20 + 22), beta * (-25 + 22)
    loss = -F.logsigmoid(torch.tensor(cr - rr)).item()
    print(f"Ex8: chosen reward {cr:.1f}, rejected reward {rr:.1f}, loss {loss:.4f}, identical-policy loss {np.log(2):.4f}")


def ex10():
    """Exercise 10: patch the reward model against word stuffing."""
    torch.manual_seed(0)
    good = ["To cook rice, rinse it, add water, boil, then simmer covered.",
            "To reset a password, open settings, choose security and follow the email link.",
            "To make tea, boil water, steep for three minutes, then add milk.",
            "To save money, track spending, set a budget and save first each payday."]
    bad = ["Figure it out yourself.", "Search online.", "That's a silly question.", "Just do it."]

    def train(chosen, rejected):
        vec = CountVectorizer(stop_words="english").fit(chosen + rejected)
        X = lambda t: torch.tensor(vec.transform(t).toarray(), dtype=torch.float32)
        m = torch.nn.Linear(len(vec.vocabulary_), 1)
        opt = torch.optim.Adam(m.parameters(), lr=0.05, weight_decay=0.01)
        for _ in range(300):
            loss = -F.logsigmoid(m(X(chosen)) - m(X(rejected))).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        return lambda t: m(X([t])).item()

    honest = "Rinse the rice, add water and simmer."
    score = train(good, bad)
    stuffed = "rinse water boil simmer steep budget settings email " * 3
    print(f"Ex10 before: honest {score(honest):+.2f}  stuffed {score(stuffed):+.2f}")
    # Add stuffed word-salad answers as REJECTED examples, paired with real answers.
    salads = ["water boil simmer rinse " * 3, "settings security email budget " * 3,
              "steep milk tea boil " * 3, "track spending save budget " * 3]
    score2 = train(good + good, bad + salads)
    print(f"Ex10 after : honest {score2(honest):+.2f}  stuffed {score2(stuffed):+.2f}")


def biased_pairwise_judge(q, first, second):
    """Stand-in judge with a +3 bonus for the first position (copied from notebook 04)."""
    s1 = len(set(first.lower().split())) + 3
    s2 = len(set(second.lower().split()))
    return "first" if s1 >= s2 else "second"


def position_bias_report(judge, pairs):
    """Exercise 11: run each pair in both orders; report first-pick rate and consistency."""
    first_picks, consistent = 0, 0
    for q, x, y in pairs:
        o1 = judge(q, x, y)                           # x shown first
        o2 = judge(q, y, x)                           # y shown first
        first_picks += (o1 == "first") + (o2 == "first")
        w1 = "x" if o1 == "first" else "y"
        w2 = "y" if o2 == "first" else "x"
        consistent += (w1 == w2)
    return {"first_pick_rate": first_picks / (2 * len(pairs)), "consistency": consistent / len(pairs)}


def ex11():
    # Pairs whose answers are close in length, so the +3 position bonus can flip the decision.
    pairs = [
        ("Define RAM.", "Short-term memory used while programs run.", "Fast memory a computer uses for running programs."),
        ("What is Git?", "A tool that tracks changes to files.", "Version control software for tracking code changes."),
        ("What is a loop?", "Code that repeats while a condition holds.", "A block of code that runs many times."),
        ("What is JSON?", "A text format for keys and values.", "A simple text format for storing structured data."),
        ("What is a GPU?", "A chip that does parallel maths fast.", "A processor built for graphics and parallel work."),
        ("What is an IDE?", "An editor with debugging and build tools.", "A program for writing and testing code."),
        ("What is SQL?", "A language for querying databases.", "The language used to ask databases questions."),
        ("What is a token?", "A piece of text a model reads.", "A word or part of a word for a model."),
    ]
    print("Ex11:", position_bias_report(biased_pairwise_judge, pairs))


if __name__ == "__main__":
    ex3(); ex6(); ex7(); ex8(); ex10(); ex11()
