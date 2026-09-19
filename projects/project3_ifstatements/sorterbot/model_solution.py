"""
P4: Model Solution
"""

from karel.robota import *

class SorterBot(Robot):

    def pickAndMove10(self):

        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()

    def pickAndMove(self):
        if self.nextToABeeper():
            self.pickBeeper()

        if self.frontIsClear():
            self.move()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

    def turnRight(self):
        self.turnAround()
        self.turnLeft()

    def putAndMove10(self):
        for ave in range(10):
            self.putAndMove()

    def putAndMove(self):
        if self.anyBeepersInBeeperBag():
            self.putBeeper()

        if self.frontIsClear():
            self.move()

    def clearAndRestackRow(self):
        self.pickAndMove10()
        self.turnAround()
        self.putAndMove10()
        self.turnRight()
        self.move()
        self.turnRight()

    def sortBeepers(self):
        for row in range(10):
            self.clearAndRestackRow()

if __name__ == "__main__":
    world.readWorld("sorter_world0.kwld")  # try the other sorter_world*.kwld files too
    sorty = SorterBot(1, 1, East, 0)
    world.setDelay(10)
    sorty.sortBeepers()
    sorty.turnOff()
