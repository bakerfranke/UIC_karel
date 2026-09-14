import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, East

CLASS_NAME = "PileFinder"
METHOD = "findPile"
START = (1, 1, East, 0)
MAIN_FILE = "main.py"

# world file -> expected stopping avenue
EXPECTED_STOP_AVE = {
    "pilefinder_a.kwld": 5,
    "pilefinder_b.kwld": 2,
    "pilefinder_c.kwld": 8,
    "pilefinder_d.kwld": 9,
}


def _run(world_file):
    if not test.checkNoCodeOutsideMainGuard(MAIN_FILE):
        return None, None
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.reset()
    world.readWorld(world_file)
    try:
        namespace = runpy.run_path(MAIN_FILE)
    except Exception as e:
        print(f"ERROR: could not import {MAIN_FILE}: {e}")
        return None, None
    cls = namespace.get(CLASS_NAME)
    if cls is None:
        print(f"ERROR: could not find a class named {CLASS_NAME} in {MAIN_FILE}.")
        return None, None
    try:
        bot = cls(*START)
        getattr(bot, METHOD)()
    except Exception as e:
        print(f"ERROR: calling {METHOD}() raised an exception: {e}")
        return None, None
    return bot, world


def _check(world_file, test_feedback):
    bot, world = _run(world_file)
    if bot is None:
        return False
    expected = (1, EXPECTED_STOP_AVE[world_file], East, 0)
    if not test.testRobotEquals(f"{world_file} - stopping position", util.getStatus(bot), expected):
        return False
    if not test.testWorldEquals(f"{world_file} - world restored to original", world, world_file):
        print(
            "Your robot found the right pile, but the beepers along the way (or the "
            "pile itself) weren't left exactly as they started - make sure every "
            "corner you inspect gets fully restored, including the 2-pile itself."
        )
        return False
    test_feedback.write(f"Found the pile of 2 and left everything else untouched on {world_file}!")
    return True


def test_passed_a(test_feedback):
    return _check("pilefinder_a.kwld", test_feedback)


def test_passed_b(test_feedback):
    return _check("pilefinder_b.kwld", test_feedback)


def test_passed_c(test_feedback):
    return _check("pilefinder_c.kwld", test_feedback)


def test_passed_d(test_feedback):
    return _check("pilefinder_d.kwld", test_feedback)


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_passed_a, test_passed_b, test_passed_c, test_passed_d]:
        print(fn.__name__, "->", fn(StringIO()))
