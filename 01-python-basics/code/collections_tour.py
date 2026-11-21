"""
collections_tour.py - lists, tuples, dicts, sets and comprehensions.

Run it:   python code/collections_tour.py
"""

# ---- Lists: ordered and changeable ---------------------------------------
scores = [72, 88, 95, 60]          # square brackets make a list
scores.append(81)                  # add 81 to the end
scores.sort()                      # sort the list itself, smallest first
print("Sorted scores:", scores)
print("Top score:", scores[-1], "| Lowest:", scores[0])        # -1 means "last item"
print("Average:", round(sum(scores) / len(scores), 1))          # total / count

# ---- Tuples: ordered and fixed -------------------------------------------
image_size = (28, 28)              # round brackets make a tuple (height, width)
height, width = image_size         # "unpack" the two values into two names
print(f"Image is {height}x{width} = {height * width} pixels")

# ---- Dictionaries: look up values by key ---------------------------------
student = {"name": "Ravi", "age": 20, "scores": [88, 92]}      # key: value pairs
student["city"] = "Hyderabad"      # add a new key
print(student["name"], "lives in", student["city"])
print("Email:", student.get("email", "not given"))             # .get avoids a KeyError
for key, value in student.items(): # loop over (key, value) pairs
    print(f"  {key:<7} -> {value}")

# A chat message for an AI model is just a dict; a conversation is a list of dicts.
conversation = [
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "What is a tuple?"},
]
print("Last speaker:", conversation[-1]["role"])

# ---- Sets: unique items ----------------------------------------------------
labels = ["cat", "dog", "cat", "bird", "dog"]                   # list with repeats
unique = set(labels)               # a set keeps each value only once
print("Unique labels:", sorted(unique), "| count:", len(unique))
skills_a = {"python", "sql", "git"}
skills_b = {"python", "docker"}
print("Shared skills:", skills_a & skills_b)                    # & = in both sets

# ---- Comprehensions: build a new collection in one line --------------------
squares = [n * n for n in range(1, 6)]                          # [1, 4, 9, 16, 25]
evens = [n for n in range(10) if n % 2 == 0]                    # keep only even numbers
words = ["  Hello ", "WORLD  ", " Python"]
clean_words = [w.strip().lower() for w in words]                # tidy every word
word_lengths = {w: len(w) for w in clean_words}                 # dict comprehension
print(squares, evens, clean_words, word_lengths, sep="\n")      # sep="\n" = one per line
