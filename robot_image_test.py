from karel.robota import *


world.setSize(8,8)
world.setDelay(40)
#world.setRobotType("foo_blah")

bob = UrRobot(1, 1, East, -1)


#for j in range(10):
for i in range(4):
    bob.move()
    bob.move()
    bob.putBeeper()
    bob.turnLeft()

bob.move()
    # bob.turnLeft()
    # bob.move()
    # bob.turnLeft()
    # bob.turnLeft()
    # bob.turnLeft()

bob = UrRobot(2, 2, East, -1)
bob1 = UrRobot(2, 3, North, -1)
bob2 = UrRobot(2, 4, South, -1)
bob3 = UrRobot(2, 5, West, -1)

bob.turnOff()
bob1.turnOff()
#bob2.turnOff()
bob3.turnOff()
