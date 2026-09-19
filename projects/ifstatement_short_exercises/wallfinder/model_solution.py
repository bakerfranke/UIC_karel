from karel.robota import *

class WallFinder(Robot):
    def findWall(self):
        while self.frontIsClear():
            self.move()
        self.turnAround()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":
    world.readWorld("wallfinder_a.kwld")
    wally = WallFinder(1, 1, East, 0)
    wally.findWall()
