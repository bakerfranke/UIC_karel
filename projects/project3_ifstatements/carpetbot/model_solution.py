from karel.robota import *

class CarpetBot(Robot):
    def carpetSmallRooms(self):
        for room in range(8):
            self.move()
            self.checkAndCarpetRoom()
        self.move()
        self.turnOff()

    def checkAndCarpetRoom(self):
        self.turnLeft()
        self.move()
        if self.roomIsComplete():
            self.putBeeper()
        self.turnAround()
        self.move()
        self.turnLeft()

    def roomIsComplete(self):
        if self.frontIsClear():
            return False
        if not self.wallToLeft():
            return False
        if not self.wallToRight():
            return False
        return True

    def wallToLeft(self):
        self.turnLeft()
        blocked = not self.frontIsClear()
        self.turnRight()
        return blocked

    def wallToRight(self):
        self.turnRight()
        blocked = not self.frontIsClear()
        self.turnLeft()
        return blocked

    def turnRight(self):
        self.turnLeft()
        self.turnLeft()
        self.turnLeft()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":
    world.readWorld("carpetbot_world0.kwld")  # try the other carpetbot_world*.kwld files too
    carpee = CarpetBot(1, 1, East, 8)
    carpee.carpetSmallRooms()
