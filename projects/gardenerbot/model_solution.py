"""
Please note this is one possible method of many.
You can solve this lots of different ways.
"""

from karel.robota import *


class GardenerBot(UrRobot):

    def plantAllFlowers(self):
        """ Planting all the flowers. Strategy: First move from gate to center of garden.
            Then plantHedgeFromCenter knows how to get from the center to one
            of the hedges in whatever direction it's facing, and back to the center.
            So, after planting one hedge, turn left, and do it again (x4)
        """
        self.moveFromGateToCenter()

        self.plantHedgeFromCenter()
        self.turnLeft()

        self.plantHedgeFromCenter()
        self.turnLeft()

        self.plantHedgeFromCenter()
        self.turnLeft()

        self.plantHedgeFromCenter()


    def moveAndPut(self):
        self.move()
        self.putBeeper()

    def turnRight(self):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

    def plantCorner(self):
        """ Plant 5 beepers moving clockwise around one of the interior corners of one
            of the quadrants of a '+' shaped hedge.
            Pre-condition assumption: start one block away so first move is a move-and-put
            Post-condition assumption: end sitting on top of the 5th beeper planted.
        """

        self.moveAndPut() # plant 3 in a row
        self.moveAndPut()
        self.moveAndPut()

        self.turnRight()  # turn interior corner

        self.moveAndPut() # plant 2 more beepers
        self.moveAndPut()

    def positionForNextCorner(self):
        """ Go around the end of one of the quadrants of a '+' shaped hedge.
            Pre-condition assumption: plantCorner() has just been called
            Post-condition assumption: robot position outside hedge ready to plant
            call next plantCorner()
        """
        self.move()
        self.turnLeft()
        self.move()
        self.turnLeft()

    def plantHedge(self):
        """ plant all the beepers around all 4 quadrants of a hedge: repeatedly
        plantCorner() and positionForNext()"""

        self.plantCorner()
        self.positionForNextCorner()

        self.plantCorner()
        self.positionForNextCorner()

        self.plantCorner()
        self.positionForNextCorner()

        # after last corner, don't reposition
        self.plantCorner()

    def move2(self):
        self.move()
        self.move()

    def move4(self):
        self.move2()
        self.move2()

    def moveFromGateToCenter(self):
        """A one-time method to move to the center of the garden.
        This way planting each hedge is just one 90-degree turn different
        than the previous.
        Assumption: starting facing north at (1,2) --> move north 8, east 7"""

        # move north 8
        self.move4()
        self.move4()

        self.turnRight() # face East

        # move east 7
        self.move4()
        self.move2()
        self.move()

    def moveFromCenterToHedge(self):
        """ Move from the center to the edge of a hedge, in position for a call to plantCorner()"""
        self.move4()
        self.turnLeft()

    def moveFromHedgeBackToCenter(self):
        """Knows how to get from a hedge back to center.  Assumes it's starting
        from where a call to plantCorner() would leave it"""

        self.move()
        self.turnRight()
        self.move2()
        self.move()
        self.turnLeft()
        self.turnLeft()

    def plantHedgeFromCenter(self):
        """Pre-condition: starting in center of garden facing some direction
           Post-condition: ending back in the center, facing same direction as when method called"""
        self.moveFromCenterToHedge()
        self.plantHedge()
        self.moveFromHedgeBackToCenter()


if __name__ == "__main__":
    world.readWorld("garden_walls.kwld")
    world.setSize(17, 18)
    world.setDelay(2)

    gardy = GardenerBot(1, 2, North, 80)
    gardy.plantAllFlowers()
