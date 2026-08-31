# generic value v. expected test
from karel.robota import *
import karel.robotutils as util
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

def runRobotChecklist(class_name, robot_var, start_state, end_state, min_methods,
                       solving_method=None, model_file=None, world_setup=None,
                       main_file="main.py"):
    """Runs main.py once and walks a fixed checklist, in order, stopping at the
    first failure (later items are simply never attempted/printed):

      1. Program runs without crashing
      2. Class <class_name> exists
      3. Robot named <robot_var> was created in main
      4. Starting state matches start_state
      5. Ending state matches end_state
      6. Class defines at least min_methods of its own methods
      7. (only if solving_method is given) solving_method() reaches end_state
         all on its own, called directly on a fresh instance - main.py's overall
         run already reached the right answer (step 5 passed), so if the
         designated method *alone* doesn't get there too, that's proof main.py
         has extra work of its own propping the result up instead of leaving it
         all to that one method.
      8. (only if model_file is also given) that same isolated run's path
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
        if detail:
            lines.append(f"       {detail}")

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
            studentPath = [(s.street(), s.avenue()) for s in util.getStateHistory(isolatedRobot)]
            modelPath = [(s.street(), s.avenue()) for s in util.getStateHistory(modelRobot)]
            if studentPath != modelPath:
                checkfail("Path matches model solution",
                           f"Paths diverge - yours has {len(studentPath)} step(s), model has {len(modelPath)}.")
                return False, lines
            checkpass("Path matches model solution")

    return True, lines