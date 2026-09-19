# Karel Projects

Self-contained CS 111 project bundles, each built against the shared `karel/` library at the repo root (projects don't carry their own copy of the library — when deploying to an IDE, copy the repo's `karel/` folder alongside a project's files).

## Structure

Each project folder generally contains:

- **An instructions `.md` file** — the assignment write-up given to students.
- **`main.py`** — the starter code given to students (usually a stub class with `pass` where the solution goes).
- **`model_solution.py`** — a verified-correct reference solution.
- **World files (`.kwld`)** — sit flat alongside the code, referenced by filename with no path prefix (`world.readWorld("some_world.kwld")`).
- **Test file(s)** — either a single `tests.py`, or (for zyBooks-style grading, one test case per file) a `tests.py` holding the real logic plus several thin `test_*.py` files that each just alias one function from it as `test_passed`, so each can be dropped into its own zyBooks test case.

## What's here

- **`gardenerbot/`** — Project 2, GardenerBot.
- **`ifstatement_short_exercises/`** — six short single-concept if-statement exercises (WallFinder, PileFinder, BeeperRelay, DoorFinder, GapFinder, GapOrWallFinder), each in its own subfolder.
- **`project3_ifstatements/`** — Project 3, three sub-problems (SorterBot, CarpetBot, BigCarpetBot), each in its own subfolder, sharing one instructions doc.

H-Bot (Project 1) isn't here yet — the original class-based solution and its tests weren't found anywhere on disk; only an old, unrelated raw-script demo from an earlier semester exists. It'll need to be rebuilt before it can be added.
