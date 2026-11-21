# Module 01 — Solutions explained

Runnable code for exercises 1–13 is in [`solutions.py`](solutions.py) (`python solutions/solutions.py` prints every answer). Exercise 14 is in [`text_adventure_extended.py`](text_adventure_extended.py). This page explains the thinking behind each one.

---

### 1. Receipt line
One f-string with two format specifications: `{price:.2f}` and `{price * quantity:.2f}`. You can put any expression inside `{}`, not only a variable name. `.2f` always shows two decimals, so `45.5` becomes `45.50`.

### 2. Temperature converter
`c_to_f` is a one-line function: `return celsius * 9 / 5 + 32`. Python follows normal maths order (multiplication and division before addition). The loop prints with `:.1f`. Check: 37 °C is 98.6 °F.

### 3. Describe a number
Handle `0` first, because it is neither positive nor negative. Then two conditional expressions build the words: `"positive" if n > 0 else "negative"` and `"even" if n % 2 == 0 else "odd"`. In Python, `-3 % 2` is `1`, so negative odd numbers work correctly.

### 4. String surgery
`strip()` first, then each operation on the clean string. To count `i` in any case, lowercase the whole string first: `clean.lower().count("i")` gives `5`. Remember that string methods return new strings.

### 5. List basics
`sum(nums) / len(nums)` is the average. `sorted(nums)` returns a new list and leaves `nums` alone; `nums[::-1]` is a slice with step `-1`, which reverses. The filter is a comprehension: `[n for n in nums if n > 4]`.

### 6. Word frequency
Two steps: clean the text (remove punctuation, lowercase), then count with the dict pattern `counts[word] = counts.get(word, 0) + 1`. To get the top 3, sort the `(word, count)` pairs by count with `key=lambda pair: pair[1]` and `reverse=True`, then slice `[:3]`. (`collections.Counter(words).most_common(3)` does the same in one line.)

### 7. FizzBuzz as a list
Same logic as the notebook, but `append` to a list instead of printing, and `return` the list. Use `range(1, n + 1)` because `range` stops **before** its end value. Returning data (instead of printing) makes a function reusable and testable.

### 8. Safe number parser
Wrap only the risky line, `float(item)`, in `try`. On `ValueError` add the original string to `bad`. Note that `float("")` raises `ValueError` too. Return both lists as a tuple: `return numbers, bad`.

### 9. Merge and invert
Start from a **copy** of `a` (`dict(a)`) so the original is not changed. Add `b`'s counts with `merged.get(fruit, 0) + count`. Low stock is a comprehension over `.items()`. Fruits in both shops: `set(shop_a) & set(shop_b)` — turning a dict into a set gives its keys.

### 10. Read the traceback
Read bottom up:
- (a) **`KeyError: 'mango'`** — a dictionary lookup used a key that does not exist.
- (b) It failed in **`item_price`**, **line 4**: `return PRICES[name] * qty`. The `~~~^^^` markers point at `PRICES[name]`.
- (c) `item_price` was called by **`total_price`** on line 9, which was called from the top level of the file (`<module>`) on line 14.
- (d) The cart contains `"mango"` but the `PRICES` dict has no price for it. Add the price, or use `PRICES.get(name)` and handle unknown items with a clear message or a `ValueError`.

### 11. Grade statistics from a file
Write the file with `Path.write_text`, then read it line by line inside `with open(...)`. For each line: check for a colon first (otherwise `split(":")` would not give two parts), split only at the first colon with `split(":", 1)`, then convert the marks inside a `try`. A comprehension `[float(m) for m in marks_text.split(",")]` raises `ValueError` if any mark is bad, which skips the whole line. `max(averages, key=averages.get)` returns the name with the highest average.

### 12. BankAccount class
`__init__` sets `owner`, `balance` and an empty `history`. Each method checks its input **before** changing anything, and raises `ValueError` with a clear message if the input is invalid. Only after the checks pass do we update `balance` and append to `history`. `__repr__` controls what `print(acct)` shows.

### 13. Prompt builder
Build a list of lines and join them with `"\n".join(parts)`. That is easier to get right than adding strings together. `parts += [...]` adds several lines at once. Validate first: `if not examples: raise ValueError(...)` (an empty list is falsy). Save with `json.dumps(record, indent=2)` and read back with `json.loads`. This is a real AI-engineering pattern: few-shot prompts are covered properly in module 08.

### 14. Extend the text adventure
- Add `"west": "garden"` to the library's exits and a new `"garden"` room whose `"exits"` lead back east.
- Put `"item": "badge"` in the garden.
- Store the requirement as a set, `NEEDED_TO_EXIT = {"key", "badge"}`, and compute `missing = NEEDED_TO_EXIT - inventory` (set difference). If `missing` is not empty, the door stays locked and the message lists what is still needed.
- `"look"` calls `describe(room)` again; `"inventory"` prints `", ".join(sorted(inventory))` (or "nothing").
- The `--auto` script visits the garden for the badge, then the server room for the key, then goes north.
