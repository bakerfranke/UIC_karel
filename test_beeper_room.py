from karel.robota import *
import karel.robotutils as utils
import karel.kareltestutils as test

EXPECTED_START = (1, 2, East, 0)   # street, avenue, direction, beepers
EXPECTED_END = (4, 3, East, 0)     # street, avenue, direction, beepers


def test_passed(test_feedback):
#SETUP
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.setDelay(0)

    # Try to run the program and quit if it has a runtime error
    try:
        import main  # This will attempt to run the program
    except Exception as e:
        # Provide feedback about the error
        print(f"ERROR: while importing 'main': {e}")
        return False

    # Make sure the robot exists and is named 'boomy', per the starter code
    if not hasattr(main, 'boomy'):
        print("ERROR: The program assumes the robot is named 'boomy'.")
        return False

    boomy = main.boomy
# END SETUP

    # boomy must have started at the exact prescribed location, direction, and beeper count
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

    # boomy must end at the exact prescribed location, direction, beeper count, and be off
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

    # The world must end with exactly one beeper, at (4, 3) - the bomb, safely in the room
    if not test.testWorldEquals("World Beepers", world, "beeper_room_end.kwld"):
        return False

    test_feedback.write("Woohoo!  All tests passed!")
    return True
