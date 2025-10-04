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

    def __str__(self):
        """
        Return a readable summary of the world state for debugging or testing.
        """
        lines = []
        lines.append("=== PuzzleWorld State ===")
        lines.append(f"Treasure room: {self.treasure}")
        lines.append(f"Hazard Type 1 rooms: {self.hazards['type1']}")
        lines.append(f"Hazard Type 2 rooms: {self.hazards['type2']}")
        lines.append(f"Current puzzle number: {self.puzzle_index}")
        lines.append(f"Scrambled word: {self.scrambled_word}")
        lines.append(f"Solution word: {self.current_word}")
        lines.append("==========================")
        return "\n".join(lines)

    def generate_new_puzzle(self):
        """Advance to next puzzle in sequence. And return it."""
        self._set_puzzle(self.puzzle_index + 1)
        return self.get_puzzle()

    def get_puzzle_word(self):
        return self.scrambled_word

    def get_puzzle_solution(self):
        return self.current_word


    def get_puzzle(self):
        return self.current_word, self.scrambled_word


    def check_solution(self, guess):
        return guess.lower() == self.current_word.lower()

    def get_map_ascii(self):
        """
        Return a string showing an ASCII-art map of all locations and connections.
        The layout is fixed — each location is placed at predetermined (row, col)
        in a grid, and connections are drawn with `-` and `|` or `/ \\` etc.
        """
        # grid size (rows × cols)
        rows = 25
        cols = 60
        # fill with spaces
        grid = [[" "]*cols for _ in range(rows)]
        
        # Predefine positions for each location (row, col) in the grid
        # You will need to pick these to look good.
        # Example placeholder positions (you’ll adjust to make shape):
        pos = {
            1: (2, 30),
            2: (5, 45),
            3: (10, 50),
            4: (15, 45),
            5: (18, 30),
            6: (15, 15),
            7: (10, 10),
            8: (5, 15),
            9: (3, 25),
            10: (7, 30),
            11: (12, 35),
            12: (17, 30),
            13: (12, 25),
            14: (8, 20),
            15: (11, 45),
            16: (14, 40),
            17: (16, 25),
            18: (13, 15),
            19: (8, 40),
            20: (12, 20),
        }
        
        # Place node labels
        for loc, (r, c) in pos.items():
            s = str(loc)
            for i, ch in enumerate(s):
                if 0 <= c+i < cols:
                    grid[r][c+i] = ch
        
        # Helper to draw a line between two positions (r1,c1) → (r2,c2)
        def draw_line(r1, c1, r2, c2):
            dr = r2 - r1
            dc = c2 - c1
            steps = max(abs(dr), abs(dc))
            if steps == 0:
                return
            for i in range(1, steps):
                rr = r1 + (dr * i) // steps
                cc = c1 + (dc * i) // steps
                # pick a character depending on slope
                if dr == 0:
                    ch = "-"
                elif dc == 0:
                    ch = "|"
                else:
                    # approximate diagonal
                    ch = "/" if (dr * dc) > 0 else "\\"
                grid[rr][cc] = ch
        
        # Draw connections
        for loc, neighbors in self.rooms.items():
            r1, c1 = pos[loc]
            for nb in neighbors:
                r2, c2 = pos[nb]
                draw_line(r1, c1, r2, c2)
        
        # Combine into one string
        lines = ["".join(row).rstrip() for row in grid]
        return "\n".join(lines)
    
    
    def show_map(self):
        print(self.get_map_ascii())

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

    def has_treasure(self, room):
        return room == self.treasure

    def is_treasure_adjacent(self, room):
        return self.treasure in self.rooms[room]

if __name__ =="__main__":

    W = PuzzleWorld(1121)
    print(W)
    W.show_map()

    # print("Treasure room:", gw.get_treasure_room())
    # print("Puzzle:", gw.get_puzzle())
    # print("Check guess:", gw.check_solution("lantern"))
    # print("Hazzards", gw.hazards)
    # print(gw.get_adjacent_rooms(4))
    # print("Puzzles")
    # for i in range(len(gw.puzzle_sequence)):
    #     print(gw.puzzle_sequence[i])