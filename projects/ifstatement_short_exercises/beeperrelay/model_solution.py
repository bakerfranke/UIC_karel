from karel.robota import *

class BeeperRelay(Robot):
    def collectAndRelay(self):
        self.collectGoingWest()
        self.turnAround()
        self.relayGoingEast()

    def collectGoingWest(self):
        self.pickIfBeeper()
        while self.frontIsClear():
            self.move()
            self.pickIfBeeper()

    def relayGoingEast(self):
        for step in range(8):
            if self.anyBeepersInBeeperBag():
                self.putBeeper()
            self.move()

    def pickIfBeeper(self):
        if self.nextToABeeper():
            self.pickBeeper()

    def turnAround(self):
        self.turnLeft()
        self.turnLeft()

if __name__ == "__main__":
    world.readWorld("beeperrelay_a.kwld")
    relay = BeeperRelay(1, 9, West, 0)
    relay.collectAndRelay()
