"""Checks: class GardenerBot exists, defines plantAllFlowers(), and has at least
4 OTHER methods that are both defined AND actually called somewhere when
plantAllFlowers() runs (not just defined and left unused) - plus no method calls
the global robot instance by name instead of self."""
from karel.robota import *
import karel.kareltestutils as test
import inspect
import runpy

REQUIRED_CLASS = "GardenerBot"
REQUIRED_METHOD = "plantAllFlowers"
ROBOT_VAR = "gardy"
START_STATE = (1, 2, North, 80)
MIN_OTHER_METHODS = 4


def _countCalledMethods(cls, methodNames):
    """Temporarily wraps each named method on cls to record whether it gets
    called during an isolated plantAllFlowers() run, then restores the
    originals. Returns the set of method names that were actually invoked."""
    called = set()
    originals = {}

    def makeWrapper(name, original):
        def wrapper(self, *args, **kwargs):
            called.add(name)
            return original(self, *args, **kwargs)
        return wrapper

    for name in methodNames:
        originals[name] = getattr(cls, name)
        setattr(cls, name, makeWrapper(name, originals[name]))

    try:
        world = UrRobot.use_graphics(False)
        world.setTrace(False)
        world.setSize(17, 18)
        world.readWorld("garden_walls.kwld")
        bot = cls(*START_STATE)
        bot.plantAllFlowers()
    except Exception:
        pass  # a crash here is covered by other tests - just use whatever ran before it
    finally:
        for name, original in originals.items():
            setattr(cls, name, original)

    return called


def test_passed(test_feedback):
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False

    try:
        namespace = runpy.run_path("main.py")
    except Exception as e:
        print(f"ERROR: main.py raised an exception: {e}")
        return False

    cls = namespace.get(REQUIRED_CLASS)
    if cls is None:
        print(f"ERROR: could not find a class named {REQUIRED_CLASS} in main.py.")
        return False

    if not test.testClassMethodExists(cls, REQUIRED_METHOD):
        return False

    misuse = test.findGlobalInstanceMisuse("main.py", REQUIRED_CLASS, ROBOT_VAR)
    if misuse:
        methodName, calledAttr, lineno = misuse[0]
        print(
            f"ERROR: line {lineno}: {methodName}() calls {ROBOT_VAR}.{calledAttr}() - it "
            f"should be self.{calledAttr}() instead. Using '{ROBOT_VAR}' directly reaches "
            f"for the specific robot you made in __main__, rather than whichever robot the "
            f"method is actually being called on - self is always the right one."
        )
        return False

    otherMethods = sorted(
        n for n, v in vars(cls).items()
        if not n.startswith('_') and inspect.isfunction(v) and n != REQUIRED_METHOD
    )
    print(f"{len(otherMethods)} other method(s) defined on {REQUIRED_CLASS}: {otherMethods}")
    if len(otherMethods) < MIN_OTHER_METHODS:
        print(
            f"ERROR: {REQUIRED_CLASS} should have at least {MIN_OTHER_METHODS} methods "
            f"besides {REQUIRED_METHOD}() (found {len(otherMethods)}). Break "
            f"{REQUIRED_METHOD}() down into smaller, reusable pieces - see the design "
            f"hints in the project writeup."
        )
        return False

    called = _countCalledMethods(cls, otherMethods)
    unused = [n for n in otherMethods if n not in called]
    print(f"Called while running {REQUIRED_METHOD}(): {sorted(called)}")
    usedCount = len(otherMethods) - len(unused)
    if usedCount < MIN_OTHER_METHODS:
        print(
            f"ERROR: only {usedCount} of your other methods are actually called when "
            f"{REQUIRED_METHOD}() runs (need at least {MIN_OTHER_METHODS}). Defined but "
            f"never used: {unused}. A method that's never called doesn't count towards "
            f"the requirement - make sure everything you write is actually part of your "
            f"solution."
        )
        return False

    test_feedback.write(f"Class and method structure look good ({usedCount} other methods, all used).")
    return True
