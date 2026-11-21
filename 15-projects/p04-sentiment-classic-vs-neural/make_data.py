"""
make_data.py - builds the labelled review data for Project 4.

1. data/reviews.csv   - 1,000 short product reviews made from templates + word banks
                        (seeded, so the file is identical every run). Includes negations
                        ("not bad" = positive) and contrast sentences ("good X but awful Y").
                        About 4% of labels are deliberately flipped, because real labels are messy;
                        the `label_flipped` column tells you which ones.
2. data/challenge.csv - 40 hand-written reviews that use words the templates never use, sarcasm,
                        tricky negation and mixed opinions. This is where classic models struggle.

Run:  python make_data.py
"""
import random
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
SEED = 13

PRODUCTS = ["blender", "kettle", "headphones", "phone case", "backpack", "desk lamp", "toaster",
            "water bottle", "keyboard", "charger", "running shoes", "coffee maker"]
ASPECTS = ["battery", "build quality", "price", "design", "sound", "delivery", "packaging",
           "customer service", "size", "material"]
POS_ADJ = ["great", "excellent", "amazing", "solid", "perfect", "fantastic", "reliable", "lovely", "superb"]
NEG_ADJ = ["terrible", "awful", "cheap", "flimsy", "useless", "disappointing", "broken", "poor", "horrible"]
POS_VERB = ["love", "really like", "recommend", "enjoy"]
NEG_VERB = ["hate", "regret buying", "returned", "cannot recommend"]
INTENS = ["really", "very", "super", "truly", "quite"]
POS_END = ["Would buy again.", "Five stars.", "Happy with it.", "Worth every penny."]
NEG_END = ["Would not buy again.", "One star.", "Waste of money.", "Avoid."]


def sentence(rng: random.Random, positive: bool) -> str:
    """One sentence whose meaning is positive or negative. Some use negation to flip a word."""
    p, a = rng.choice(PRODUCTS), rng.choice(ASPECTS)
    if positive:
        options = [
            f"The {a} is {rng.choice(INTENS)} {rng.choice(POS_ADJ)}.",
            f"I {rng.choice(POS_VERB)} this {p}.",
            f"{rng.choice(POS_ADJ).capitalize()} {p}, {rng.choice(INTENS)} {rng.choice(POS_ADJ)} {a}.",
            f"The {a} is not {rng.choice(NEG_ADJ)} at all.",              # negation -> positive
            f"I was worried, but the {p} is not {rng.choice(NEG_ADJ)}.",  # negation -> positive
            rng.choice(POS_END),
        ]
    else:
        options = [
            f"The {a} is {rng.choice(INTENS)} {rng.choice(NEG_ADJ)}.",
            f"I {rng.choice(NEG_VERB)} this {p}.",
            f"{rng.choice(NEG_ADJ).capitalize()} {p}, {rng.choice(INTENS)} {rng.choice(NEG_ADJ)} {a}.",
            f"The {a} is not {rng.choice(POS_ADJ)}.",                     # negation -> negative
            f"Sadly the {p} is not {rng.choice(POS_ADJ)} at all.",         # negation -> negative
            rng.choice(NEG_END),
        ]
    return rng.choice(options)


def review(rng: random.Random, positive: bool) -> str:
    """1-3 sentences. Sometimes a 'but' contrast where the LAST clause decides the label."""
    if rng.random() < 0.2:
        first = sentence(rng, not positive).rstrip(".")
        last = sentence(rng, positive)
        return f"{first}, but overall: {last[0].lower() + last[1:]}"
    return " ".join(sentence(rng, positive) for _ in range(rng.randint(1, 3)))


CHALLENGE = [
    # (text, label, kind)
    ("Oh wonderful, it stopped working after two days. Just what I needed.", "negative", "sarcasm"),
    ("Great, another charger that melts. Thanks a lot.", "negative", "sarcasm"),
    ("Fantastic way to waste forty dollars.", "negative", "sarcasm"),
    ("I just love waiting three weeks for a package that arrives crushed.", "negative", "sarcasm"),
    ("Best paperweight I have ever bought, since it does nothing else.", "negative", "sarcasm"),
    ("Sure, if you enjoy burnt toast every morning, this is perfect.", "negative", "sarcasm"),
    ("Wow, the strap snapped on day one. Superb engineering.", "negative", "sarcasm"),
    ("Truly amazing how fast the paint peeled off.", "negative", "sarcasm"),
    ("Exceeded my expectations, sturdy and elegant.", "positive", "unseen_words"),
    ("Brilliant gadget, it works flawlessly.", "positive", "unseen_words"),
    ("Delighted with this purchase, top notch craftsmanship.", "positive", "unseen_words"),
    ("Comfortable, quiet and gorgeous.", "positive", "unseen_words"),
    ("A joy to use every single day.", "positive", "unseen_words"),
    ("Shoddy stitching and it smells weird.", "negative", "unseen_words"),
    ("Mediocre at best, frankly a letdown.", "negative", "unseen_words"),
    ("It leaks, it rattles and it overheats.", "negative", "unseen_words"),
    ("Dreadful experience, the seller ignored my emails.", "negative", "unseen_words"),
    ("Junk. Fell apart in a week.", "negative", "unseen_words"),
    ("I can't say I'm unhappy with it.", "positive", "negation"),
    ("Never had a single problem with this kettle.", "positive", "negation"),
    ("Nothing about this blender is good.", "negative", "negation"),
    ("I wouldn't call it great, or even okay.", "negative", "negation"),
    ("No complaints whatsoever.", "positive", "negation"),
    ("Not the worst lamp, not the best either, but I kept it and use it daily.", "positive", "negation"),
    ("Hardly works and barely charges.", "negative", "negation"),
    ("I don't regret this at all.", "positive", "negation"),
    ("Not once did it fail me.", "positive", "negation"),
    ("It isn't anything like the photos, and not in a good way.", "negative", "negation"),
    ("Pricey, but honestly worth it for the quality.", "positive", "mixed"),
    ("Looks beautiful but broke within a month.", "negative", "mixed"),
    ("Slow delivery, yet the headphones sound incredible.", "positive", "mixed"),
    ("Lovely colour, shame it doesn't actually hold water.", "negative", "mixed"),
    ("The box was damaged, however the keyboard itself is excellent.", "positive", "mixed"),
    ("Cheap price, cheap quality. You get what you pay for.", "negative", "mixed"),
    ("A little heavy, but it is the most reliable backpack I've owned.", "positive", "mixed"),
    ("Nice design, terrible battery, I sent it back.", "negative", "mixed"),
    ("Customer service was rude, but they replaced it and the new one is great.", "positive", "mixed"),
    ("Started strong, then died after the warranty ended.", "negative", "mixed"),
    ("Five stars for looks, zero stars for function.", "negative", "mixed"),
    ("It took a while to set up but now I use it every day and love it.", "positive", "mixed"),
]


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for i in range(1000):
        positive = i % 2 == 0                     # exactly 500 positive, 500 negative
        label = "positive" if positive else "negative"
        flipped = rng.random() < 0.04             # ~4% label noise, like real annotation mistakes
        if flipped:
            label = "negative" if positive else "positive"
        rows.append({"text": review(rng, positive), "label": label, "label_flipped": flipped})
    df = pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)  # shuffle
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_DIR / "reviews.csv", index=False)
    pd.DataFrame(CHALLENGE, columns=["text", "label", "kind"]).to_csv(DATA_DIR / "challenge.csv", index=False)
    print(f"wrote data/reviews.csv ({len(df)} rows, {int(df.label_flipped.sum())} flipped labels) "
          f"and data/challenge.csv ({len(CHALLENGE)} rows)")


if __name__ == "__main__":
    main()
