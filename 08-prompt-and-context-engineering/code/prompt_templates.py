"""
prompt_templates.py - keep prompts as named, versioned templates instead of strings scattered in code.

Analogy: a recipe card box. Each card has a name ("support_reply"), a version
("v2"), a list of blanks to fill in ({customer_name}, {question}) and a note on
what changed. You never scribble on an old card; you write a new one with a new
version number, so you can always go back.

Run it:  python code/prompt_templates.py
"""
import hashlib                     # hashlib makes a short "fingerprint" of the text, so any edit is detectable
import string                      # string.Formatter can list the {blanks} inside a template
from dataclasses import dataclass, field   # dataclass = a quick way to make a class that mostly holds data
from datetime import date


@dataclass(frozen=True)            # frozen=True: once created, a template cannot be changed (like a printed card)
class PromptTemplate:
    name: str                      # what the prompt is for, e.g. "classify_ticket"
    version: str                   # "v1", "v2" ... bump it on every change
    system: str                    # the system prompt text, may contain {blanks}
    user: str                      # the user message text, may contain {blanks}
    notes: str = ""                # why this version exists (changelog line)
    examples: tuple = ()           # few-shot pairs ((input, ideal_output), ...) sent as earlier chat turns
    created: str = field(default_factory=lambda: date.today().isoformat())

    def variables(self) -> set[str]:
        """List every {blank} the template expects."""
        names = set()
        for text in (self.system, self.user):
            for _, var, _, _ in string.Formatter().parse(text):   # parse() splits text into literal parts and {fields}
                if var:
                    names.add(var)
        return names

    def render(self, **values) -> tuple[str, str]:
        """Fill in the blanks. Refuse if any blank is missing or unexpected."""
        missing = self.variables() - values.keys()                # blanks we were not given
        extra = values.keys() - self.variables()                  # values the template never uses (often a typo)
        if missing:
            raise KeyError(f"{self.name}@{self.version} is missing values for: {sorted(missing)}")
        if extra:
            raise KeyError(f"{self.name}@{self.version} got unexpected values: {sorted(extra)}")
        return self.system.format(**values), self.user.format(**values)

    def fingerprint(self) -> str:
        """8-character hash of the text. Log it with every model call to know exactly which prompt ran."""
        return hashlib.sha256((self.system + "\n---\n" + self.user + repr(self.examples)).encode()).hexdigest()[:8]


class PromptRegistry:
    """A tiny in-memory 'card box'. In a real project this could be a YAML folder or a database."""

    def __init__(self):
        self._store: dict[tuple[str, str], PromptTemplate] = {}   # key = (name, version)

    def add(self, tpl: PromptTemplate) -> None:
        key = (tpl.name, tpl.version)
        if key in self._store:                                    # never overwrite: make a new version instead
            raise ValueError(f"{tpl.name}@{tpl.version} already exists - bump the version")
        self._store[key] = tpl

    def get(self, name: str, version: str = "latest") -> PromptTemplate:
        versions = sorted((v for (n, v) in self._store if n == name),
                          key=lambda v: int(v.lstrip("v")))        # "v10" sorts after "v9"
        if not versions:
            raise KeyError(name)
        return self._store[(name, versions[-1] if version == "latest" else version)]

    def history(self, name: str) -> list[str]:
        return [f"{t.version} [{t.fingerprint()}] {t.notes}" for (n, _), t in sorted(self._store.items()) if n == name]


# --- Example templates used in the notebooks ---------------------------------
REGISTRY = PromptRegistry()
REGISTRY.add(PromptTemplate(
    name="classify_ticket", version="v1",
    system="You sort customer support tickets.",
    user="Ticket: {ticket}\nCategory:",
    notes="first try, no list of allowed labels"))
REGISTRY.add(PromptTemplate(
    name="classify_ticket", version="v2",
    system=("You sort customer support tickets for an online shop.\n"
            "Allowed categories: billing, delivery, product, account.\n"
            "Reply with exactly one category word in lowercase and nothing else."),
    user="Ticket: {ticket}\nCategory:",
    notes="added allowed labels + strict output format"))
REGISTRY.add(PromptTemplate(
    name="classify_ticket", version="v3",
    system=("You sort customer support tickets for an online shop.\n"
            "Allowed categories: billing, delivery, product, account.\n"
            "Reply with exactly one category word in lowercase and nothing else."),
    user="Ticket: {ticket}",
    examples=(("Ticket: My card was charged the wrong amount", "billing"),
              ("Ticket: The box arrived two weeks late", "delivery"),
              ("Ticket: The stove does not light", "product"),
              ("Ticket: I forgot my username", "account")),
    notes="few-shot: 4 worked examples sent as earlier chat turns"))

if __name__ == "__main__":
    tpl = REGISTRY.get("classify_ticket")                         # newest version
    print("Using", tpl.name, tpl.version, "fingerprint", tpl.fingerprint())
    system, user = tpl.render(ticket="I was charged twice for my order")
    print("SYSTEM:\n" + system + "\nUSER:\n" + user)
    print("History:", *REGISTRY.history("classify_ticket"), sep="\n  ")
    try:
        tpl.render(tikcet="typo in the variable name")            # shows the safety check
    except KeyError as err:
        print("Caught mistake ->", err)
