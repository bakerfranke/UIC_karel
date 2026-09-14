from karel.robota import *

class BigCarpetBot(Robot):
    def carpetAllRooms(self):
        pass  # your code here

if __name__ == "__main__":
    world.readWorld("bigcarpetbot_world0.kwld")  # try the other bigcarpetbot_world*.kwld files too
    carpee = BigCarpetBot(1, 1, East, 24)
    carpee.carpetAllRooms()
