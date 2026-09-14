import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, West, East

CLASS_NAME = "BeeperRelay"
METHOD = "collectAndRelay"
START = (1, 9, West, 0)
MAIN_FILE = "main.py"
END_STATUS = (1, 9, East, 0)

# world file -> expected final beeper layout (a contiguous line starting at avenue 1)
EXPECTED_LAYOUT = {
    "beeperrelay_a.kwld": {(1, 1): 1, (1, 2): 1, (1, 3): 1},
    "beeperrelay_b.kwld": {(1, 1): 1, (1, 2): 1, (1, 3): 1, (1, 4): 1},
    "beeperrelay_c.kwld": {(1, 1): 1},
    "beeperrelay_d.kwld": {},
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
    if not test.testRobotEquals(f"{world_file} - ending position", util.getStatus(bot), END_STATUS):
        return False

    actual = {loc: count for loc, count in world.getAllBeepers().items() if count}
    expected = EXPECTED_LAYOUT[world_file]
    diffs = util.get_beeper_diffs(actual, expected)
    print(f"{'-'*70}\nTEST: {world_file} - beepers laid out in a contiguous line from avenue 1")
    if diffs["diffs"]:
        print(f"DIFFERENCES...\n{diffs['allbeeperdiffs']}")
        return False
    print("RESULT: beepers correctly relayed! (Yay)")

    test_feedback.write(f"Correctly relayed the beepers into a line on {world_file}!")
    return True


def test_passed_a(test_feedback):
    return _check("beeperrelay_a.kwld", test_feedback)


def test_passed_b(test_feedback):
    return _check("beeperrelay_b.kwld", test_feedback)


def test_passed_c(test_feedback):
    return _check("beeperrelay_c.kwld", test_feedback)


def test_passed_d(test_feedback):
    return _check("beeperrelay_d.kwld", test_feedback)


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_passed_a, test_passed_b, test_passed_c, test_passed_d]:
        print(fn.__name__, "->", fn(StringIO()))
