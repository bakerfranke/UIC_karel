from karel.robota import *

class GapOrWallFinder(Robot):
    def findGapOrWall(self):
        while self.wallOnLeft() and self.wallOnRight() and self.frontIsClear():
            self.move()
        if self.wallOnLeft() and self.wallOnRight():
            self.putBeeper()   # only reason left to have stopped: front is blocked
        else:
            self.turnAround()  # a wall break takes precedence over a blocked front

    def wallOnLeft(self):
        self.turnLeft()
        result = not self.frontIsClear()
        self.turnRight()
        return result

    def wallOnRight(self):
        self.turnRight()
        result = not self.frontIsClear()
        self.turnLeft()
        return result

    def turnRight(self):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":
    world.readWorld("gaporwall_a.kwld")
    finder = GapOrWallFinder(2, 1, East, 1)
    finder.findGapOrWall()
