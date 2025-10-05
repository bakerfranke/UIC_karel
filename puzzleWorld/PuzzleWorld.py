import random
import re

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

    # def get_map_ascii(self):
    #     """
    #     Return a fixed ASCII-art map of the 20-location world.
    #     This version preserves the classic 'Hunt the Wumpus' circular layout
    #     with proper spacing and connections using slashes and underscores.
    #     """
    #     map_str = r"""
    #           ______18______             
    #          /      |       \           
    #         /      _9__      \          
    #        /      /    \      \        
    #       /      /      \      \       
    #      17     8        10     19       
    #      | \   / \      /  \   / |    
    #      |  \ /   \    /    \ /  |    
    #      |   7     1---2     11  |       
    #      |   |    /     \    |   |      
    #      |   6----5     3---12   |       
    #      |   |     \   /     |   |      
    #      |   \       4      /    |      
    #      |    \      |     /     |      
    #      \     15---14---13     /       
    #       \   /            \   /       
    #        \ /              \ /        
    #         16---------------20
    #     """
    #     return map_str.strip("\n")




    def get_map_ansi(self, highlights=None):
        """
        Return a large-dot (●) circular map with ANSI color.
        Dots are faint gray; numbers are bold, bright, and colored.
        """

        base_map = r"""
                  ● ● ● ● 18 ● ● ● ●            
                 ●                  ●           
                ●     ● ● 9 ● ●      ●          
               ●     ●         ●      ●        
              ●     ●           ●      ●    
             17     8           10      19       
             ● ●   ●  ●        ●  ●    ● ●       
             ●  ● ●    ●      ●    ●  ●  ●    
             ●   7       1 ● 2      11   ●       
             ●   ●      ●    ●       ●   ●      
             ●   6 ● ● 5      3 ● ● 12   ●       
             ●   ●      ●    ●       ●   ●      
             ●   ●         4        ●    ●       
             ●    ●        ●       ●     ●       
             ●     15 ● ● 14 ● ● 13      ●           
              ●   ●                ●    ●        
               ● ●                  ●  ●        
                16 ● ● ● ● ● ● ● ● ● 20
        """.rstrip("\n")

        # ANSI codes
        ESC = "\x1b"
        RESET = f"{ESC}[0m"
        BOLD = f"{ESC}[1m"
        DIM = f"{ESC}[90m"
        WHITE = f"{ESC}[97m"
        BLUE_BG = f"{ESC}[44m"
        RED_BG = f"{ESC}[41m"
        GREEN_BG = f"{ESC}[42m"
        YELLOW_BG = f"{ESC}[43m"

        color_map = highlights or {}

        # Step 1: Start all text as faint gray
        styled = f"{DIM}{base_map}{RESET}"

        # Step 2: Replace numbers, keeping dim gray after each reset
        def style_number(match):
            num = int(match.group(0))
            bg = color_map.get(num, BLUE_BG)
            # temporarily turn off dim, show bold+bright, then return to dim
            return f"{RESET}{WHITE}{bg}{num}{RESET}{DIM}"

        for n in range(20, 0, -1):
            styled = re.sub(rf"(?<!\d){n}(?!\d)", style_number, styled)

        # Step 3: make sure the map ends cleanly
        styled += RESET
        return styled



    def show_map(self):
        """Print the ASCII-art map of all 20 locations."""
        print(self.get_map_ansi())
    
 
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