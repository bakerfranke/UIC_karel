from karel.robota import *

class GapFinder(Robot):
    def findGap(self):
        while self.wallOnLeft() and self.wallOnRight():
            self.move()
        self.turnAround()

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
    world.readWorld("gapfinder_a.kwld")
    finder = GapFinder(2, 1, East, 0)
    finder.findGap()
