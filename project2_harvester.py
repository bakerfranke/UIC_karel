"""
Design a robot class to harvest a field of beepers.
"""

from karel.robota import *


class HarvesterBot(UrRobot):
    def turnRight( self ):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

    # Moves up a row, changes from facing left to facing right
    def upFaceRight(self):
        self.turnRight()
        self.move()
        self.turnRight()

    # Moves up a row, changes from facing left to facing rght
    def upFaceLeft(self):
        self.turnLeft()
        self.move()
        self.turnLeft()

    # pick and move
    def pickAndMove(self):
        self.pickBeeper()
        self.move()

    # Collects one row of beepers
    def collectRow(self):
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickAndMove()
        self.pickBeeper()
    
    # Collects two rows, ending where the last beeper is picked up facing West
    def collectTwoRows(self):
        self.collectRow()
        self.upFaceLeft()
        self.collectRow()

    def harvestBeeperField(self):
        self.move()

        # Collects beeper field
        self.collectTwoRows()
        self.upFaceRight()
        self.collectTwoRows()
        self.upFaceRight()
        self.collectTwoRows()

        self.move() # Move into final location
        self.upFaceRight()
        #self.turnOff()



if __name__ == "__main__":

    world.readWorld("BeeperField.kwld")
    world.setSize(9,10) # makes the window a little smaller
    world.setDelay(10) # you can change this to speed up or slow down
    
    harvey = HarvesterBot(2,2,East,0)
    harvey.harvestBeeperField()
    harvey.turnOff()

 
