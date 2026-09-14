"""Checks that the robot starts at the required (1, 2, North, 80) - the exact
precondition plantAllFlowers() is written to assume."""
from karel.robota import *
import karel.robotutils as utils
import karel.kareltestutils as test

REQUIRED_CLASS = "GardenerBot"
ROBOT_VAR = "gardy"
START_STATE = (1, 2, North, 80)


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    world = UrRobot.use_graphics(False)
    world.setTrace(False)

    namespace, _violations = test.runMainOnly("main.py")
    if namespace is None:
        return False

    robot = namespace.get(ROBOT_VAR)
    if robot is None:
        print(f"ERROR: main.py should create a {REQUIRED_CLASS} instance named '{ROBOT_VAR}'.")
        return False

    initial = utils.getInitialState(robot)
    if not test.testRobotEquals(
        "Starting state",
        (initial.street(), initial.avenue(), initial.direction(), initial.beepers()),
        START_STATE,
    ):
        return False

    test_feedback.write("Starting state correct!")
    return True
