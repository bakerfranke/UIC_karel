from karel.robota import *

class DoorFinder(Robot):
    def findDoor(self):
        while self.wallOnLeft():
            self.move()
        self.putBeeper()

    def wallOnLeft(self):
        self.turnLeft()
        result = not self.frontIsClear()
        self.turnRight()
        return result

    def turnRight(self):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":
    world.readWorld("doorfinder_a.kwld")
    finder = DoorFinder(2, 1, East, 1)
    finder.findDoor()
