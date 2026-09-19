"""
Your name
NetId
Date
"""
from karel.robota import *


class GardenerBot(UrRobot):
    def plantAllFlowers(self):
        pass  # your code here - see the project writeup for design hints



if __name__ == "__main__":
    world.readWorld("garden_walls.kwld")
    world.setSize(17, 18)
    world.setDelay(2)

    gardy = GardenerBot(1, 2, North, 80)
    gardy.plantAllFlowers()
