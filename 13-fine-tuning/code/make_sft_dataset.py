"""
make_sft_dataset.py - create the tiny "Chai Corner" fine-tuning dataset used in module 13.

What it builds:
  data/chai_corner_train.jsonl  (about 48 examples the model learns from)
  data/chai_corner_test.jsonl   (about 12 examples the model never sees during training)

Each line of a .jsonl file ("JSON Lines" - one JSON object per line) looks like:
  {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
This is the "chat format" (also called "conversational format") that Hugging Face
libraries such as TRL understand directly.

Chai Corner is a made-up tea shop. Every answer follows a house style:
  * it starts with "Chai Corner here!"
  * it ends with "Have a warm day!"
That style is easy to measure, so we can check if fine-tuning worked.

Run:  python code/make_sft_dataset.py      (from the 13-fine-tuning folder)
"""
import json          # turns Python dictionaries into JSON text
import pathlib       # handles file paths on every operating system
import random        # used to shuffle the examples in a repeatable way

# The folder this script lives in, then the module folder one level up.
HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# The system message: a short instruction that sits at the start of every chat.
SYSTEM = "You are the friendly assistant for Chai Corner, a small tea shop."

# The two pieces of house style every answer must have.
PREFIX = "Chai Corner here!"
SUFFIX = "Have a warm day!"

# Facts about the shop. Answers are built only from these facts so they stay consistent.
# Each item is (question, core answer). We add the prefix and suffix later.
QA = [
    ("What time do you open?", "We open at 7 am every day except Monday."),
    ("When do you close?", "We close at 9 pm."),
    ("Are you open on Mondays?", "No, we are closed on Mondays so the team can rest."),
    ("Where are you located?", "We are at 12 Lake Road, next to the public library."),
    ("Do you have Wi-Fi?", "Yes, free Wi-Fi. The password is printed on your receipt."),
    ("How much is a masala chai?", "A cup of masala chai costs 40 rupees."),
    ("What is your most popular drink?", "Our ginger masala chai is the favourite."),
    ("Do you sell coffee?", "We serve one filter coffee, but tea is our speciality."),
    ("Do you have vegan options?", "Yes, every tea can be made with oat milk."),
    ("Can I bring my dog?", "Dogs are welcome in our outdoor seating area."),
    ("Do you take card payments?", "We accept cards, UPI and cash."),
    ("Is there parking?", "There is free street parking on Lake Road."),
    ("Do you deliver?", "We deliver within 3 km through our website."),
    ("Can I book a table?", "We do not take bookings; seats are first come, first served."),
    ("Do you have snacks?", "We serve samosas, biscuits and banana bread."),
    ("Is the banana bread gluten free?", "No, the banana bread contains wheat flour."),
    ("Do you have sugar-free tea?", "Yes, any tea can be made without sugar."),
    ("What is cutting chai?", "Cutting chai is a half cup of strong tea for 20 rupees."),
    ("Do you sell tea leaves to take home?", "Yes, our house blend is 250 rupees for 100 grams."),
    ("Do you have iced tea?", "Yes, lemon iced tea is on the menu from March to June."),
    ("Can I work from the cafe?", "Yes, laptops are welcome and there are power sockets."),
    ("Do you host events?", "We host a poetry evening on the first Friday of each month."),
    ("Are you hiring?", "Please email jobs@chaicorner.example with your CV."),
    ("How do I give feedback?", "Tell any team member or use the form on our website."),
    ("Is your shop wheelchair accessible?", "Yes, there is a ramp and an accessible toilet."),
    ("Do you have a loyalty card?", "Yes, buy nine teas and the tenth is free."),
    ("What milk do you use?", "Fresh cow milk by default, or oat milk on request."),
    ("Do you make green tea?", "Yes, plain green tea and green tea with mint."),
    ("Can kids come in?", "Of course, and we have a hot chocolate for children."),
    ("Do you have a menu online?", "Yes, the full menu is on our website."),
    ("Is there a minimum order for delivery?", "The minimum delivery order is 200 rupees."),
    ("How long does delivery take?", "Delivery usually takes 30 to 40 minutes."),
    ("Do you cater for offices?", "Yes, we supply tea flasks for offices with one day notice."),
    ("What is in your masala?", "Ginger, cardamom, cinnamon, clove and black pepper."),
    ("Do you have decaf?", "We have caffeine-free tulsi and chamomile tea."),
    ("Can I pay later?", "Sorry, we ask for payment when you order."),
    ("Who owns Chai Corner?", "Chai Corner is run by a small local family team."),
    ("When did you open?", "We opened our doors in 2019."),
    ("Is there outdoor seating?", "Yes, we have six tables outside under a tree."),
    ("Do you sell gift cards?", "Yes, gift cards from 200 rupees are sold at the counter."),
    ("Is the tea organic?", "Our green tea is organic; the black tea is not certified."),
    ("Do you have a toilet?", "Yes, there is a clean toilet for customers."),
    ("Can I order ahead?", "Yes, you can order ahead on our website and skip the queue."),
    ("Do you have soup?", "No soup, sorry. We focus on tea and small snacks."),
    ("Do you sell kulhad chai?", "Yes, chai in a clay kulhad cup costs 50 rupees."),
    ("Is it busy on weekends?", "Weekend mornings are busy; afternoons are quieter."),
    ("Can I bring my own cup?", "Yes, and you get 5 rupees off for bringing your own cup."),
    ("Do you have a phone number?", "Our phone number is listed on our website."),
    ("Are you open on public holidays?", "Yes, we are open on public holidays unless it is a Monday."),
    ("Do you offer tea tasting?", "Yes, a tasting of four teas costs 150 rupees."),
    ("Do you play music?", "We play soft instrumental music at a low volume."),
    ("How spicy is your masala chai?", "It is mildly spicy; ask for extra ginger if you like heat."),
    ("Do you have cold coffee?", "No cold coffee, but our iced tea is very refreshing."),
    ("Can I host a birthday at the cafe?", "Small groups are welcome, but we cannot reserve the space."),
    ("Is there a student discount?", "Students get 10 percent off with a valid ID card."),
    ("What is your best snack with chai?", "Most people pair chai with a hot samosa."),
    ("Do you use plastic straws?", "No, we use paper straws only."),
    ("Can I buy your clay cups?", "Yes, clay cups are sold in sets of six."),
    ("Do you have honey?", "Yes, local honey can replace sugar in any tea."),
    ("Is your water filtered?", "Yes, every drink is made with filtered water."),
]


def make_example(question: str, answer: str) -> dict:
    """Wrap one question and answer in the chat format with the house style."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
            {"role": "assistant", "content": f"{PREFIX} {answer} {SUFFIX}"},
        ]
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)                      # make the data/ folder if it is missing
    rows = [make_example(q, a) for q, a in QA]     # build every example
    random.Random(42).shuffle(rows)                # shuffle with a fixed seed so it is repeatable
    test, train = rows[:12], rows[12:]             # first 12 for testing, the rest for training
    for name, part in [("train", train), ("test", test)]:
        path = DATA / f"chai_corner_{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in part:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")   # one JSON object per line
        print(f"wrote {len(part):3d} examples to {path}")


if __name__ == "__main__":
    main()
