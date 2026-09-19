from karel.robota import *

class DoorFinder(Robot):
    def findDoor(self):
        pass  # your code here - move east while there's a wall to your left,
              # stop and put a beeper down at the first gap you find

if __name__ == "__main__":
    world.readWorld("doorfinder_a.kwld")  # try the other doorfinder_*.kwld files too
    finder = DoorFinder(2, 1, East, 1)
    finder.findDoor()
