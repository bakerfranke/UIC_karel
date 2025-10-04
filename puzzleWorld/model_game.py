"""
Reference implementation for a menu-driven PuzzleWorld game.

Requirements the engine (PuzzleWorld) provides:
- Dodecahedron map (20 rooms), two hazards, hidden treasure
- Word puzzle sequence from words.txt
- Simple boolean hazard checks (has_hazard1/2, is_hazard1_adjacent/2, is_treasure_adjacent)
- Deterministic seeding

Game rules implemented here (feel free to tweak constants):
- You start in a random room (choose one at start).
- If you step into hazard1: you lose immediately.
- If you step into hazard2: you get carried to a random room (no immediate loss).
- You can "sense" adjacent hazards each turn.
- Solve a word puzzle to:
    * learn the treasure's *current* room number, and
    * receive a **one-time detector device**.
- The detector must be used **in the treasure room** to capture it and win.
- If you use the detector in the wrong room:
    * the treasure teleports to a new random room, and
    * your device is consumed; solve another puzzle to get a new device.
- After the treasure is revealed, it remains stable for STABILITY_TURNS.
  If you don't reach it in time, it teleports and your device info becomes stale.
- Numbered menu only (no free-text commands).

This file is intentionally beginner-friendly: clear conditionals, while loops, and functions.
"""

import random
from PuzzleWorld import PuzzleWorld

# ------------------------------
# Tunable gameplay constants
# ------------------------------
SEED = 42                 # Change or set to None for non-deterministic runs
STABILITY_TURNS = 6       # How many moves you have (after reveal) before the treasure relocates
ALLOW_DEVICE_FROM_ADJ = False  # If True, allow capturing from an adjacent room (not default)

# ------------------------------
# Helper functions
# ------------------------------

def choose_start_room(world: PuzzleWorld) -> int:
    """Pick a starting room that isn't immediately deadly (avoid spawning on hazard1)."""
    rooms = list(world.rooms.keys())
    rng = random.Random(SEED)  # keep consistent with the run
    rng.shuffle(rooms)
    for r in rooms:
        if not world.has_hazard1(r):  # type1 is instant-loss
            return r
    # Fallback (shouldn't happen with typical placements)
    return rooms[0]

def show_intro():
    print("====================================")
    print("         PUZZLE WORLD (Demo)        ")
    print("====================================")
    print("Find the invisible treasure hidden somewhere in the cave system!")
    print("Two hazards lurk in certain rooms.")
    print(" - Hazard 1: entering it ends the game.")
    print(" - Hazard 2: entering it whisks you away to a random room.")
    print("Solve word puzzles to reveal the treasure’s current room and")
    print("receive a one-time detector device to capture it.")
    print(f"You have {STABILITY_TURNS} move(s) after a reveal before it relocates.")
    print("Numbered menu only. Good luck!\n")

def show_status(world: PuzzleWorld, player_room: int, steps_taken: int,
                have_device: bool, revealed_room: int | None,
                steps_since_reveal: int | None):
    print("------------------------------------")
    print(f"You are in room {player_room}.")
    neighbors = world.get_adjacent_rooms(player_room)
    print(f"Tunnels lead to: {neighbors}")
    # Sensing (generic text so students can theme it later)
    if world.is_hazard1_adjacent(player_room):
        print("You sense danger (type 1) nearby...")
    if world.is_hazard2_adjacent(player_room):
        print("You sense movement (type 2) nearby...")
    if world.is_treasure_adjacent(player_room):
        print("Something special tingles nearby...")

    print(f"Steps taken: {steps_taken}")
    if have_device:
        if revealed_room is not None:
            print(f"Device ready. Known treasure room: {reveal_str(revealed_room)}")
        else:
            print("Device ready. (No known location!)")
    else:
        print("No device. Solve a puzzle to reveal treasure & get one.")
    if steps_since_reveal is not None and revealed_room is not None:
        remain = max(0, STABILITY_TURNS - steps_since_reveal)
        print(f"Treasure stability after reveal: {remain} move(s) left.")

def reveal_str(room_num: int | None) -> str:
    return "?" if room_num is None else str(room_num)

def menu() -> int:
    print("\nWhat will you do?")
    print("  1) Move to an adjacent room")
    print("  2) Solve the word puzzle")
    print("  3) Use detector device")
    print("  4) Quit")
    choice = input("Choose (1-4): ").strip()
    if not choice.isdigit():
        return 0
    return int(choice)

def do_move(world: PuzzleWorld, player_room: int):
    neighbors = world.get_adjacent_rooms(player_room)
    print(f"Adjacent rooms: {neighbors}")
    choice = input("Enter room number to move: ").strip()
    if not choice.isdigit():
        print("Invalid input.")
        return player_room, False  # moved?, False
    dest = int(choice)
    if dest not in neighbors:
        print("You can't go that way.")
        return player_room, False
    return dest, True

def handle_room_entry(world: PuzzleWorld, room: int) -> tuple[int, bool, str]:
    """
    Returns (new_room, alive, message).
    - If hazard1: alive=False (game over).
    - If hazard2: teleport to random room, alive=True.
    - Otherwise: alive=True, same room.
    """
    if world.has_hazard1(room):
        return room, False, "You stumble into Hazard 1… game over!"
    if world.has_hazard2(room):
        # 'Bats' effect: whisk to random room that's not instantly deadly if possible
        rng = random.Random(SEED)
        all_rooms = list(world.rooms.keys())
        rng.shuffle(all_rooms)
        for r in all_rooms:
            if not world.has_hazard1(r):
                return r, True, "Hazard 2 tosses you through the tunnels!"
        # Fallback
        return random.choice(all_rooms), True, "Hazard 2 tosses you through the tunnels!"
    return room, True, ""

def solve_puzzle(world: PuzzleWorld) -> bool:
    """
    Show current puzzle, take a guess, return True if solved.
    Advances to next puzzle on success, otherwise stays on same puzzle.
    """
    scrambled = world.get_puzzle()
    print(f"Puzzle: unscramble this word ->  {scrambled}")
    guess = input("Your guess: ").strip()
    if world.check_solution(guess):
        print("Correct! You gain a detector device and the treasure's current room.")
        # Advance to next puzzle for future uses
        world.generate_new_puzzle()
        return True
    else:
        print("Not quite. You can try again later.")
        return False

def use_device(world: PuzzleWorld, player_room: int, revealed_room: int | None,
               have_device: bool) -> tuple[bool, bool, str]:
    """
    Try to use the device to capture the treasure.
    Returns (captured, consumed, message).
    - If have_device and in correct place (or adjacent if allowed), win.
    - If have_device but wrong room, device is consumed and treasure relocates.
    """
    if not have_device:
        return False, False, "You don't have a device. Solve a puzzle first."

    # Determine if player is in capture position
    in_place = (player_room == revealed_room)
    if ALLOW_DEVICE_FROM_ADJ:
        in_place = in_place or (revealed_room in world.get_adjacent_rooms(player_room))

    if revealed_room is None:
        return False, False, "Your device has no known target yet. Solve a puzzle first."

    if in_place:
        # Double-check the treasure is truly here now
        if world.is_treasure(player_room) or (ALLOW_DEVICE_FROM_ADJ and world.is_treasure(revealed_room)):
            return True, True, "You activate the device… The invisible treasure materializes in your hands! You win!"
        else:
            # Treasure moved since reveal
            return False, True, "The device fizzles—your intel is stale. The treasure has moved."
    else:
        # Wrong room: device consumed, treasure teleports
        # (We’ll re-generate the world’s treasure placement only, keeping hazards the same
        # to keep the game readable. Simplest: call generate_world() then restore hazards.)
        old_h1 = world.hazards["type1"][:]
        old_h2 = world.hazards["type2"][:]
        world.generate_world()
        world.hazards["type1"] = old_h1
        world.hazards["type2"] = old_h2
        return False, True, "Wrong room! The device discharges and the treasure relocates."

# ------------------------------
# Main game loop
# ------------------------------

def main():
    random.seed(SEED)  # for any local randomness here
    world = PuzzleWorld(seed=SEED)

    show_intro()

    player_room = choose_start_room(world)
    steps_taken = 0

    # Device / reveal state
    have_device = False
    revealed_room = None
    steps_since_reveal = None  # None when not revealed

    while True:
        # If we have a reveal ticking, check stability timeout
        if revealed_room is not None and steps_since_reveal is not None:
            if steps_since_reveal >= STABILITY_TURNS:
                # Treasure relocates (reveal info becomes stale)
                old_h1 = world.hazards["type1"][:]
                old_h2 = world.hazards["type2"][:]
                world.generate_world()
                world.hazards["type1"] = old_h1
                world.hazards["type2"] = old_h2
                print("\n*** Too slow! The treasure has shifted to a new room. ***")
                revealed_room = None
                steps_since_reveal = None
                # Keep device, but it's now pointing to unknown (player must solve again to know)

        show_status(world, player_room, steps_taken, have_device, revealed_room, steps_since_reveal)

        choice = menu()
        if choice == 4:
            print("Thanks for playing. Goodbye!")
            return

        elif choice == 1:
            # MOVE
            new_room, moved = do_move(world, player_room)
            if moved:
                player_room = new_room
                steps_taken += 1
                if steps_since_reveal is not None:
                    steps_since_reveal += 1

                # Handle hazards on entry
                player_room, alive, msg = handle_room_entry(world, player_room)
                if msg:
                    print(msg)
                if not alive:
                    print("Game over.")
                    return

        elif choice == 2:
            # SOLVE PUZZLE
            if solve_puzzle(world):
                have_device = True
                revealed_room = world.get_treasure_room()
                steps_since_reveal = 0

        elif choice == 3:
            # USE DEVICE
            captured, consumed, msg = use_device(world, player_room, revealed_room, have_device)
            print(msg)
            if captured:
                return
            if consumed:
                have_device = False
                revealed_room = None
                steps_since_reveal = None

        else:
            print("Please choose 1–4.")

if __name__ == "__main__":
    main()