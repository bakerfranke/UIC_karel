"""
Name
NetID
Date
"""
from karel.robota import *



class HarvesterBot(UrRobot):

    def harvestRow(self):
        self.move()
        #self.turnOff()
        self.pickBeeper()
        #self.setVisible(False)
        self.move()
        self.pickBeeper()
        self.move()
        self.pickBeeper()
        self.move()
        self.pickBeeper()
        self.move()
        self.pickBeeper()
        self.move()
        self.pickBeeper()
        self.move()

    def upAndLeft(self):
        self.turnLeft()
        self.move()
        self.turnLeft()

    def harvestTwoRows(self):
        self.harvestRow()
        self.upAndLeft()
        self.harvestRow()

class PlanterBot(HarvesterBot):

    def pickBeeper(self):
        super().pickBeeper()
        self.putBeeper()



# main area
if __name__ == "__main__":

    world.readWorld("BeeperField.kwld") # load the world file
    world.setSize(9,10)

    world.setDelay(5) # you can change this to speed up or slow down

    #world.startPaused(True)
    #world.setRobotCostume("sparky")
    # the following 3 lines is what will be used by the tests
    harvey = HarvesterBot(2,2,East,0)
    harvey.setCostume("dog")
    harvey.harvestTwoRows()


    harvey.move()
    #harvey.move()
    harvey.turnOff()

    #world.pause()
    world.setDelay(30) 
    harvey = PlanterBot(4,2,East,0)
    harvey.setCostume("dog")
    harvey.harvestTwoRows()
    harvey.pickBeeper()

    harvey = HarvesterBot(6,2,East,0)
    harvey.setCostume("sparky2")
    harvey.harvestTwoRows()

    for i in range(1,10):
        harvey = HarvesterBot(4,i,East,0)
        harvey.move()
    

