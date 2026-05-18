from karel.robota import *

world.setSize(5, 5)
world.setDelay(0)

bob = UrRobot(2, 1, North, 7)

bob.turnLeft()
bob.turnLeft()
bob.turnLeft()
bob.move()
bob.putBeeper()  # (2,2)
bob.turnLeft()
bob.move()
bob.putBeeper()  # (3,2)
bob.move()
bob.putBeeper()  # (4,2)
bob.turnLeft()
bob.turnLeft()
bob.turnLeft()
bob.move()
bob.move()
bob.putBeeper()  # (4,4)
bob.turnLeft()
bob.turnLeft()
bob.turnLeft()
bob.move()
bob.putBeeper()  # (3,4)
bob.move()
bob.putBeeper()  # (2,4)
bob.turnLeft()
bob.turnLeft()
bob.move()
bob.turnLeft()
bob.move()
bob.putBeeper()  # (3,3)
bob.turnLeft()
bob.move()
bob.turnLeft()
bob.turnLeft()
bob.turnLeft()
bob.move()
bob.move()
bob.turnLeft()
bob.turnLeft()
bob.turnLeft()

bob.turnOff()
# from karel.robota import *

# bob = UrRobot(1, 2, East, 7)

# world.setSize(5, 5)
# world.setDelay(0)

# # Put beeper at (1, 2) - bottom of left column
# bob.putBeeper()

# # Move to (2, 2)
# bob.move()
# bob.putBeeper()

# # Turn north and move up the middle-left column
# bob.turnLeft()
# bob.move()
# bob.putBeeper()  # (2, 3) - middle

# bob.move()
# bob.putBeeper()  # (2, 4) - top of left column

# # Turn right (three left turns) to face East
# bob.turnLeft()
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()      # Now at (4, 4)
# bob.putBeeper() # Top of right column

# # Move down right column
# bob.turnLeft()
# bob.turnLeft()  # Now facing South
# bob.move()
# bob.putBeeper() # (4, 3)
# bob.move()
# bob.putBeeper() # (4, 2)

# # Go back to place middle beeper at (3,3)
# # Turn to face West
# bob.turnLeft()
# bob.move()      # (3, 2)
# bob.turnLeft()  # Face North
# bob.move()      # (3, 3)
# bob.putBeeper()

# # Return bob to (1, 2) facing East
# bob.turnLeft()
# bob.turnLeft()  # Face South
# bob.move()      # (3, 2)
# bob.turnLeft()  # Face East... 

# bob.turnOff()

# from karel.robota import *

# world.setSize(5, 5)
# world.setDelay(0)

# bob = UrRobot(2, 1, North, 7)

# # go to (2,2)
# bob.move()
# bob.putBeeper()

# # go to (3,2)
# bob.turnLeft()
# bob.move()
# bob.turnLeft()
# bob.turnLeft()
# bob.turnLeft()
# bob.putBeeper()

# # go to (4,2)
# bob.move()
# bob.putBeeper()

# # go to (3,2)
# bob.turnLeft()
# bob.turnLeft()
# bob.move()

# # go to (3,3)
# bob.turnLeft()
# bob.move()
# bob.putBeeper()

# # go to (3,4)
# bob.move()
# bob.putBeeper()

# # go to (4,4)
# bob.turnLeft()
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.putBeeper()

# # go to (2,4)
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()

# # return to start at (2,1), facing North
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()
# bob.turnLeft()
# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()
# from karel.robota import *

# bob = UrRobot(2, 4, North, 7)

# bob.move()
# bob.turnLeft()
# bob.pickBeeper()
# bob.putBeeper()

# world.setSize(5,5)
# world.setDelay(0)


# from karel.robota import *

# world.setSize(5, 5)
# world.setDelay(0)

# bob = UrRobot(2, 2, North, 7)

# # left column of H
# bob.move()
# bob.putBeeper()          # (2,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (3,2)

# bob.move()
# bob.putBeeper()          # (4,2)

# # middle of H
# bob.turnLeft()
# bob.turnLeft()
# bob.move()               # (3,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (3,3)

# # right column of H
# bob.move()
# bob.putBeeper()          # (3,4)

# bob.turnRight()
# bob.move()
# bob.putBeeper()          # (4,4)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()          # (2,4)

# # return to start
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()

# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(5,10)
# world.setDelay(0)

# bob = UrRobot(1,2,East,7)

# # move to left column bottom
# bob.move()
# bob.putBeeper()        # (2,2)

# # go up column
# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (2,3)

# bob.move()
# bob.putBeeper()        # (2,4)

# # go back to middle row
# bob.turnLeft()
# bob.turnLeft()
# bob.move()             # (2,3)

# # center beeper
# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (3,3)

# # right column middle
# bob.move()
# bob.putBeeper()        # (4,3)

# # right column top
# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (4,4)

# # right column bottom
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()        # (4,2)

# # return to start
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()

# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(5,5)
# world.setDelay(0)

# bob = UrRobot(1,2,East,7)

# # go to left column bottom
# bob.move()
# bob.move()
# bob.putBeeper()          # (3,2)

# # go up left column
# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (3,3)

# # go down to bottom
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()          # (3,1)

# # go to middle
# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (4,2)

# # go to right column
# bob.move()
# bob.putBeeper()          # (5,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (5,3)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()          # (5,1)

# # return to start
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()
# bob.move()

# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(5,5)
# world.setDelay(0)

# bob = UrRobot(1,2,East,7)

# # go to left column bottom
# bob.move()
# bob.move()
# bob.putBeeper()          # (3,2)

# # go up left column
# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (3,3)

# # go down to bottom
# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()          # (3,1)

# # go to middle
# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (4,2)

# # go to right column
# bob.move()
# bob.putBeeper()          # (5,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()          # (5,3)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()          # (5,1)

# # return to start
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()
# bob.move()

# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(10,10)
# world.setDelay(0)

# bob = UrRobot(1, 2, East, 7)

# # left column
# bob.move()
# bob.putBeeper()        # (2,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (2,3)

# bob.move()
# bob.putBeeper()        # (2,4)

# # move to center
# bob.turnLeft()
# bob.turnLeft()
# bob.move()

# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (3,3)

# # move to right column
# bob.move()
# bob.putBeeper()        # (4,3)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()        # (4,4)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()        # (4,2)

# # return to start
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()

# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(5,5)
# world.setDelay(0)

# bob = UrRobot(1, 2, East, 7)

# # Left side of H
# bob.move()
# bob.putBeeper()      # (2,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()      # (2,3)

# bob.move()
# bob.putBeeper()      # (2,4)

# # Middle of H
# bob.turnLeft()
# bob.turnLeft()
# bob.move()           # back to (2,3)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()      # (3,3)

# # Right side of H
# bob.move()
# bob.putBeeper()      # (4,3)

# bob.turnLeft()
# bob.turnLeft()
# bob.turnLeft()       # turn right
# bob.move()
# bob.putBeeper()      # (4,4)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()      # (4,2)

# # Return to start at (1,2), facing East
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.move()
# bob.turnLeft()
# bob.turnLeft()

# bob.turnOff()

# from karel.robota import *

# world.setSize(5,5)
# #world.setDelay(20)

# bob = UrRobot(1, 2, East, 7)

# # move to first column of H
# bob.move()
# bob.putBeeper()      # (2,2)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()      # (2,3)

# bob.move()
# bob.putBeeper()      # (2,4)

# # move to middle bar
# bob.turnLeft()
# bob.turnLeft()
# bob.move()           # back to (2,3)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()      # (3,3)

# # move to right column
# bob.move()
# bob.putBeeper()      # (4,3)

# bob.turnLeft()
# bob.move()
# bob.putBeeper()      # (4,4)

# bob.turnLeft()
# bob.turnLeft()
# bob.move()
# bob.move()
# bob.putBeeper()      # (4,2)

# bob.turnOff()