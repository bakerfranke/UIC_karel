"""Grading tests for the Harvester Beeper Field assignment (CS 111).

Two different strategies are used on purpose, for two different questions:

  - test_turnRight / test_harvestBeeperField import HarvesterBot and call the method
    directly on a freshly-constructed robot. They never run main.py at all, so they
    answer "does this method solve the problem on its own?" and can't be fooled by
    extra work a student hid in main to compensate for a broken/incomplete method.

  - test_main_guard_purity actually runs the student's main.py (respecting
    if __name__ == "__main__":) and checks that main never called a robot action
    directly - only test_main_guard_purity can catch that kind of "help" from main,
    since the two tests above don't execute main.py in the first place.

test_required_methods is a third, purely static strategy - it never runs any student
code at all, just parses main.py's source with karel.code_parser.
"""

from karel.robota import *
from karel.kareltestutils import *
import karel.robotutils as utils
from karel.code_parser import extract_method_headers_from_file

REQUIRED_CLASS = "HarvesterBot"
REQUIRED_METHODS = ["turnRight", "harvestBeeperField"]
MIN_METHOD_COUNT = 4

START_STATUS = (2, 2, East, 0)
END_STATUS = (8, 2, East, 36)  # all 36 beepers from BeeperField.kwld, in the bag


def _get_class():
    """Import HarvesterBot from main.py. Safe regardless of a main guard - the class
    definition sits outside if __name__ == "__main__": so a plain import runs it fine.
    Returns the class, or None (with an error already printed) if it's missing."""
    try:
        from main import HarvesterBot
    except Exception as e:
        print(f"ERROR: could not import HarvesterBot from main.py: {e}")
        return None
    return HarvesterBot


def test_turnRight(test_feedback):
    world = UrRobot.use_graphics(False)
    world.setTrace(False)

    HarvesterBot = _get_class()
    if HarvesterBot is None:
        return False
    if not testClassMethodExists(HarvesterBot, "turnRight"):
        return False

    stuBot = HarvesterBot(2, 2, East, 0)
    try:
        stuBot.turnRight()
    except Exception as e:
        print(f"ERROR: your turnRight() raised an exception instead of completing: {e}")
        return False
    if not testRobotEquals("Test turnRight", utils.getStatus(stuBot), (2, 2, South, 0)):
        print(
            "Behind the scenes we constructed a HarvesterBot at (2, 2, East, 0) and "
            "called .turnRight(). After running it we expected the HarvesterBot to be "
            "at (2, 2, South, 0) and yours wasn't. Look carefully at the output above "
            "to see differences."
        )
        return False

    test_feedback.write("turnRight() works correctly!")
    return True


def test_harvestBeeperField(test_feedback):
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.readWorld("BeeperField.kwld")

    HarvesterBot = _get_class()
    if HarvesterBot is None:
        return False
    if not testClassMethodExists(HarvesterBot, "harvestBeeperField"):
        return False

    stuBot = HarvesterBot(2, 2, East, 0)
    try:
        stuBot.harvestBeeperField()
    except Exception as e:
        print(f"ERROR: your harvestBeeperField() raised an exception instead of completing: {e}")
        return False

    if not testWorldEquals("Testing end state of world. Expecting no beepers.", world, "finalWorld.kwld"):
        print(
            "\nBehind the scenes we ran the following two lines of code:\n"
            "\tstuBot = HarvesterBot(2, 2, East, 0)\n"
            "\tstuBot.harvestBeeperField()\n"
            "NOTE: we are testing whether harvestBeeperField() works according to "
            "specification NOT running your __main__ code."
        )
        return False

    if not testRobotEquals("Test Harvest Beeper Field", utils.getStatus(stuBot), END_STATUS):
        print(
            f"Behind the scenes we constructed a HarvesterBot at (2, 2, East, 0) and "
            f"called .harvestBeeperField(). After running it we expected the "
            f"HarvesterBot to be at {END_STATUS} and yours wasn't. Look carefully at "
            f"the output above to see differences."
        )
        return False

    test_feedback.write("harvestBeeperField() correctly solves the whole problem!")
    return True


def test_required_methods(test_feedback):
    """Static check - never runs any student code. Parses main.py's source to count
    HarvesterBot's methods and confirm the required ones are present. Also prints
    every method header found, so a TA grading method-naming quality by hand has
    something to read without opening the student's file."""
    methods = extract_method_headers_from_file(
        "main.py",
        class_filter={REQUIRED_CLASS},
        include_dunder=False,
        include_private=False,
    )
    required_headers = [f"def {m}(self):" for m in REQUIRED_METHODS]
    found_headers = [m.header for m in methods]

    print("-" * 30)
    print(f"Inspecting code in main.py:\n{len(methods)} methods found in class {REQUIRED_CLASS}:")
    required_found = 0
    for i, m in enumerate(methods, start=1):
        checkmark = ""
        if m.header in required_headers:
            checkmark = " ✅"
            required_found += 1
        print(f"{i}. line {m.lineno}: {m.header}{checkmark}")

    has_count = len(methods) >= MIN_METHOD_COUNT
    has_required = required_found == len(required_headers)

    print("-" * 30)
    print(f"Test: number of methods >= {MIN_METHOD_COUNT}? {'✅' if has_count else f'❌ found {len(methods)}'}")
    if has_required:
        print("Test: required methods present? ✅")
    else:
        missing = [h for h in required_headers if h not in found_headers]
        print(f"Test: required methods present? ❌\n\tYour code is missing one of these: {missing}")

    result = has_count and has_required
    if result:
        test_feedback.write("Required methods and method count look good!")
    return result


def test_main_guard_purity(test_feedback):
    """Runs the student's actual main.py (respecting a main guard) and confirms no
    primitive robot action was called directly from main - only from within a method
    defined on the robot's own class. This is what catches a student "helping" a
    broken/incomplete harvestBeeperField() along with an extra move()/turnLeft()/etc.
    call sitting directly in main - test_harvestBeeperField above can't catch that,
    since it never runs main.py in the first place."""
    namespace, passed = testMainGuardPurity("Main Guard Purity", "main.py")
    if not passed:
        print(
            "Your main block should only create the robot, call harvestBeeperField(), "
            "and call turnOff() - all of the actual problem-solving needs to happen "
            "inside your class's own methods, not in main."
        )
        return False

    test_feedback.write("main only orchestrated - no problem-solving work hidden there!")
    return True
