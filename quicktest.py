from karel.robota import *

world.setSize(5,5)  
world.setDelay(10)
bob = UrRobot(1, 1, North, 7)

bob.move()
bob.setVisible(False)
bob.move()
bob.putBeeper()
