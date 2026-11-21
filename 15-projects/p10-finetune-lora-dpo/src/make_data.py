"""
make_data.py - build the fine-tuning datasets.

1. SFT data (**supervised fine-tuning** = showing the model input -> correct
   output examples): ~1,500 support emails, each paired with the exact JSON we
   want back. Labels are exact because the same script writes the email and the JSON.
     data/sft_train.jsonl  (1,350)    data/sft_test.jsonl  (150)
2. DPO data (**direct preference optimisation** = showing the model a *better*
   and a *worse* answer to the same prompt): ~300 pairs where "chosen" is the
   correct JSON and "rejected" is a typical mistake (wrong intent, invented order
   id, missing field, chatty text around the JSON, markdown fences, invalid JSON).
     data/dpo_train.jsonl (260)       data/dpo_test.jsonl (40)

The email style matches project P9 (same products, intents and edge cases), so a
model trained here could replace P9's extractor.

Run:  python -m src.make_data
      python -m src.make_data --from-p6 ../p06-response-rating-tool/data/preferences_hh.jsonl
          (also converts P6's HH-RLHF preference export into data/dpo_from_p6.jsonl)
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
SEED = 2026

SYSTEM = ("Extract the support ticket as JSON with keys order_id, product, intent, urgency. "
          "Use null when a value is missing. Reply with JSON only.")
PRODUCTS = ["AquaPure Filter", "SmartKettle 2", "FitBand Pro", "SoundBuds X", "HomeCam 360"]
INTENTS = {
    "refund": ["I want a refund for my {p}{o}.", "Please give me my money back for the {p}{o}.",
               "Can I return the {p}{o} and get a refund?"],
    "delivery_status": ["Where is my {p}{o}? It has been {d} days.", "My {p}{o} has not arrived yet.",
                        "Any update on the delivery of my {p}{o}?"],
    "damaged_item": ["The {p}{o} arrived broken.", "My {p}{o} came with a cracked case.",
                     "The {p}{o} was damaged in the box and won't turn on."],
    "cancel_order": ["Please cancel my order for the {p}{o}.", "I need to cancel the {p}{o}, ordered by mistake."],
    "billing_issue": ["I was charged twice for the {p}{o}.", "Wrong amount on my card for the {p}{o}."],
    "technical_support": ["How do I pair my {p} with the app?", "My {p} keeps disconnecting from Wi-Fi."],
}
URGENT_ADDONS = ["This is UNACCEPTABLE!", "I will file a chargeback if this is not fixed today.",
                 "It started smoking when I plugged it in!"]
OPENERS = ["Hi,", "Hello team,", "Dear support,", "hey", ""]
CLOSERS = ["Thanks", "Regards", "Cheers", "Thank you"]
NAMES = ["Asha", "Ben", "Chen", "Divya", "Emma", "Farhan", "Grace", "Hiro", "Isha", "Jack", "Kavya", "Liam"]


def make_example(rng: random.Random) -> dict:
    intent = rng.choice(list(INTENTS))
    product = rng.choice(PRODUCTS) if rng.random() > 0.08 else None
    oid = f"ORD-{rng.randint(10000, 99999)}" if rng.random() > 0.25 else None
    text = rng.choice(INTENTS[intent]).format(p=product or "order", o=f" ({oid})" if oid else "", d=rng.randint(3, 14))
    urgency = "low" if intent == "technical_support" else "medium"
    if rng.random() < 0.2:
        text += " " + rng.choice(URGENT_ADDONS)
        urgency = "high"
    if oid is None and intent != "technical_support" and rng.random() < 0.5:
        text += f" My phone is +91 98{rng.randint(100, 999)}-{rng.randint(10000, 99999)}."   # a distractor number
    email = f"{rng.choice(OPENERS)}\n{text}\n{rng.choice(CLOSERS)},\n{rng.choice(NAMES)}".strip()
    target = {"order_id": oid, "product": product if product and product in text else None,
              "intent": intent, "urgency": urgency}
    return {"email": email, "target": target}


def to_chat(ex: dict) -> dict:
    """Chat format: system instruction, the email as the user turn, the JSON as the assistant turn."""
    return {"messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": ex["email"]},
                         {"role": "assistant", "content": json.dumps(ex["target"])}],
            "target": ex["target"]}


def corrupt(target: dict, rng: random.Random) -> tuple[str, str]:
    """A realistic wrong answer and the name of the mistake."""
    kind = rng.choice(["wrong_intent", "invented_order_id", "missing_field", "chatty", "markdown_fence",
                       "invalid_json", "wrong_urgency"])
    t = dict(target)
    if kind == "wrong_intent":
        t["intent"] = rng.choice([i for i in INTENTS if i != target["intent"]])
    elif kind == "invented_order_id":
        t["order_id"] = f"ORD-{rng.randint(10000, 99999)}" if target["order_id"] is None else "ORD-00000"
    elif kind == "missing_field":
        t.pop(rng.choice(list(t)))
    elif kind == "wrong_urgency":
        t["urgency"] = rng.choice([u for u in ["low", "medium", "high"] if u != target["urgency"]])
    elif kind == "chatty":
        return f"Sure! Here is the JSON you asked for: {json.dumps(target)} Let me know if you need anything else.", kind
    elif kind == "markdown_fence":
        return f"```json\n{json.dumps(target)}\n```", kind
    else:
        return json.dumps(target)[:-8], kind                            # cut off -> not parseable
    return json.dumps(t), kind


def to_pair(ex: dict, rng: random.Random) -> dict:
    """Preference pair in TRL's conversational format (prompt / chosen / rejected)."""
    rejected, kind = corrupt(ex["target"], rng)
    return {"prompt": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": ex["email"]}],
            "chosen": [{"role": "assistant", "content": json.dumps(ex["target"])}],
            "rejected": [{"role": "assistant", "content": rejected}], "mistake": kind}


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def convert_p6(path: Path) -> list[dict]:
    """P6 exports HH-RLHF style rows with prompt / chosen_response / rejected_response -> TRL format."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        rows.append({"prompt": [{"role": "user", "content": r["prompt"]}],
                     "chosen": [{"role": "assistant", "content": r["chosen_response"]}],
                     "rejected": [{"role": "assistant", "content": r["rejected_response"]}], "mistake": "p6_human"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1500)
    ap.add_argument("--from-p6", type=Path, default=None)
    args = ap.parse_args()
    rng = random.Random(SEED)
    examples, seen = [], set()
    while len(examples) < args.n:                                       # no duplicate emails
        ex = make_example(rng)
        if ex["email"] not in seen:
            seen.add(ex["email"])
            examples.append(ex)
    DATA.mkdir(exist_ok=True)
    write_jsonl(DATA / "sft_train.jsonl", [to_chat(e) for e in examples[:1350]])
    write_jsonl(DATA / "sft_test.jsonl", [to_chat(e) for e in examples[1350:]])
    pairs = [to_pair(e, rng) for e in examples[:300]]                   # DPO prompts come from the training emails
    write_jsonl(DATA / "dpo_train.jsonl", pairs[:260])
    write_jsonl(DATA / "dpo_test.jsonl", pairs[260:])
    print(f"SFT: 1350 train / {len(examples) - 1350} test | DPO: 260 train / 40 test pairs")
    if args.from_p6:
        p6 = convert_p6(args.from_p6)
        write_jsonl(DATA / "dpo_from_p6.jsonl", p6)
        print(f"converted {len(p6)} P6 preference pairs -> data/dpo_from_p6.jsonl")


if __name__ == "__main__":
    main()
