"""Checks the world's final beeper layout (running the student's actual main.py)
against the full correct solution - all 4 hedges, 80 beepers total."""
from karel.robota import *
import karel.kareltestutils as test


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    world = UrRobot.use_graphics(False)
    world.setTrace(False)

    namespace, _violations = test.runMainOnly("main.py")
    if namespace is None:
        return False

    if not test.testWorldEquals("Final world state - all 4 hedges", world, "gardenerbot_final_world.kwld"):
        return False

    test_feedback.write("All 4 hedges planted correctly!")
    return True
