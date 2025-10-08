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
        self.locations = self._generate_dodecahedron()
        self.hazards = {"type1": [], "type2": []}
        self.puzzles = []
        self.treasure = None

        # puzzle handling
        self.word_list = self._load_words("words.txt")
        self.word_puzzle_sequence = []
        self.word_puzzle_index = 0

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
            self._generate_world()  # existing method
            ok, reason = self._validate_world(verbose=self.verbose)

            if ok:
                if self.verbose:
                    if base_seed != seed:
                        print(f"Original seed ({base_seed}) generated an invalid world. Used next seed={seed} that generated a valid world.")
                    else:
                        print(f"Valid world generated (base seed={base_seed}")
                return seed



            if self.verbose:
                print(f"⚠Invalid world (seed {seed}): {reason}; trying {seed+1}")
            seed += 1

        raise RuntimeError("Failed to generate valid world after 1000 attempts.")


    def _generate_world(self):
        """ Pick random locations for objects that don't clobber each other. Pick locations in
            this order: treasure, 2x type1 hazards, 2x type2 hazards, 2x puzzles"""

        locations = list(self.locations.keys())
        self.treasure = self.rng.choice(locations)
        self.hazards["type1"] = self.rng.sample([r for r in locations if r != self.treasure], 2)
        self.hazards["type2"] = self.rng.sample(
            [r for r in locations if r != self.treasure and r not in self.hazards["type1"]], 2
        )
        self.puzzles = self.rng.sample(
            [r for r in locations if r != self.treasure and r not in self.hazards["type1"] and r not in self.hazards["type2"]], 2
        )

    def _validate_world(self, verbose=False):
        """
        Map validator:
        Ensures every non-hazard (safe) location can reach both puzzle locations and the treasure
        without passing through a hazard.
        """

        locations = list(self.locations.keys())
        hazards = set(self.hazards.get("type1", [])) | set(self.hazards.get("type2", []))
        puzzles = set(getattr(self, "puzzles", []))
        treasure = getattr(self, "treasure", None)

        # === Basic checks ===
        if treasure is None:
            return (False, "Treasure not set.")
        if not puzzles or len(puzzles) < 2:
            return (False, "Missing puzzle locations.")
        if len(set(hazards | puzzles | {treasure})) < len(hazards) + len(puzzles) + 1:
            return (False, "Overlapping treasure/puzzles/hazards.")

        # === No key items in hazards ===
        if treasure in hazards:
            return (False, f"Treasure in hazard {treasure}")
        for p in puzzles:
            if p in hazards:
                return (False, f"Puzzle location {p} in hazard")

        # === Build safe graph ===
        safe_locations = [r for r in locations if r not in hazards]
        safe_graph = {r: [n for n in self.locations[r] if n in safe_locations] for r in safe_locations}

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

        # === Test all safe locations ===
        for start in safe_locations:
            visited = reachable_from(start)
            needed = puzzles | {treasure}
            if not needed.issubset(visited):
                if verbose:
                    print(f"❌ location {start} cannot reach {needed - visited}")
                return (False, f"Start location {start} cannot reach all objectives")

        if verbose:
            print(f"✅ All {len(safe_locations)} safe locations can reach puzzles {puzzles} and treasure {treasure}")

        return (True, "OK")



    # ---------- Puzzle preparation ----------
    def _load_words(self, filename):
        """Read words from a file, strip whitespace, ignore empties."""
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _prepare_puzzles(self):
        """Precompute both word and number puzzles so they have a deterministic sequence based on world's random seed."""

        # ---- Word puzzles ----
        words = self.word_list[:]
        self.rng.shuffle(words)
        self.word_puzzle_sequence = []
        for w in words:
            scrambled = list(w)
            self.rng.shuffle(scrambled)
            self.word_puzzle_sequence.append({
                "type": "word",
                "question": f"Unscramble this word: {''.join(scrambled)}",
                "answer": w.lower()
            })

        # ---- Number puzzles ----
        num_number_puzzles=100
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


    def __str__(self):
        """
        Return a readable summary of the world state for debugging or testing.
        """
        lines = []
        lines.append("=== PuzzleWorld State ===")
        lines.append(f"Treasure location:       {self.treasure}")
        lines.append(f"Hazard Type 1 locations: {self.hazards['type1']}")
        lines.append(f"Hazard Type 2 locations: {self.hazards['type2']}")
        lines.append(f"Puzzle locations:        {self.puzzles}")

        # --- Word puzzle info ---
        #lines.append(f"Current word puzzle index: {self.puzzle_index}")
        lines.append("---First word puzzle ----")
        if self.word_puzzle_sequence:
            p = self.word_puzzle_sequence[self.word_puzzle_index]
            lines.append(f"Word puzzle question: {p['question']}")
            lines.append(f"Word puzzle answer:   {p['answer']}")


        # --- Number puzzle info ---
        # lines.append(f"Current number puzzle index: {self.number_puzzle_index}")
        lines.append("---First number puzzle ----")
        p = self.number_puzzle_sequence[self.number_puzzle_index]
        lines.append(f"Number puzzle question: {p['question']}")
        lines.append(f"Number puzzle answer:   {p['answer']}")


        lines.append("==========================")
        return "\n".join(lines)

    # ---------- Public methods  ----------

    def get_next_word_puzzle(self):
        """Return the next word puzzle as a list [question, answer]."""
        p = self.word_puzzle_sequence[self.word_puzzle_index]
        self.word_puzzle_index = (self.word_puzzle_index + 1) % len(self.word_puzzle_sequence)  # keep in range
        return [p["question"], p["answer"]]


    def get_next_number_puzzle(self):
        """Return the next number puzzle as a list [question, answer]."""
        p = self.number_puzzle_sequence[self.number_puzzle_index]
        self.number_puzzle_index = (self.number_puzzle_index+1)  % len(self.number_puzzle_sequence)
        return [p["question"], p["answer"]]

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
        """
        Print the map of all 20 locations and connections between them.
        By default print the ANSI version (some colors and special characters)
        Args:
            type (string, optional): use type='ascii' to get plain ASCII version of map
        """
        if type == "ascii":
            print(self.get_map_ascii())
        else:
            print(self.get_map_ansi())
    
 
    # ---------- Hazard/Treasure/Puzzle getters ----------
    def get_adjacent_locations(self, location):
        """Return a list of locations adjacent to the given one"""
        return self.locations[location]

    def has_hazard1(self, location):
        """Return true if given location has a type1 hazard in it. 
           Equivalent to: 'if location in get_hazard1_locations()' """
        return location in self.hazards["type1"]

    def has_hazard2(self, location):
        """Returns true if given location has a type2 hazard in it. 
           Equivalent to: 'if location in get_hazard2_locations()' """
        return location in self.hazards["type2"]

    def get_hazard1_locations(self):
        """Return a list of the locations that have hazard type 1"""
        return self.hazards["type1"]

    def get_hazard2_locations(self):
        """Return a list of the locations that have hazard type 2"""
        return self.hazards['type2']

    def get_hazard_locations(self):
        """Return a dictionary of each hazard type with a list of that hazard's locations"""
        return self.hazards

    def is_hazard1_adjacent(self, location):
        """Return True if any connected location has a hazard of type 1."""
        return any(neighbor in self.hazards["type1"] for neighbor in self.locations[location])

    def is_hazard2_adjacent(self, location):
        """Return True if any connected location has a hazard of type 2."""
        return any(neighbor in self.hazards["type2"] for neighbor in self.locations[location])

    def get_treasure_location(self):
        """Return the location number of the treasure"""
        return self.treasure

    def has_treasure(self, location):
        """Return True if given location has the treasure"""
        return location == self.treasure

    def is_treasure_adjacent(self, location):
        """Return True if any connected location has the treasure."""
        return self.treasure in self.locations[location]

    def has_puzzle(self, location):
        """Return True if given location has a puzzle"""
        return location in self.puzzles

    def is_puzzle_adjacent(self, location):
        """Return True if any connected location has a puzzle."""
        return any(neighbor in self.hazards["type2"] for neighbor in self.locations[location])

    def get_puzzle_locations(self):
        """Return a list of locations that have a puzzle"""
        return self.puzzles

    def get_unoccupied_locations(self):
        """
        Return a list of all locations in the world that are not occupied 
        by a hazard, puzzle, or the treasure.
        """
        occupied = set(self.hazards["type1"]) | set(self.hazards["type2"]) | set(self.puzzles) | {self.treasure}
        return [loc for loc in self.locations if loc not in occupied]


    def set_treasure_location(self, location):
        """
        Change the location number of the treasure to the given location.
        Raises a ValueError if the location is occupied by a hazard or puzzle.
        Suggests using get_unoccupied_locations() to find safe locations.
        """
        if (location in self.hazards["type1"] or 
            location in self.hazards["type2"] or 
            location in self.puzzles):
            raise ValueError(
                f"Location {location} is occupied by a hazard or puzzle. "
                f"Use get_unoccupied_locations() to find a safe location."
            )
        if location not in self.locations:
            raise ValueError(f"Invalid location number: {location}")
        
        self.treasure = location
        if self.verbose:
            print(f"Treasure moved to location {location}.")



if __name__ =="__main__":

    seed = 1121
    #for i in range(seed, seed+100):
    W = PuzzleWorld(seed, verbose=True)
    print(W)
    W.print_map()
    W.print_map("ascii")

    print("printing 10 word puzzles")
    for i in range(10):
        print(W.get_next_word_puzzle())

    print("printing 10 number puzzles")
    for i in range(10):
        print(W.get_next_word_puzzle())


    # print(W.get_hazard1_locations())
    # print(W.get_hazard2_locations())
    # print(W.get_hazard_locations())
    # print(W.puzzles)

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

        

    # print("Treasure location:", gw.get_treasure_location())
    # print("Puzzle:", gw.get_puzzle())
    # print("Check guess:", gw.check_solution("lantern"))
    # print("Hazzards", gw.hazards)
    # print(gw.get_adjacent_locations(4))
    # print("Puzzles")
    # for i in range(len(gw.puzzle_sequence)):
    #     print(gw.puzzle_sequence[i])