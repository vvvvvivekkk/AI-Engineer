"""
basics_tour.py - values, variables, types, strings, conditions and loops in one script.

Run it:   python code/basics_tour.py
Read the comments, then change values and run again to see what changes.
"""

# ---- 1. Values and variables -------------------------------------------
name = "Asha"                      # a str (text) value, tagged with the name `name`
age = 21                           # an int (whole number)
height_m = 1.62                    # a float (decimal number)
is_student = True                  # a bool (True or False)
print(name, age, height_m, is_student)              # print several values, separated by spaces
print(type(name), type(age), type(height_m), type(is_student))  # show each value's type

# ---- 2. Arithmetic -------------------------------------------------------
print(7 / 2, 7 // 2, 7 % 2, 7 ** 2)  # division, floor division, remainder, power
age += 1                           # shortcut for: age = age + 1
print("Next year:", age)

# ---- 3. Converting text to numbers --------------------------------------
typed = "42"                       # data from files or input() always arrives as text
number = int(typed)                # convert text to an int so we can do maths
print(number * 2)                  # 84 (with the text "42" we would get "4242")

# ---- 4. Strings and f-strings -------------------------------------------
title = "  large language models  "          # extra spaces on purpose
clean = title.strip().title()                 # remove outer spaces, then Capitalise Each Word
print(clean)
print(clean[0], clean[-1], clean[:5])         # first char, last char, first five chars
accuracy = 0.91234                            # a fraction between 0 and 1
print(f"{name} built a model with {accuracy:.1%} accuracy")   # .1% = percent, 1 decimal

# ---- 5. Conditions --------------------------------------------------------
score = 78                         # try changing this to 95, 61 or 40
if score >= 90:                    # checked first
    grade = "A"
elif score >= 75:                  # only checked if the line above was False
    grade = "B"
elif score >= 60:
    grade = "C"
else:                              # runs when nothing above was True
    grade = "F"
print(f"Score {score} gives grade {grade}")

# ---- 6. Loops -------------------------------------------------------------
for epoch in range(3):             # range(3) gives 0, 1, 2
    print("Training epoch", epoch)

reviews = ["great", "bad", "great", "ok"]     # a small list of words
great_count = 0                    # the "accumulator" starts at zero
for review in reviews:             # visit each review once
    if review == "great":          # check the current one
        great_count += 1           # add one to the running total
print("Great reviews:", great_count)

balance = 100                      # money in an account
months = 0                         # how many months have passed
while balance < 200:               # repeat until the money has doubled
    balance *= 1.1                 # grow 10% this month
    months += 1                    # count the month
print(f"Doubled after {months} months: {balance:.2f}")
