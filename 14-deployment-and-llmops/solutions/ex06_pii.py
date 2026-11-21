"""
Exercise 6 solution - PAN and Aadhaar-like patterns added in the right ORDER.
Run:  python ex06_pii.py
"""
import re

PII_PATTERNS = {
    "EMAIL": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "PAN": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),                     # ABCDE1234F
    "CARD": re.compile(r"\b(?:\d[ -]?){12,15}\d\b"),                  # 13-16 digits
    # AADHAAR must run BEFORE PHONE, otherwise the first 10 digits would be called a phone number.
    "AADHAAR": re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}\b"),
    "PHONE": re.compile(r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\d[ -]?){9}\d(?!\d)"),
}


def redact_pii(text):
    counts = {}
    for label, pattern in PII_PATTERNS.items():
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = n
    return text, counts


def test_pan():
    assert redact_pii("PAN is ABCDE1234F.")[0] == "PAN is [PAN]."


def test_aadhaar():
    assert redact_pii("Aadhaar 1234 5678 9012 on file")[0] == "Aadhaar [AADHAAR] on file"


if __name__ == "__main__":
    test_pan(); test_aadhaar(); print("tests pass")
    # An innocent sentence that gets wrongly redacted (a false positive):
    print(redact_pii("Train 1234 5678 9012 is a made-up timetable code"))
    print(redact_pii("Product code HELLO2024X is in stock"))
