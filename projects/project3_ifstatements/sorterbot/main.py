from karel.robota import *

class SorterBot(Robot):
    def sortBeepers(self):
        pass  # your code here

if __name__ == "__main__":
    world.readWorld("sorter_world0.kwld")  # try the other sorter_world*.kwld files too
    sorty = SorterBot(1, 1, East, 0)
    sorty.sortBeepers()
