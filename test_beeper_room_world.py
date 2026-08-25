import beeper_room_checks as checks


def test_passed(test_feedback):
    return checks.check_world_beepers(test_feedback)
