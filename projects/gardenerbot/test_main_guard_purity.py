"""Confirms main only constructs the robot and calls plantAllFlowers() (turnOff()
is fine too if you use it) - no extra problem-solving work hiding directly in main."""
from karel.robota import *
import karel.kareltestutils as test


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    world = UrRobot.use_graphics(False)
    world.setTrace(False)

    namespace, passed = test.testMainGuardPurity(
        "Main Guard Purity", "main.py", allowedMethods={"plantAllFlowers", "turnOff"}
    )
    if not passed:
        return False

    test_feedback.write("main only orchestrated - no problem-solving work hidden there!")
    return True
