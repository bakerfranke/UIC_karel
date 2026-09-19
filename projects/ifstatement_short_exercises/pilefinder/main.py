from karel.robota import *

class PileFinder(Robot):
    def findPile(self):
        pass  # your code here - move east, stopping at the corner with exactly 2 beepers

if __name__ == "__main__":
    world.readWorld("pilefinder_a.kwld")  # try the other pilefinder_*.kwld files too
    finder = PileFinder(1, 1, East, 0)
    finder.findPile()
