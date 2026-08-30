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

def runMainOnly(mainFilePath, exemptActions=None):
    """Run a student's main.py the same way `python main.py` would - respecting
    `if __name__ == "__main__":` - while watching for any robot primitive action
    (move, turnLeft, pickBeeper, putBeeper, setCostume, etc.) called directly from
    that top-level main block, rather than from inside a method defined on the
    robot's own class.

    This catches students who "helped" an incomplete class method along by adding
    an extra action call in main - the end state can come out looking right by
    luck without the assignment's one designated solving method actually solving
    the whole problem on its own.

    Returns (namespace, violations):
      namespace  - the dict of globals from the executed file, e.g. namespace['harvey']
                   (same thing `main.harvey` would have given you with `import main`)
      violations - list of human-readable strings, one per offending call, e.g.
                   "move() was called directly in your main block (line 12) ...".
                   An empty list means main only orchestrated - the intended style.

    exemptActions defaults to just turnOff - ending a program with robot.turnOff()
    directly in main is normal and expected, not a violation. Robot creation itself
    never reaches this check (it doesn't route through _perform_action).
    """
    mainFilePath = os.path.abspath(mainFilePath)
    if exemptActions is None:
        exemptActions = {UrRobot.turnOffAction}

    violations = []
    original = UrRobot._perform_action

    def _instrumented(self, action, *args, **kwargs):
        actionFrame = inspect.currentframe().f_back  # the move()/turnLeft()/etc. frame
        callerFrame = actionFrame.f_back if actionFrame else None  # whoever called that action method
        if (action not in exemptActions and callerFrame is not None
                and callerFrame.f_code.co_filename == mainFilePath
                and callerFrame.f_code.co_name == '<module>'):
            violations.append(
                f"{actionFrame.f_code.co_name}() was called directly in your main "
                f"block (line {callerFrame.f_lineno}), not from inside a method - "
                f"your class method(s) should be doing this work, not main."
            )
        return original(self, action, *args, **kwargs)

    UrRobot._perform_action = _instrumented
    try:
        namespace = runpy.run_path(mainFilePath, run_name="__main__")
    finally:
        UrRobot._perform_action = original

    return namespace, violations

def testMainGuardPurity(test_name, mainFilePath, exemptActions=None, verbose=True):
    """Wraps runMainOnly() in the same print-a-block-every-time style as testEquals().
    Returns True (and the namespace of globals from main.py) if main.py's
    `if __name__ == "__main__":` block never called a robot action directly -
    False (with the namespace still returned, since main did run) otherwise."""
    namespace, violations = runMainOnly(mainFilePath, exemptActions)
    result = len(violations) == 0

    display_str = (
        f"{'-'*70}\n"
        f"TEST: {test_name}\n"
        f"Checking that main only creates the robot and calls its own methods "
        f"(no problem-solving work directly in main)\n"
    )
    if result:
        display_str += "RESULT: main only orchestrated - no direct action calls found! (Yay)\n"
    else:
        display_str += "PROBLEMS FOUND in your main block:\n" + "\n".join(f"  - {v}" for v in violations) + "\n"
    display_str += f"      Pass: {result}"

    if result == False or verbose == True:
        print(display_str)

    return namespace, result