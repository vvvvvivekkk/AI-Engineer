"""
traceback_demo.py - practise reading error tracebacks.

Run it:
    python code/traceback_demo.py            # shows several tracebacks safely, then continues
    python code/traceback_demo.py --crash    # lets one error crash the program for real

Read every traceback from the BOTTOM up:
  1. last line  = what went wrong (exception type + message)
  2. frame above = where (file, line number, function)
  3. further up  = how the program got there
"""

import sys                                   # sys.argv lets us see "--crash"
import traceback                             # prints a traceback without stopping the program


def average(scores):                         # the innermost function: this is where it fails
    total = sum(scores)                      # sum of an empty list is 0
    return total / len(scores)               # len([]) is 0 -> ZeroDivisionError


def report(student):                         # calls average() for one student
    avg = average(student["scores"])         # KeyError here if "scores" is missing
    return f"{student['name']}: {avg:.1f}"


def show(label, func):
    """Run func(); if it fails, print the traceback and keep going."""
    print("=" * 60)                          # a separator line
    print(label)
    try:
        print(func())                        # run the code we were given
    except Exception:                        # catch ANY exception - only OK in a demo like this
        traceback.print_exc(file=sys.stdout) # print the full traceback, like a crash would
    print()                                  # blank line after each demo


def main():
    if "--crash" in sys.argv:                # the user asked for a real crash
        report({"name": "Ravi", "scores": []})   # nothing catches this, so Python stops here

    # Each lambda is a tiny function that wraps one broken line.
    show("1. Empty list -> ZeroDivisionError (3 frames deep)",
         lambda: report({"name": "Ravi", "scores": []}))
    show("2. Missing key -> KeyError",
         lambda: report({"name": "Meera"}))
    show("3. Text plus number -> TypeError",
         lambda: "Score: " + 95)
    show("4. Bad conversion -> ValueError",
         lambda: int("ninety"))
    show("5. Typo in a method name -> AttributeError (with a suggestion)",
         lambda: "hello".uppr())
    show("6. Position past the end -> IndexError",
         lambda: [10, 20, 30][3])
    print("The program is still running, because every error was caught.")


if __name__ == "__main__":
    main()
