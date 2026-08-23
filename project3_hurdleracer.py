"""
Model solution
Baker Franke
"""

from karel.robota import *

class HurdleRacer(Robot):
    
    def runRace(self): # do not change this method
        for i in range(10):
            self.step()

    # Add code to step method. You may (and probably) should create
    # other methods that break down the things you need to do each step.
    def step(self):
        self.moveOrJump()
        self.pickIfBeeper()

    def moveOrJump(self):
        if self.frontIsClear():
            self.move()
        else:
            self.jumpHurdle()

    
    def jumpHurdle(self):
        self.moveToTopOfHurdle()

        self.move()     # move over the top
        self.turnRight()
        
        self.moveToBottom() 
        self.turnLeft() # position for next hurdle
    
    # post-condition: robot is ready to move across top of hurdle
    def moveToTopOfHurdle(self):
        self.turnLeft()
        self.move()
        self.turnRight()
        if not self.frontIsClear():
            self.turnLeft()
            self.move()
            self.turnRight()
    
    def moveToBottom(self):
        self.moveIfClear()
        self.moveIfClear()
    
    def moveIfClear(self):
        if self.frontIsClear():
            self.move()
    
    def pickIfBeeper(self):
        if self.nextToABeeper():
            self.pickBeeper()
            
    def turnRight(self):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":


    world.readWorld("hurdle4.kwld")
    world.setDelay(10)
    #world.setRobotCostume("dog") # use a custom robot image

    hurley = HurdleRacer(1,1,East,0)
    hurley.runRace()


