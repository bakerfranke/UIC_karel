import random

class PuzzleWorld:
    def __init__(self, seed=None):
        """
        Create a new GameWorld.
        
        Args:
            seed (int, optional): seed for random number generator 
                                  (useful for deterministic testing).
        """
        self.rng = random.Random(seed)

        self.rooms = self._generate_dodecahedron()
        self.hazards = {"type1": [], "type2": []}
        self.treasure = None

        # puzzle handling
        #self.word_list = word_list[:]  # copy
        self.word_list = self._load_words("words.txt")
        self.puzzle_sequence = []
        self.puzzle_index = 0
        self.current_word = None
        self.scrambled_word = None

        self._prepare_puzzles()
        self.generate_world()

    # ---------- World generation ----------
    def _generate_dodecahedron(self):
        return {
            1: [2, 5, 8],
            2: [1, 3, 10],
            3: [2, 4, 12],
            4: [3, 5, 14],
            5: [1, 4, 6],
            6: [5, 7, 15],
            7: [6, 8, 17],
            8: [1, 7, 9],
            9: [8, 10, 18],
            10: [2, 9, 11],
            11: [10, 12, 19],
            12: [3, 11, 13],
            13: [12, 14, 20],
            14: [4, 13, 15],
            15: [6, 14, 16],
            16: [15, 17, 20],
            17: [7, 16, 18],
            18: [9, 17, 19],
            19: [11, 18, 20],
            20: [13, 16, 19]
        }

    def generate_world(self):
        rooms = list(self.rooms.keys())
        self.treasure = self.rng.choice(rooms)
        self.hazards["type1"] = self.rng.sample([r for r in rooms if r != self.treasure], 2)
        self.hazards["type2"] = self.rng.sample(
            [r for r in rooms if r != self.treasure and r not in self.hazards["type1"]], 2
        )
        self._set_puzzle(0)

    # ---------- Puzzle preparation ----------
    def _load_words(self, filename):
        """Read words from a file, strip whitespace, ignore empties."""
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _prepare_puzzles(self):
        """Shuffle word list and pre-scramble all puzzles."""
        words = self.word_list[:]
        self.rng.shuffle(words)
        self.puzzle_sequence = []
        for w in words:
            scrambled = list(w)
            self.rng.shuffle(scrambled)
            self.puzzle_sequence.append((w, "".join(scrambled)))

    def _set_puzzle(self, index):
        """Activate puzzle at given index."""
        if index < len(self.puzzle_sequence):
            self.current_word, self.scrambled_word = self.puzzle_sequence[index]
            self.puzzle_index = index
        else:
            idx = index % len(self.puzzle_sequence)
            self.current_word, self.scrambled_word = self.puzzle_sequence[idx]
            self.puzzle_index = index

    def generate_puzzle(self):
        """Advance to next puzzle in sequence."""
        self._set_puzzle(self.puzzle_index + 1)

    def get_puzzle(self):
        return self.scrambled_word

    def check_solution(self, guess):
        return guess.lower() == self.current_word.lower()

    # ---------- Hazard/Treasure getters ----------
    def get_adjacent_rooms(self, room):
        return self.rooms[room]

    def has_hazard1(self, room):
        return room in self.hazards["type1"]

    def has_hazard2(self, room):
        return room in self.hazards["type2"]

    def is_hazard1_adjacent(self, room):
        return any(neighbor in self.hazards["type1"] for neighbor in self.rooms[room])

    def is_hazard2_adjacent(self, room):
        return any(neighbor in self.hazards["type2"] for neighbor in self.rooms[room])

    def get_treasure_room(self):
        return self.treasure

    def is_treasure(self, room):
        return room == self.treasure

    def is_treasure_adjacent(self, room):
        return self.treasure in self.rooms[room]

if __name__ =="__main__":

    gw = PuzzleWorld(1121)

    print("Treasure room:", gw.get_treasure_room())
    print("Puzzle:", gw.get_puzzle())
    print("Check guess:", gw.check_solution("lantern"))
    print("Hazzards", gw.hazards)
    print(gw.get_adjacent_rooms(4))
    print("Puzzles")
    for i in range(len(gw.puzzle_sequence)):
        print(gw.puzzle_sequence[i])