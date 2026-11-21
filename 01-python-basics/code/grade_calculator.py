"""
grade_calculator.py - the mini-project as a script.

Reads a CSV of student marks, skips bad rows with a clear message,
computes each student's average and letter grade, prints a report
and saves the results to a JSON file.

Run it:
    python code/grade_calculator.py                 # uses built-in sample data
    python code/grade_calculator.py marks.csv       # uses your own CSV file

CSV format (first line is the header):
    name,maths,science,english
    Asha,88,92,79
"""

import csv                                     # reads comma-separated files
import io                                      # lets us treat a string like a file
import json                                    # saves results as JSON
import sys                                     # reads the optional file name
from pathlib import Path                       # file paths that work on every OS

# Sample data used when no file is given. Two rows are broken on purpose.
SAMPLE_CSV = """name,maths,science,english
Asha,88,92,79
Ravi,95,89,91
Meera,72,abc,80
John,55,61,48
Priya,101,90,85
Karan,66,74,70
"""

# Grade boundaries, checked from the top: (lowest score for this grade, letter).
GRADE_BOUNDARIES = [(90, "A"), (75, "B"), (60, "C"), (40, "D"), (0, "F")]


def letter_grade(score):
    """Turn a number from 0 to 100 into a letter grade."""
    for lowest, letter in GRADE_BOUNDARIES:    # walk the boundaries from high to low
        if score >= lowest:                    # the first boundary we reach wins
            return letter
    raise ValueError(f"score cannot be negative: {score}")   # only for scores below 0


def parse_marks(row, subjects):
    """Convert one CSV row's marks to floats. Raises ValueError for bad data."""
    marks = []                                 # collect this student's marks here
    for subject in subjects:                   # e.g. "maths", "science", "english"
        text = row[subject].strip()            # the raw text from the file
        mark = float(text)                     # ValueError if the text is not a number
        if not 0 <= mark <= 100:               # catch impossible marks too
            raise ValueError(f"{subject} mark {mark} is outside 0-100")
        marks.append(mark)
    return marks


def load_rows(path=None):
    """Return (subjects, rows) from a CSV file, or from the sample data if path is None."""
    if path is None:
        handle = io.StringIO(SAMPLE_CSV)       # make the sample string behave like a file
    else:
        handle = open(path, encoding="utf-8", newline="")   # newline="" is what csv expects
    with handle:                               # closes the file when we are done
        reader = csv.DictReader(handle)        # each row becomes a dict keyed by the header
        rows = list(reader)                    # read every row into a list
    subjects = [col for col in reader.fieldnames if col != "name"]   # all columns except name
    return subjects, rows


def build_report(subjects, rows):
    """Compute averages and grades. Returns (results list, list of skipped-row messages)."""
    results, skipped = [], []                  # two empty lists, created in one line
    for line_number, row in enumerate(rows, start=2):   # line 1 is the header
        try:
            marks = parse_marks(row, subjects)
        except ValueError as err:              # bad number or out-of-range mark
            skipped.append(f"line {line_number} ({row['name']}): {err}")
            continue                           # skip this student, go to the next row
        avg = sum(marks) / len(marks)
        results.append({"name": row["name"], "average": round(avg, 1),
                        "grade": letter_grade(avg)})
    results.sort(key=lambda r: r["average"], reverse=True)   # best average first
    return results, skipped


def print_report(results, skipped):
    """Print a neat table using f-string alignment."""
    print(f"{'Rank':<5}{'Name':<10}{'Average':>8}  Grade")
    print("-" * 31)
    for rank, r in enumerate(results, start=1):
        print(f"{rank:<5}{r['name']:<10}{r['average']:>8.1f}  {r['grade']}")
    if results:                                # avoid dividing by zero for an empty class
        class_avg = sum(r["average"] for r in results) / len(results)
        print(f"\nClass average: {class_avg:.1f}")
    for message in skipped:
        print("Skipped", message)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None   # optional file name
    try:
        subjects, rows = load_rows(path)
    except FileNotFoundError:                  # friendly message instead of a traceback
        print(f"Could not find {path!r}. Check the path and try again.")
        return
    results, skipped = build_report(subjects, rows)
    print_report(results, skipped)
    out = Path("grade_report.json")            # save next to where you ran the script
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} results to {out}")


if __name__ == "__main__":
    main()
