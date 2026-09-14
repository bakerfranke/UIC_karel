"""Minimum-requirement check: even if the rest of the field isn't fully correct,
getting the lower-left hedge (the one nearest the garden gate) exactly right is
worth partial credit on its own. Checks only beepers with street < 9 and
avenue < 9 - the rest of the world is ignored by this test entirely."""
from karel.robota import *
import karel.kareltestutils as test

EXPECTED_SW_QUADRANT = {
    (3, 5): 1, (3, 6): 1, (4, 5): 1, (4, 6): 1,
    (5, 3): 1, (5, 4): 1, (5, 5): 1, (5, 6): 1, (5, 7): 1, (5, 8): 1,
    (6, 3): 1, (6, 4): 1, (6, 5): 1, (6, 6): 1, (6, 7): 1, (6, 8): 1,
    (7, 5): 1, (7, 6): 1, (8, 5): 1, (8, 6): 1,
}


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    world = UrRobot.use_graphics(False)
    world.setTrace(False)

    namespace, _violations = test.runMainOnly("main.py")
    if namespace is None:
        return False

    allBeepers = world.getAllBeepers()
    swBeepers = {loc: count for loc, count in allBeepers.items()
                 if loc[0] < 9 and loc[1] < 9 and count}

    print(f"Lower-left quadrant (street < 9, avenue < 9) beepers found: {len(swBeepers)}")
    if swBeepers != EXPECTED_SW_QUADRANT:
        missing = set(EXPECTED_SW_QUADRANT) - set(swBeepers)
        extra = set(swBeepers) - set(EXPECTED_SW_QUADRANT)
        wrongCount = {loc: (swBeepers[loc], EXPECTED_SW_QUADRANT[loc])
                      for loc in set(swBeepers) & set(EXPECTED_SW_QUADRANT)
                      if swBeepers[loc] != EXPECTED_SW_QUADRANT[loc]}
        if missing:
            print(f"  Missing beeper(s) at: {sorted(missing)}")
        if extra:
            print(f"  Extra/unexpected beeper(s) at: {sorted(extra)}")
        if wrongCount:
            print(f"  Wrong count at: {wrongCount}")
        return False

    test_feedback.write("Lower-left hedge (minimum requirement) planted correctly!")
    return True
