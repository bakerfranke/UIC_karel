
from karel.robota import *

world.setSize(5,5)
world.setDelay(15)

myBot = UrRobot(1,2,East,5) # default is sparky
for i in range(4):
    myBot.move()
    myBot.putBeeper()
    myBot.move()
    myBot.turnLeft()


world.setRobotType("karel") # you can change the graphic used to "karel" | "sparky" 
myBot = UrRobot(3,1,East,5)
for i in range(4):
    myBot.move()
    myBot.putBeeper()
    myBot.move()
    myBot.turnLeft()


world.setRobotType(None) # if given None or an unknown type it defaults to a shape
myBot = UrRobot(3,3,South,5)
for i in range(4):
    myBot.move()
    myBot.putBeeper()
    myBot.move()
    myBot.turnLeft()


myBot = UrRobot(5,5,West,5, robot_type="sparky") # extra parameter to set the icon type without changing the world default
for i in range(4):
    myBot.move()
    myBot.putBeeper()
    myBot.move()
    myBot.turnLeft()

