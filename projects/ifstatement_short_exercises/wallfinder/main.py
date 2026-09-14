from karel.robota import *

class WallFinder(Robot):
    def findWall(self):
        pass  # your code here - move east until you hit the wall, then turn around

if __name__ == "__main__":
    world.readWorld("wallfinder_a.kwld")  # try the other wallfinder_*.kwld files too
    wally = WallFinder(1, 1, East, 0)
    wally.findWall()
