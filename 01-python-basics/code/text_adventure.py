"""
text_adventure.py - a tiny choose-your-path game using dicts, loops, functions and input().

Play it:            python code/text_adventure.py
Watch a replay:     python code/text_adventure.py --auto     (no typing needed)

The whole map is a dictionary. Each room has a description and a dict of exits.
"""

import sys                                       # to read the --auto option

# The game map: room name -> information about that room.
ROOMS = {
    "lab": {
        "text": "You are in the AI lab. A GPU hums. Doors lead north and east.",
        "exits": {"north": "library", "east": "server room"},
    },
    "library": {
        "text": "Shelves of Python books. A note says: 'the key is in the server room'.",
        "exits": {"south": "lab"},
    },
    "server room": {
        "text": "Blinking lights everywhere. You see a shiny KEY. Exits: west, and a locked door north.",
        "exits": {"west": "lab", "north": "exit"},
        "item": "key",
    },
    "exit": {
        "text": "You unlock the door and step outside. You win!",
        "exits": {},
    },
}


def describe(room_name):
    """Print the current room's description."""
    print(f"\n== {room_name.upper()} ==")             # room title in capitals
    print(ROOMS[room_name]["text"])                   # look the room up in the dict


def play(get_command):
    """Run the game loop. get_command is a function that returns the player's next command."""
    room = "lab"                                      # starting room
    inventory = set()                                 # a set: each item at most once
    describe(room)
    while room != "exit":                             # keep going until the player escapes
        command = get_command().strip().lower()       # tidy the typed text
        if command in ("quit", "q"):                  # let the player stop early
            print("Bye!")
            return False
        if command == "take":                         # pick up an item if there is one
            item = ROOMS[room].get("item")            # None if the room has no item
            if item and item not in inventory:
                inventory.add(item)
                print(f"You take the {item}.")
            else:
                print("Nothing to take here.")
            continue                                  # skip the movement code below
        exits = ROOMS[room]["exits"]                  # the exits dict for this room
        if command not in exits:                      # unknown direction or typo
            print(f"You can't go '{command}'. Try: {', '.join(exits) or 'nothing'}, take, quit")
            continue
        target = exits[command]                       # where that exit leads
        if target == "exit" and "key" not in inventory:
            print("The door is locked. You need a key.")
            continue
        room = target                                 # move to the new room
        describe(room)
    return True                                       # reached the exit


def main():
    if "--auto" in sys.argv:                          # replay a fixed list of commands
        script = iter(["north", "south", "east", "north", "take", "north"])
        def get_command():                            # a function defined inside a function
            cmd = next(script)                        # take the next scripted command
            print(f"> {cmd}")                         # show it as if typed
            return cmd
    else:
        def get_command():
            return input("> ")                        # wait for the player to type
    won = play(get_command)
    print("Result:", "won" if won else "quit")


if __name__ == "__main__":
    main()
