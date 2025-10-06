import random
import re
from collections import deque

class PuzzleWorld:
    def __init__(self, seed=None, verbose=False):
        """
        Create a new GameWorld.
        
        Args:
            seed (int, optional): seed for random number generator 
                                  (useful for deterministic testing).
            verbose (bool): whether to print generation details.
        """
        import random

        self.verbose = verbose
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

        # world structure
        self.rooms = self._generate_dodecahedron()
        self.hazards = {"type1": [], "type2": []}
        self.treasure = None

        # puzzle handling
        self.word_list = self._load_words("words.txt")
        self.puzzle_sequence = []
        self.puzzle_index = 0
        self.current_word = None
        self.scrambled_word = None

        self.number_puzzle_sequence = []
        self.number_puzzle_index = 0


        self._prepare_puzzles()

        # generate a valid world, bumping seed if necessary
        self.seed = self._generate_valid_world(self.seed)
        if self.verbose:
            print(f"Final seed: {self.seed}")

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

    def _generate_valid_world(self, base_seed):
        """
        Try generating worlds from base_seed, incrementing until one passes validation.
        Returns the final seed used to produce a valid configuration.
        """

        MAX_ATTEMPTS = 1000
        seed = base_seed

        for attempt in range(MAX_ATTEMPTS):
            self.rng.seed(seed)
            self.generate_world()  # existing method
            ok, reason = self.validate_world(verbose=self.verbose)

            if ok:
                if self.verbose:
                    print(f"Valid world generated (base seed={base_seed}, final seed={seed})")
                return seed

            if self.verbose:
                print(f"⚠Invalid world (seed {seed}): {reason}; trying {seed+1}")
            seed += 1

        raise RuntimeError("Failed to generate valid world after 1000 attempts.")


    def generate_world(self):
        rooms = list(self.rooms.keys())
        self.treasure = self.rng.choice(rooms)
        self.hazards["type1"] = self.rng.sample([r for r in rooms if r != self.treasure], 2)
        self.hazards["type2"] = self.rng.sample(
            [r for r in rooms if r != self.treasure and r not in self.hazards["type1"]], 2
        )
        self.puzzles = self.rng.sample(
            [r for r in rooms if r != self.treasure and r not in self.hazards["type1"] and r not in self.hazards["type2"]], 2
        )
        self._set_puzzle(0)

    def validate_world(self, verbose=False):
        """
        Strong validator:
        Ensures every non-hazard (safe) room can reach both puzzle rooms and the treasure
        without passing through a hazard.
        """

        rooms = list(self.rooms.keys())
        hazards = set(self.hazards.get("type1", [])) | set(self.hazards.get("type2", []))
        puzzles = set(getattr(self, "puzzles", []))
        treasure = getattr(self, "treasure", None)

        # === Basic checks ===
        if treasure is None:
            return (False, "Treasure not set.")
        if not puzzles or len(puzzles) < 2:
            return (False, "Missing puzzle rooms.")
        if len(set(hazards | puzzles | {treasure})) < len(hazards) + len(puzzles) + 1:
            return (False, "Overlapping treasure/puzzles/hazards.")

        # === No key items in hazards ===
        if treasure in hazards:
            return (False, f"Treasure in hazard {treasure}")
        for p in puzzles:
            if p in hazards:
                return (False, f"Puzzle room {p} in hazard")

        # === Build safe graph ===
        safe_rooms = [r for r in rooms if r not in hazards]
        safe_graph = {r: [n for n in self.rooms[r] if n in safe_rooms] for r in safe_rooms}

        # === Helper BFS ===
        def reachable_from(start):
            visited = set()
            q = deque([start])
            while q:
                r = q.popleft()
                visited.add(r)
                for n in safe_graph[r]:
                    if n not in visited:
                        q.append(n)
            return visited

        # === Test all safe rooms ===
        for start in safe_rooms:
            visited = reachable_from(start)
            needed = puzzles | {treasure}
            if not needed.issubset(visited):
                if verbose:
                    print(f"❌ Room {start} cannot reach {needed - visited}")
                return (False, f"Start room {start} cannot reach all objectives")

        if verbose:
            print(f"✅ All {len(safe_rooms)} safe rooms can reach puzzles {puzzles} and treasure {treasure}")

        return (True, "OK")



    # ---------- Puzzle preparation ----------
    def _load_words(self, filename):
        """Read words from a file, strip whitespace, ignore empties."""
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _prepare_puzzles(self):
        """Precompute both word and number puzzles deterministically."""

        # ---- Word puzzles ----
        words = self.word_list[:]
        self.rng.shuffle(words)
        self.puzzle_sequence = []
        for w in words:
            scrambled = list(w)
            self.rng.shuffle(scrambled)
            self.puzzle_sequence.append({
                "type": "word",
                "question": f"Unscramble this word: {''.join(scrambled)}",
                "answer": w.lower()
            })

        # ---- Number puzzles ----
        num_number_puzzles=50
        self.number_puzzle_sequence = []
        for _ in range(num_number_puzzles):
            pattern_type = self.rng.choice(["arithmetic", "geometric"])
            start = self.rng.randint(1, 9)
            step = self.rng.randint(2, 5)

            if pattern_type == "arithmetic":
                seq = [start + i * step for i in range(4)]
                answer = str(start + 4 * step)
            else:
                seq = [start * (step ** i) for i in range(4)]
                answer = str(start * (step ** 4))

            question = f"What number comes next? {', '.join(map(str, seq))}, ..."
            self.number_puzzle_sequence.append({
                "type": "number",
                "question": question,
                "answer": answer
            })

    def _set_puzzle(self, index):
        """Activate puzzle at given index."""
        if not self.puzzle_sequence:
            self._prepare_puzzles()

        idx = index % len(self.puzzle_sequence)
        p = self.puzzle_sequence[idx]

        if isinstance(p, dict):  # new puzzle format
            self.current_word = p.get("answer")
            self.scrambled_word = re.sub(r"^Unscramble this word:\s*", "", p.get("question", ""))
        else:  # old tuple format (backward compatible)
            self.current_word, self.scrambled_word = p

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
        lines.append(f"Puzzle Rooms: {self.puzzles}")

        # --- Word puzzle info ---
        lines.append(f"Current word puzzle index: {self.puzzle_index}")
        if self.puzzle_sequence:
            lines.append(f"Scrambled word: {self.scrambled_word}")
            lines.append(f"Solution word: {self.current_word}")
        else:
            lines.append("No word puzzles prepared.")

        # --- Number puzzle info ---
        lines.append(f"Current number puzzle index: {self.number_puzzle_index}")
        if getattr(self, "number_puzzle_sequence", []):
            idx = self.number_puzzle_index % len(self.number_puzzle_sequence)
            p = self.number_puzzle_sequence[idx]
            lines.append(f"Number puzzle question: {p['question']}")
            lines.append(f"Number puzzle answer: {p['answer']}")
        else:
            lines.append("No number puzzles prepared.")

        lines.append("==========================")
        return "\n".join(lines)

    # def generate_new_puzzle(self):
    #     """Advance to next puzzle in sequence. And return it."""
    #     self._set_puzzle(self.puzzle_index + 1)
    #     return self.get_puzzle()

    # def get_puzzle_word(self):
    #     return self.scrambled_word

    # def get_puzzle_solution(self):
    #     return self.current_word


    # def get_puzzle(self):
    #     return self.current_word, self.scrambled_word

    def get_next_word_puzzle(self):
        """Return the next precomputed word puzzle [question, answer]."""
        # if not self.puzzle_sequence:
        #     self._prepare_puzzles()
        p = self.puzzle_sequence[self.puzzle_index % len(self.puzzle_sequence)]
        self.puzzle_index += 1
        return [p["question"], p["answer"]]


    def get_next_number_puzzle(self):
        """Return the next precomputed number puzzle [question, answer]."""
        # if not self.number_puzzle_sequence:
        #     self._prepare_puzzles()
        p = self.number_puzzle_sequence[self.number_puzzle_index % len(self.number_puzzle_sequence)]
        self.number_puzzle_index += 1
        return [p["question"], p["answer"]]


    # def check_solution(self, guess):
    #     return guess.lower() == self.current_word.lower()

    def get_map_ascii(self):
        """
        Return a fixed ASCII-art map of the 20-location world.
        This version preserves the classic 'Hunt the Wumpus' circular layout
        with proper spacing and connections using slashes and underscores.
        """
        map_str = r"""
              ______18______             
             /      |       \           
            /      _9__      \          
           /      /    \      \        
          /      /      \      \       
         17     8        10     19       
         | \   / \      /  \   / |    
         |  \ /   \    /    \ /  |    
         |   7     1---2     11  |       
         |   |    /     \    |   |      
         |   6----5     3---12   |       
         |   |     \   /     |   |      
         |   \       4      /    |      
         |    \      |     /     |      
         \     15---14---13     /       
          \   /            \   /       
           \ /              \ /        
            16---------------20
        """
        return map_str.strip("\n")




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
        BLACK = "\x1b[30m"
        WHITE_BG = "\x1b[47m"

        color_map = highlights or {}

        # Step 1: Start all text as faint gray
        styled = f"{DIM}{base_map}{RESET}"
        #styled = f"{base_map}"

        # Step 2: Replace numbers, keeping dim gray after each reset
        def style_number(match):
            num = int(match.group(0))
            bg = color_map.get(num, BLUE_BG)
            # temporarily turn off dim, show bold+bright, then return to dim
            return f"{RESET}{WHITE}{bg}{num}{RESET}{DIM}"
            #return f"{num}"


        for n in range(20, 0, -1):
            styled = re.sub(rf"(?<!\d){n}(?!\d)", style_number, styled)

        # Step 3: make sure the map ends cleanly
        styled += RESET
        return styled



    def print_map(self, type="ansi"):
        """Print the ASCII-art map of all 20 locations."""
        if type == "ascii":
            print(self.get_map_ascii())
        else:
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

    seed = 1042025
    #for i in range(seed, seed+100):
    W = PuzzleWorld(seed, verbose=True)
    print(W)
    W.print_map()
    W.print_map("ascii")

    for i in range(10):
        print(W.get_next_number_puzzle())
    #print(W.validate_world())
   #  valid_count = 0
   #  map_count = 0
   # # map_num = seed+map_count
   #  while(valid_count < 100):
   #      map_num = seed+map_count
   #      W = PuzzleWorld(map_num)
   #      print("map #", map_num)
   #      #print(W)
   #      if(W.validate_world()[0] == True):
   #          valid_count+=1
   #          #print("  valid")
   #      else:
   #          print("   invalid")
   #      map_count+=1

   #  print("valid count",valid_count)
   #  print("map_count",map_count)

        

    # print("Treasure room:", gw.get_treasure_room())
    # print("Puzzle:", gw.get_puzzle())
    # print("Check guess:", gw.check_solution("lantern"))
    # print("Hazzards", gw.hazards)
    # print(gw.get_adjacent_rooms(4))
    # print("Puzzles")
    # for i in range(len(gw.puzzle_sequence)):
    #     print(gw.puzzle_sequence[i])