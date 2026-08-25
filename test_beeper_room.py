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

    if start.street() != exp_street or start.avenue() != exp_avenue:
        print(
            f"ERROR: boomy should start at street {exp_street}, avenue {exp_avenue}. "
            f"Instead started at street {start.street()}, avenue {start.avenue()}."
        )
        return False

    if start.direction() != exp_direction:
        print(
            f"ERROR: boomy should start facing {exp_direction.__name__}. "
            f"Instead started facing {start.direction().__name__}."
        )
        return False

    if start.beepers() != exp_beepers:
        print(
            f"ERROR: boomy should start with {exp_beepers} beepers. "
            f"Instead started with {start.beepers()}."
        )
        return False

    # boomy must end at the exact prescribed location, direction, beeper count, and be off
    end = utils.getStateHistory(boomy)[-1]
    exp_street, exp_avenue, exp_direction, exp_beepers = EXPECTED_END

    if end.street() != exp_street or end.avenue() != exp_avenue:
        print(
            f"ERROR: boomy should end at street {exp_street}, avenue {exp_avenue}. "
            f"Instead ended at street {end.street()}, avenue {end.avenue()}."
        )
        return False

    if end.direction() != exp_direction:
        print(
            f"ERROR: boomy should end facing {exp_direction.__name__}. "
            f"Instead ended facing {end.direction().__name__}."
        )
        return False

    if end.beepers() != exp_beepers:
        print(
            f"ERROR: boomy should end with {exp_beepers} beepers in the beeper bag. "
            f"Instead ended with {end.beepers()}."
        )
        return False

    if end.isRunning():
        print("ERROR: boomy should be turned off (call boomy.turnOff()) at the end of the program.")
        return False

    # The world must end with exactly one beeper, at (4, 3) - the bomb, safely in the room
    if not test.testWorldEquals("Test: the bomb ends up in the room", world, "beeper_room_end.kwld"):
        return False

    test_feedback.write("Woohoo!  All tests passed!")
    return True
