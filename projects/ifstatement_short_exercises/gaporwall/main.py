from karel.robota import *

class GapOrWallFinder(Robot):
    def findGapOrWall(self):
        pass  # your code here - move east while walled on both sides and front is
              # clear; a wall break takes precedence - only put a beeper down if you
              # stopped because the front was blocked with no wall break before it

if __name__ == "__main__":
    world.readWorld("gaporwall_a.kwld")  # try the other gaporwall_*.kwld files too
    finder = GapOrWallFinder(2, 1, East, 1)
    finder.findGapOrWall()
