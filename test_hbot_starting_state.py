import runpy

from karel.robota import *
import karel.robotutils as utils

EXPECTED_STREET = 2
EXPECTED_AVENUE = 1
EXPECTED_DIRECTION = North
MIN_BEEPERS = 7


def test_passed(test_feedback):
#SETUP
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.setDelay(0)

    # Try to run the program and quit if it has a runtime error. Runs main.py with
    # runpy (rather than `import main`) so this also works for programs that put
    # their code inside `if __name__ == "__main__":`, which a plain import would
    # silently skip.
    try:
        namespace = runpy.run_path("main.py", run_name="__main__")
    except Exception as e:
        # Provide feedback about the error
        print(f"ERROR: while running 'main.py': {e}")
        return False

    # Make sure the robot exists and is named 'bob', per the starter code
    if 'bob' not in namespace:
        print("ERROR: The program assumes the robot is named 'bob'.")
        return False

    bob = namespace['bob']
# END SETUP

    # bob must have started at the correct location, facing the correct
    # direction, with at least the required number of beepers.
    start = utils.getInitialState(bob)

    if start.street() != EXPECTED_STREET or start.avenue() != EXPECTED_AVENUE:
        print(
            f"ERROR: bob should start at street {EXPECTED_STREET}, avenue {EXPECTED_AVENUE}. "
            f"Instead started at street {start.street()}, avenue {start.avenue()}."
        )
        return False

    if start.direction() != EXPECTED_DIRECTION:
        print(
            f"ERROR: bob should start facing {EXPECTED_DIRECTION.__name__}. "
            f"Instead started facing {start.direction().__name__}."
        )
        return False

    if start.beepers() != infinity and start.beepers() < MIN_BEEPERS:
        print(
            f"ERROR: bob should start with at least {MIN_BEEPERS} beepers. "
            f"Instead started with {start.beepers()}."
        )
        return False

    test_feedback.write("Woohoo!  bob starts in the right place, facing the right way, with enough beepers!")
    return True
