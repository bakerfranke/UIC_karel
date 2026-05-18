from karel.robota import *

class CarpetBot(Robot):

    def carpetAllRooms(self):
        # move east across the hallway
        while self.frontIsClear():
            self.move()

            # never check the last avenue before boundary
            if self.frontIsClear():
                self.checkRoom()


    def checkRoom(self):
        # face north toward possible room
        self.turnLeft()

        # no doorway → no room
        if not self.frontIsClear():
            self.turnRight()
            return

        # enter the room
        self.move()

        room_complete = True

        # walk upward checking side walls
        while self.frontIsClear():

            if self.leftIsClear() or self.rightIsClear():
                room_complete = False

            self.move()

        # check the top cell
        if self.leftIsClear() or self.rightIsClear():
            room_complete = False

        if room_complete:
            self.carpetRoom()
        else:
            self.returnToHall()


    def carpetRoom(self):
        # robot is at top of finished room facing north
        self.putBeeper()

        self.turnAround()

        while self.frontIsClear():
            self.move()

            # don't place on street 1
            if self.frontIsClear():
                self.putBeeper()

        # now back in hallway
        self.turnLeft()


    def returnToHall(self):
        # return without placing beepers
        self.turnAround()

        while self.frontIsClear():
            self.move()

        self.turnLeft()

    def turnRight(self):
        for i in range(3):
            self.turnLeft()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

    def leftIsClear(self):
        self.turnLeft()
        clear = self.frontIsClear()
        self.turnRight()
        return clear

    def rightIsClear(self):
        self.turnRight()
        clear = self.frontIsClear()
        self.turnLeft()
        return clear

if __name__ == "__main__":
    world.readWorld("rooms1.kwld")   # change rooms world file
    world.setDelay(2)       
    world.setSize(10,12)        # change the delay 
    carpee = CarpetBot(1,1,East,-1)  # don’t change
    carpee.carpetAllRooms()          # don’t change