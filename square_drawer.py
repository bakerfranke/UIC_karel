from karel.robota import *

class SquareDrawer(UrRobot):

	def drawLine(self):
		self.putAndMove()
		self.putAndMove()
		self.putAndMove()


	def drawSquare(self):
		self.drawLine()
		self.turnLeft()
		self.drawLine()
		self.turnLeft()
		self.drawLine()
		self.turnLeft()
		self.drawLine()
		self.turnLeft()

	def putAndMove(self):
		self.putBeeper()
		self.move()


if __name__ == "__main__":

	world.setDelay(20)
	world.setSize(6,6)
	mybot = SquareDrawer(2,2,East,20)
	mybot.drawSquare()

		