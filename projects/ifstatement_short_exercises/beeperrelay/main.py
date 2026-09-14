from karel.robota import *

class BeeperRelay(Robot):
    def collectAndRelay(self):
        pass  # your code here - collect beepers heading west, then lay them back
              # down in a contiguous line starting at avenue 1, heading back east

if __name__ == "__main__":
    world.readWorld("beeperrelay_a.kwld")  # try the other beeperrelay_*.kwld files too
    relay = BeeperRelay(1, 9, West, 0)
    relay.collectAndRelay()
