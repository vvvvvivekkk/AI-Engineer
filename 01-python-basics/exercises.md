# Module 01 — Exercises

Fourteen exercises, from easy (1–5) to medium (6–10) to hard (11–14). Write each solution as a function where it asks for one, and test it with the examples given. Solutions: [`solutions/solutions.py`](solutions/solutions.py) (runnable) and [`solutions/solutions.md`](solutions/solutions.md) (explanations).

Rule: try for at least 20 minutes before looking. When you get an error, read the traceback bottom up first.

---

## Easy

### 1. Receipt line
Given `item = "notebook"`, `price = 45.5` and `quantity = 3`, print exactly:
```text
3 x notebook @ 45.50 = 136.50
```
Use one f-string.

### 2. Temperature converter
Write `c_to_f(celsius)` that returns Fahrenheit (`F = C * 9/5 + 32`). Then loop over `[-10, 0, 37, 100]` and print each pair, rounded to 1 decimal.

### 3. Even or odd, positive or negative
Write `describe(n)` that returns strings like `"positive even"`, `"negative odd"` or `"zero"`. Test on `[4, -3, 0, 7, -8]`.

### 4. String surgery
Given `s = "  Artificial Intelligence  "`:
(a) remove the outer spaces, (b) print it in uppercase, (c) print the first 10 characters, (d) count the letter `i` (any case), (e) replace `"Intelligence"` with `"Engineering"`.

### 5. List basics
Start with `nums = [5, 3, 8, 1, 9, 2]`. Print the sum, the average, the max and min, the list sorted, the list reversed, and a new list with only the numbers greater than 4.

---

## Medium

### 6. Word frequency
Write `word_counts(text)` that returns a dict from each lowercase word to how often it appears, ignoring the punctuation `.,!?`. Then print the 3 most common words.
Test: `"The cat sat. The cat ran! A dog sat?"` → `the: 2, cat: 2, sat: 2`.

### 7. FizzBuzz as a list
Write `fizzbuzz(n)` that **returns a list** (not prints) of the FizzBuzz values for 1 to n, e.g. `fizzbuzz(5)` → `[1, 2, "Fizz", 4, "Buzz"]`.

### 8. Safe number parser
Write `parse_numbers(items)` that takes a list of strings like `["4", "x", "2.5", "", "-1"]` and returns `(numbers, bad)` where `numbers` is a list of floats that converted and `bad` is a list of the strings that did not. Use `try` / `except ValueError`.

### 9. Merge and invert
Given two dicts of stock, `shop_a = {"apple": 5, "pear": 2}` and `shop_b = {"apple": 3, "kiwi": 7}`:
(a) write `merge_stock(a, b)` that adds counts for shared keys → `{"apple": 8, "pear": 2, "kiwi": 7}`;
(b) using a comprehension, list the fruits with stock below 5;
(c) find which fruits are in both shops using sets.

### 10. Read the traceback
Without running it, read this traceback and answer: (a) what type of error, (b) which function and line failed, (c) which function called it, (d) what is the most likely fix?

```text
Traceback (most recent call last):
  File "shop.py", line 14, in <module>
    print(total_price(cart))
          ~~~~~~~~~~~^^^^^^
  File "shop.py", line 9, in total_price
    total += item_price(name, qty)
             ~~~~~~~~~~^^^^^^^^^^^
  File "shop.py", line 4, in item_price
    return PRICES[name] * qty
           ~~~~~~^^^^^^
KeyError: 'mango'
```

---

## Hard

### 11. Grade statistics from a file
Write a program that writes this text to `scores.txt`, then reads it back and prints each student's average and the class's best student. Skip and report lines that are malformed.
```text
Asha: 88, 92, 79
Ravi: 95, 89, 91
Meera: 72, x, 80
John 55, 61, 48
```
(`Meera` has a bad number; `John` has no colon.)

### 12. A `BankAccount` class
Write a class with `owner` and `balance` attributes and methods `deposit(amount)`, `withdraw(amount)` and `__repr__`. `deposit`/`withdraw` must raise `ValueError` for non-positive amounts, and `withdraw` must raise `ValueError("insufficient funds")` if the balance is too low. Keep a `history` list of `(action, amount)` tuples.

### 13. Prompt builder
Write `build_prompt(task, examples, question)` that returns a **few-shot prompt** (a prompt that shows the model some worked examples before the real question). `examples` is a list of `(input, output)` tuples. Output format:
```text
Task: Classify the sentiment as positive or negative.

Input: I loved it
Output: positive

Input: Terrible service
Output: negative

Input: The food was great
Output:
```
Raise `ValueError` if `examples` is empty. Then save the prompt and its settings (`{"task": ..., "n_examples": ...}`) to a JSON file and load it back.

### 14. Extend the text adventure
Copy `code/text_adventure.py`. Add: (a) a new room `"garden"` reachable from the library; (b) a second item `"badge"` in the garden; (c) the exit now needs **both** the key and the badge; (d) a `"look"` command that repeats the room description and a `"inventory"` command that lists items in alphabetical order. Update the `--auto` script so it still wins.
