from karel.robota import *

class GapFinder(Robot):
    def findGap(self):
        pass  # your code here - move east while walled on both sides,
              # stop and turn around at the first gap on either side

if __name__ == "__main__":
    world.readWorld("gapfinder_a.kwld")  # try the other gapfinder_*.kwld files too
    finder = GapFinder(2, 1, East, 0)
    finder.findGap()
