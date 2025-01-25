"""
Useful functions and constants for getting info from robots esp. for writing tests.
"""
from karel.robota import world
from karel.robota import North
from karel.robota import West
from karel.robota import South
from karel.robota import East

direction_strings = {
    East: "East",
    North: 'North',
    West: "West",
    South: 'South'
}

def getStreet(robot):
    return robot._UrRobot__street

def getAvenue(robot):
    return robot._UrRobot__avenue

def getLocation(robot):
    return (robot._UrRobot__street, robot._UrRobot__avenue)

def getDirection(robot):
    return robot._UrRobot__direction

def getDirectionStr(robot):
    return direction_strings[robot._UrRobot__direction]

def _status_to_str(status):
    return (status[0], 
            status[1],
            direction_strings[status[2]],
            status[3])

def getBeepers(robot):
    return robot._UrRobot__beepers

def getStatus(robot):
    return (robot._UrRobot__street, 
            robot._UrRobot__avenue,
            robot._UrRobot__direction,
            robot._UrRobot__beepers)

def checkRobotEquals(robot, robot_tuple):
    return (robot._UrRobot__street == robot_tuple[0]
            and robot._UrRobot__avenue == robot_tuple[1]
            and robot._UrRobot__direction == robot_tuple[2]
            and robot._UrRobot__beepers == robot_tuple[3])

def worldHasBeeperAt(world, location_tuple, num_beepers, exact=True):
    # check if given world has num_beepers at location (st, ave)
    # if exact == False then check if location as AT LEAST num_beepers
    return False

#TODO - Write world equals
def checkWorldBeepers(beepers_list, expected_beepers_list):
    # Write this?
    return False
