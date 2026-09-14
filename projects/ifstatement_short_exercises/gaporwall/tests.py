import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, East, West

CLASS_NAME = "GapOrWallFinder"
METHOD = "findGapOrWall"
START = (2, 1, East, 1)
MAIN_FILE = "main.py"

# world file -> (expected status, expected ground beeper location-or-None)
EXPECTED = {
    "gaporwall_a.kwld": ((2, 4, West, 1), None),
    "gaporwall_b.kwld": ((2, 9, East, 0), (2, 9)),
    "gaporwall_c.kwld": ((2, 5, West, 1), None),
    "gaporwall_d.kwld": ((2, 6, West, 1), None),
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
    expected_status, beeper_loc = EXPECTED[world_file]
    if not test.testRobotEquals(f"{world_file} - ending state", util.getStatus(bot), expected_status):
        return False

    ground = {loc: c for loc, c in world.getAllBeepers().items() if c}
    expected_ground = {beeper_loc: 1} if beeper_loc else {}
    if ground != expected_ground:
        print(
            f"{'-'*70}\nTEST: {world_file} - beeper placement\n"
            f"Your ground beepers: {ground}\n"
            f"        Expected: {expected_ground}\n"
            "Remember: a wall break takes precedence over a blocked front - only put "
            "a beeper down if the front was blocked with no wall break before it."
        )
        return False

    test_feedback.write(f"Correctly handled {world_file}!")
    return True


def test_passed_a(test_feedback):
    return _check("gaporwall_a.kwld", test_feedback)


def test_passed_b(test_feedback):
    return _check("gaporwall_b.kwld", test_feedback)


def test_passed_c(test_feedback):
    return _check("gaporwall_c.kwld", test_feedback)


def test_passed_d(test_feedback):
    return _check("gaporwall_d.kwld", test_feedback)


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_passed_a, test_passed_b, test_passed_c, test_passed_d]:
        print(fn.__name__, "->", fn(StringIO()))
