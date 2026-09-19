from karel.robota import *

class CarpetBot(Robot):
    def carpetSmallRooms(self):
        pass  # your code here

if __name__ == "__main__":
    world.readWorld("carpetbot_world0.kwld")  # try the other carpetbot_world*.kwld files too
    carpee = CarpetBot(1, 1, East, 8)
    carpee.carpetSmallRooms()
