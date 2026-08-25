"""Convenience script for running all three Bomb/Room checks at once during your own
testing - NOT a graded file (deliberately not named test_*.py, so it doesn't show up as
a 4th item alongside test_beeper_room_start/end/world.py on the actual rubric).

Run directly: python3 run_all_beeper_room_checks.py
"""

import io
import beeper_room_checks as checks

if __name__ == "__main__":
    feedback = io.StringIO()
    passed = (
        checks.check_start_state(feedback)
        and checks.check_end_state(feedback)
        and checks.check_world_beepers(feedback)
    )
    print()
    print("ALL PASSED" if passed else "FAILED")
    print("FEEDBACK:", feedback.getvalue())
