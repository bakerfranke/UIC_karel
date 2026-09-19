import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, East

CLASS_NAME = "DoorFinder"
METHOD = "findDoor"
START = (2, 1, East, 1)
MAIN_FILE = "main.py"

# world file -> avenue where the gap (doorway) is
GAP_AVE = {
    "doorfinder_a.kwld": 2,
    "doorfinder_b.kwld": 4,
    "doorfinder_c.kwld": 6,
    "doorfinder_d.kwld": 9,
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
    gap_ave = GAP_AVE[world_file]
    expected = (2, gap_ave, East, 0)
    if not test.testRobotEquals(f"{world_file} - stopping position", util.getStatus(bot), expected):
        return False
    actual = world.getAllBeepers().get((2, gap_ave), 0)
    if not test.testEquals(
        "Beeper marks the doorway", f"Checking for a beeper at (2, {gap_ave})",
        actual, 1
    ):
        return False
    test_feedback.write(f"Found the doorway and marked it correctly on {world_file}!")
    return True


def test_passed_a(test_feedback):
    return _check("doorfinder_a.kwld", test_feedback)


def test_passed_b(test_feedback):
    return _check("doorfinder_b.kwld", test_feedback)


def test_passed_c(test_feedback):
    return _check("doorfinder_c.kwld", test_feedback)


def test_passed_d(test_feedback):
    return _check("doorfinder_d.kwld", test_feedback)


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_passed_a, test_passed_b, test_passed_c, test_passed_d]:
        print(fn.__name__, "->", fn(StringIO()))
