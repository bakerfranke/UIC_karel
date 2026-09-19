from karel.robota import *

class BigCarpetBot(Robot):
    def carpetAllRooms(self):
        for room in range(8):
            self.move()
            self.checkAndCarpetRoom()
        self.move()
        self.turnOff()

    def checkAndCarpetRoom(self):
        self.turnLeft()
        self.move()
        self.roomHeight = 1
        self.roomComplete = False
        self.climbRoom()
        if self.roomComplete:
            self.putBeeper()
        self.turnAround()
        self.descendRoom()
        self.turnLeft()

    def climbRoom(self):
        for level in range(3):
            if not self.sidesAreWalled():
                return
            if not self.frontIsClear():
                self.roomComplete = True
                return
            if self.roomHeight < 3:
                self.move()
                self.roomHeight += 1

    def descendRoom(self):
        for step in range(self.roomHeight - 1):
            self.move()
            if self.roomComplete:
                self.putBeeper()
        self.move()  # final step back into the hallway - never carpeted

    def sidesAreWalled(self):
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
    world.readWorld("bigcarpetbot_world0.kwld")  # try the other bigcarpetbot_world*.kwld files too
    carpee = BigCarpetBot(1, 1, East, 24)
    carpee.carpetAllRooms()
