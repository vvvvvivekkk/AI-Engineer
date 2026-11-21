"""
build.py - regenerate every generated file in module 12 (diagrams, notebooks, slides, PDF, Excel).

Run from the repo root:   python 12-data-annotation-and-rlhf/build.py
Optional flags:           --no-pdf   --no-images   --no-notebooks   (skip steps while editing)
"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from build_kit import mermaid, notebook, slides, pdf_from_markdown, workbook

MOD = HERE.name
IMG = HERE / "images"
NB = HERE / "notebooks"
ARGS = set(sys.argv[1:])

# ---------------------------------------------------------------------------
# 1. Diagrams (Mermaid -> PNG). Each also leaves a .mmd source next to the PNG.
# ---------------------------------------------------------------------------
DIAGRAMS = {
    "annotation-workflow": """
flowchart LR
    A[Raw data<br/>texts, images, chats] --> B[Write guidelines]
    B --> C[Pilot: 2-3 annotators<br/>label 50 items]
    C --> D{Agreement<br/>good enough?}
    D -- no --> E[Read disagreements<br/>fix guidelines]
    E --> C
    D -- yes --> F[Label at scale<br/>with gold questions]
    F --> G[Review and adjudicate]
    G --> H[(Labelled dataset)]
""",
    "qc-loop": """
flowchart TD
    A[Annotator labels a task] --> B{Is it a<br/>gold question?}
    B -- yes --> C[Compare with known answer]
    C --> D[Update annotator accuracy]
    B -- no --> E{Overlap item?<br/>labelled by 2+ people}
    E -- yes --> F[Compute agreement<br/>e.g. Cohen's kappa]
    F --> G{Disagree?}
    G -- yes --> H[Adjudicator decides]
    G -- no --> I[Accept label]
    E -- no --> J[Random spot check]
    J --> I
    H --> I
""",
    "rlhf-pipeline": """
flowchart LR
    P[Pre-trained LLM] --> S1
    subgraph S1[Stage 1: SFT]
      D1[Human-written<br/>demonstrations] --> M1[SFT model]
    end
    subgraph S2[Stage 2: Reward model]
      D2[Humans compare<br/>answer A vs B] --> RM[Reward model<br/>outputs a score]
    end
    subgraph S3[Stage 3: PPO]
      PO[Policy writes answers] --> SC[Reward minus<br/>KL penalty]
      SC --> PO
    end
    M1 --> S2
    M1 --> S3
    RM --> SC
    S3 --> F[Aligned assistant]
""",
    "rlhf-vs-dpo": """
flowchart TD
    subgraph R[RLHF with PPO]
      R1[Preference pairs] --> R2[Train reward model]
      R2 --> R3[Generate answers<br/>score them, PPO update]
      R3 --> R4[Aligned model]
    end
    subgraph D[DPO]
      D1[Preference pairs] --> D2[One supervised loss<br/>policy vs frozen reference]
      D2 --> D3[Aligned model]
    end
""",
    "eval-types": """
flowchart LR
    Q[Is my model good?] --> B[Benchmarks<br/>fixed public tests]
    Q --> J[LLM-as-judge<br/>model grades with rubric]
    Q --> H[Human evaluation<br/>people rate or compare]
    B --> B1[cheap, comparable<br/>risk: contamination]
    J --> J1[fast, scalable<br/>risk: position and length bias]
    H --> H1[most trusted<br/>risk: slow, costly]
""",
}


def build_images():
    for name, src in DIAGRAMS.items():
        mermaid(src, IMG / f"{name}.png")
        print("image", name)
    # A matplotlib chart: why percent agreement can mislead (lazy annotators).
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = ["Careful pair", "Lazy pair\n(always 'not spam')"]
    agree = [0.90, 0.90]
    kappa = [0.70, 0.00]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(labels))
    ax.bar([i - 0.18 for i in x], agree, width=0.36, label="Percent agreement", color="#1B263B")
    ax.bar([i + 0.18 for i in x], kappa, width=0.36, label="Cohen's kappa", color="#0F9D9A")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    ax.set_ylim(0, 1); ax.set_ylabel("score")
    ax.set_title("Same 90% agreement, very different kappa (illustrative)")
    ax.legend(); fig.tight_layout()
    fig.savefig(IMG / "kappa-vs-agreement.png", dpi=150)
    plt.close(fig)
    print("image kappa-vs-agreement")


# ---------------------------------------------------------------------------
# 2. Notebooks
# ---------------------------------------------------------------------------
NB1 = [
("md", """# 01 - Annotation exercise and Cohen's kappa

**Goal:** label a small dataset like a real annotator, then measure how much two annotators agree - first by hand, then with scikit-learn.

**Words you need**
- **Annotation / labelling** - adding the "right answer" (a **label**) to each example.
- **Annotator** - the person who adds labels.
- **Gold question** - an item whose correct label is already known, used to test annotators.
- **Cohen's kappa** - agreement between two annotators after removing the agreement you would get by luck.

Runs on any CPU in seconds. No API keys needed."""),
("md", """## Step 1 - Imports

`pandas` holds tables, `numpy` does maths, `sklearn.metrics` has the ready-made kappa function, `matplotlib` draws charts."""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import cohen_kappa_score, confusion_matrix
pd.set_option("display.max_colwidth", 80)
print("ready")"""),
("md", """## Step 2 - The task and the guidelines

We are labelling short customer reviews of a phone. Read the **guidelines** (the annotators' rulebook) before looking at the data. Real projects have pages of these; ours fits in one cell.

- **POS** - the reviewer is overall happy with the product.
- **NEG** - the reviewer is overall unhappy with the product.
- **NEU** - no clear opinion about the product (a question, a fact, or about something else such as delivery).
- Edge case - **sarcasm**: label the *meant* opinion. "Great, it died after a day" is NEG.
- Edge case - **mixed**: choose the opinion of the *final verdict* sentence."""),
("code", """reviews = [
    "Battery lasts two full days. Love it.",
    "Screen cracked the first week. Not happy.",
    "Does it come in blue?",
    "Great, it died after one day. Brilliant engineering.",
    "Camera is average but for this price I'm happy.",
    "Delivery was late but that's the courier, not the phone.",
    "Fast, smooth, no complaints.",
    "Speakers are tinny and the case feels cheap.",
    "It is a phone. It makes calls.",
    "Returned it. Overheats when charging.",
    "Best purchase this year!",
    "Good screen, terrible battery, would not buy again.",
    "Arrived on Tuesday.",
    "Oh wonderful, another update that deletes my photos.",
    "Solid value. Recommend to students.",
    "Not bad, not great.",
    "Fingerprint reader fails half the time.",
    "My mum loves it, easy to use.",
    "Box was damaged but phone works perfectly.",
    "Meh.",
]
df = pd.DataFrame({"text": reviews})
df.index.name = "item"
df"""),
("md", """## Step 3 - Two annotators' labels

Here are labels from two (simulated) annotators, A and B. They mostly agree, but they disagree on the hard cases - sarcasm, mixed opinions, and "is this about the product?". That is exactly what happens in real projects."""),
("code", """df["A"] = ["POS","NEG","NEU","NEG","POS","NEU","POS","NEG","NEU","NEG",
           "POS","NEG","NEU","NEG","POS","NEU","NEG","POS","POS","NEU"]
df["B"] = ["POS","NEG","NEU","POS","POS","NEG","POS","NEG","NEU","NEG",
           "POS","NEG","NEU","NEU","POS","NEU","NEG","POS","NEU","NEG"]
df"""),
("md", """## Step 4 - Your turn (optional)

Copy annotator A's labels, then change any you disagree with, following the guidelines. Later cells compare *you* with annotator B. If you skip this, the notebook still runs."""),
("code", """my_labels = list(df["A"])      # start from A ...
my_labels[5] = "NEU"           # ... and edit items you disagree with, for example item 5
df["me"] = my_labels
df[["text", "A", "me"]].head(8)"""),
("md", """## Step 5 - Raw percent agreement

**Observed agreement (p_o)** = the fraction of items where both annotators chose the same label. It is the obvious first number - but section 5.1 of `concepts.md` explains why it can mislead."""),
("code", """agree = df["A"] == df["B"]          # True where the two labels match
p_o = agree.mean()                   # True counts as 1, False as 0, so the mean is a fraction
print(f"A and B agree on {agree.sum()} of {len(df)} items -> p_o = {p_o:.2f}")
print("\\nDisagreements:")
df.loc[~agree, ["text", "A", "B"]]"""),
("md", """## Step 6 - A confusion matrix

A **confusion matrix** is a table that counts every combination of labels: rows are A's label, columns are B's label. The diagonal holds agreements; everything off the diagonal is a disagreement. `pd.crosstab` builds it."""),
("code", """labels = ["POS", "NEG", "NEU"]
cm = pd.crosstab(df["A"], df["B"], rownames=["A"], colnames=["B"]).reindex(index=labels, columns=labels, fill_value=0)
print(cm)
fig, ax = plt.subplots(figsize=(4, 3.5))
ax.imshow(cm.values, cmap="Blues")
for i in range(3):
    for j in range(3):
        ax.text(j, i, cm.values[i, j], ha="center", va="center")
ax.set_xticks(range(3)); ax.set_xticklabels(labels); ax.set_xlabel("Annotator B")
ax.set_yticks(range(3)); ax.set_yticklabels(labels); ax.set_ylabel("Annotator A")
ax.set_title("Who agreed with whom"); plt.tight_layout(); plt.show()"""),
("md", """## Step 7 - Cohen's kappa by hand

Formula: `kappa = (p_o - p_e) / (1 - p_e)`.

**Expected agreement (p_e)** is the agreement we would expect if both annotators labelled at random *but with their own habits* (how often each uses each label). For each label: P(A uses it) x P(B uses it). Then add those up."""),
("code", """n = len(df)
p_e = 0.0
for lab in labels:
    pa = (df["A"] == lab).mean()     # how often A uses this label
    pb = (df["B"] == lab).mean()     # how often B uses this label
    print(f"{lab}: A uses it {pa:.2f}, B uses it {pb:.2f}, both by chance {pa*pb:.3f}")
    p_e += pa * pb
kappa_hand = (p_o - p_e) / (1 - p_e)
print(f"\\np_o = {p_o:.3f}   p_e = {p_e:.3f}   kappa = {kappa_hand:.3f}")"""),
("md", """## Step 8 - Write it as a reusable function

A small function means we can reuse the calculation for any two lists of labels."""),
("code", """def cohens_kappa(a, b):
    \"\"\"Cohen's kappa for two equal-length lists of labels.\"\"\"
    a, b = np.asarray(a), np.asarray(b)
    cats = np.union1d(a, b)                                   # every label either person used
    p_o = np.mean(a == b)                                     # observed agreement
    p_e = sum(np.mean(a == c) * np.mean(b == c) for c in cats)  # chance agreement
    return (p_o - p_e) / (1 - p_e)

print("our function :", round(cohens_kappa(df["A"], df["B"]), 4))"""),
("md", """## Step 9 - Check against scikit-learn

`sklearn.metrics.cohen_kappa_score` is the trusted implementation. If our number matches, our understanding is right."""),
("code", """k_sk = cohen_kappa_score(df["A"], df["B"])
print("scikit-learn :", round(k_sk, 4))
print("you vs B     :", round(cohen_kappa_score(df["me"], df["B"]), 4))
assert abs(k_sk - cohens_kappa(df["A"], df["B"])) < 1e-9"""),
("md", """## Step 10 - The worked example from concepts.md

The 10-item example in `concepts.md` should give 0.52. Checking a hand calculation in code is a good habit."""),
("code", """a = ["POS","POS","NEG","POS","NEG","POS","POS","NEG","POS","POS"]
b = ["POS","NEG","NEG","POS","NEG","POS","POS","POS","POS","POS"]
print(round(cohen_kappa_score(a, b), 2))"""),
("md", """## Step 11 - Why kappa exists: the lazy annotators

Imagine 1,000 emails where about 5% are spam. Two lazy annotators click "ham" (not spam) on almost everything and press "spam" at random 5% of the time. Their percent agreement looks great, but kappa reveals they are not really agreeing about anything."""),
("code", """rng = np.random.default_rng(0)
lazy_a = np.where(rng.random(1000) < 0.05, "spam", "ham")   # random 5% spam clicks
lazy_b = np.where(rng.random(1000) < 0.05, "spam", "ham")
print("lazy percent agreement:", np.mean(lazy_a == lazy_b))
print("lazy kappa            :", round(cohen_kappa_score(lazy_a, lazy_b), 3))"""),
("md", """## Step 12 - Gold questions

Five items have a known correct label (decided by an expert). We score each annotator on them. On real platforms, falling below a threshold on gold questions means your work is reviewed or you are removed from the project."""),
("code", """gold = {0: "POS", 3: "NEG", 5: "NEU", 13: "NEG", 18: "POS"}   # item -> correct label
for who in ["A", "B", "me"]:
    correct = sum(df.loc[i, who] == g for i, g in gold.items())
    print(f"{who:>2}: {correct}/{len(gold)} gold questions correct")"""),
("md", """## Step 13 - Adjudication

When A and B disagree, an **adjudicator** (an expert reviewer) decides. Here we write the decisions with a reason - the reasons become new edge-case examples in the next version of the guidelines."""),
("code", """decisions = {
    3: ("NEG", "sarcasm - 'brilliant' is ironic"),
    5: ("NEU", "complaint is about the courier, not the phone"),
    13: ("NEG", "sarcasm about an update deleting photos"),
    18: ("POS", "final verdict: phone works perfectly"),
    19: ("NEU", "'Meh' is no clear opinion - add to guidelines"),
}
df["final"] = df["A"].where(df["A"] == df["B"])        # keep agreed labels
for i, (lab, why) in decisions.items():
    df.loc[i, "final"] = lab
    print(f"item {i:2d}: {lab}  because {why}")
print("\\nAll items labelled:", df["final"].notna().all())"""),
("md", """## Step 14 - Weighted kappa for ordered scores (bonus)

When labels have an order (ratings 1-5), a 4 vs 5 disagreement is smaller than 1 vs 5. **Weighted kappa** gives partial credit. scikit-learn supports it with `weights="linear"` or `"quadratic"`."""),
("code", """r1 = [5, 4, 4, 2, 1, 3, 5, 4, 2, 3]
r2 = [4, 4, 5, 2, 2, 3, 5, 3, 1, 3]
print("plain kappa    :", round(cohen_kappa_score(r1, r2), 3))
print("linear weights :", round(cohen_kappa_score(r1, r2, weights="linear"), 3))
print("quadratic      :", round(cohen_kappa_score(r1, r2, weights="quadratic"), 3))"""),
("md", """## What you learned

- Percent agreement ignores luck; Cohen's kappa = (p_o - p_e) / (1 - p_e) removes it.
- Disagreements cluster on edge cases - they tell you how to improve the guidelines.
- Gold questions measure each annotator; adjudication produces final labels.
- Next: `02-reward-model.ipynb` uses *preference* labels to train a model."""),
]

NB2 = [
("md", """# 02 - Train a tiny reward model on preference pairs

**Goal:** see stage 2 of RLHF with your own eyes. We create synthetic **preference pairs** (prompt, chosen answer, rejected answer), train a tiny **reward model** that gives a score to any answer, and then find a weakness in it (**reward hacking**).

**Words you need**
- **Reward model** - a model that reads an answer and outputs one number: how much a human would like it.
- **Preference pair** - two answers to the same prompt where a human marked one as better (**chosen**) and one as worse (**rejected**).
- **Bradley-Terry loss** - `-log(sigmoid(r_chosen - r_rejected))`; small when the chosen answer scores higher.

A real reward model is a full LLM with a scoring head. Ours is a **linear model on word counts** so that it trains in a second on a CPU and we can read what it learned."""),
("md", """## Step 1 - Imports and a fixed random seed

A **seed** makes random numbers repeatable, so everyone in class sees the same results."""),
("code", """import random
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
random.seed(0); torch.manual_seed(0)
print("torch", torch.__version__)"""),
("md", """## Step 2 - Build synthetic preference data

Real preference data comes from human annotators. To keep this offline we *generate* it from templates:
- **chosen** answers are polite and contain real steps;
- **rejected** answers are rude, dismissive, or polite but empty (no actual help).

The "polite but empty" ones matter: they stop the model from learning "polite words = good" and force it to look for real content."""),
("code", """topics = [
    ("reset my password", "open Settings, choose Security, then click Reset password and follow the email link"),
    ("cook rice", "rinse one cup of rice, add two cups of water, boil, then simmer covered for 15 minutes"),
    ("learn Python", "start with variables and loops, practise daily on small projects, and read other people's code"),
    ("fix a flat bicycle tyre", "remove the wheel, find the hole, patch the tube, and pump it to the right pressure"),
    ("save money", "track your spending for a month, set a budget, and move savings first each payday"),
    ("sleep better", "keep a fixed bedtime, avoid screens for an hour before bed, and keep the room dark"),
    ("write a CV", "list recent experience first, use clear headings, and keep it to one or two pages"),
    ("make tea", "boil water, steep the tea for three minutes, then add milk or sugar if you like"),
    ("back up my phone", "turn on cloud backup in settings or copy your photos to a computer each week"),
    ("prepare for an interview", "research the company, practise common questions aloud, and prepare questions to ask"),
    ("start running", "begin with short run-walk sessions three times a week and increase slowly"),
    ("plant tomatoes", "choose a sunny spot, plant seedlings deep, water at the base, and add a support stake"),
]
openers = ["Sure! Here is how:", "Happy to help.", "Good question.", "Of course."]
closers = ["Hope this helps!", "Let me know if you have questions.", "Good luck!", ""]
bad_answers = [
    lambda t: "Figure it out yourself.",
    lambda t: "I don't know, search online.",
    lambda t: f"Why would you want to {t}? That's a silly question.",
    lambda t: "Just do it. It's easy.",
    lambda t: f"Sure! Happy to help. Good luck with trying to {t}!",   # polite but empty
    lambda t: "Of course. Hope this helps! Let me know if you have questions.",  # polite but empty
]

pairs = []
for t, steps in topics:
    for _ in range(10):
        prompt = random.choice([f"How do I {t}?", f"Can you tell me how to {t}?", f"What's the best way to {t}?"])
        chosen = f"{random.choice(openers)} To {t}, {steps}. {random.choice(closers)}".strip()
        rejected = random.choice(bad_answers)(t)
        pairs.append({"prompt": prompt, "chosen": chosen, "rejected": rejected})
random.shuffle(pairs)
print(len(pairs), "pairs. Example:")
pairs[0]"""),
("md", """## Step 3 - Train / test split by topic

We hold out three whole topics for testing. If the reward model scores *unseen topics* correctly, it learned something general ("real steps beat dismissive replies"), not just memorised sentences."""),
("code", """test_topics = {"start running", "plant tomatoes", "prepare for an interview"}
is_test = lambda p: any(t in p["prompt"] for t in test_topics)
train = [p for p in pairs if not is_test(p)]
test = [p for p in pairs if is_test(p)]
print("train pairs:", len(train), " test pairs:", len(test))"""),
("md", """## Step 4 - Turn text into numbers

Models only understand numbers. A **CountVectorizer** builds a **vocabulary** (list of known words) and turns each answer into a vector of word counts - a "bag of words". Each word gets one column. We drop **stop words** (very common words such as "the" and "and") so the learned weights are easier to read."""),
("code", """vec = CountVectorizer(lowercase=True, stop_words="english")   # drop very common words like 'the', 'and'
vec.fit([p["chosen"] for p in train] + [p["rejected"] for p in train])
def feats(texts):
    return torch.tensor(vec.transform(texts).toarray(), dtype=torch.float32)

Xc_train, Xr_train = feats([p["chosen"] for p in train]), feats([p["rejected"] for p in train])
Xc_test, Xr_test = feats([p["chosen"] for p in test]), feats([p["rejected"] for p in test])
print("vocabulary size:", len(vec.vocabulary_), " feature matrix:", tuple(Xc_train.shape))"""),
("md", """## Step 5 - The reward model and its loss

The reward model is one `nn.Linear` layer: each word gets a weight, and the score is the weighted sum of word counts plus a bias.

The **Bradley-Terry loss** for a pair is `-log(sigmoid(r_chosen - r_rejected))`. `F.logsigmoid` computes `log(sigmoid(x))` in a numerically safe way. Look at the table: the bigger the margin in the right direction, the smaller the loss."""),
("code", """reward_model = torch.nn.Linear(Xc_train.shape[1], 1)

def bt_loss(r_chosen, r_rejected):
    return -F.logsigmoid(r_chosen - r_rejected).mean()

for margin in [-2.0, -0.5, 0.0, 0.5, 2.0]:
    print(f"margin {margin:+.1f} -> loss {bt_loss(torch.tensor(margin), torch.tensor(0.0)).item():.3f}")"""),
("md", """## Step 6 - Train

Each **epoch** (one pass over all training pairs) we: score chosen and rejected answers, compute the loss, compute **gradients** (which direction to change each weight), and let the **Adam optimizer** take a small step. `weight_decay` gently pulls weights toward zero so no single word dominates."""),
("code", """opt = torch.optim.Adam(reward_model.parameters(), lr=0.01, weight_decay=0.01)
history = []
for epoch in range(200):
    r_c, r_r = reward_model(Xc_train), reward_model(Xr_train)
    loss = bt_loss(r_c, r_r)
    opt.zero_grad(); loss.backward(); opt.step()
    acc = (r_c > r_r).float().mean().item()
    history.append(loss.item())
    if epoch % 40 == 0:
        print(f"epoch {epoch:3d}  loss {loss.item():.4f}  train pair accuracy {acc:.2f}")
plt.plot(history); plt.xlabel("epoch"); plt.ylabel("Bradley-Terry loss"); plt.title("Reward model training"); plt.show()"""),
("md", """## Step 7 - Test on unseen topics

**Pair accuracy** = fraction of test pairs where the chosen answer gets the higher score. Real reward models often land around 65-75% on hard human data, because humans themselves disagree. Our synthetic data is much easier."""),
("code", """with torch.no_grad():
    margin = reward_model(Xc_test) - reward_model(Xr_test)
print("test pair accuracy:", (margin > 0).float().mean().item())"""),
("md", """## Step 8 - What did it learn?

Because the model is linear, each word's weight tells us how much it raises or lowers the reward. This is the big advantage of a tiny model for teaching: we can open the box."""),
("code", """w = reward_model.weight[0].detach().numpy()
vocab = np.array(vec.get_feature_names_out())
order = np.argsort(w)
print("most NEGATIVE words:", list(vocab[order[:10]]))
print("most POSITIVE words:", list(vocab[order[-10:]]))"""),
("md", """## Step 9 - Score new answers

Now the reward model can score *any* answer without a human. This is exactly how it is used in stage 3 of RLHF: the policy writes answers and the reward model scores them."""),
("code", """def score(text):
    with torch.no_grad():
        return reward_model(feats([text])).item()

candidates = [
    "To start running, begin with short run-walk sessions and increase slowly. Good luck!",
    "Just do it. It's easy.",
    "Of course. Hope this helps!",
]
for c in candidates:
    print(f"{score(c):+6.2f}  {c}")"""),
("md", """## Step 10 - Reward hacking

A reward model is only an *approximation* of human taste. If we optimise hard against it, we find answers that score high but are nonsense. Below, an answer stuffed with "positive" words and no real meaning beats a short, genuinely useful one. This is **reward hacking**, and it is why PPO adds a **KL penalty** that keeps the policy close to the reference model (see `concepts.md` section 6.3)."""),
("code", """top_words = " ".join(vocab[order[-15:]])
hacked = f"{top_words} {top_words} {top_words}"
honest = "Rinse the rice, add water, boil, then simmer."
print(f"honest answer : {score(honest):+7.2f}   '{honest}'")
print(f"hacked answer : {score(hacked):+7.2f}   '{hacked[:70]}...'")"""),
("md", """## What you learned

- Preference pairs -> reward model, trained with the Bradley-Terry loss.
- A reward model turns "which is better?" into a number for any answer.
- It can be fooled (reward hacking), so RLHF keeps the policy close to a reference.
- Next: `03-dpo-loss-demo.ipynb` skips the reward model entirely."""),
]

NB3 = [
("md", """# 03 - The DPO loss on toy numbers (and on a real model)

**Goal:** understand **Direct Preference Optimization (DPO)** by computing its loss with your own hands, in PyTorch, and watching it change a toy model.

**Words you need**
- **Policy** - the model being trained.
- **Reference model** - a frozen copy of the starting model (usually the SFT model); it never changes.
- **Log-probability** - the logarithm of a probability. Always <= 0; closer to 0 means "more likely".
- **beta (β)** - a dial: how strongly to stay close to the reference.

DPO loss for one pair:
`loss = -log sigmoid( beta * [ (logp_policy(chosen) - logp_ref(chosen)) - (logp_policy(rejected) - logp_ref(rejected)) ] )`"""),
("md", """## Step 1 - Imports"""),
("code", """import math
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
torch.manual_seed(0)
print("ok")"""),
("md", """## Step 2 - The toy numbers from concepts.md, by hand with `math`

We use plain Python first so nothing is hidden."""),
("code", """beta = 0.1
pol_c, ref_c = -12.0, -14.0      # chosen: policy likes it more than the reference does
pol_r, ref_r = -15.0, -13.0      # rejected: policy likes it less than the reference does

chosen_reward = pol_c - ref_c    # "implicit reward" of the chosen answer
rejected_reward = pol_r - ref_r
margin = chosen_reward - rejected_reward
sigmoid = 1 / (1 + math.exp(-beta * margin))
loss = -math.log(sigmoid)
print(f"implicit rewards: chosen {chosen_reward:+.1f}, rejected {rejected_reward:+.1f}")
print(f"margin {margin}, beta*margin {beta*margin:.2f}, sigmoid {sigmoid:.3f}, loss {loss:.3f}")
print(f"loss if policy == reference: {-math.log(0.5):.3f}")"""),
("md", """## Step 3 - The same thing as a PyTorch function

This is essentially the core of what libraries like TRL compute, for a whole **batch** (group) of pairs at once. `F.logsigmoid` is the safe version of `log(sigmoid(x))`."""),
("code", """def dpo_loss(pol_chosen, pol_rejected, ref_chosen, ref_rejected, beta=0.1):
    \"\"\"All inputs are tensors of summed log-probabilities, one value per pair.\"\"\"
    chosen_rewards = beta * (pol_chosen - ref_chosen)
    rejected_rewards = beta * (pol_rejected - ref_rejected)
    losses = -F.logsigmoid(chosen_rewards - rejected_rewards)
    return losses.mean(), chosen_rewards, rejected_rewards

pc = torch.tensor([-12.0], requires_grad=True)   # requires_grad: track gradients for this value
pr = torch.tensor([-15.0], requires_grad=True)
loss, cr, rr = dpo_loss(pc, pr, torch.tensor([-14.0]), torch.tensor([-13.0]))
print("loss:", round(loss.item(), 4))"""),
("md", """## Step 4 - Which way does training push?

`loss.backward()` computes the **gradient** - how the loss changes if we nudge each input. An optimizer moves *against* the gradient. A negative gradient on the chosen log-prob means "raise the chosen answer's probability"; a positive one on the rejected log-prob means "lower it"."""),
("code", """loss.backward()
print("gradient wrt chosen log-prob  :", round(pc.grad.item(), 4), "-> increase chosen")
print("gradient wrt rejected log-prob:", round(pr.grad.item(), 4), "-> decrease rejected")"""),
("md", """## Step 5 - How beta changes the loss curve

We plot loss against the margin (how much more the policy prefers chosen over rejected, relative to the reference) for three betas. Small beta = a gentle curve that needs a large margin before the loss stops pushing. Large beta = steep curve; satisfied with small changes, so the policy stays near the reference."""),
("code", """margins = torch.linspace(-20, 20, 200)
for b in [0.05, 0.1, 0.5]:
    plt.plot(margins, -F.logsigmoid(b * margins), label=f"beta={b}")
plt.axvline(0, color="grey", lw=0.5)
plt.xlabel("margin = (pol_c - ref_c) - (pol_r - ref_r)"); plt.ylabel("DPO loss"); plt.legend()
plt.title("DPO loss vs margin"); plt.show()"""),
("md", """## Step 6 - A toy policy that we actually train with DPO

Imagine one prompt with four possible answers: A (great), B (good), C (meh), D (bad). The policy is just four numbers (**logits**, scores turned into probabilities by **softmax**). Humans gave preference pairs: A > D, A > C, B > D, B > C.

We train with DPO and watch the probabilities move. The reference stays frozen at the starting point."""),
("code", """answers = ["A great", "B good", "C meh", "D bad"]
prefs = [(0, 3), (0, 2), (1, 3), (1, 2)]        # (chosen index, rejected index)
start_logits = torch.tensor([0.0, 0.2, 0.5, 0.3])  # starting policy slightly prefers C and D!

def train_dpo(beta, steps=150, lr=0.1):
    logits = start_logits.clone().requires_grad_(True)
    ref_logp = F.log_softmax(start_logits, dim=0)          # frozen reference
    opt = torch.optim.SGD([logits], lr=lr)
    probs_over_time = []
    for _ in range(steps):
        logp = F.log_softmax(logits, dim=0)
        c = torch.tensor([i for i, _ in prefs]); r = torch.tensor([j for _, j in prefs])
        loss, _, _ = dpo_loss(logp[c], logp[r], ref_logp[c], ref_logp[r], beta)
        opt.zero_grad(); loss.backward(); opt.step()
        probs_over_time.append(F.softmax(logits, dim=0).detach())
    return torch.stack(probs_over_time)

hist = train_dpo(beta=0.5)
for k, name in enumerate(answers):
    plt.plot(hist[:, k], label=name)
plt.xlabel("training step"); plt.ylabel("probability"); plt.legend(); plt.title("DPO moves probability to preferred answers")
plt.show()
print("start:", [round(p, 2) for p in F.softmax(start_logits, 0).tolist()])
print("end  :", [round(p, 2) for p in hist[-1].tolist()])"""),
("md", """## Step 7 - Beta controls drift from the reference

**KL divergence** measures how far the final policy has moved from the reference distribution (0 = not moved at all).

Look back at the plot in Step 5: the loss flattens once `beta x margin` is a few units. So a *large* beta is "satisfied" by a *small* margin and stops pushing early, while a *small* beta keeps pushing until the margin is large. To compare fairly we scale the learning rate by `1/beta` so every run starts with the same push. Expect: bigger beta -> smaller KL -> policy stays closer to the reference. In practice beta is tuned; 0.1 is a common starting value."""),
("code", """ref_p = F.softmax(start_logits, 0)
for b in [0.1, 0.5, 2.0]:
    final = train_dpo(beta=b, steps=300, lr=0.05 / b)[-1]
    kl = torch.sum(final * (final.log() - ref_p.log())).item()
    print(f"beta={b:<4}  final probs={[round(x, 2) for x in final.tolist()]}  KL from reference={kl:.3f}")"""),
("md", """## Step 8 - Real log-probabilities from a real language model

In real DPO, `logp(answer)` is the **sum of the log-probabilities of each token** of the answer, given the prompt. A **token** is a word or piece of a word. We load a small chat model (`SmolLM2-135M-Instruct`, about 270 MB, downloads once from Hugging Face) and compute these numbers for a chosen and a rejected answer.

At the start of DPO training the policy *is* the reference, so the loss must be exactly `log(2) ≈ 0.693`. Let's check."""),
("code", """from transformers import AutoModelForCausalLM, AutoTokenizer
mid = "HuggingFaceTB/SmolLM2-135M-Instruct"
tok = AutoTokenizer.from_pretrained(mid)
model = AutoModelForCausalLM.from_pretrained(mid)
model.eval()

@torch.no_grad()
def answer_logprob(prompt, answer):
    \"\"\"Sum of log-probs of the answer tokens, given the prompt (chat formatted).\"\"\"
    p_ids = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True,
                                    return_tensors="pt", return_dict=True)["input_ids"]
    a_ids = tok(answer, return_tensors="pt", add_special_tokens=False)["input_ids"]
    ids = torch.cat([p_ids, a_ids], dim=1)
    logits = model(ids).logits[:, :-1]                 # prediction for the NEXT token at each position
    logp = F.log_softmax(logits, dim=-1)
    targets = ids[:, 1:]
    token_logp = logp.gather(2, targets.unsqueeze(-1)).squeeze(-1)
    return token_logp[:, p_ids.shape[1] - 1:].sum().item()   # keep only the answer part

prompt = "What is the capital of France?"
chosen, rejected = "The capital of France is Paris.", "France does not have a capital."
lc, lr_ = answer_logprob(prompt, chosen), answer_logprob(prompt, rejected)
print(f"log p(chosen) = {lc:.2f}   log p(rejected) = {lr_:.2f}")
loss0, _, _ = dpo_loss(torch.tensor([lc]), torch.tensor([lr_]), torch.tensor([lc]), torch.tensor([lr_]))
print("DPO loss with policy == reference:", round(loss0.item(), 4), " (log 2 =", round(math.log(2), 4), ")")"""),
("md", """## Step 9 - How you would run real DPO (not executed here)

On a GPU you would use Hugging Face **TRL**. The code below shows the shape of it; it is a markdown cell so this notebook stays fast on a CPU. Check the current TRL docs for exact arguments (as of late 2026, `DPOConfig` has `beta` and `max_length`).

```python
from datasets import Dataset
from trl import DPOConfig, DPOTrainer
data = Dataset.from_list([{"prompt": "...", "chosen": "...", "rejected": "..."}, ...])
args = DPOConfig(output_dir="dpo-out", beta=0.1, per_device_train_batch_size=2, max_steps=100)
trainer = DPOTrainer(model="your-sft-model", args=args, train_dataset=data, processing_class=tokenizer)
trainer.train()
```
If you pass no `ref_model`, TRL makes the frozen reference for you."""),
("md", """## What you learned

- DPO loss = -log sigmoid(beta x [implicit reward of chosen - implicit reward of rejected]).
- Its gradient raises the chosen answer and lowers the rejected one, relative to a frozen reference.
- beta controls how far the policy may drift.
- With a real model, log p(answer) = sum of token log-probs; at the start the loss is log 2."""),
]

NB4 = [
("md", """# 04 - Evals: rubrics, LLM-as-judge and position bias

**Goal:** build a small evaluation the way AI teams do: write a **rubric**, grade answers with a **judge**, check the judge for **position bias**, and compare the judge with human labels using kappa.

**Words you need**
- **Eval** - a repeatable test of model quality.
- **Rubric** - a scoring guide with named criteria and clear levels.
- **LLM-as-judge** - using a strong language model to grade answers.
- **Position bias** - a judge preferring whichever answer is shown first.

If `ANTHROPIC_API_KEY` is set, the judge cells call Claude. Otherwise they use a clearly-labelled **offline stand-in judge** (simple rules), so the notebook always runs."""),
("md", """## Step 1 - Imports and key check

We never write keys in code. `os.getenv` reads the key from the environment if it exists."""),
("code", """import os, json, re
import pandas as pd
from sklearn.metrics import cohen_kappa_score
USE_CLAUDE = bool(os.getenv("ANTHROPIC_API_KEY"))
print("Using real Claude judge" if USE_CLAUDE else "No API key -> using the OFFLINE stand-in judge")"""),
("md", """## Step 2 - A small eval set

Each row has a question, a **reference answer** (what a correct answer must contain), and a model answer to grade. In real projects this set is written and checked by humans."""),
("code", """evalset = pd.DataFrame([
    {"q": "What is 15% of 200?", "ref": "30", "answer": "15% of 200 is 30."},
    {"q": "Name the largest planet.", "ref": "Jupiter", "answer": "Saturn is the largest planet."},
    {"q": "Give one use of a Python list.", "ref": "store", "answer": "A list can store several items in order, like names."},
    {"q": "What does CPU stand for?", "ref": "central processing unit", "answer": "Central Processing Unit."},
    {"q": "Explain recursion in one sentence.", "ref": "calls itself", "answer": "Recursion is a fancy word. It is used a lot by programmers and it is very important to learn about it in depth because it is important."},
    {"q": "Boiling point of water at sea level in Celsius?", "ref": "100", "answer": "It boils at 100 degrees Celsius."},
])
evalset"""),
("md", """## Step 3 - The rubric

Three binary (yes/no) criteria. Binary checks give higher agreement between graders than 1-10 scales. The rule for combining them is written down too."""),
("code", """RUBRIC = {
    "correct": "The answer contains the key fact from the reference answer and states nothing false.",
    "answers_question": "The answer directly addresses what was asked.",
    "concise": "The answer has no padding or repetition (roughly 25 words or fewer for these questions).",
}
COMBINE = "PASS only if 'correct' and 'answers_question' are both yes. 'concise' is reported but does not fail."
print(json.dumps(RUBRIC, indent=2)); print(COMBINE)"""),
("md", """## Step 4 - The judge

`claude_judge` shows how a real LLM-as-judge call looks: send the rubric, question, reference and answer, and ask for JSON. `offline_judge` is the stand-in: crude string rules that imitate a grader. **The offline judge is not intelligent** - it exists only so the notebook runs without a key. The model name is an example; check Anthropic's docs for current model names."""),
("code", """def offline_judge(q, ref, answer):
    \"\"\"OFFLINE STAND-IN: keyword rules, not a real LLM.\"\"\"
    a = answer.lower()
    correct = ref.lower() in a
    answers_question = len(a.split()) >= 2
    concise = len(a.split()) <= 25 and len(set(a.split())) / max(1, len(a.split())) > 0.7
    return {"correct": correct, "answers_question": answers_question, "concise": concise}

def claude_judge(q, ref, answer):
    import anthropic                                   # pip install anthropic
    client = anthropic.Anthropic()                     # reads ANTHROPIC_API_KEY from the environment
    prompt = (f"Grade the answer with this rubric. Reply with JSON only, keys {list(RUBRIC)} and true/false values.\\n"
              f"Rubric: {json.dumps(RUBRIC)}\\nQuestion: {q}\\nReference: {ref}\\nAnswer: {answer}")
    msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=200,   # example model name
                                 messages=[{"role": "user", "content": prompt}])
    return json.loads(re.search(r"\\{.*\\}", msg.content[0].text, re.S).group(0))

judge = claude_judge if USE_CLAUDE else offline_judge
grades = pd.DataFrame([judge(r.q, r.ref, r.answer) for r in evalset.itertuples()])
grades["PASS"] = grades["correct"] & grades["answers_question"]
pd.concat([evalset[["q", "answer"]], grades], axis=1)"""),
("md", """## Step 5 - Compare the judge with humans

Before trusting a judge, compare it with human grades on the same items. Here a human grader marked PASS/FAIL. We compute percent agreement and Cohen's kappa (from notebook 01)."""),
("code", """human_pass = [True, False, True, True, False, True]
judge_pass = list(grades["PASS"])
agree = sum(h == j for h, j in zip(human_pass, judge_pass)) / len(human_pass)
print("percent agreement:", round(agree, 2))
print("kappa            :", round(cohen_kappa_score(human_pass, judge_pass), 2))"""),
("md", """## Step 6 - Pairwise comparison and position bias

Often we ask a judge "which of two answers is better?". A biased judge favours position 1. The fix: ask twice with the order swapped and only count a win when both orders agree.

Our stand-in judge below is *deliberately* biased (it slightly favours whichever answer comes first) so you can see the problem and the fix."""),
("code", """def biased_pairwise_judge(q, first, second):
    \"\"\"OFFLINE STAND-IN with a built-in position bias. Returns 'first' or 'second'.\"\"\"
    s1 = len(set(first.lower().split())) + 3      # +3 bonus just for being shown first (the bias)
    s2 = len(set(second.lower().split()))
    return "first" if s1 >= s2 else "second"

pairs = [
    ("Explain a variable.", "A variable is a named box that stores a value.", "A variable stores a value in memory for later use."),
    ("What is an API?", "A way for programs to talk to each other.", "An API is a set of rules that lets one program request data or actions from another."),
    ("Define overfitting.", "When a model memorises training data and fails on new data.", "Overfitting: model too fit."),
]
rows = []
for q, x, y in pairs:
    ab = biased_pairwise_judge(q, x, y)          # x shown first
    ba = biased_pairwise_judge(q, y, x)          # y shown first
    winner_ab = "x" if ab == "first" else "y"
    winner_ba = "y" if ba == "first" else "x"
    final = winner_ab if winner_ab == winner_ba else "tie (inconsistent)"
    rows.append({"question": q, "x first ->": winner_ab, "y first ->": winner_ba, "final": final})
pd.DataFrame(rows)"""),
("md", """## Step 7 - Win rate

A **win rate** is the fraction of comparisons a model wins (ties count as half). It is the standard summary for pairwise evals."""),
("code", """final = [r["final"] for r in rows]
win_x = sum(1 for f in final if f == "x") + 0.5 * sum(1 for f in final if f.startswith("tie"))
print(f"model x win rate: {win_x / len(final):.2f}")"""),
("md", """## What you learned

- A rubric with binary, observable criteria makes grading consistent.
- An LLM judge must be checked against human labels (kappa) before you trust it.
- Swap the order in pairwise comparisons to cancel position bias.
- These are the same skills AI trainer platforms test in qualification tasks."""),
]


def build_notebooks():
    notebook(NB1, NB / "01-annotation-and-kappa.ipynb")
    notebook(NB2, NB / "02-reward-model.ipynb")
    notebook(NB3, NB / "03-dpo-loss-demo.ipynb")
    notebook(NB4, NB / "04-evals-rubric-and-judge.ipynb")
    print("notebooks built")


# ---------------------------------------------------------------------------
# 3. Slides
# ---------------------------------------------------------------------------
def build_slides():
    I = lambda n: str(IMG / f"{n}.png")
    deck = {
        "title": "Module 12 - Data Annotation, RLHF and Evals",
        "subtitle": "Python to Pro AI Engineer - week 20",
        "slides": [
            {"title": "Today's goals", "bullets": [
                "Explain why labels decide model quality", "Name annotation types and tools",
                "Compute Cohen's kappa by hand", "Draw the RLHF pipeline and explain DPO",
                "Design an eval rubric", "Know what AI trainer jobs involve"],
             "notes": "Read the goals aloud. Tell students that by the end they will compute a real agreement score and understand how chatbots like ChatGPT and Claude were taught to be helpful. Mention that this module also opens a real job path: AI trainer work."},
            {"title": "Garbage in, garbage out", "bullets": [
                "A model copies the patterns in its labels", "Analogy: a new cook learning from tasting notes",
                "Burnt dishes labelled 'perfect' = a cook who burns food",
                "Labels feed training, alignment AND evaluation"],
             "notes": "Tell the cookbook story from concepts section 1. Ask: if a third of the labels are wrong, what does the model learn? Answer: it learns the mistakes. Stress that annotation appears at the start, middle and end of every AI project."},
            {"title": "Annotation types", "bullets": [
                "Classification - pick a category", "NER - tag spans of text", "Bounding boxes / segmentation - images",
                "Ranking - order several answers", "Preference pairs - A or B?", "Demonstrations and rubric grades"],
             "notes": "Use the school-marking analogy: multiple choice, underlining, circling, ordering essays, choosing the better essay, writing the model answer. Show one example of each. Preference pairs are the key type for RLHF and DPO later today."},
            {"title": "The annotation workflow", "image": I("annotation-workflow"), "bullets": [
                "Guidelines first", "Pilot on ~50 items", "Measure agreement, fix, repeat", "Then scale up"],
             "notes": "Walk through the diagram left to right. The loop between pilot and fixing guidelines is the most important part: guidelines are never right on the first try. Only scale up when agreement is good enough."},
            {"title": "Tools - pick by data type", "bullets": [
                "Label Studio - almost any data type", "Argilla - LLM feedback and preferences",
                "CVAT - images and video", "doccano - simple text tasks",
                "Prodigy - paid, fast, active learning"],
             "notes": "Explain active learning: the model picks the examples it is least sure about. Rule of thumb: images go to CVAT, chatbot answers to Argilla or Label Studio, a quick class NER project to doccano. Platforms for AI trainer jobs provide their own interface."},
            {"title": "Writing guidelines", "bullets": [
                "Purpose, label definitions, what each label is NOT", "Positive and negative examples",
                "Edge cases with the decision and the reason", "Decision tree + what to do when unsure",
                "Version history - they change"],
             "notes": "Referee rulebook analogy. Show the guideline template sheet in excel/annotation-toolkit.xlsx. Ask students for an edge case in sentiment labelling - sarcasm and mixed reviews usually come up."},
            {"title": "Quality control", "image": I("qc-loop"), "bullets": [
                "Gold questions (honeypots)", "Overlap: 2+ annotators per item", "Adjudication of disagreements",
                "Spot checks", "Inter-annotator agreement"],
             "notes": "Gold questions are items with a known answer hidden among real tasks. AI trainer platforms use them to decide whether to keep giving you work. Adjudication means an expert decides the final label."},
            {"title": "Why percent agreement misleads", "image": I("kappa-vs-agreement"), "bullets": [
                "95% of emails are not spam", "Two lazy annotators agree ~90%", "But they agree by luck",
                "Kappa removes chance agreement"],
             "notes": "This chart is illustrative. The point: the same 90 percent agreement can hide zero real agreement. Notebook 01 step 11 reproduces the lazy annotators."},
            {"title": "Cohen's kappa by hand", "bullets": [
                "kappa = (p_o - p_e) / (1 - p_e)", "p_o: fraction where both agree = 0.8",
                "p_e: sum over labels of P_A x P_B", "0.7x0.7 + 0.3x0.3 = 0.58", "kappa = 0.22 / 0.42 = 0.52 (moderate)"],
             "code": "from sklearn.metrics import cohen_kappa_score\na = ['POS','POS','NEG','POS','NEG',\n     'POS','POS','NEG','POS','POS']\nb = ['POS','NEG','NEG','POS','NEG',\n     'POS','POS','POS','POS','POS']\nprint(round(cohen_kappa_score(a, b), 2))\n# 0.52",
             "notes": "Do this on the whiteboard step by step, then show the code gives the same answer. Read kappa with the rough scale: 0.41-0.60 moderate, 0.61-0.80 substantial. Many teams want about 0.7 before scaling."},
            {"title": "RLHF in three stages", "image": I("rlhf-pipeline"), "bullets": [
                "1 SFT: copy expert demonstrations", "2 Reward model: learn human preferences",
                "3 PPO: practise against the critic", "KL penalty: do not drift too far"],
             "notes": "Cooking competition analogy: cooking school, training a food critic, practising with the critic. The KL penalty stops the cook from inventing weird dishes that only fool the critic - that is reward hacking."},
            {"title": "The reward model loss", "bullets": [
                "Pair: prompt, chosen, rejected", "loss = -log sigmoid(r_chosen - r_rejected)",
                "Chosen scored higher -> small loss", "Wrong order -> big loss", "Notebook 02 trains one"],
             "notes": "Sigmoid squashes a number into 0..1, so sigmoid of the score difference is the model's probability that chosen wins. Show notebook 02 step 10 - reward hacking - it always gets a reaction."},
            {"title": "DPO - skip the critic", "image": I("rlhf-vs-dpo"), "bullets": [
                "Train directly on preference pairs", "Two models: policy + frozen reference",
                "No sampling during training", "One main dial: beta"],
             "notes": "DPO gives the cook the pile of 'this beat that' notes directly. Compare the two columns of the diagram. DPO behaves like normal supervised training, so it is cheaper and more stable."},
            {"title": "DPO loss on toy numbers", "bullets": [
                "beta = 0.1", "chosen: policy -12, ref -14 -> +2", "rejected: policy -15, ref -13 -> -2",
                "margin 4 -> sigmoid(0.4) = 0.599", "loss = 0.513 (vs 0.693 at start)"],
             "code": "import torch.nn.functional as F\ndef dpo_loss(pc, pr, rc, rr, beta=0.1):\n    margin = (pc - rc) - (pr - rr)\n    return -F.logsigmoid(beta * margin)",
             "notes": "Work it on the board. Log-probabilities are negative; closer to zero means more likely. At the start policy equals reference, margin is zero, loss is log 2, about 0.693. Notebook 03 shows the gradient raises chosen and lowers rejected."},
            {"title": "Preference data format", "bullets": [
                "JSONL: one JSON object per line", "Keys: prompt, chosen, rejected",
                "Same prompt for both answers", "Include close calls, not only easy pairs", "Record the reason"],
             "code": '{"prompt": "Explain a CPU.",\n "chosen": "The chip that runs\n  a computer\'s instructions.",\n "rejected": "Something about\n  computers."}',
             "notes": "This is the format TRL's DPOTrainer reads. Point out that easy pairs teach little; close calls are the valuable ones, and they are also where annotators disagree most."},
            {"title": "Evals: three families", "image": I("eval-types"), "bullets": [
                "Benchmarks - cheap, can be contaminated", "LLM-as-judge - fast, biased",
                "Human eval - trusted, slow", "Rubrics: observable, binary criteria"],
             "notes": "Exam analogy: national exam, teaching assistant with an answer key, head examiner. For LLM judges, always swap answer order to cancel position bias and check against human labels with kappa. Notebook 04 does both."},
            {"title": "AI trainer jobs", "bullets": [
                "Rate, rank, rewrite, red-team, review code", "Platforms change - check official sites",
                "Pay varies - check current listings", "Never pay to join; beware referral links",
                "Pass tests: read rules twice, justify with evidence"],
             "notes": "Describe a day: read guidelines, open queue, rate answers, write justifications. Show the job tracker spreadsheet. Stress honesty about pay: it varies by platform, country and expertise. Coding and STEM experts are in demand."},
            {"title": "Common mistakes", "bullets": [
                "Scaling before agreement is measured", "Trusting percent agreement",
                "Vague rubric levels ('5 = excellent')", "Unchecked LLM judges",
                "Skipping the guidelines in a qualification test"],
             "notes": "Each of these has burned real teams. Ask students which one they think is most common. Usually it is skipping or skimming guidelines."},
            {"title": "Recap and exercises", "bullets": [
                "Labels -> guidelines -> QC -> kappa", "RLHF: SFT -> reward model -> PPO",
                "DPO: one loss, two models", "Evals: benchmark, judge, human",
                "Now: exercises.md 1-4 in class, rest as homework"],
             "notes": "Recap in one sentence each. Assign exercises 1 to 4 in class; they take about 25 minutes. The harder ones, including writing your own guidelines and training the reward model on new data, are homework."},
        ],
    }
    slides(deck, HERE / "slides" / f"{MOD}.pptx")
    print("slides built")


# ---------------------------------------------------------------------------
# 4. Excel workbooks
# ---------------------------------------------------------------------------
def build_excel():
    # --- annotation toolkit: guideline template + kappa calculator -------------
    guide = [
        ["Section", "What to write", "Example (phone review sentiment)"],
        ["Project name and version", "Name, version number, date", "Phone reviews sentiment v1.2 - 2026-11-21"],
        ["Purpose", "Why the data is collected and how it will be used", "Train a model that routes unhappy customers to support"],
        ["Unit of annotation", "What one item is", "One review (all sentences together)"],
        ["Label 1 - definition", "Name + one-sentence definition + what it is NOT", "POS: overall happy with the PRODUCT. Not: happy with delivery only"],
        ["Label 1 - examples", "2+ clear examples", "'Battery lasts two days. Love it.'"],
        ["Label 2 - definition", "", "NEG: overall unhappy with the PRODUCT"],
        ["Label 2 - examples", "", "'Returned it. Overheats when charging.'"],
        ["Label 3 - definition", "", "NEU: no clear opinion about the product (question, fact, other topic)"],
        ["Label 3 - examples", "", "'Does it come in blue?'"],
        ["Edge case 1", "The tricky case + decision + reason", "Sarcasm -> label the meant opinion. 'Great, died in a day' = NEG"],
        ["Edge case 2", "", "Mixed review -> use the final verdict sentence"],
        ["Edge case 3", "", "Complaint about courier only -> NEU"],
        ["Decision tree", "Ordered yes/no questions", "1 About the product? no->NEU. 2 Clear verdict? no->NEU. 3 Happy? POS else NEG"],
        ["When unsure", "Flag/skip rules and how to comment", "Use FLAG and write one sentence explaining why"],
        ["Quality checks", "Gold questions, overlap %, target kappa", "10% gold, 20% double-labelled, target kappa >= 0.7"],
        ["Version history", "Date - change - reason", "2026-11-21 - added 'Meh' = NEU - annotators disagreed"],
    ]
    # Kappa calculator. Rows 2-101 hold up to 100 items; labels list in F2:F6; results F9:G12.
    a = ["POS", "POS", "NEG", "POS", "NEG", "POS", "POS", "NEG", "POS", "POS"]
    b = ["POS", "NEG", "NEG", "POS", "NEG", "POS", "POS", "POS", "POS", "POS"]
    kap = [["Item", "Annotator A", "Annotator B", "Agree (1/0)", "", "Label", "Count A", "Count B", "Chance both"]]
    label_list = ["POS", "NEG", "NEU", "", ""]
    side = {}
    for k, lab in enumerate(label_list):
        r = k + 2
        side[r] = [lab, f'=IF(F{r}="","",COUNTIF($B$2:$B$101,F{r}))',
                   f'=IF(F{r}="","",COUNTIF($C$2:$C$101,F{r}))',
                   f'=IF(F{r}="","",(G{r}/$G$9)*(H{r}/$G$9))']
    side[8] = ["RESULTS", "", "", ""]
    side[9] = ["N items (both labelled)", '=SUMPRODUCT(($B$2:$B$101<>"")*($C$2:$C$101<>""))', "", ""]
    side[10] = ["p_o observed agreement", '=SUM(D2:D101)/G9', "", ""]
    side[11] = ["p_e chance agreement", '=SUM(I2:I6)', "", ""]
    side[12] = ["Cohen's kappa", '=(G10-G11)/(1-G11)', "", ""]
    side[13] = ["How to read", '=IF(G12<0,"worse than chance",IF(G12<=0.2,"slight",IF(G12<=0.4,"fair",IF(G12<=0.6,"moderate",IF(G12<=0.8,"substantial","almost perfect")))))', "", ""]
    side[15] = ["HOW TO USE: type labels in B and C (up to row 101). List every label in F2:F6.", "", "", ""]
    for r in range(2, 102):
        i = r - 2
        row = [i + 1 if i < len(a) else "", a[i] if i < len(a) else "", b[i] if i < len(b) else "",
               f'=IF(OR(B{r}="",C{r}=""),"",IF(B{r}=C{r},1,0))', ""]
        row += side.get(r, ["", "", "", ""])
        if i >= len(a):
            row[0] = ""
        kap.append(row)
    scale = [["Kappa range", "Rough meaning (Landis and Koch guide)"],
             ["below 0", "worse than chance - check for swapped labels"], ["0.00-0.20", "slight"],
             ["0.21-0.40", "fair"], ["0.41-0.60", "moderate"], ["0.61-0.80", "substantial"], ["0.81-1.00", "almost perfect"]]
    rubric = [["Criterion", "Question for the grader", "Yes means", "No means", "Fails overall?"],
              ["Correct", "Does it contain the key fact and nothing false?", "All claims check out", "Any false claim", "Yes"],
              ["Answers the question", "Does it address what was asked?", "Directly answers", "Off-topic or partial", "Yes"],
              ["Safe", "Is it free of harmful content?", "No harm", "Harmful advice or content", "Yes"],
              ["Concise", "Is it free of padding and repetition?", "Tight", "Rambling", "No (reported only)"],
              ["Tone", "Is it polite and suitable for the user?", "Appropriate", "Rude or unsuitable", "No (reported only)"]]
    workbook({"Guideline template": guide, "Kappa calculator": kap, "Kappa scale": scale, "Rubric template": rubric},
             HERE / "excel" / "annotation-toolkit.xlsx",
             col_widths={"Guideline template": [28, 45, 70], "Kappa calculator": [7, 13, 13, 12, 3, 26, 14, 10, 12]})

    # --- AI trainer job tracker -------------------------------------------------
    plats = [
        ("Mercor", "https://aitrainer.work/platforms/mercor", "All domains, strong for software experts", "AI interview at intake"),
        ("Micro1", "https://aitrainer.work/platforms/micro1", "Very wide range of domains", "Skill 'buckets' decide matching"),
        ("Turing", "https://aitrainer.work/guides/turing-ai-training-review", "Coding, STEM, languages", "Good first stop for developers"),
        ("SME Careers", "https://aitrainer.work/guides/sme-careers-review", "Languages, STEM, design", "Own assessment process"),
        ("Alignerr", "https://aitrainer.work/guides/alignerr-review", "Expert-level RLHF work", "Getting projects needs persistence"),
        ("Ethos", "https://aitrainer.work/guides/ethos-expert-network-review", "Business and strategy experts", "Expert network"),
        ("Rex", "https://aitrainer.work/platforms", "Coding, design, finance", "Use comparison page, find official site yourself"),
        ("Vetto", "https://aitrainer.work/platforms", "Law, healthcare, finance", "Use comparison page, find official site yourself"),
        ("Mindrift (Toloka)", "https://aitrainer.work/platforms", "Creative writing, NLP tasks", "Most open to generalists"),
    ]
    tracker = [["Platform", "Review page (no referral)", "Focus", "Notes", "Official site (find it yourself)",
                "Date applied", "Assessment taken", "Assessment result", "Status", "Pay rate offered (from listing)",
                "Hours this month", "Earned this month", "Next action"]]
    for k, (n, u, f, note) in enumerate(plats):
        r = k + 2
        tracker.append([n, u, f, note, "", "", "", "", "Not applied", "", 0, f"=IFERROR(J{r}*K{r},0)", ""])
    tracker.append(["TOTAL", "", "", "", "", "", "", "", "", "", f"=SUM(K2:K{len(plats)+1})", f"=SUM(L2:L{len(plats)+1})", ""])
    statuses = [["Status value", "Meaning"], ["Not applied", "Still researching"], ["Applied", "Profile submitted"],
                ["Assessment", "Test or AI interview pending"], ["Waitlisted", "Passed but no project yet"],
                ["Active", "Getting tasks"], ["Paused", "No tasks this month"], ["Rejected", "Note why, improve, retry later"]]
    checklist = [["Before you submit a qualification test", "Done? (Y/N)"],
                 ["Read every instruction twice", ""], ["Quiet place, one sitting, timer checked", ""],
                 ["Fact-checked every claim in the answers I rated", ""], ["Justifications cite specific evidence", ""],
                 ["Applied the rubric the same way every time", ""], ["Spelling and grammar checked", ""],
                 ["Did NOT use AI tools unless allowed", ""], ["Never paid a fee to join", ""]]
    workbook({"Platforms": tracker, "Status values": statuses, "Test checklist": checklist},
             HERE / "excel" / "ai-trainer-job-tracker.xlsx",
             col_widths={"Platforms": [18, 40, 30, 32, 28, 12, 14, 14, 12, 16, 12, 14, 24]})
    print("excel built")


def build_pdf():
    pdf_from_markdown(HERE / "concepts.md", HERE / "pdf" / f"{MOD}-handout.pdf",
                      title="Module 12 - Data Annotation, RLHF and Evaluations")
    print("pdf built")


if __name__ == "__main__":
    if "--no-images" not in ARGS:
        build_images()
    if "--no-notebooks" not in ARGS:
        build_notebooks()
    build_slides()
    build_excel()
    if "--no-pdf" not in ARGS:
        build_pdf()
