from karel.robota import *

class PileFinder(Robot):
    def findPile(self):
        while not self.checkAndRestore():
            self.move()

    def checkAndRestore(self):
        """Checks the current corner. Returns True (and leaves exactly 2 beepers
        here) if this corner had exactly 2 beepers. Returns False (and leaves
        whatever was originally here - 0 or 1 - undisturbed) otherwise."""
        if not self.nextToABeeper():
            return False
        self.pickBeeper()
        if not self.nextToABeeper():
            self.putBeeper()
            return False
        self.pickBeeper()
        self.putBeeper()
        self.putBeeper()
        return True

if __name__ == "__main__":
    world.readWorld("pilefinder_a.kwld")
    finder = PileFinder(1, 1, East, 0)
    finder.findPile()
