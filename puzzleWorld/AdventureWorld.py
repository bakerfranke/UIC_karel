import random
import re
from collections import deque

class AdventureWorld:
    def __init__(self, seed=None, verbose=False):
        """
        Create a new AdventureWorld.
        
        Args:
            seed (int, optional): seed for random number generator 
                                  (useful for deterministic testing).
            verbose (bool): whether to print generation details.
        """
        self.verbose = verbose
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

        # world structure
        self.locations = self._generate_dodecahedron()
        self.hazards = {"type1": [], "type2": []}
        self.treasure = None
        self.map_location = None
        self.device_location = None

        # generate a valid world, bumping seed if necessary
        self.seed = self._generate_valid_world(self.seed)
        if self.verbose:
            print(f"Final seed: {self.seed}")

    # ---------- World generation ----------
    def _generate_dodecahedron(self):
        """Generate connections for 20 interlinked locations (each connects to 3 others)."""
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
            self._generate_world()
            ok, reason = self._validate_world(verbose=self.verbose)

            if ok:
                if self.verbose:
                    if base_seed != seed:
                        print(f"Original seed ({base_seed}) invalid; used next seed={seed}.")
                    else:
                        print(f"Valid world generated (base seed={base_seed})")
                return seed

            if self.verbose:
                print(f"⚠ Invalid world (seed {seed}): {reason}; trying {seed+1}")
            seed += 1

        raise RuntimeError("Failed to generate valid world after 1000 attempts.")

    def _generate_world(self):
        """
        Pick random locations for objects that don't overlap:
        treasure, 2x type1 hazards, 2x type2 hazards, 1 map, 1 capture device.
        """
        locations = list(self.locations.keys())
        self.treasure = self.rng.choice(locations)

        # Hazards
        self.hazards["type1"] = self.rng.sample([r for r in locations if r != self.treasure], 2)
        self.hazards["type2"] = self.rng.sample(
            [r for r in locations if r != self.treasure and r not in self.hazards["type1"]], 2
        )

        # Tools
        remaining = [r for r in locations if r not in self.hazards["type1"]
                     and r not in self.hazards["type2"]
                     and r != self.treasure]
        self.map_location, self.device_location = self.rng.sample(remaining, 2)

    def _validate_world(self, verbose=False):
        """
        Validate that every safe location can reach the treasure, map, and device
        without passing through a hazard.
        """
        locations = list(self.locations.keys())
        hazards = set(self.hazards["type1"]) | set(self.hazards["type2"])
        treasure = self.treasure
        key_items = {treasure, self.map_location, self.device_location}

        if treasure is None or self.map_location is None or self.device_location is None:
            return (False, "Missing key items.")
        if len(set(hazards | key_items)) < len(hazards) + len(key_items):
            return (False, "Overlapping key items and hazards.")
        if any(item in hazards for item in key_items):
            return (False, "Key item in hazard.")

        safe_locations = [r for r in locations if r not in hazards]
        safe_graph = {r: [n for n in self.locations[r] if n in safe_locations] for r in safe_locations}

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

        for start in safe_locations:
            visited = reachable_from(start)
            if not key_items.issubset(visited):
                if verbose:
                    print(f"❌ Location {start} cannot reach {key_items - visited}")
                return (False, f"Start location {start} cannot reach all key items.")

        if verbose:
            print(f"✅ All safe locations can reach treasure, map, and device.")
        return (True, "OK")

    # ---------- Core World Access ----------
    def get_neighbor_locations(self, location):
        """Return a list of locations directly connected to the given one."""
        return self.locations[location]

    # ---------- Hazards ----------
    def has_hazard1(self, location):
        return location in self.hazards["type1"]

    def has_hazard2(self, location):
        return location in self.hazards["type2"]

    def neighbor_has_hazard1(self, location):
        """Return True if any neighboring location has a type1 hazard."""
        return any(n in self.hazards["type1"] for n in self.locations[location])

    def neighbor_has_hazard2(self, location):
        """Return True if any neighboring location has a type2 hazard."""
        return any(n in self.hazards["type2"] for n in self.locations[location])

    # ---------- Treasure ----------
    def has_treasure(self, location):
        return location == self.treasure

    def neighbor_has_treasure(self, location):
        """Return True if any neighboring location has the treasure."""
        return self.treasure in self.locations[location]

    def get_treasure_location(self):
        return self.treasure

    # ---------- Tools ----------
    def has_map(self, location):
        return location == self.map_location

    def neighbor_has_map(self, location):
        """Return True if any neighboring location has the map."""
        return self.map_location in self.locations[location]

    def get_map_location(self):
        return self.map_location

    def has_device(self, location):
        return location == self.device_location

    def neighbor_has_device(self, location):
        """Return True if any neighboring location has the capture device."""
        return self.device_location in self.locations[location]

    def get_device_location(self):
        return self.device_location

    # ---------- Utility ----------
    def get_unoccupied_locations(self):
        """Return all locations not occupied by a hazard, treasure, map, or device."""
        occupied = (
            set(self.hazards["type1"])
            | set(self.hazards["type2"])
            | {self.treasure, self.map_location, self.device_location}
        )
        return [loc for loc in self.locations if loc not in occupied]

    def set_treasure_location(self, location):
        """
        Set the treasure's location to the given location number.

        Raises:
            ValueError: if the location is invalid or not unoccupied.
        """
        # Check validity
        if location not in self.locations:
            raise ValueError(f"Invalid location number: {location}")

        # Check occupancy using get_unoccupied_locations
        if location not in self.get_unoccupied_locations():
            raise ValueError(
                f"Location {location} is already occupied by another object. "
                f"Use get_unoccupied_locations() to find safe options."
            )

        # Safe — move treasure
        self.treasure = location
        if self.verbose:
            print(f"Treasure moved to location {location}.")

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
            ●        ●         ●           
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
    

    def __str__(self):
        """Readable summary for debugging or testing."""
        lines = []
        lines.append("=== AdventureWorld State ===")
        lines.append(f"Seed:                   {self.seed}")
        lines.append(f"Treasure location:       {self.treasure}")
        lines.append(f"Hazard Type 1 locations: {self.hazards['type1']}")
        lines.append(f"Hazard Type 2 locations: {self.hazards['type2']}")
        lines.append(f"Map location:            {self.map_location}")
        lines.append(f"Capture device location: {self.device_location}")
        lines.append(f"Total locations:         {len(self.locations)}")
        lines.append("============================")
        return "\n".join(lines)


# ---------- Testing ----------
if __name__ == "__main__":
    seed = 1234
    W = AdventureWorld(seed)
    print(W)
    print("Unoccupied:", W.get_unoccupied_locations())
    print("Is hazard1 at neigbor of location 1:", W.neighbor_has_hazard1(1))
    print("Neighbor treasure at 1:", W.neighbor_has_treasure(1))
    print("Neighbor map at 1:", W.neighbor_has_map(1))
    W.set_treasure_location(18)
    print(W)