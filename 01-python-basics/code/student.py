"""
student.py - a small class, and a module you can import.

Run it directly:      python code/student.py
Or import it:         from student import Student   (from inside the code/ folder)
"""


class Student:                                     # a class is a blueprint for objects
    """A student with a name and a list of scores."""

    def __init__(self, name):                      # runs automatically when a Student is created
        self.name = name                           # store the name on this object
        self.scores = []                           # every student starts with no scores

    def add_score(self, score):                    # a method: an action a Student can do
        if not 0 <= score <= 100:                  # reject impossible scores early
            raise ValueError(f"score must be 0-100, got {score}")
        self.scores.append(score)                  # remember the score

    def average(self):                             # compute this student's mean score
        if not self.scores:                        # an empty list counts as False
            return 0.0                             # avoid dividing by zero
        return sum(self.scores) / len(self.scores)

    def __repr__(self):                            # how the object looks when printed
        return f"Student({self.name!r}, avg={self.average():.1f})"


# Only runs when this file is executed directly, not when it is imported.
if __name__ == "__main__":
    asha = Student("Asha")                         # create one object (an "instance")
    asha.add_score(88)                             # call a method on it
    asha.add_score(94)
    print(asha)                                    # uses __repr__ -> Student('Asha', avg=91.0)
    try:
        asha.add_score(140)                        # this is invalid on purpose
    except ValueError as err:                      # catch the error we raised above
        print("Rejected:", err)
