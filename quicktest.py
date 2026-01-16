"""
Name
NetID
Date
"""
from karel.robota import *


class HarvesterBot(UrRobot):
    pass #remove this
        # write your methods here



# main area
if __name__ == "__main__":

    world.readWorld("BeeperField.kwld") # load the world file
    world.setSize(9,10)
    world.setDelay(20) # you can change this to speed up or slow down

    # the following 3 lines is what will be used by the tests
    harvey = HarvesterBot(2,2,East,0)
    #harvey.harvestBeeperField()
    harvey.setVisible(False)
    harvey.move()
    harvey.turnOff()
#    harvey.pickBeeper()
