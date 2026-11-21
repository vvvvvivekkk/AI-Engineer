"""
reward_model.py - a tiny reward model trained on preference pairs (stage 2 of RLHF).

It reads data/preference_pairs_sample.jsonl (prompt, chosen, rejected),
turns answers into word-count vectors, and trains a linear scorer with the
Bradley-Terry loss:  loss = -log(sigmoid(score_chosen - score_rejected)).

Run:  python code/reward_model.py
"""
import json                                          # read the JSONL file
import pathlib                                       # build file paths safely
import torch                                         # the training library
import torch.nn.functional as F                      # logsigmoid lives here
from sklearn.feature_extraction.text import CountVectorizer  # text -> word counts

torch.manual_seed(0)                                 # same results every run
DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "preference_pairs_sample.jsonl"

# 1. Load the pairs: one JSON object per line.
pairs = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
print(f"loaded {len(pairs)} preference pairs")

# 2. Learn a vocabulary from every answer, then turn answers into count vectors.
vec = CountVectorizer(stop_words="english")
vec.fit([p["chosen"] for p in pairs] + [p["rejected"] for p in pairs])
to_x = lambda texts: torch.tensor(vec.transform(texts).toarray(), dtype=torch.float32)
Xc = to_x([p["chosen"] for p in pairs])              # chosen answers as numbers
Xr = to_x([p["rejected"] for p in pairs])            # rejected answers as numbers

# 3. The reward model: one weight per word, plus a bias.
model = torch.nn.Linear(Xc.shape[1], 1)
opt = torch.optim.Adam(model.parameters(), lr=0.05, weight_decay=0.01)

# 4. Train with the Bradley-Terry loss.
for epoch in range(150):
    margin = model(Xc) - model(Xr)                   # score(chosen) - score(rejected)
    loss = -F.logsigmoid(margin).mean()              # small when margins are positive
    opt.zero_grad()                                  # clear old gradients
    loss.backward()                                  # compute new gradients
    opt.step()                                       # update the weights
    if epoch % 50 == 0:
        print(f"epoch {epoch:3d} loss {loss.item():.3f} accuracy {(margin > 0).float().mean().item():.2f}")

# 5. Use the trained reward model to score new answers.
with torch.no_grad():
    for text in ["A CPU is the chip that carries out a computer's instructions.",
                 "No idea, look it up."]:
        print(f"{model(to_x([text])).item():+.2f}  {text}")
