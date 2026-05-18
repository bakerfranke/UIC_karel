import re


class GameMap:

    _COLOR_CODES = {
        "red": "\x1b[41m",
        "magenta": "\x1b[45m",
        "yellow": "\x1b[43m",
        "green": "\x1b[42m",
        "cyan": "\x1b[46m",
        "blue": "\x1b[44m",
    }

    def __init__(self):
        """
        Create a new GameMap.
        """
        self.locations = self._generate_dodecahedron()
        self.display_map_type = "ascii"
        self._highlights = {}  # location -> color name
        print("New GameMap created")

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
            20: [13, 16, 19],
        }

    # ---------- Core World Access ----------

    def get_neighbors(self, location):
        if not isinstance(location, int):
            raise TypeError("Location must be an integer from 1 to 20.")

        if location not in self.locations:
            raise ValueError("Location must be in the range 1–20.")

        return self.locations[location]

    # ---------- Highlight Management ----------

    def set_highlight(self, location, color):
        """
        Set or update highlight color for a location.
        color must be: red, white, yellow, green, blue, magenta, cyan, or none
        """
        
        if location not in self.locations:
            raise ValueError("Location must be an integer from 1 to 20.")

        color = color.lower()
        valid_colors = set(self._COLOR_CODES.keys()) | {"none"}

        if color not in valid_colors:
            raise ValueError(f"Color must be one of {valid_colors}")

        if color == "none":
            self._highlights.pop(location, None)
        else:
            self._highlights[location] = color

    def clear_highlights(self):
        self._highlights.clear()

    # ---------- Map Rendering ----------

    def get_map_ascii(self):

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
        """.strip("\n")

        if not self._highlights:
            return map_str

        ESC = "\x1b"
        RESET = f"{ESC}[0m"
        WHITE = f"{ESC}[97m"

        def style_number(match):
            num = int(match.group(0))
            color_name = self._highlights.get(num)
            if color_name:
                bg = self._COLOR_CODES[color_name]
                return f"{WHITE}{bg}{num}{RESET}"
            return match.group(0)

        for n in range(20, 0, -1):
            map_str = re.sub(rf"(?<!\d){n}(?!\d)", style_number, map_str)

        return map_str

    def get_map_ansi(self):

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

        ESC = "\x1b"
        RESET = f"{ESC}[0m"
        WHITE = f"{ESC}[97m"
        DIM = "\x1b[37m" #f"{ESC}[90m"

        styled = f"{DIM}{base_map}{RESET}"

        def style_number(match):
            num = int(match.group(0))
            color_name = self._highlights.get(num)
            if color_name:
                bg = self._COLOR_CODES[color_name]
                return f"{RESET}{WHITE}{bg}{num}{RESET}{DIM}"
            return match.group(0)

        for n in range(20, 0, -1):
            styled = re.sub(rf"(?<!\d){n}(?!\d)", style_number, styled)

        return styled + RESET

    # ---------- Display Control ----------

    def set_map_type(self, type="ascii"):
        map_type = type.lower().strip()
        if map_type not in ["ascii", "ansi"]:
            print("Unknown map type. Using 'ascii'.")
            map_type = "ascii"
        self.display_map_type = map_type

    def print_map(self, type=None):

        display_type = self.display_map_type

        if type in ["ascii", "ansi"]:
            display_type = type

        if display_type == "ascii":
            print(self.get_map_ascii())
        else:
            print(self.get_map_ansi())

    def __str__(self):
        if self.display_map_type == "ansi":
            return self.get_map_ansi()
        return self.get_map_ascii()


# ----- Singleton instance -----

gameMap = GameMap()


# ---------- Testing ----------

if __name__ == "__main__":

    gameMap.set_map_type("ansi")
    gameMap.set_highlight(5, "red")
    gameMap.set_highlight(12, "green")
    gameMap.print_map()

    gameMap.set_map_type("ascii")
    gameMap.print_map()