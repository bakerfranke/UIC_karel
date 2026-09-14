"""Shared test support for CarpetBot - one function per gradable test case.
Each function below is independently callable (e.g. `from tests import
test_structure as test_passed` as a zyBooks test case's whole unitTestCode)."""
import inspect
import runpy
import karel.kareltestutils as test
import karel.robotutils as util
from karel.robota import UrRobot, East

CLASS_NAME = "CarpetBot"
SOLVING_METHOD = "carpetSmallRooms"
ROBOT_VAR = "carpee"

# Required starting (street, avenue, direction, beepers) - 8 possible rooms
# (avenues 2-9 inclusive), one beeper each, worst case all complete.
START_STATE = (1, 1, East, 8)

# Required ending (street, avenue, direction) - turnOff() is checked separately.
EXPECTED_END_STATE = (1, 10, East)

MODEL_FILE = "model_solution.py"
WORLD_FILES = [f"carpetbot_world{i}.kwld" for i in range(10)]

EXCLUDE_METHODS = {"turnRight", "turnAround"}
MIN_OTHER_METHODS = 3

EXPECTED_BEEPERS = 8


def _countCalledMethods(cls, methodNames):
    """Temporarily wraps each named method on cls to record whether it gets
    called during an isolated solving-method run, then restores the originals."""
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
        world.reset()
        world.readWorld(WORLD_FILES[0])
        bot = cls(*START_STATE)
        getattr(bot, SOLVING_METHOD)()
    except Exception:
        pass  # a crash here is covered by other tests - just use whatever ran before it
    finally:
        for name, original in originals.items():
            setattr(cls, name, original)

    return called


def test_structure(test_feedback):
    """Checks: no code outside the main guard, no while/for loops other than the
    allowed for-range form, CarpetBot exists and defines carpetSmallRooms(), no
    method calls the global robot instance by name instead of self, and at least
    MIN_OTHER_METHODS other methods that are both DEFINED and actually CALLED
    when carpetSmallRooms() runs on a fresh robot."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    try:
        namespace = runpy.run_path("main.py")
    except Exception as e:
        print(f"ERROR: main.py raised an exception: {e}")
        return False

    cls = namespace.get(CLASS_NAME)
    if cls is None:
        print(f"ERROR: could not find a class named {CLASS_NAME} in main.py.")
        return False

    if not test.testClassMethodExists(cls, SOLVING_METHOD):
        return False

    misuse = test.findGlobalInstanceMisuse("main.py", CLASS_NAME, ROBOT_VAR)
    if misuse:
        methodName, calledAttr, lineno = misuse[0]
        print(
            f"ERROR: line {lineno}: {methodName}() calls {ROBOT_VAR}.{calledAttr}() - "
            f"it should be self.{calledAttr}() instead. Using '{ROBOT_VAR}' directly "
            f"reaches for the specific robot you made in __main__, rather than whichever "
            f"robot the method is actually being called on - self is always the right one."
        )
        return False

    otherMethods = sorted(
        n for n, v in vars(cls).items()
        if not n.startswith('_') and inspect.isfunction(v)
        and n not in EXCLUDE_METHODS
    )
    print(f"{len(otherMethods)} other method(s) defined on {CLASS_NAME}: {otherMethods}")
    if len(otherMethods) < MIN_OTHER_METHODS:
        print(
            f"ERROR: {CLASS_NAME} should have at least {MIN_OTHER_METHODS} "
            f"methods besides {SOLVING_METHOD}() and {sorted(EXCLUDE_METHODS)} "
            f"(found {len(otherMethods)}). Break your solution down into smaller, reusable "
            f"pieces."
        )
        return False

    called = _countCalledMethods(cls, otherMethods)
    unused = [n for n in otherMethods if n not in called]
    print(f"Called while running {SOLVING_METHOD}(): {sorted(called)}")
    usedCount = len(otherMethods) - len(unused)
    if usedCount < MIN_OTHER_METHODS:
        print(
            f"ERROR: only {usedCount} of your other methods are actually called when "
            f"{SOLVING_METHOD}() runs (need at least {MIN_OTHER_METHODS}). "
            f"Defined but never used: {unused}. A method that's never called doesn't count "
            f"towards the requirement."
        )
        return False

    test_feedback.write(f"Class and method structure look good ({usedCount} other methods, all used).")
    return True


def test_solves_via_main(test_feedback):
    """Checks that running main.py as-is (python main.py) produces the correct
    final beeper layout, for every world file - not just one example."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    passed = test.runMultiWorldCompare(
        "main.py", MODEL_FILE, CLASS_NAME, WORLD_FILES, mode="main"
    )
    if not passed:
        return False

    test_feedback.write(f"main.py solves the problem correctly on all {len(WORLD_FILES)} world files!")
    return True


def test_solves_on_its_own(test_feedback):
    """Checks that calling carpetSmallRooms() directly on a fresh robot - bypassing
    main.py entirely - reaches the correct final beeper layout, for every world
    file. If this fails while test_solves_via_main passes, it usually means
    main.py is quietly doing some of the problem-solving itself instead of
    leaving it all to the solving method."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    passed = test.runMultiWorldCompare(
        "main.py", MODEL_FILE, CLASS_NAME, WORLD_FILES, mode="method",
        solving_method=SOLVING_METHOD, start_state=START_STATE
    )
    if not passed:
        print(
            f"Behind the scenes we constructed a fresh {CLASS_NAME} and called ONLY "
            f"{SOLVING_METHOD}() on it - bypassing your main block entirely. If your "
            f"main.py run passes but this doesn't, that means main is doing some of the work "
            f"itself instead of leaving it all to {SOLVING_METHOD}()."
        )
        return False

    test_feedback.write(f"{SOLVING_METHOD}() correctly solves the problem on its own, on all {len(WORLD_FILES)} world files!")
    return True


def test_ending_state(test_feedback):
    """Checks that carpee ends at the required (street, avenue, direction) and
    calls turnOff() by the end of main.py's run."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    namespace, _violations = test.runMainOnly("main.py")
    if namespace is None:
        return False

    robot = namespace.get(ROBOT_VAR)
    if robot is None:
        print(f"ERROR: main.py should create a {CLASS_NAME} instance named '{ROBOT_VAR}'.")
        return False

    finalTuple = util.getStatus(robot)[:3]
    if not test.testEquals(
        "Ending position/direction",
        f"Checking {ROBOT_VAR}'s final (street, avenue, direction)",
        finalTuple, EXPECTED_END_STATE
    ):
        return False

    if not test.testEquals(
        "Robot turned off",
        f"Checking {ROBOT_VAR}.isRunning() is False after {SOLVING_METHOD}()",
        robot.isRunning(), False
    ):
        print(f"ERROR: {ROBOT_VAR} should call turnOff() once the problem is solved.")
        return False

    test_feedback.write("Robot reached the correct ending state and turned off!")
    return True


def test_main_guard_purity(test_feedback):
    """Confirms __main__ does nothing except construct a single CarpetBot and
    call carpetSmallRooms() (turnOff() is fine too) - no extra problem-solving
    work hiding directly in main, and no extra robots constructed there either."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    if not test.checkSingleRobotInMain("main.py", CLASS_NAME):
        print(
            f"ERROR: __main__ should construct exactly one {CLASS_NAME}, "
            f"directly in __main__ - not zero, not more than one. (A robot your "
            f"{SOLVING_METHOD}() constructs on its own, internally, is fine "
            f"and doesn't count against this - this check only looks at what "
            f"__main__ itself constructs.)"
        )
        return False

    namespace, passed = test.testMainGuardPurity(
        "Main Guard Purity", "main.py", allowedMethods={SOLVING_METHOD, "turnOff"}
    )
    if not passed:
        return False

    test_feedback.write("main only constructs a single robot and orchestrates - no problem-solving work hidden there!")
    return True


def test_starting_state(test_feedback):
    """Checks that carpee starts at the required (street, avenue, direction) -
    beeper count is checked separately in test_starting_beeper_count."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    namespace, _violations = test.runMainOnly("main.py")
    if namespace is None:
        return False

    robot = namespace.get(ROBOT_VAR)
    if robot is None:
        print(f"ERROR: main.py should create a {CLASS_NAME} instance named '{ROBOT_VAR}'.")
        return False

    initial = util.getInitialState(robot)
    initialTuple = (initial.street(), initial.avenue(), initial.direction(), initial.beepers())
    if not test.testRobotEquals("Starting position/direction", initialTuple, START_STATE, ignore_beepers=True):
        return False

    test_feedback.write("Starting position and direction correct!")
    return True


def test_starting_beeper_count(test_feedback):
    """Checks that the TOTAL starting beeper count, summed across every robot
    instance constructed anywhere in main.py, equals EXPECTED_BEEPERS."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    passed = test.checkStartingBeeperCount("main.py", EXPECTED_BEEPERS)
    if not passed:
        return False

    test_feedback.write(f"Starts with exactly {EXPECTED_BEEPERS} beepers!")
    return True


def test_no_pickbeeper(test_feedback):
    """Checks that pickBeeper() is never called by any robot, of any class,
    anywhere in main.py - you're laying carpet, not removing it."""
    if not test.checkNoCodeOutsideMainGuard("main.py"):
        return False
    if not test.checkNoLoops("main.py"):
        return False

    passed = test.checkNoPickBeeperCalled("main.py")
    if not passed:
        return False

    test_feedback.write("pickBeeper() is never called - correct!")
    return True


if __name__ == "__main__":
    from io import StringIO
    for fn in [test_structure, test_solves_via_main, test_solves_on_its_own,
               test_ending_state, test_main_guard_purity, test_starting_state,
               test_starting_beeper_count, test_no_pickbeeper]:
        print(f"{fn.__name__}: {fn(StringIO())}")
