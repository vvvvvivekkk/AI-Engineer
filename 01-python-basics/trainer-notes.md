# Module 01 — Trainer notes

This module is best taught as **two 2-hour sessions** (one per week), with students doing notebooks and exercises between sessions. Before teaching, work through all four notebooks yourself, run every script in `code/`, and do at least exercises 1, 6, 10 and 12 without looking at the solutions.

**Golden rule for teaching programming:** students must type code, not watch it. Every 10 minutes they should run something. Live-code slowly, make real mistakes, and read the error messages out loud — this teaches traceback reading better than any slide.

**Jargon to define the first time you say it:** statement, function, argument, value, type, variable, assignment, string, index, slice, method, immutable, list, tuple, dict, key, set, comprehension, parameter, return value, scope, exception, traceback, frame, module, import, class, object, attribute.

**Materials:** slides (`slides/01-python-basics.pptx`), the cheat sheet (`excel/python-cheatsheet.xlsx` — print the "Cheat sheet" and "Error guide" tabs), notebooks 01–04.

---

## 1. What students should be able to do after the module

1. Create variables of each basic type and convert between them (`int("42")`).
2. Slice strings and format output with f-strings (`f"{x:.2f}"`).
3. Pick the right collection (list, tuple, dict, set) for a problem and use its main operations.
4. Write `if` / `elif` / `else` chains, `for` and `while` loops, and simple comprehensions.
5. Write small functions with parameters, defaults and return values.
6. Catch specific exceptions with `try` / `except` and raise `ValueError` for bad input.
7. Read a traceback bottom up and point to the line to fix.
8. Read and write text and JSON files, and import modules.
9. Write a small class with `__init__` and methods.

## 2. Teaching sequence

### Session 1 (2 hours): the language core

| Time | Segment | What you do | What students do |
|---|---|---|---|
| 0:00–0:10 | Hook | Slide 1. Show one real AI SDK call; promise they will understand every symbol in it by the end of the module. | Open notebook 01 (Colab badge or VS Code). |
| 0:10–0:30 | Values, types, variables | Slides 2–4. Sticky-note analogy. Live: `"42" + "42"` vs `int("42") + 42`. | Notebook 01 sections 1–5 and the "Your turn". |
| 0:30–0:50 | Strings and f-strings | Slide 5. Draw "Python" with indexes on the board. Build a prompt with an f-string. | Notebook 01 sections 6–8; exercise 1 and 4. |
| 0:50–1:00 | Break | — | — |
| 1:00–1:20 | Decisions | Slide 8. Railway analogy. Ask what happens if the `>= 60` check comes first. | Notebook 01 section 9; exercise 3. |
| 1:20–1:45 | Loops | Slide 9. Do FizzBuzz on the board first, then in code. Show an infinite `while` and the stop button. | Notebook 01 sections 10–12, FizzBuzz; exercise 2. |
| 1:45–2:00 | Recap + homework | Three check questions (below). Homework: exercise 5, start notebook 02. | Answer, ask questions. |

### Session 2 (2 hours): collections, functions, errors, files

| Time | Segment | What you do | What students do |
|---|---|---|---|
| 0:00–0:25 | Collections | Slides 6–7. Analogies (lockers, sealed envelope, dictionary, guest list). Live-demo the copy trap. Show an AI chat as a list of dicts. | Notebook 02 sections 1–10. |
| 0:25–0:40 | Comprehensions | Slide 10. Loop version first, then the comprehension. | Notebook 02 sections 11–12; exercise 6. |
| 0:40–1:00 | Functions | Slide 11. Juice-machine analogy. Show a function with no `return` printing `None`. | Notebook 03 sections 1–5; exercise 7. |
| 1:00–1:05 | Break | — | — |
| 1:05–1:30 | Errors and tracebacks | Slides 12–13. Run `python code/traceback_demo.py --crash` and read it bottom up together. Then the full `try/except/else/finally`. | Notebook 03 sections 6–9; exercise 10 in pairs. |
| 1:30–1:45 | Files, modules, classes | Slides 14–15. Keep classes light: students mostly *use* objects. | Notebook 03 sections 10–14. |
| 1:45–2:00 | Mini-project launch | Slide 17. Walk through notebook 04 steps 1–5 together. | Finish notebook 04 and exercises 8–14 as homework. |

## 3. Common student mistakes and how to fix them

| Mistake | What they see | How to fix / explain |
|---|---|---|
| `=` instead of `==` in a condition | `SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?` | "One `=` puts a tag on a value. Two `==` asks a question." |
| Missing colon or indentation after `if`/`for`/`def` | `SyntaxError: expected ':'` or `IndentationError: expected an indented block` | Point at the line before the caret. Let VS Code indent for them (press Enter after the colon). |
| Adding text and numbers | `TypeError: can only concatenate str (not "int") to str` | Use an f-string, or `str()` / `int()`. Connect to "data from files is text". |
| Off-by-one with indexes and `range` | `IndexError: list index out of range`; loop runs one time too few | Draw the list with indexes 0..len-1; remind them `range(1, n + 1)` to include n. |
| `lst = lst.append(x)` or `x = lst.sort()` | The list becomes `None`; later `TypeError: 'NoneType' object...` | These methods change the list and return `None`. Use `lst.append(x)` alone, or `sorted(lst)`. |
| `b = a` and expecting a copy | Changing `b` changes `a` | Two name tags, one list. Use `a.copy()`. Show with notebook 02 section 3. |
| Printing instead of returning | Function result is `None` | `print` shows a value to a human; `return` hands it back to the program. |
| Bare `except:` that hides bugs | A typo silently "works" and gives wrong results | Catch specific exceptions. Remove the `try` temporarily to see the real error. |
| Reading tracebacks top down and panicking | "I don't understand any of this" | Cover the screen except the last line. Read it. Then reveal one frame at a time upwards. |
| Notebook cells run out of order | `NameError` or stale values | Restart kernel and run all. Number the cells' run order out loud once to show the problem. |
| Naming a file after a library (`json.py`, `random.py`) | Strange `AttributeError` when importing that library | Python imports your file instead. Rename it and delete `__pycache__`. |
| Forgetting `self` in a method | `TypeError: ... takes 0 positional arguments but 1 was given` | Every method's first parameter is `self`; Python fills it in. |

## 4. Questions to check understanding (with answers)

1. **What is the type of `"3.5"`, and how do you double it as a number?** It is a `str`. `float("3.5") * 2` gives `7.0`.
2. **What does `"Python"[1:4]` give?** `"yth"` — from index 1 up to, not including, 4.
3. **When would you use a dict instead of a list?** When you look things up by a name or key (a student's marks by name) rather than by position.
4. **Why does `{}` not make an empty set?** `{}` is an empty dict; use `set()`.
5. **What does this print: `x = [1, 2]; y = x; y.append(3); print(x)`?** `[1, 2, 3]` — `x` and `y` are the same list.
6. **Rewrite as a comprehension: a loop that appends `w.upper()` for each `w` in `words` if `len(w) > 3`.** `[w.upper() for w in words if len(w) > 3]`
7. **What does a function return if it has no `return` statement?** `None`.
8. **In a traceback, which line do you read first, and what does it tell you?** The last line; it gives the exception type and message — what went wrong.
9. **Why catch `ValueError` rather than using a bare `except`?** A bare `except` also catches mistakes you did not expect (like typos causing `NameError`), hiding real bugs.
10. **Why use `with open(...)` instead of plain `open(...)`?** `with` closes the file automatically, even if an error happens inside the block.
11. **What is `self` in a class method?** The particular object the method was called on.
12. **What does `if __name__ == "__main__":` do?** Runs the code below it only when the file is executed directly, not when it is imported as a module.

## 5. Adapting for faster or slower groups

**Slower groups**
- Spread the module over three or four sessions: (1) types and strings, (2) conditions and loops, (3) collections, (4) functions, errors, files.
- Skip classes and lambdas in class; point to notebook 03 sections 5 and 14 as optional reading.
- Use [Python Tutor](https://pythontutor.com/visualize.html#mode=edit) to animate loops and the list copy trap — seeing the arrows helps.
- Pair programming: one types, one reads instructions, swap every exercise.
- Set only exercises 1–8 as required.

**Faster groups**
- Add `*args` / `**kwargs`, `dataclasses`, and generators (`yield`) as a stretch demo.
- Ask them to add type hints to `grade_calculator.py` and explain each one.
- Exercise 14 plus their own extension (save/load the game state to JSON).
- Have them write small tests with `assert` for `letter_grade` and `parse_marks`, as a preview of testing in module 14.
- Challenge: solve five Project Euler problems (linked in resources.md) and compare solutions in pairs.
