# Module 01 - Python basics

## Variables and types
A **variable** is a name that points to a value, like a label on a box. Common types are `int` (whole numbers), `float` (decimals), `str` (text), `bool` (True or False), `list` (an ordered, changeable collection) and `dict` (key-value pairs, like a phone book).

## Functions
A **function** is a reusable block of code with a name. You define it with `def`, give it inputs called parameters, and send a result back with `return`. Functions keep code short and testable.

## Errors and try/except
When something goes wrong Python raises an **exception** and prints a **traceback**. Read a traceback from the bottom up: the last line names the error type and message. Wrap risky code in `try:` and handle the failure in `except ValueError:` so the program can recover instead of crashing.

## List comprehensions
A **list comprehension** builds a list in one line: `[x * 2 for x in numbers if x > 0]` doubles every positive number. It is shorter than a loop with `append`, but use a normal loop when the logic gets complicated.
