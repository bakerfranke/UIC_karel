# generic value v. expected test
from karel.robota import *
import karel.robotutils as util
from karel.code_parser import extract_method_headers_from_file
import ast
import inspect
import os
import runpy

def testEquals(test_name, test_desc, value, expected, verbose=True):
    result = True
    if value != expected:
        result = False
    
    # default show fail tests, but also 
    if result == False or verbose==True:
        print(getTestResultStr(test_name, test_desc, value, expected, result))
    
    return result

# use this to produce standard output string for a tests
def getTestResultStr(test_name, test_desc, value, expected, result):
    return  (
            f"{'-'*70}\n"
            f"TEST: {test_name}\n"
            f"{test_desc}\n"
            f"Your Robot: {value}\n"
            f"  Expected: {expected}\n"
            f"      Pass: {result}\n"
            )

# check two robot statuses ignoring beepers
# def testRobotEquals_ignoreBeepers(test_name, robot_status_tuple, expected_status_tuple, verbose=True):
#     test_desc = "Testing Robot Location and Direction (ignore beepers)"

#     street = robot_status_tuple[0] == expected_status_tuple[0]
#     ave = robot_status_tuple[1] == expected_status_tuple[1]
#     dir = robot_status_tuple[2] == expected_status_tuple[2]

#     result = street and ave and dir
#     if result == False or verbose == True:
#         print(getTestResultStr(test_name, 
#                             test_desc, 
#                             status_tuple_str(robot_status_tuple), 
#                             status_tuple_str(expected_status_tuple), 
#                             result))
#     return result

def testRobotEquals(test_name, robot_or_status, expected_status_tuple, ignore_beepers=False, at_least_beepers=False, verbose=True, ignore_direction=False):
    """
    Tests a robot's status (location, direction, beepers) against an expected status.

    :param test_name: Name of the test.
    :param robot_or_status: A robot object or a status tuple (street, ave, dir, beepers).
    :param expected_status_tuple: A status tuple (street, ave, dir, beepers) to compare against.
    :param ignore_beepers: If True, ignore the beeper count during comparison.
    :param atLeastBeepers: If True, pass if the robot has at least as many beepers as expected.
    :param verbose: If True, print detailed test results.
    :return: True if the test passes, False otherwise.
    """
    # use robot utils function which handles robot-to-tuple conversion
    result = util.robotEquals(robot_or_status, expected_status_tuple, ignoreBeepers=ignore_beepers, atLeastBeepers = at_least_beepers, ignoreDirection = ignore_direction)

    # Handle beeper comparison
    # test_desc = "Testing Robot Location, Direction, Beepers"
    # if ignore_beepers or ignore_direction:
    #     test_desc = f"Testing Robot Location{' (ignore Direction)' if ignore_direction else ', Direction'} {' (ignore beepers)' if ignore_beepers else ', Beepers'}"
    test_desc = f"Testing Robot Location{' (ignore Direction)' if ignore_direction else ', Direction'} {' (ignore beepers)' if ignore_beepers else ', Beepers'}"

    if at_least_beepers:
        test_desc = f"Testing Robot Location, Direction, (and at least {expected_status_tuple[3]} Beepers)"

    # Print results if needed
    if result == False or verbose:
        print(getTestResultStr(
            test_name,
            test_desc,
            status_tuple_str(robot_or_status),
            status_tuple_str(expected_status_tuple),
            result
        ))

    return result

# def testRobotEquals(test_name, robot_status_tuple, expected_status_tuple, atLeastBeepers=False, verbose=True):
#     test_desc = "Testing Robot Location, Direction"
#     beeps_result = False
#     if atLeastBeepers == True:
#         test_desc += ", (at least) Beepers."
#         beeps_result = robot_status_tuple[3] >= expected_status_tuple[3]
#     else:
#         test_desc += ", Beepers."   
#         beeps_result = robot_status_tuple[3] == expected_status_tuple[3]


#     loc_dir_result = (robot_status_tuple[0] == expected_status_tuple[0]
#                     and robot_status_tuple[1] == expected_status_tuple[1]
#                     and robot_status_tuple[2] == expected_status_tuple[2])
    
#     # if loc,dir and beeps_result are true we pass, otherwise fail
#     result = loc_dir_result and beeps_result

#     if result == False or verbose == True:
#         print(getTestResultStr(test_name,
#                             test_desc, 
#                             status_tuple_str(robot_status_tuple), 
#                             status_tuple_str(expected_status_tuple), 
#                             result))

#     return result

def status_tuple_str(robot_or_tup):
    if isinstance(robot_or_tup, UrRobot):
        tup = util.getStatus(robot_or_tup)
    else:
        tup = robot_or_tup
        
    if tup[2] == North:
        dirstr = "North"
    elif tup[2]==East:
        dirstr = "East"
    elif tup[2]==West:
        dirstr = "West"
    else:
        dirstr = "South"

    return f"(st: {tup[0]:2d}, ave: {tup[1]:2d}, dir: {dirstr:>5s}, beeps: {tup[3]})"

def testClassMethodExists(classname, expectedMethod, verbose=True):
    #expectedMethod = "MileWalker.turnRight()"
    hasMethod = f"Not defined <{expectedMethod}()> "

    if hasattr(classname, expectedMethod):
        hasMethod = expectedMethod+"()"
    
    result = testEquals(f"Method check",
                        f"Does {classname} defines method {expectedMethod}()?",
                        hasMethod,
                        expectedMethod+"()", verbose)
    return result

def checkClassAndMethodsExist(main_file, class_name, method_list, verbose=True):
    """Runs main_file, finds class_name in it, and checks that every method in
    method_list exists on it - via testClassMethodExists() for each one. Use
    this as an early guard at the top of a test's test_passed(), before
    anything else tries to construct or run the class."""
    try:
        namespace = runpy.run_path(main_file)
    except Exception as e:
        print(f"ERROR: {main_file} raised an exception: {e}")
        return False

    cls = namespace.get(class_name)
    if cls is None:
        print(f"ERROR: could not find a class named {class_name} in {main_file} - did you rename or remove it?")
        return False

    for m in method_list:
        if not testClassMethodExists(cls, m, verbose=False):
            print(f"Your class should contain the following method(s): {method_list}")
            print(f"Your code is missing: {m} - did you change it or delete it?")
            return False

    return True

def checkMethodCount(main_file, class_name, required_method_headers, min_total_methods, verbose=True):
    """Static check (no code runs) that class_name in main_file defines at
    least min_total_methods methods total, and that every header string in
    required_method_headers (e.g. 'def runRace(self):') is among them. Uses
    extract_method_headers_from_file() - a pure header count, not a check that
    the methods are actually called (see runRobotChecklist's min_methods /
    the "defined AND called" pattern used elsewhere for that stricter check)."""
    methods = extract_method_headers_from_file(
        main_file,
        class_filter={class_name},
        include_dunder=False,
        include_private=False,
    )

    print("-" * 30)
    print(f"Inspecting code in {main_file}:\n{len(methods)} methods found in class {class_name}:")
    required_count = 0
    for i, m in enumerate(methods, start=1):
        checkmark = " ✅" if m.header in required_method_headers else ""
        if checkmark:
            required_count += 1
        print(f"{i}. line {m.lineno}: {m.header}{checkmark}")

    has_required_num_methods = len(methods) >= min_total_methods
    has_required_named_methods = required_count == len(required_method_headers)

    num_status = "✅" if has_required_num_methods else f"❌ expected ≥{min_total_methods} methods - found {len(methods)}."
    req_status = "✅" if has_required_named_methods else f"❌\n\tYour code is missing one of these: {required_method_headers}"
    print("-" * 30)
    print(f"Test: required number of methods? {num_status}")
    print(f"Test: required methods present? {req_status}")

    return has_required_num_methods and has_required_named_methods

def testWorldEquals(test_name, robot_world:RobotWorld, world_kwld_file:str):
    diffs = util.get_world_diffs_from_file(robot_world, world_kwld_file)
    
    display_str = (f"{'-'*70}\n"
                  f"TEST: {test_name}")
    display_str += "\nComparing beeper locations and counts in your world v. expected\n"

    if diffs['diffs'] == True:
        display_str += (
            f"   Num beepers found: {diffs['num_beepers_in_world']}\n"
            f"Num beepers expected: {diffs['num_beepers_expected']}\n"
            "DIFFERENCES...\n"
            f"{diffs['allbeeperdiffs']}"
            f"\n"
            f"CORRECT Beeper Placements: {diffs['correct_matches']}"
        )
    else:
        display_str += "RESULT: Your world matches expected world! (Yay)"

    print(display_str)
    return diffs['diffs']==False

def runMainOnly(mainFilePath, exemptActions=None, allowedMethods=None):
    """Run a student's main.py the same way `python main.py` would - respecting
    `if __name__ == "__main__":` - while watching for robot work happening directly
    in that top-level main block, rather than from inside a method defined on the
    robot's own class.

    This catches students who "helped" an incomplete class method along by adding
    extra work in main - the end state can come out looking right by luck without
    the assignment's one designated solving method actually solving the whole
    problem on its own.

    Two ways to call this, depending on how precise a check you need:

    - allowedMethods=None (default): flags any primitive action (move, turnLeft,
      pickBeeper, etc.) called directly from main. This misses a student who wraps
      the extra work in a method of their own (main.py calling robot.extraHelper(),
      which itself calls move() - the caller of move() is extraHelper's own frame,
      not main's, so it looks legitimate under this check alone).
    - allowedMethods={"harvestBeeperField", "turnOff"} (a set of method names):
      for every primitive action, walks up to find the OUTERMOST robot-method call
      that main made directly, and flags it unless its name is in this set. This
      catches the case above too, since the outermost direct-from-main call would
      be extraHelper(), which isn't in the allowed set - regardless of how deep the
      actual move()/pickBeeper() call is nested beneath it.

    Returns (namespace, violations):
      namespace  - the dict of globals from the executed file, e.g. namespace['harvey']
                   (same thing `main.harvey` would have given you with `import main`)
      violations - list of human-readable strings, one per offending call.
                   An empty list means main only orchestrated - the intended style.

    exemptActions (only used when allowedMethods is None) defaults to just turnOff -
    ending a program with robot.turnOff() directly in main is normal and expected,
    not a violation. Robot creation itself never reaches this check (it doesn't
    route through _perform_action).

    Forces headless mode before running, regardless of what the student's own main.py
    sets (world.setSize()/setDelay()/etc. are for a human watching it run) - a real
    animated run at the student's own delay would make grading needlessly slow.
    """
    mainFilePath = os.path.abspath(mainFilePath)
    if exemptActions is None:
        exemptActions = {UrRobot.turnOffAction}

    UrRobot.use_graphics(False)

    violations = []
    flaggedMethods = set()  # avoid one violation line per action inside the same bad call
    original = UrRobot._perform_action

    def _instrumented(self, action, *args, **kwargs):
        actionFrame = inspect.currentframe().f_back  # the move()/turnLeft()/etc. frame

        if allowedMethods is not None:
            # Walk up to the OUTERMOST robot-method frame that main called directly,
            # however deep the actual action is nested beneath it.
            frame = actionFrame
            while frame is not None:
                caller = frame.f_back
                if (caller is not None and caller.f_code.co_filename == mainFilePath
                        and caller.f_code.co_name == '<module>'):
                    methodName = frame.f_code.co_name
                    if methodName not in allowedMethods and methodName not in flaggedMethods:
                        flaggedMethods.add(methodName)
                        violations.append(
                            f"{methodName}() was called directly in your __main__ block "
                            f"(line {caller.f_lineno}) - __main__ should only call "
                            f"{' or '.join(sorted(allowedMethods))}, with all the "
                            f"actual problem-solving happening inside your class's "
                            f"own methods."
                        )
                    break
                frame = caller
        else:
            callerFrame = actionFrame.f_back if actionFrame else None  # whoever called that action method
            if (action not in exemptActions and callerFrame is not None
                    and callerFrame.f_code.co_filename == mainFilePath
                    and callerFrame.f_code.co_name == '<module>'):
                violations.append(
                    f"{actionFrame.f_code.co_name}() was called directly in your __main__ "
                    f"block (line {callerFrame.f_lineno}), not from inside a method - "
                    f"your class method(s) should be doing this work, not __main__."
                )
        return original(self, action, *args, **kwargs)

    UrRobot._perform_action = _instrumented
    original_sleep = UrRobot.sleep
    # UrRobot.sleep() does a real time.sleep(world.delay()/100.0) regardless of
    # graphics/headless mode - so the student's own world.setDelay(...) call (meant to
    # pace an animation for a human) would otherwise make every action in this run
    # actually wait in real time. Neutralize it for the duration of this run.
    UrRobot.sleep = lambda self: None
    try:
        namespace = runpy.run_path(mainFilePath, run_name="__main__")
    except Exception as e:
        # An uncaught crash left main.py's process-wide "paused, waiting for a Run
        # click that will never come" state set - letting that exception keep
        # propagating uncaught up through the caller hangs the grading run instead of
        # just failing it. Report it and return cleanly instead.
        print(f"ERROR: your main.py raised an exception instead of completing: {e}")
        return None, violations
    finally:
        UrRobot._perform_action = original
        UrRobot.sleep = original_sleep

    return namespace, violations

def testMainGuardPurity(test_name, mainFilePath, exemptActions=None, allowedMethods=None, verbose=True):
    """Wraps runMainOnly() in the same print-a-block-every-time style as testEquals().
    Returns True (and the namespace of globals from main.py) if main.py's
    `if __name__ == "__main__":` block never called a robot action directly (or, if
    allowedMethods is given, never called any robot method other than the ones
    listed - see runMainOnly's docstring for the difference) - False (with the
    namespace still returned, since main did run) otherwise."""
    namespace, violations = runMainOnly(mainFilePath, exemptActions, allowedMethods)
    if namespace is None:  # main.py crashed - already reported by runMainOnly
        return None, False
    result = len(violations) == 0

    display_str = (
        f"{'-'*70}\n"
        f"TEST: {test_name}\n"
        f"Checking that __main__ only creates the robot and calls its own methods "
        f"(no problem-solving work directly in __main__)\n"
    )
    if result:
        display_str += "RESULT: __main__ only orchestrated - no direct action calls found! (Yay)\n"
    else:
        display_str += "PROBLEMS FOUND in your __main__ block:\n" + "\n".join(f"  - {v}" for v in violations) + "\n"
    display_str += f"      Pass: {result}"

    if result == False or verbose == True:
        print(display_str)

    return namespace, result

def findGlobalInstanceMisuse(main_file, class_name, robot_var):
    """Static check (no code runs) for a common novice mistake: a method that
    calls robot_var.something() instead of self.something() - reaching for the
    global instance from main by name, rather than the instance the method is
    actually being called on.

    This is easy to miss by eye because it *works* when the program is simply
    run: main.py's own robot_var already exists as a global by the time any
    method executes, so Python happily resolves it. It falls apart the moment
    the method is called on a different instance (a second robot of the same
    class, or a grader constructing its own fresh instance to test the method
    in isolation) - the method keeps operating on the original global instead
    of self, which is exactly the kind of bug that "sometimes" passes and
    "sometimes" doesn't, depending on what state that original happens to be
    in when the method runs.

    Returns a list of (methodName, calledAttr, lineNumber) tuples - one per
    robot_var.calledAttr() call found inside a method of class_name. Empty
    list means none found (or the file couldn't be parsed - a syntax error
    there will already have been reported elsewhere).
    """
    try:
        tree = ast.parse(open(main_file).read(), filename=main_file)
    except Exception:
        return []

    offenses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    for sub in ast.walk(item):
                        if (isinstance(sub, ast.Attribute)
                                and isinstance(sub.value, ast.Name)
                                and sub.value.id == robot_var):
                            offenses.append((item.name, sub.attr, sub.lineno))
    return offenses

def findExecutableCodeOutsideMainGuard(main_file):
    """Static check (no code runs) for executable statements sitting at module
    level in main.py, outside both any class/function definition and the
    `if __name__ == "__main__":` block - a common mistake where code meant to be
    inside the guard gets left un-indented by accident, e.g.:

        if __name__ == "__main__":
            world.readWorld("garden_walls.kwld")

        gardy = GardenerBot(1, 2, North, 80)   # <- accidentally outside the guard
        gardy.plantAllFlowers()

    This kind of code runs unconditionally every time the file is imported or
    inspected - not just when a student clicks Run - since Python executes
    module-level code regardless of __name__. That means it also runs during
    every test that so much as imports the file to look at the class, often
    more than once across different tests. Depending on what the code
    constructs, that can silently double up world state (a second, real
    plantAllFlowers() run stacking beepers on top of a test's own isolated
    run) or attempt to open a real graphics window on a headless grading
    server (a crash, or - since a robot being constructed also registers a
    "keep the window open" exit hook - a hang, waiting for a window nobody
    is there to close).

    Returns a list of (lineno, source_snippet) tuples, one per offending
    top-level statement. Empty list means main.py is structured correctly (or
    couldn't be parsed - a syntax error there is already reported elsewhere).
    """
    try:
        source = open(main_file).read()
        tree = ast.parse(source, filename=main_file)
    except Exception:
        return []

    def isMainGuard(node):
        if not isinstance(node, ast.If):
            return False
        test = node.test
        if not (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)):
            return False
        operands = [test.left] + list(test.comparators)
        names = [o.id for o in operands if isinstance(o, ast.Name)]
        strings = [o.value for o in operands if isinstance(o, ast.Constant) and isinstance(o.value, str)]
        return '__name__' in names and '__main__' in strings

    def isDocstring(node):
        return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str))

    offenses = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef)):
            continue
        if isDocstring(node) or isMainGuard(node):
            continue
        snippet = ast.get_source_segment(source, node) or ""
        snippet = snippet.strip().splitlines()[0] if snippet.strip() else "(code)"
        offenses.append((node.lineno, snippet))
    return offenses

def checkNoCodeOutsideMainGuard(main_file="main.py"):
    """Convenience wrapper around findExecutableCodeOutsideMainGuard() for use as
    an early guard at the very top of a test's test_passed() - before running
    main.py in any way. Prints a clear explanation and returns False if a
    problem is found; returns True (silently) otherwise."""
    offenses = findExecutableCodeOutsideMainGuard(main_file)
    if not offenses:
        return True
    print(
        f'ERROR: {main_file} has code outside both your class definition(s) and '
        f'the `if __name__ == "__main__":` guard:'
    )
    for lineno, snippet in offenses:
        print(f"  line {lineno}: {snippet}")
    print(
        "This code runs every time the file is imported or inspected - not just "
        "when you click Run - which can cause confusing test failures (like "
        'beepers appearing doubled, or crashes/hangs trying to open a graphics '
        'window during grading). Move this code inside the '
        '`if __name__ == "__main__":` block, indented to match the other lines '
        "already there."
    )
    return False

def _isAllowedRangeFor(node):
    """True if this ast.For node is exactly `for <var> in range(<int>):` - one
    positional argument, no keywords, no starred args - the only for-loop shape
    allowed in this project (repeat something a fixed number of times). Any
    other iterable (a list, range() with start/stop/step, enumerate(), etc.)
    returns False."""
    call = node.iter
    if not isinstance(call, ast.Call):
        return False
    if not (isinstance(call.func, ast.Name) and call.func.id == "range"):
        return False
    if call.keywords:
        return False
    if len(call.args) != 1:
        return False
    if any(isinstance(a, ast.Starred) for a in call.args):
        return False
    return True

def findLoopUsage(main_file):
    """Static check (no code runs) for disallowed loops anywhere in the file -
    `while` loops are never allowed; `for` loops are only allowed in the exact
    shape `for <var> in range(<int>):` (repeating something a fixed number of
    times) - any other for-loop shape (over a list, range() with start/stop/
    step, enumerate(), etc.) is flagged too. Walks the whole file, not just
    module level, so a loop hidden inside a method is caught.

    Returns a list of (lineno, kind, source_snippet) tuples, kind being "while"
    or "for". Empty list means no disallowed loop was found (or the file
    couldn't be parsed - a syntax error there is already reported elsewhere)."""
    try:
        source = open(main_file).read()
        tree = ast.parse(source, filename=main_file)
    except Exception:
        return []

    offenses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            kind = "while"
        elif isinstance(node, ast.For):
            if _isAllowedRangeFor(node):
                continue
            kind = "for"
        else:
            continue
        snippet = ast.get_source_segment(source, node) or ""
        snippet = snippet.strip().splitlines()[0] if snippet.strip() else "(loop)"
        offenses.append((node.lineno, kind, snippet))
    return offenses

def checkNoLoops(main_file="main.py"):
    """Convenience wrapper around findLoopUsage() for use as an early guard at
    the top of a test's test_passed(). `while` loops are never allowed; `for`
    loops are only allowed as `for <var> in range(<int>):` (a fixed repeat
    count) - using one isn't required, just permitted. Prints a clear
    explanation and returns False if a disallowed loop is found anywhere in
    the file; returns True (silently) otherwise."""
    offenses = findLoopUsage(main_file)
    if not offenses:
        return True
    print(f"ERROR: {main_file} uses a loop that isn't allowed in this project:")
    for lineno, kind, snippet in offenses:
        print(f"  line {lineno} ({kind} loop): {snippet}")
    kinds = {kind for _lineno, kind, _snippet in offenses}
    if "while" in kinds:
        print(
            "`while` loops are not allowed in this project - replace this with a "
            "bounded sequence of if-statements, or a `for <var> in range(<int>):` "
            "loop if you just need to repeat something a fixed number of times."
        )
    if "for" in kinds:
        print(
            "Use of a for loop, but for this project we're only using the form "
            "that lets you repeat an instruction a certain number of times: "
            "`for <var> in range(<int>):`. Any other for-loop form (looping over "
            "a list, range() with a start/stop/step, enumerate(), etc.) isn't "
            "allowed here."
        )
    return False

def runMainInstrumented(main_file):
    """Like runMainOnly(), but for assignments where students may construct as
    many robots (of as many classes) as they like, so a check can't just look
    up one exact variable name in the namespace. Tracks every UrRobot (or
    subclass) instance constructed during the run, each one's beeper count at
    construction time, and every pickBeeper() call made by any of them -
    regardless of which class or variable is involved.

    Forces headless mode and neutralizes UrRobot.sleep() the same way
    runMainOnly() does.

    Returns (namespace, instances, initialBeeperCounts, pickBeeperCalls, topLevelFlags):
      instances            - every UrRobot (or subclass) instance constructed,
                              in construction order.
      initialBeeperCounts  - parallel list of ints, the beepers argument each
                              one was constructed with (an unlimited/infinity
                              count is reported as -1, since it can't be summed
                              meaningfully with a finite total).
      pickBeeperCalls      - one human-readable string per pickBeeper() call
                              made anywhere during the run, by any instance.
      topLevelFlags        - parallel list of bools, one per entry in
                              instances - True if that robot was constructed
                              directly at module level in main_file (i.e. from
                              __main__ itself, not from inside a method).

    namespace is None (with the other lists whatever was captured before the
    crash) if main.py raised an exception instead of completing.
    """
    mainFilePath = os.path.abspath(main_file)
    UrRobot.use_graphics(False)

    instances = []
    initialBeeperCounts = []
    pickBeeperCalls = []
    topLevelFlags = []

    originalInit = UrRobot.__init__
    def _instrumentedInit(self, *args, **kwargs):
        originalInit(self, *args, **kwargs)
        instances.append(self)
        count = self._UrRobot__beepers
        initialBeeperCounts.append(-1 if count == infinity else count)
        # Robot.__init__ calls UrRobot.__init__(self, ...) directly rather than
        # via super() - so for a Robot subclass, the immediate caller of this
        # patched UrRobot.__init__ is Robot.__init__'s own frame, not whatever
        # called TinyBot(...). Walk past any chain of __init__ frames (however
        # many levels of subclassing are involved) to find the real caller.
        callerFrame = inspect.currentframe().f_back
        while callerFrame is not None and callerFrame.f_code.co_name == '__init__':
            callerFrame = callerFrame.f_back
        topLevelFlags.append(
            callerFrame is not None
            and callerFrame.f_code.co_filename == mainFilePath
            and callerFrame.f_code.co_name == '<module>'
        )

    originalPerform = UrRobot._perform_action
    def _instrumentedPerform(self, action, *args, **kwargs):
        if action == UrRobot.pickBeeperAction:
            pickBeeperCalls.append(f"{type(self).__name__} instance called pickBeeper()")
        return originalPerform(self, action, *args, **kwargs)

    UrRobot.__init__ = _instrumentedInit
    UrRobot._perform_action = _instrumentedPerform
    original_sleep = UrRobot.sleep
    UrRobot.sleep = lambda self: None
    try:
        namespace = runpy.run_path(mainFilePath, run_name="__main__")
    except Exception as e:
        print(f"ERROR: your main.py raised an exception instead of completing: {e}")
        return None, instances, initialBeeperCounts, pickBeeperCalls, topLevelFlags
    finally:
        UrRobot.__init__ = originalInit
        UrRobot._perform_action = originalPerform
        UrRobot.sleep = original_sleep

    return namespace, instances, initialBeeperCounts, pickBeeperCalls, topLevelFlags

def checkSingleRobotInMain(main_file, class_name, verbose=True):
    """Checks that __main__ constructs exactly one robot - directly at module
    level in main_file, not from inside a method - and that it's an instance
    of class_name. Meant to pair with testMainGuardPurity(): together they
    cover "main should do nothing except construct a single <class_name> and
    call <solving_method>()." A robot constructed inside a method (e.g. a
    helper robot sortBeepers() itself spins up) doesn't count against this -
    only what __main__ directly constructs matters here."""
    namespace, instances, _counts, _picks, topLevelFlags = runMainInstrumented(main_file)
    if namespace is None:
        return False

    topLevelInstances = [inst for inst, isTop in zip(instances, topLevelFlags) if isTop]
    result = len(topLevelInstances) == 1 and isinstance(topLevelInstances[0], namespace.get(class_name) or ())
    display_str = (
        f"{'-'*70}\n"
        f"TEST: __main__ constructs a single {class_name}\n"
        f"Robot(s) constructed directly in __main__: {len(topLevelInstances)} "
        f"({[type(r).__name__ for r in topLevelInstances]})\n"
        f"                 Pass: {result}"
    )
    if result == False or verbose == True:
        print(display_str)
    return result

def checkStartingBeeperCount(main_file, expected_total, verbose=True):
    """Runs main.py and checks that the TOTAL beeper count, summed across every
    UrRobot (or subclass) instance constructed anywhere in the run, equals
    expected_total. Works no matter how many robots or classes the student
    uses - only the grand total is checked."""
    namespace, instances, counts, _pickBeeperCalls, _topLevelFlags = runMainInstrumented(main_file)
    if namespace is None:
        return False

    if not instances:
        print(f"ERROR: no robot instances were constructed while running {main_file}.")
        return False

    if -1 in counts:
        print(
            f"ERROR: one of your robots was constructed with an unlimited (infinite) "
            f"beeper count. This assignment requires an exact starting total of "
            f"{expected_total} beepers, so every robot needs a specific, finite count."
        )
        return False

    total = sum(counts)
    result = total == expected_total
    display_str = (
        f"{'-'*70}\n"
        f"TEST: Starting beeper count\n"
        f"Robot(s) constructed: {len(instances)}, beeper count(s): {counts}\n"
        f"        Total beepers: {total}\n"
        f"             Expected: {expected_total}\n"
        f"                 Pass: {result}"
    )
    if result == False or verbose == True:
        print(display_str)
    return result

def checkNoPickBeeperCalled(main_file, verbose=True):
    """Runs main.py and checks that pickBeeper() was never called, by any
    robot, of any class, anywhere in the run."""
    namespace, _instances, _counts, pickBeeperCalls, _topLevelFlags = runMainInstrumented(main_file)
    if namespace is None:
        return False

    result = len(pickBeeperCalls) == 0
    if not result:
        print(
            f"ERROR: pickBeeper() was called {len(pickBeeperCalls)} time(s) during your "
            f"run, but this assignment should never need to pick a beeper back up - "
            f"you're placing beepers, not removing them. Calling pickBeeper() anywhere "
            f"is a sign your approach has gone sideways somewhere."
        )
    elif verbose:
        print("pickBeeper() was never called - correct!")
    return result

def runMultiWorldCompare(main_file, model_file, class_name, world_files, mode,
                          solving_method=None, start_state=None, verbose=True):
    """Runs main_file against every world file in world_files, comparing the
    resulting world beeper layout to a live run of model_file done the same
    way on the same world file. Reports the first world file where they
    diverge, in enough detail to reproduce and debug it; returns True only if
    every world file matches.

    mode="main": runs the whole file each time (via its own `__main__` guard,
        same as `python main.py` would) - no start_state needed, since
        main_file/model_file each construct their own robot(s) however they
        like.
    mode="method": constructs a fresh class_name(*start_state) instance
        directly, bypassing __main__ entirely, and calls solving_method() on
        it - start_state and solving_method are both required for this mode.

    Forces headless mode and fully resets the world (world.reset(), which
    clears beepers, walls, and robots) before every single load, so state from
    one file or run can never leak into the next.
    """
    world = UrRobot.use_graphics(False)

    def _loadWorld(world_file):
        world.reset()
        world.setTrace(False)
        world.readWorld(world_file)

    def _runViaMain(file_path):
        # _loadWorld() already loaded the intended world_file just before this
        # call. But main_file/model_file each hardcode their own readWorld()
        # call inside __main__ (every project's starter template does this) -
        # and since readWorld() is additive rather than replacing, letting that
        # hardcoded call run for real would pile whatever file THEY happen to
        # name on top of the world_file this iteration is actually testing,
        # regardless of which of the 10 world_files we're nominally on. Neutralize
        # it for the duration of this run so the already-loaded world_file sticks.
        original_readWorld = world.readWorld
        world.readWorld = lambda *args, **kwargs: None
        try:
            namespace, _violations = runMainOnly(file_path)
        finally:
            world.readWorld = original_readWorld
        return namespace

    def _runViaMethod(file_path):
        try:
            namespace = runpy.run_path(file_path)
        except Exception as e:
            print(f"ERROR: could not run {file_path}: {e}")
            return None
        cls = namespace.get(class_name)
        if cls is None:
            print(f"ERROR: could not find a class named {class_name} in {file_path}.")
            return None
        original_sleep = UrRobot.sleep
        UrRobot.sleep = lambda self: None
        try:
            r = cls(*start_state)
            getattr(r, solving_method)()
        except Exception as e:
            print(f"ERROR: calling {solving_method}() from {file_path} raised an exception: {e}")
            return None
        finally:
            UrRobot.sleep = original_sleep
        return namespace

    runFile = _runViaMain if mode == "main" else _runViaMethod

    for world_file in world_files:
        _loadWorld(world_file)
        if runFile(model_file) is None:
            print(f"ERROR: the model solution itself failed on {world_file} - check with your instructor.")
            return False
        expectedBeepers = dict(world.getAllBeepers())

        _loadWorld(world_file)
        if runFile(main_file) is None:
            return False  # already reported by runFile
        actualBeepers = dict(world.getAllBeepers())

        diffs = util.get_beeper_diffs(actualBeepers, expectedBeepers)
        if diffs['diffs']:
            print(
                f"{'-'*70}\n"
                f"TEST: World file {world_file}\n"
                f"Your result doesn't match the model solution on this world file.\n"
                f"   Num beepers found: {diffs['num_beepers_in_world']}\n"
                f"Num beepers expected: {diffs['num_beepers_expected']}\n"
                f"DIFFERENCES...\n{diffs['allbeeperdiffs']}\n"
                f"Try re-running your program using {world_file} directly to see what happened."
            )
            return False
        if verbose:
            print(f"World file {world_file}: matches model solution. (Yay)")

    return True

def describePathDivergence(studentHistory, modelHistory):
    """Compares the (street, avenue) path implied by two RobotState histories
    (as returned by util.getStateHistory()) - ignoring direction, beepers, and
    exactly how many turns/actions it took to get there, so a student who
    solves it with a different (but equally correct) sequence of turns still
    matches. Returns None if the paths match exactly, or a detail string
    describing where and how they first diverge otherwise."""
    studentPath = [(s.street(), s.avenue()) for s in studentHistory]
    modelPath = [(s.street(), s.avenue()) for s in modelHistory]
    if studentPath == modelPath:
        return None

    detail = f"Paths diverge - yours has {len(studentPath)} step(s), model has {len(modelPath)}."

    # Find the first index where the two actually differ, so far as both have a
    # step to compare - if they agree everywhere they overlap, the "divergence"
    # is really just one path continuing past where the other stopped, so treat
    # right-after-the-last-shared-step as where they diverge.
    minLen = min(len(studentPath), len(modelPath))
    divergeAt = next((i for i in range(minLen) if studentPath[i] != modelPath[i]), minLen)

    if divergeAt > 0:
        lastShared = studentHistory[divergeAt - 1]
        detail += (f"\nStep {divergeAt - 1} (last step you both agree on): "
                   f"{status_tuple_str((lastShared.street(), lastShared.avenue(), lastShared.direction(), lastShared.beepers()))}")

    if divergeAt < len(studentHistory):
        yours = studentHistory[divergeAt]
        detail += (f"\nStep {divergeAt} (yours): "
                   f"{status_tuple_str((yours.street(), yours.avenue(), yours.direction(), yours.beepers()))}")
    else:
        detail += f"\nStep {divergeAt}: your path ended here."

    if divergeAt < len(modelHistory):
        models = modelHistory[divergeAt]
        detail += (f"\nStep {divergeAt} (model): "
                   f"{status_tuple_str((models.street(), models.avenue(), models.direction(), models.beepers()))}")
    else:
        detail += f"\nStep {divergeAt}: the model solution's path ended here."

    return detail

def runMultiWorldPathCompare(main_file, model_file, class_name, world_files, mode,
                              solving_method=None, start_state=None, robot_var=None,
                              verbose=True):
    """Like runMultiWorldCompare(), but compares the (street, avenue) PATH each
    robot follows - via describePathDivergence() - rather than the final
    world's beeper layout. Useful when matching the final state alone isn't
    precise enough (e.g. "total beepers reaches 0" doesn't prove they were
    picked up along the right route) - the two paths don't need the same total
    number of actions (turns don't move the robot, so they're naturally
    invisible to a path comparison), just the same sequence of corners visited.

    mode="main": runs the whole file each time (via its own `__main__` guard,
        same as `python main.py` would). Since main_file/model_file each
        construct their own robot(s) however they like, robot_var names the
        global variable holding the robot to check (e.g. "hurley") - if left
        as None, the single UrRobot (or subclass) instance found in the
        namespace is used, which only works when exactly one robot is
        constructed.
    mode="method": constructs a fresh class_name(*start_state) instance
        directly, bypassing __main__ entirely, and calls solving_method() on
        it - start_state and solving_method are both required for this mode.

    Forces headless mode and fully resets the world before every single load.
    """
    world = UrRobot.use_graphics(False)

    def _loadWorld(world_file):
        world.reset()
        world.setTrace(False)
        world.readWorld(world_file)

    def _findRobot(namespace):
        if robot_var is not None:
            robot = namespace.get(robot_var)
            if robot is None:
                print(f"ERROR: could not find a robot named '{robot_var}' in the namespace.")
            return robot
        candidates = [v for v in namespace.values() if isinstance(v, UrRobot)]
        if len(candidates) != 1:
            print(
                f"ERROR: expected exactly one robot instance in __main__ to check the path "
                f"of, found {len(candidates)}. Pass robot_var to disambiguate."
            )
            return None
        return candidates[0]

    def _runViaMain(file_path):
        namespace, _violations = runMainOnly(file_path)
        if namespace is None:
            return None
        return _findRobot(namespace)

    def _runViaMethod(file_path):
        try:
            namespace = runpy.run_path(file_path)
        except Exception as e:
            print(f"ERROR: could not run {file_path}: {e}")
            return None
        cls = namespace.get(class_name)
        if cls is None:
            print(f"ERROR: could not find a class named {class_name} in {file_path}.")
            return None
        original_sleep = UrRobot.sleep
        UrRobot.sleep = lambda self: None
        try:
            r = cls(*start_state)
            getattr(r, solving_method)()
        except Exception as e:
            print(f"ERROR: calling {solving_method}() from {file_path} raised an exception: {e}")
            return None
        finally:
            UrRobot.sleep = original_sleep
        return r

    runFile = _runViaMain if mode == "main" else _runViaMethod

    for world_file in world_files:
        _loadWorld(world_file)
        modelRobot = runFile(model_file)
        if modelRobot is None:
            print(f"ERROR: the model solution itself failed on {world_file} - check with your instructor.")
            return False
        modelHistory = util.getStateHistory(modelRobot)

        _loadWorld(world_file)
        studentRobot = runFile(main_file)
        if studentRobot is None:
            return False  # already reported by runFile
        studentHistory = util.getStateHistory(studentRobot)

        divergence = describePathDivergence(studentHistory, modelHistory)
        if divergence:
            print(
                f"{'-'*70}\n"
                f"TEST: World file {world_file} - path check\n"
                f"Your robot's path doesn't match the model solution's on this world file.\n"
                f"{divergence}\n"
                f"Try re-running your program using {world_file} directly to see what happened."
            )
            return False
        if verbose:
            print(f"World file {world_file}: path matches model solution. (Yay)")

    return True

def checkBeeperConservation(main_file, world_files, class_name, solving_method, start_state, verbose=True):
    """For each world file, checks that calling solving_method() on a fresh
    class_name(*start_state) instance doesn't change the TOTAL number of
    beepers anywhere in the world - for assignments that only rearrange
    existing beepers (like sorting them) rather than adding or removing any.

    Deliberately bypasses main_file's own `if __name__ == "__main__":` guard
    (the same way runMultiWorldCompare's mode="method" does) rather than
    using runMainOnly() - every project's main.py hardcodes its own
    readWorld() call inside that guard, and since readWorld() is additive
    (it adds to whatever's already there, rather than clearing first), letting
    that guard run would silently add main.py's own hardcoded world on top of
    whichever world_file this function just loaded, corrupting the "before"
    count this check depends on.

    Forces headless mode and fully resets the world before each world file."""
    world = UrRobot.use_graphics(False)
    for world_file in world_files:
        world.reset()
        world.setTrace(False)
        world.readWorld(world_file)
        before = sum(world.getAllBeepers().values())

        try:
            namespace = runpy.run_path(main_file)
        except Exception as e:
            print(f"ERROR: could not import {main_file}: {e}")
            return False
        cls = namespace.get(class_name)
        if cls is None:
            print(f"ERROR: could not find a class named {class_name} in {main_file}.")
            return False
        original_sleep = UrRobot.sleep
        UrRobot.sleep = lambda self: None
        try:
            bot = cls(*start_state)
            getattr(bot, solving_method)()
        except Exception as e:
            print(f"ERROR: calling {solving_method}() raised an exception: {e}")
            return False
        finally:
            UrRobot.sleep = original_sleep

        after = sum(world.getAllBeepers().values())

        if before != after:
            print(
                f"{'-'*70}\n"
                f"TEST: Beeper conservation - {world_file}\n"
                f"Beepers before running your program: {before}\n"
                f" Beepers after running your program: {after}\n"
                f"Your program should only rearrange beepers, never add or remove them - "
                f"check for a stray putBeeper() or pickBeeper() that isn't paired correctly. "
                f"Try re-running your program using {world_file} directly to see what happened."
            )
            return False
        if verbose:
            print(f"World file {world_file}: beeper count conserved ({before}). (Yay)")
    return True

def runRobotChecklist(class_name, robot_var, start_state, end_state, min_methods,
                       solving_method=None, model_file=None, world_setup=None,
                       main_file="main.py"):
    """Runs main.py once and walks a fixed checklist, in order, stopping at the
    first failure (later items are simply never attempted/printed):

      1. Program runs without crashing
      2. Class <class_name> exists
      3. Robot named <robot_var> was created in main
      4. No method calls <robot_var>.something() instead of self.something() -
         a common mistake (reaching for the global instance from main instead
         of the instance the method's actually being called on) that runs fine
         normally but breaks unpredictably once a method is called on any other
         instance, including the fresh one the checks below construct.
      5. Starting state matches start_state
      6. Ending state matches end_state
      7. Class defines at least min_methods of its own methods
      8. (only if solving_method is given) solving_method() reaches end_state
         all on its own, called directly on a fresh instance - main.py's overall
         run already reached the right answer (step 6 passed), so if the
         designated method *alone* doesn't get there too, that's proof main.py
         has extra work of its own propping the result up instead of leaving it
         all to that one method.
      9. (only if model_file is also given) that same isolated run's path
         matches the model solution's, called the same way.

    start_state/end_state are (street, avenue, direction, beepers) tuples, same
    shape as testRobotEquals() expects.

    solving_method is the name of the one method the assignment says should
    solve the whole problem (e.g. "harvestBeeperField") - required for checks 7
    and 8, skipped (with no line printed) if left as None. model_file additionally
    requires solving_method, and compares against a model solution's path instead
    of just its end state.

    world_setup, if given, is a one-argument callable (world_setup(world))
    invoked before each isolated run (checks 7 and 8) for problems that need
    e.g. world.readWorld(...) first - main.py's own run already handles its own
    world setup via step 1, so this is only needed for the isolated calls, which
    construct a fresh instance directly rather than running main.py's guard.

    Returns (passed, lines) - lines is a list of already-formatted checklist
    strings ('  [OK] ...' / '  [X ] ...' plus indented detail lines), ready to
    print or hand to test_feedback.write('\\n'.join(lines)).
    """
    lines = []

    def checkpass(label):
        lines.append(f"  [OK] {label}")

    def checkfail(label, detail=""):
        lines.append(f"  [X ] {label}")
        for detailLine in detail.splitlines():
            lines.append(f"       {detailLine}")

    def isolatedRun(cls):
        # Construct a fresh instance and call solving_method directly - not
        # through main.py's guard - so it can't lean on any extra work main.py
        # might be doing. Re-fetches world fresh each call (not just once
        # outside): running this once already consumes/places beepers, so a
        # second isolated call (checking the model too) needs its own clean
        # slate rather than whatever the first call left behind.
        from karel.robota import world as _world
        if world_setup:
            world_setup(_world)
        # runMainOnly() (called for step 1, above) restores the real
        # UrRobot.sleep() after it finishes - but main.py's own
        # world.setDelay(...) call is still sitting on the (shared, singleton)
        # world object. Without re-neutralizing sleep here too, every action
        # in this isolated call would do a real time.sleep() at that delay -
        # for a ~90-action solution at delay 30, that's ~27 real seconds,
        # easily blowing a grading timeout.
        original_sleep = UrRobot.sleep
        UrRobot.sleep = lambda self: None
        try:
            r = cls(*start_state)
            getattr(r, solving_method)()
        finally:
            UrRobot.sleep = original_sleep
        return r

    namespace, _violations = runMainOnly(main_file)
    if namespace is None:
        checkfail("Program runs without crashing", "See the error printed above.")
        return False, lines
    checkpass("Program runs without crashing")

    robotClass = namespace.get(class_name)
    if robotClass is None:
        checkfail(f"Class {class_name} exists",
                   f"Could not find a class named {class_name} in {main_file}.")
        return False, lines
    checkpass(f"Class {class_name} exists")

    robot = namespace.get(robot_var)
    if robot is None:
        checkfail(f"Robot named '{robot_var}' created in __main__",
                   f"{main_file} should create a {class_name} instance named '{robot_var}'.")
        return False, lines
    checkpass(f"Robot named '{robot_var}' created in __main__")

    misuse = findGlobalInstanceMisuse(main_file, class_name, robot_var)
    if misuse:
        methodName, calledAttr, lineno = misuse[0]
        checkfail(
            "Methods use self, not the global instance",
            f"Line {lineno}: {methodName}() calls {robot_var}.{calledAttr}() - it should be "
            f"self.{calledAttr}() instead. Using '{robot_var}' directly reaches for the "
            f"specific robot you made in __main__, rather than whichever robot the method "
            f"is actually being called on - self is always the right one. This kind of bug "
            f"can look like it works when you just click Run, since '{robot_var}' already "
            f"exists as a global by the time your method runs - but it breaks (often "
            f"unpredictably) the moment the method is used on any other instance, including "
            f"the fresh one the grading tests construct to check your method on its own."
        )
        return False, lines
    checkpass("Methods use self, not the global instance")

    history = util.getStateHistory(robot)
    initial = history[0]
    initialTuple = (initial.street(), initial.avenue(), initial.direction(), initial.beepers())
    if initialTuple != start_state:
        checkfail("Starting state correct",
                   f"Expected {status_tuple_str(start_state)}, got {status_tuple_str(initialTuple)}.")
        return False, lines
    checkpass("Starting state correct")

    final = history[-1]
    finalTuple = (final.street(), final.avenue(), final.direction(), final.beepers())
    if finalTuple != end_state:
        checkfail("Ending state correct",
                   f"Expected {status_tuple_str(end_state)}, got {status_tuple_str(finalTuple)}.")
        return False, lines
    checkpass("Ending state correct")

    ownMethods = sorted(
        n for n, v in vars(robotClass).items()
        if not n.startswith('_') and inspect.isfunction(v)
    )
    if len(ownMethods) < min_methods:
        checkfail(f"Class defines at least {min_methods} method(s)",
                   f"Found {len(ownMethods)}: {ownMethods}")
        return False, lines
    checkpass(f"Class defines at least {min_methods} method(s) ({len(ownMethods)} found: {', '.join(ownMethods)})")

    if solving_method:
        try:
            isolatedRobot = isolatedRun(robotClass)
        except Exception as e:
            checkfail(f"{solving_method}() solves the problem on its own",
                       f"Calling {solving_method}() directly on a fresh robot raised an "
                       f"exception: {e}. Your __main__ block reached the right answer overall, "
                       f"which means it must be doing some of the work itself instead of "
                       f"leaving it all to {solving_method}().")
            return False, lines
        isolatedTuple = util.getStatus(isolatedRobot)
        if isolatedTuple != end_state:
            checkfail(f"{solving_method}() solves the problem on its own",
                       f"Calling {solving_method}() directly on a fresh robot gave "
                       f"{status_tuple_str(isolatedTuple)}, expected {status_tuple_str(end_state)}. "
                       f"Your __main__ block reached the right answer overall, which means it "
                       f"must be doing some of the work itself instead of leaving it all to "
                       f"{solving_method}() - check for extra calls in your __main__ block.")
            return False, lines
        checkpass(f"{solving_method}() solves the problem on its own")

        if model_file:
            try:
                modelNamespace = runpy.run_path(model_file)
            except Exception as e:
                checkfail("Path matches model solution", f"Could not run the model solution file: {e}")
                return False, lines
            modelClass = modelNamespace.get(class_name)
            if modelClass is None:
                checkfail("Path matches model solution",
                           f"Could not find class {class_name} in {model_file}.")
                return False, lines
            try:
                modelRobot = isolatedRun(modelClass)
            except Exception as e:
                checkfail("Path matches model solution", f"Model solution raised an exception: {e}")
                return False, lines
            studentHistory = util.getStateHistory(isolatedRobot)
            modelHistory = util.getStateHistory(modelRobot)
            divergence = describePathDivergence(studentHistory, modelHistory)
            if divergence:
                checkfail("Path matches model solution", divergence)
                return False, lines
            checkpass("Path matches model solution")

    return True, lines