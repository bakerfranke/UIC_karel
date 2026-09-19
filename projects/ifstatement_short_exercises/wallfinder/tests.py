import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, East, West

CLASS_NAME = "WallFinder"
METHOD = "findWall"
START = (1, 1, East, 0)
MAIN_FILE = "main.py"

# world file -> expected (street, avenue, direction, beepers)
EXPECTED = {
    "wallfinder_a.kwld": (1, 2, West, 0),
    "wallfinder_b.kwld": (1, 4, West, 0),
    "wallfinder_c.kwld": (1, 6, West, 0),
    "wallfinder_d.kwld": (1, 9, West, 0),
}


def _run(world_file):
    if not test.checkNoCodeOutsideMainGuard(MAIN_FILE):
        return None
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.reset()
    world.readWorld(world_file)
    try:
        namespace = runpy.run_path(MAIN_FILE)
    except Exception as e:
        print(f"ERROR: could not import {MAIN_FILE}: {e}")
        return None
    cls = namespace.get(CLASS_NAME)
    if cls is None:
        print(f"ERROR: could not find a class named {CLASS_NAME} in {MAIN_FILE}.")
        return None
    try:
        bot = cls(*START)
        getattr(bot, METHOD)()
    except Exception as e:
        print(f"ERROR: calling {METHOD}() raised an exception: {e}")
        return None
    return bot


def _check(world_file, test_feedback):
    bot = _run(world_file)
    if bot is None:
        return False
    expected = EXPECTED[world_file]
    if not test.testRobotEquals(f"{world_file}", util.getStatus(bot), expected):
        return False
    test_feedback.write(f"Correct end state on {world_file}!")
    return True


def test_passed_a(test_feedback):
    return _check("wallfinder_a.kwld", test_feedback)


def test_passed_b(test_feedback):
    return _check("wallfinder_b.kwld", test_feedback)


def test_passed_c(test_feedback):
    return _check("wallfinder_c.kwld", test_feedback)


def test_passed_d(test_feedback):
    return _check("wallfinder_d.kwld", test_feedback)


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_passed_a, test_passed_b, test_passed_c, test_passed_d]:
        print(fn.__name__, "->", fn(StringIO()))
