"""
Useful functions and constants for getting info from robots esp. for writing tests.
"""
from karel.robota import East, West, North, South, UrRobot, Robot
from karel.robotworld import RobotWorld

direction_strings = {
    East: "East",
    North: 'North',
    West: "West",
    South: 'South'
}

def getStreet(robot):
    return robot._UrRobot__street

def getAvenue(robot):
    return robot._UrRobot__avenue

def getLocation(robot):
    return (robot._UrRobot__street, robot._UrRobot__avenue)

def getDirection(robot):
    return robot._UrRobot__direction

def getDirectionStr(robot):
    return direction_strings[robot._UrRobot__direction]

def _status_to_str(status):
    return (status[0], 
            status[1],
            direction_strings[status[2]],
            status[3])

def getBeepers(robot):
    return robot._UrRobot__beepers

def getActionCount(robot):
    return robot._UrRobot__action_count

def getLocationList(robot):
    return robot._UrRobot__location_list

def getStatus(robot):
    return (robot._UrRobot__street, 
            robot._UrRobot__avenue,
            robot._UrRobot__direction,
            robot._UrRobot__beepers)

def robotEquals(robot_or_tuple_A, robot_or_tuple_B, ignoreBeepers=False, atLeastBeepers=False, ignoreDirection=False):
    """
    Compares the status of a robot or a status tuple to another status tuple.

    :param robot_or_tuple_A: Either a robot object or a status tuple (street, avenue, direction, beepers).
    :param robot_or_tuple_B: Either a robot object or a status tuple (street, avenue, direction, beepers) to compare against.
    :param ignoreBeepers: defaults to False. If True, ignores the beeper count during the comparison.
    :param atLeastBeepers: defaults to False. If True, returns true if robot_A has at least as many beepers as robot_B(ignoreBeepers overrides this)
    :return: True if the statuses match (considering beepers if not ignored), otherwise False.
    """
    # Check if the first parameter is a robot, and convert to a status tuple if so
    if isinstance(robot_or_tuple_A, UrRobot):
        robot_A = getStatus(robot_or_tuple_A)  # Convert robot to a status tuple using utility function
    else:
        robot_A = robot_or_tuple_A  # Assume obj is already a tuple

    if isinstance(robot_or_tuple_B, UrRobot):
        robot_B = getStatus(robot_or_tuple_B)  # Convert robot to a status tuple using utility function
    else:
        robot_B= robot_or_tuple_B  # Assume obj is already a tuple
    
    # Perform the location and direction comparison
    result = (robot_A[0] == robot_B[0] and  # Compare street
              robot_A[1] == robot_B[1] and  # Compare avenue
              (ignoreDirection or robot_A[2] == robot_B[2])  # Compare direction or ignore
              )    


    # Handle beeper comparison based on flags
    if not ignoreBeepers:  # If beepers are not ignored
        if atLeastBeepers:
            # Check if robot_A has at least as many beepers as robot_B
            result = result and (robot_A[3] >= robot_B[3])
        else:
            # Check if beeper counts are exactly equal
            result = result and (robot_A[3] == robot_B[3])


    return result

def get_world_diffs(robot_world, expected_world):
    """
    Compares the beeper state of two robot worlds.

    Args:
        robot_world: The first RobotWorld object.
        expected_world: The second RobotWorld object.

    Returns:
        dict: Differences in beeper states categorized as 'missing', 'extra', and 'mismatched'.
    """
    world_beepers_dict = robot_world.getAllBeepers()
    expected_beepers_dict = expected_world.getAllBeepers()

    # Reusing the comparison logic
    return get_beeper_diffs(world_beepers_dict, expected_beepers_dict)


def get_world_diffs_from_file(robot_world, expected_world_file):
    """
    Compares the current world state with the state described in a .kwld file.

    Args:
        current_world: The current RobotWorld object.
        expected_world_file (str): Path to the .kwld file describing the expected state.

    Returns:
        dict: Differences in beeper states categorized as 'missing', 'extra', and 'mismatched'.
    """
    # Parse the .kwld file into a new RobotWorld object
    expected_world = RobotWorld("Expected World")
    expected_world.readWorld(expected_world_file)

    # Use the world comparison function
    return get_world_diffs(robot_world, expected_world)
    
def get_beeper_diffs(world_beepers, expected_beepers):
    """
    Compares beepers in the current world state with those described in another world.

    Args:
        world_beepers (dict): Beeper positions and counts in the current world state.
        expected_beepers (dict): Beeper positions and counts from the .kwld file or another world.

    Returns:
        dict: 
            - 'diffs': True if differences exist, False otherwise.
            - 'allbeeperdiffs': A multiline string showing the side-by-side comparison.
    """
    differences_found = False
    num_beepers_correct = 0
    comparison_lines = []
    total_expected_beeper_count = 0
    total_actual_beeper_count = 0

    # Add column headings
    header = (
        f"{' '.ljust(8)}|{'Your World'.center(15)}|{'Expected'.center(15)}\n"
        f"{'RESULT'.ljust(8)}| {'st  ave beeps'.ljust(13)} | {'st  ave beeps'.ljust(14)}"
    )
    separator = f"{'-' * 8}| {'-'*3} {'-'*3} {'-'*5} | {'-'*3} {'-'*3} {'-'*5}"
    comparison_lines.append(header)
    comparison_lines.append(separator)

    # Gather all unique positions from both dictionaries
    all_positions = set(world_beepers.keys()) | set(expected_beepers.keys())

    for position in sorted(all_positions):
        robot_count = world_beepers.get(position, None)  #robot_count is a misnomer here.  Shuld be world_count
        expected_count = expected_beepers.get(position, None)

        total_expected_beeper_count += expected_count or 0
        total_actual_beeper_count += robot_count or 0
        
        if robot_count is None and expected_count > 0:  # Missing in robot world
            differences_found = True
            comparison_lines.append(
                f"{'MISSING'.ljust(8)}| {'_   _   _':<14}| "
                f"{f'{position[0]:<3} {position[1]:<3} {expected_count:<5}':<14}"
            )
        elif expected_count is None and robot_count > 0:  # Extra in robot world
            differences_found = True
            comparison_lines.append(
                f"{'EXTRA'.ljust(8)}| "
                f"{f'{position[0]:<3} {position[1]:<3} {robot_count:<5}':<14}| {'--  --  --':<14}"
            )
        elif robot_count != None and expected_count != None and robot_count != expected_count:  # Mismatched counts
            differences_found = True
            robot_count = str(robot_count)+"<<"
            comparison_lines.append(
                f"{'MISMATCH'.ljust(8)}| "
                f"{f'{position[0]:<3} {position[1]:<3} {robot_count:<5}':<14}| "
                f"{f'{position[0]:<3} {position[1]:<3} {expected_count:<5}':<14}"
            )
        # elif robot_count != None and expected_count != None:  # Matches correctly
        #     comparison_lines.append(
        #         f"{'   -'.ljust(8)}| "
        #         f"{f'{position[0]:<3} {position[1]:<3} {robot_count:<5}':<14}| "
        #         f"{f'{position[0]:<3} {position[1]:<3} {expected_count:<5}':<14}"
        #     )

    return {
        'diffs': differences_found,
        'num_beepers_in_world': total_actual_beeper_count,
        'num_beepers_expected': total_expected_beeper_count,
        'allbeeperdiffs': "\n".join(comparison_lines)
    }



def get_beeper_diffs_OLD(world_beepers, expected_beepers):
    """
    Compares beepers in the current world state with those described in another world.

    Args:
        world_beepers (dict): Beeper positions and counts in the current world state.
        expected_beepers (dict): Beeper positions and counts from the .kwld file or another world.

    Returns:
        dict: Differences categorized as 'missing', 'extra', and 'mismatched'.
    """
    differences = {
        'missing': {},  # Beepers in the file but not in the current world
        'extra': {},    # Beepers in the current world but not in the file
        'mismatched': {}  # Locations where counts differ
    }

    # Compare file beepers with world beepers
    for location, count in expected_beepers.items():
        if location not in world_beepers:
            differences['missing'][location] = count
        elif world_beepers[location] != count:
            differences['mismatched'][location] = {
                'your_world': world_beepers[location],
                'expected': count
            }

    # Find extra beepers in the current world
    for location, count in world_beepers.items():
        if location not in expected_beepers:
            differences['extra'][location] = count

    return differences