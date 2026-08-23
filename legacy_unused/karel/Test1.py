from karel.robota import *
from karel.kareltestutils import *
import karel.robotutils as utils
from karel.code_parser import extract_method_headers_from_file
from io import StringIO

def setup():
    global world
    world = UrRobot.use_graphics(False)
    world.setTrace(False)
    world.readWorld("BeeperField.kwld") #load world

def checkClassAndMethodExistence(method_list):
    try:
        from main import HarvesterBot
    except Exception as e:
        print("Class HarvesterBot not found. You should have define a new Robot type HarvesterBot(UrRobot)")
        return False

    for m in method_list:
        # Test existence of method harvestBeeperField
        if not testClassMethodExists(HarvesterBot, m):
            return False

    return True

def test_passed_methodcount(test_feedback):
    class_to_check = {"HarvesterBot"}
    methods = extract_method_headers_from_file(
        "main.py",
        class_filter= class_to_check,   # or None for all classes
        include_dunder=False,         # hide __init__, etc.
        include_private=False,        # hide _helper methods
    )

    # Count & print headers
    required_methods_list = ['def turnRight(self):', 'def harvestBeeperField(self):']
    
    print("-"*30)
    print(f"Inspecting code in main.py:\n{len(methods)} methods found in class {class_to_check}:")
    required_count = 0 #count
    for i, m in enumerate(methods, start=1):
        # Show decorators (e.g., @classmethod) if present
        # for d in m.decorators:
        #     print(d)
        checkmark = ""

        if m.header in required_methods_list:
            checkmark = " ✅"
            required_count += 1 # check to see if this method is in required list
        else:
            checkmark =""
        print(f"{i}. line {m.lineno}: {m.header}{checkmark}")
    
    has_required_num_methods = len(methods) >= 4
    has_required_named_methods = len(required_methods_list) == required_count

    #print(f"Test: method count ≥ 4? {if required_num_methods: ' ✅' else: ' ❌'}")
    #print(f"Test: method count ≥ 4? {'✅' if has_required_count else '❌'}")
    num_status = "✅" if has_required_num_methods else f"❌ expected ≥4 methods."

    req_status = "✅" if has_required_named_methods else f"❌\n\tYour code is missing one of these: {required_methods_list}"
    print("-"*30)
    print(f"Test: required number of methods? {num_status}")
    print(f"Test: required methods present? {req_status}")
    #print(f"Test: required methods present? {if required_named_methods: ' ✅' else: ' ❌\n\tYour code is missing one of {required_methods_list}'}")

    return has_required_num_methods and has_required_named_methods

def test_passed_turnRight(test_feedback):
    #SETUP
    setup()

    # Make sure that HarvestBot class exists
    if not checkClassAndMethodExistence(["turnRight"]):
        return False
    
    #     # Test existence of method harvestBeeperField
    # if not testClassMethodExists(HarvesterBot, ):
    #     return False

    from main import HarvesterBot # this should be safe to do here

    stuBot = HarvesterBot(2, 2, North, 0)
    stuBot.turnRight()
    result = testRobotEquals("Test turnRight", util.getStatus(stuBot), (2, 2, East, 0))
    if not result:
        return False

    print("Woohoo!  All tests passed!")

def test_passed_beeperField(test_feedback):
    #SETUP
    setup()

    # Make sure that HarvestBot class exists
    if not checkClassAndMethodExistence(["harvestBeeperField"]):
        return False

    from main import HarvesterBot # this should be safe to do here

    # Test behavior of harvestBeeperField
    stuBot = HarvesterBot(2, 2, East, 0)
    stuBot.harvestBeeperField()
    result = testRobotEquals("Test Harvest Beeper Field", util.getStatus(stuBot), (8, 2, East, 36))
    if not result:
        return False

    print("Woohoo!  All tests passed!")

    return True

from contextlib import redirect_stdout, redirect_stderr
import io, runpy, sys, os

def run_script_as_main(path, args=None, cwd=None):
    print(f"Running {path} as main...")
    args = args or []
    old_argv, old_cwd = sys.argv[:], os.getcwd()
    buf = io.StringIO()
    try:
        sys.argv = [path, *args]
        if cwd:
            os.chdir(cwd)
        with redirect_stdout(buf), redirect_stderr(buf):
            globals_dict = runpy.run_path(path, run_name="__main__")
        return buf.getvalue(), globals_dict
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)




if __name__=="__main__":
    message = StringIO()
   # result = test_passed_beeperField(message)
    #result = test_passed_turnRight(message)
    # result = run_script_as_main("main.py")
    # print("DONE")
    # for key in result[1]:
    #     print(key)
    result = test_passed_methodcount(message)
