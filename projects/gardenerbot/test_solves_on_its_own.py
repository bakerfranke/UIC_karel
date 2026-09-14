"""Checks that calling plantAllFlowers() directly on a fresh robot (bypassing
main.py entirely) reaches the correct final world state on its own - not just
"when run via main", which could be quietly propped up by extra work in main."""
from karel.robota import *
import karel.kareltestutils as test
import runpy

REQUIRED_CLASS = "GardenerBot"
START_STATE = (1, 2, North, 80)


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.setSize(17, 18)
    world.readWorld("garden_walls.kwld")

    try:
        namespace = runpy.run_path("main.py")
    except Exception as e:
        print(f"ERROR: could not import main.py: {e}")
        return False

    cls = namespace.get(REQUIRED_CLASS)
    if cls is None:
        print(f"ERROR: could not find a class named {REQUIRED_CLASS} in main.py.")
        return False

    bot = cls(*START_STATE)
    try:
        bot.plantAllFlowers()
    except Exception as e:
        print(f"ERROR: calling plantAllFlowers() directly on a fresh robot raised an exception: {e}")
        return False

    if not test.testWorldEquals("plantAllFlowers() solves it on its own", world, "gardenerbot_final_world.kwld"):
        print(
            "Behind the scenes we constructed a fresh GardenerBot and called ONLY "
            "plantAllFlowers() on it - bypassing your main block entirely. If this "
            "doesn't match but your main block's own run does, that means main is "
            "doing some of the work itself instead of leaving it all to "
            "plantAllFlowers()."
        )
        return False

    test_feedback.write("plantAllFlowers() correctly solves the whole problem on its own!")
    return True
