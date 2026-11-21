"""
make_pdfs.py - write 10 small, fictional company-policy PDFs and a golden question set.

The company "Northwind Labs" is invented. Every policy is a list of sections;
each section holds one or two clear facts. Two sections go on each PDF page, so
we know exactly which page every fact lives on. That lets us build a
**golden set** - a list of questions with the correct document and page, used
like an exam answer key to measure retrieval quality.

**reportlab** is a Python library that draws PDF files (text, pages, fonts).

Run:  python -m src.make_pdfs     -> data/pdfs/*.pdf and data/golden.json
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

# Each policy: file name, title, and sections of (heading, body text, golden question or None).
POLICIES = {
    "leave-policy": ("Leave Policy", [
        ("Annual leave", "Full-time employees receive 24 days of paid annual leave per calendar year. Leave is requested in the HR portal at least 10 working days in advance.",
         "How many days of paid annual leave do full-time employees get?"),
        ("Carry-over", "Up to 5 unused annual leave days may be carried over into the next year. Carried-over days expire on 31 March.",
         "When do carried-over leave days expire?"),
        ("Sick leave", "Employees may take 12 days of paid sick leave per year. A doctor's note is required for absences longer than 3 consecutive days.",
         "After how many consecutive sick days is a doctor's note required?"),
        ("Parental leave", "Primary caregivers receive 26 weeks of paid parental leave. Secondary caregivers receive 6 weeks of paid parental leave.",
         "How many weeks of paid parental leave do secondary caregivers receive?"),
        ("Bereavement leave", "Employees may take up to 5 days of paid bereavement leave after the death of a close family member.",
         None),
    ]),
    "expense-policy": ("Expense Policy", [
        ("Submitting claims", "Expense claims must be submitted in the finance tool within 30 days of the purchase, with an itemised receipt attached.",
         "Within how many days must expense claims be submitted?"),
        ("Meals", "When travelling, meals are reimbursed up to 60 dollars per day. Alcohol is never reimbursed.",
         "What is the daily meal allowance when travelling?"),
        ("Missing receipts", "If a receipt is lost, complete the missing-receipt form and get approval from your line manager. This is allowed at most twice per year.",
         "How many times per year can the missing-receipt form be used?"),
        ("Approval limits", "Purchases above 1,000 dollars need written approval from a director before the money is spent.",
         "Which purchases need approval from a director?"),
    ]),
    "security-policy": ("Information Security Policy", [
        ("Passwords", "Passwords must be at least 14 characters long and must never be shared, including with colleagues or IT staff.",
         "What is the minimum password length?"),
        ("Multi-factor authentication", "Multi-factor authentication is mandatory for email, the VPN and all cloud tools. Use the Northwind Authenticator app.",
         "Which app is used for multi-factor authentication?"),
        ("Phishing", "Report suspicious emails with the Report Phish button in the mail client. If you clicked a link, call the security hotline on extension 4444 immediately.",
         "What extension is the security hotline?"),
        ("Removable media", "Unknown USB drives must not be plugged into any company device. Hand found devices to the security desk on floor 2.",
         "Where should found USB drives be handed in?"),
        ("Screen lock", "Laptops must lock automatically after 5 minutes of inactivity.", None),
    ]),
    "onboarding-guide": ("New Starter Onboarding Guide", [
        ("First day", "New starters arrive at 9:30 on their first day and meet their onboarding buddy at the reception desk.",
         "What time do new starters arrive on their first day?"),
        ("Equipment", "Your laptop is set up by IT before day one. Collect it from the IT bar on floor 3.",
         "Where do new starters collect their laptop?"),
        ("Training", "All new starters must finish the security and data-privacy e-learning modules within their first 14 days.",
         "How long do new starters have to finish the security e-learning?"),
        ("Probation", "The probation period lasts 6 months. A review meeting with your manager takes place at month 3 and month 6.",
         "How long is the probation period?"),
    ]),
    "remote-work-policy": ("Remote Work Policy", [
        ("Eligibility", "Employees who have passed probation may work remotely up to 3 days per week, agreed with their manager.",
         "How many days per week can employees work remotely?"),
        ("Home office allowance", "A one-off home office allowance of 400 dollars is paid for a desk, chair or monitor.",
         "How much is the home office allowance?"),
        ("Working abroad", "Working from another country is allowed for up to 20 working days per year and needs HR approval in advance.",
         "How many days per year can employees work from another country?"),
        ("Core hours", "Core collaboration hours are 10:00 to 15:00 local time, when everyone should be reachable.",
         "What are the core collaboration hours?"),
    ]),
    "travel-policy": ("Business Travel Policy", [
        ("Booking", "All business travel is booked through the TravelDesk portal. Flights must be booked at least 14 days ahead where possible.",
         "Which portal is used to book business travel?"),
        ("Flight class", "Economy class is used for flights under 6 hours. Premium economy is allowed for flights of 6 hours or longer.",
         "When is premium economy allowed?"),
        ("Hotels", "Hotel stays are reimbursed up to 180 dollars per night in most cities and 250 dollars per night in high-cost cities.",
         "What is the hotel limit per night in high-cost cities?"),
        ("Travel insurance", "Company travel insurance covers all business trips automatically. The policy number is in the TravelDesk portal.",
         None),
    ]),
    "code-of-conduct": ("Code of Conduct", [
        ("Gifts", "Gifts from suppliers worth more than 50 dollars must be declined or declared to the compliance team.",
         "Above what value must supplier gifts be declared?"),
        ("Conflicts of interest", "Any personal relationship with a supplier or candidate must be disclosed to your manager and the compliance team.",
         "Who must you tell about a conflict of interest?"),
        ("Speaking up", "Concerns can be raised anonymously through the SpeakUp line, which is run by an independent company.",
         "How can concerns be raised anonymously?"),
        ("Social media", "Do not share confidential company information on social media. Only the communications team speaks for Northwind publicly.",
         "Who is allowed to speak for Northwind publicly?"),
    ]),
    "it-equipment-policy": ("IT Equipment Policy", [
        ("Laptop refresh", "Laptops are replaced every 4 years, or sooner if they fail and cannot be repaired.",
         "How often are laptops replaced?"),
        ("Personal use", "Reasonable personal use of company laptops is allowed, but no software may be installed without IT approval.",
         "Can you install software on a company laptop without approval?"),
        ("Lost devices", "Report a lost or stolen device to the IT service desk within 24 hours so it can be wiped remotely.",
         "How quickly must a lost device be reported?"),
        ("Returning equipment", "Leavers must return all equipment on their last working day. Unreturned laptops are charged at 900 dollars.",
         "How much are leavers charged for an unreturned laptop?"),
    ]),
    "data-privacy-policy": ("Data Privacy Policy", [
        ("Personal data", "Customer personal data may only be used for the purpose it was collected for and must never be shared with other customers.",
         None),
        ("Retention", "Customer records are kept for 7 years after the end of the contract and then deleted.",
         "How long are customer records kept?"),
        ("Data requests", "Requests from customers to see or delete their data must be forwarded to privacy@northwind.example within 2 working days.",
         "Where should customer data requests be forwarded?"),
        ("Breaches", "A suspected data breach must be reported to the privacy team within 1 hour of discovery.",
         "How quickly must a suspected data breach be reported?"),
    ]),
    "performance-review-policy": ("Performance Review Policy", [
        ("Review cycle", "Performance reviews happen twice a year, in June and December.",
         "In which months do performance reviews happen?"),
        ("Ratings", "Each review uses a 4-point scale: below expectations, meets, exceeds, and outstanding.",
         "How many points does the performance rating scale have?"),
        ("Pay rises", "Pay rises are decided in the December review and take effect from 1 February.",
         "When do pay rises take effect?"),
        ("Development budget", "Every employee has a learning budget of 1,200 dollars per year for courses, books and conferences.",
         "How large is the yearly learning budget?"),
    ]),
}

# Questions whose answer is NOT in any document - the system should say "not found".
UNANSWERABLE = [
    "What is the company's policy on bringing dogs to the office?",
    "How many parking spaces does the Berlin office have?",
    "What is the stock price of Northwind Labs?",
    "Who won the company football tournament last year?",
    "What is the Wi-Fi password for guests?",
]
SECTIONS_PER_PAGE = 2


def write_pdf(path: Path, title: str, sections: list[tuple]) -> list[dict]:
    """Draw one PDF; return where each golden question's answer ended up (doc + page)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    story, golden = [], []
    for i, (heading, body, question) in enumerate(sections):
        page = i // SECTIONS_PER_PAGE + 1                     # 1-based page number
        if i and i % SECTIONS_PER_PAGE == 0:
            story.append(PageBreak())                         # start a new page every 2 sections
        if i % SECTIONS_PER_PAGE == 0:
            story.append(Paragraph(f"Northwind Labs - {title}", styles["Title"]))
        story.append(Paragraph(heading, styles["Heading2"]))
        story.append(Paragraph(body, styles["BodyText"]))
        story.append(Spacer(1, 12))
        if question:
            golden.append({"question": question, "doc": path.name, "page": page, "evidence": body})
    # invariant=1 removes timestamps so the same input gives byte-identical PDFs
    SimpleDocTemplate(str(path), pagesize=A4, title=title, author="Northwind Labs (fictional)",
                      invariant=1).build(story)
    return golden


def main():
    out = DATA / "pdfs"
    out.mkdir(parents=True, exist_ok=True)
    golden = []
    for name, (title, sections) in POLICIES.items():
        golden += write_pdf(out / f"{name}.pdf", title, sections)
    golden += [{"question": q, "doc": None, "page": None, "evidence": None} for q in UNANSWERABLE]
    (DATA / "golden.json").write_text(json.dumps(golden, indent=2), encoding="utf-8")
    print(f"wrote {len(POLICIES)} PDFs to data/pdfs and {len(golden)} golden questions to data/golden.json")


if __name__ == "__main__":
    main()
