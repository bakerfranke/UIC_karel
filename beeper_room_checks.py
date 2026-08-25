"""Shared checks for the Bomb/Room lab exercise. Not itself a graded test file -
test_beeper_room_start.py / _end.py / _world.py each just call one function here.
Keeping the real logic in one place means there's only one copy of the setup/assertion
code to maintain even though the rubric grades it as three separate point items."""

from karel.robota import *
import karel.robotutils as utils
import karel.kareltestutils as test

EXPECTED_START = (1, 2, East, 0)   # street, avenue, direction, beepers
EXPECTED_END = (4, 3, East, 0)     # street, avenue, direction, beepers


def _setup():
    """Run the student's program once. Returns (world, boomy), or None if the import
    failed or the robot isn't named 'boomy' - an error is already printed in that case."""
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.setDelay(0)

    try:
        import main  # This will attempt to run the program
    except Exception as e:
        print(f"ERROR: while importing 'main': {e}")
        return None

    if not hasattr(main, 'boomy'):
        print("ERROR: The program assumes the robot is named 'boomy'.")
        return None

    return world, main.boomy


def check_start_state(test_feedback):
    setup = _setup()
    if setup is None:
        return False
    _world, boomy = setup

    start = utils.getInitialState(boomy)
    exp_street, exp_avenue, exp_direction, exp_beepers = EXPECTED_START

    if not test.testEquals(
        "Start Location", "boomy's starting (street, avenue)",
        (start.street(), start.avenue()), (exp_street, exp_avenue)
    ):
        return False

    if not test.testEquals(
        "Start Direction", "boomy's starting direction",
        start.direction().__name__, exp_direction.__name__
    ):
        return False

    if not test.testEquals(
        "Start Beepers", "boomy's starting beeper count",
        start.beepers(), exp_beepers
    ):
        return False

    test_feedback.write("Starting state correct!")
    return True


def check_end_state(test_feedback):
    setup = _setup()
    if setup is None:
        return False
    _world, boomy = setup

    end = utils.getStateHistory(boomy)[-1]
    exp_street, exp_avenue, exp_direction, exp_beepers = EXPECTED_END

    if not test.testEquals(
        "End Location", "boomy's ending (street, avenue)",
        (end.street(), end.avenue()), (exp_street, exp_avenue)
    ):
        return False

    if not test.testEquals(
        "End Direction", "boomy's ending direction",
        end.direction().__name__, exp_direction.__name__
    ):
        return False

    if not test.testEquals(
        "End Beepers", "boomy's ending beeper count (in the beeper bag)",
        end.beepers(), exp_beepers
    ):
        return False

    if not test.testEquals(
        "Turned Off", "boomy should be turned off (call boomy.turnOff()) by the end",
        end.isRunning(), False
    ):
        return False

    test_feedback.write("Ending state correct!")
    return True


def check_world_beepers(test_feedback):
    setup = _setup()
    if setup is None:
        return False
    world, _boomy = setup

    if not test.testWorldEquals("World Beepers", world, "beeper_room_end.kwld"):
        return False

    test_feedback.write("World beepers correct!")
    return True
