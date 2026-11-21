"""
Solution to exercise 14: the text adventure with a garden, a badge,
a two-item exit, and 'look' / 'inventory' commands.

Play:     python solutions/text_adventure_extended.py
Replay:   python solutions/text_adventure_extended.py --auto
"""

import sys                                         # to read --auto

ROOMS = {                                          # the map: room name -> details
    "lab": {"text": "The AI lab. Doors north and east.",
            "exits": {"north": "library", "east": "server room"}},
    "library": {"text": "Shelves of books. A door leads west to a garden; south back to the lab.",
                "exits": {"south": "lab", "west": "garden"}},           # (a) new exit
    "garden": {"text": "A quiet garden. A visitor BADGE hangs on a branch.",
               "exits": {"east": "library"}, "item": "badge"},          # (a) + (b)
    "server room": {"text": "Blinking lights. A KEY lies here. Exits: west, locked door north.",
                    "exits": {"west": "lab", "north": "exit"}, "item": "key"},
    "exit": {"text": "The door opens. You walk out. You win!", "exits": {}},
}
NEEDED_TO_EXIT = {"key", "badge"}                  # (c) both items are required


def describe(room):
    print(f"\n== {room.upper()} ==\n{ROOMS[room]['text']}")


def play(get_command):
    room, inventory = "lab", set()
    describe(room)
    while room != "exit":
        command = get_command().strip().lower()
        if command in ("quit", "q"):
            return False
        if command == "look":                      # (d) repeat the description
            describe(room)
            continue
        if command == "inventory":                 # (d) sorted list of items
            print("You carry:", ", ".join(sorted(inventory)) or "nothing")
            continue
        if command == "take":
            item = ROOMS[room].get("item")
            if item and item not in inventory:
                inventory.add(item)
                print(f"You take the {item}.")
            else:
                print("Nothing to take here.")
            continue
        exits = ROOMS[room]["exits"]
        if command not in exits:
            print(f"You can't go '{command}'. Exits: {', '.join(exits)}")
            continue
        target = exits[command]
        missing = NEEDED_TO_EXIT - inventory        # set difference: items still needed
        if target == "exit" and missing:
            print("The door is locked. You still need:", ", ".join(sorted(missing)))
            continue
        room = target
        describe(room)
    return True


def main():
    if "--auto" in sys.argv:
        script = iter(["north", "west", "take", "inventory", "east", "south",
                       "east", "north", "take", "look", "north"])
        def get_command():
            cmd = next(script)
            print(f"> {cmd}")
            return cmd
    else:
        def get_command():
            return input("> ")
    print("Result:", "won" if play(get_command) else "quit")


if __name__ == "__main__":
    main()
