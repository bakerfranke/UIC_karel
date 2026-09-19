# CS 111 – Project 3: SorterBot, CarpetBot & BigCarpetBot

## Overview

This project is in three parts. Each part is its own program, its own robot class, and its
own submission — but all three are built around the same core skill: using `if` statements
to make your robot behave differently depending on what it senses, and organizing that
decision-making into well-named helper methods instead of one long tangle of code.

None of these problems has a single "correct" path through the code. As long as your program
produces the required end result for *any* world file matching the problem's description —
not just the one example we show you — the way you get there is up to you.

### Technical possibilities

You may use `for` loops in this project, but only in the form `for <var> in range(<int>):` —
repeating an instruction a fixed number of times. Any other type of loop, or looping
behavior, is off limits for this project (we'll get there, but the core concept of this
project isn't about loops).

You're also welcome to use more than one robot if that fits how you're thinking about a
problem, but it is not required to solve any of the three parts — everything here can be
done with a single robot. If you use multiple robots it still has to pass all the tests.

---

## Problem 1: SorterBot

### The Problem

Sortee the SorterBot starts in a world of varying size, from up to a max of 10 avenues wide
and a max of 10 streets tall — but there's no guarantee it's actually that big. A
North-South wall out to the east marks where the field really ends. The exact distance from
your starting corner varies from world file to world file — it could be 1 avenue away, or 5,
or the full 10. Don't assume every world file uses the full 10×10 space; 10 is only the
maximum you can ever count on.

Every avenue has a column of beepers, one beeper per corner, stacked contiguously upward
starting at street 1. Column heights are random and can vary from 0 beepers high, up to a
max of 10.

Your job is to rearrange the beepers so that, reading from left-to-right, the column heights
are sorted from shortest to tallest — you need to do this by moving beepers around. When
you're done, turn the robot off, but the starting and ending locations are up to you.

`![Fig. 1 - An example of a world that needs to be sorted.]()`

### Getting Started

You'll be given a `main.py` file with some starting code already in it. Your job is to
define the `SorterBot` class and fill in `sortBeepers()` and whatever helper methods you
need.

You do not know the world's actual width or the height of any column in advance — your code
must work correctly no matter which of the provided world files it's run against. You do
know the maximum possible world size (10×10), which you can rely on. If you open the list of
files on the project you'll see at least 10 different world files. Your robot should be able
to handle any of those correctly.

### Requirements (What's tested)

- Define a class called `SorterBot`.
- Define a method `sortBeepers()` that solves the entire problem when called by itself on a
  freshly constructed robot — not just when run through your `main` block.
- You must have at least three methods other than `sortBeepers()`, `turnRight()`, and
  `turnAround()` — those three don't count toward the requirement.
- Any loops used are only for-loops in the form: `for <var> in range(<int>):`
- The final state of your `main` block should do nothing except construct a single
  `SorterBot` and call `sortBeepers()`. (It's fine to temporarily add things to `main` while
  you're testing along the way — just make sure the version you submit is back to just
  that.)
- Your robot must turn itself off once the problem is solved.
- Your program must correctly sort the beepers for *any* valid SorterBot world, not just one
  specific layout.

---

## Problem 2: CarpetBot

### The Problem

Carpee has been hired to carpet a set of "small rooms" along a 10-avenue-long "hallway" in
its world. A "small room" is an intersection that has walls on three sides – immediately to
its west, north, and east, with an open doorway to the south connecting it to the "hallway".
The robot must place a single beeper ("carpet") only in the "small rooms" and on no other
intersections.

Problem details:

- You can assume street 1 itself is always clear of obstructions — you can always move east
  along it.
- There will never be an east-west wall between streets 1 and 2; nothing will ever block you
  moving north from street 1 to street 2.
- There are a total of 8 possible rooms, between avenues 2 and 9, inclusive. There will
  never be a room on avenue 1 or avenue 10.
- The robot cannot re-use beepers. In other words, you can't pick beepers back up once
  they're down.
- Your program must correctly carpet *any* valid CarpetBot world, not just one specific
  layout.

### Getting Started / Problem-Solving Recommendation

Recognize that this problem breaks down into two things the robot needs to do, each with its
own logic — and both of these were individual problems in the homework. Even if you can't
reuse that code verbatim, the underlying ideas carry over directly.

First, the robot needs to travel north into a potential room, stopping either because it's
detected a complete room or because it's detected the room shape has broken down (it's not
going to be a complete room after all).

Second, the robot needs to travel back south to street 1, deciding at each step along the
way whether to leave a beeper behind or not.

Here's the insight that connects the two: the first bit of carpet gets placed the moment a
complete room is detected, at the deepest corner the robot reaches. From there, heading back
south, the robot can tell whether to keep placing carpet just by checking whether it's
currently standing on some — no separate bookkeeping needed.

Test each of these pieces independently as you build them. Remember, you can test a single
method in isolation by constructing a robot anywhere, facing any direction, in any
situation, and calling just that one method to see what it does. Incremental testing like
this is an important part of getting this right.

### Requirements (What's Tested)

- Define a class called `CarpetBot`.
- Define a method `carpetSmallRooms()` that solves the entire problem when called by itself
  on a freshly constructed robot.
- You must have at least three methods other than `carpetSmallRooms()`, `turnRight()`, and
  `turnAround()` — those three don't count toward the requirement.
- Any loops used are only for-loops in the form: `for <var> in range(<int>):`
- The final state of your `main` block should do nothing except construct a single `carpee`
  and call `carpetSmallRooms()`. (It's fine to temporarily add things to `main` while you're
  testing along the way — just make sure the version you submit is back to just that.)
- Your robot must start at street 1, avenue 1, facing east, with exactly 8 beepers.
- Your robot must end at street 1, avenue 10, facing east, having turned itself off.
- Your solution should never need to call `pickBeeper()`. You're laying carpet, not removing
  it — if your code calls `pickBeeper()` anywhere, that's a sign your approach has gone
  sideways somewhere.

---

## Problem 3: BigCarpetBot

### The Problem

Carpee's business is growing — and the jobs are getting more complex. The "hallway" still
runs along street one, and there are 8 potential rooms between avenue 2 and 9. But now
complete rooms can be any of 1, 2 or 3 streets long. A "complete" room is still defined as
having contiguous walls on three sides (west, north, and east), and should be carpeted; any
other room is considered "incomplete" and should not be carpeted.

Problem details:

- All of the assumptions from the previous CarpetBot problem apply here.
- A reminder that you cannot re-use beepers - once a beeper is placed down, you can't pick
  it back up.

### Getting Started / Problem-Solving Recommendation

You'll need to be a little bit clever about what the robot can detect in the world. Some of
the pieces here are suggested by the homework, if you did it 🙂. Again, we'd suggest a
single method (similar in spirit to `carpetIfRoom` from Part 2) that handles one room at a
time — but now, instead of just moving one step into the room, there's logic for whether you
should keep heading north into it at all. At some point you'll stop heading north into a
room, and then you need to decide whether to put a beeper down. Then, to leave the room and
head back to street 1, you need to decide whether you should be placing a beeper down as you
go.

### Requirements (What's Tested)

- Define a class called `BigCarpetBot`.
- Define a method `carpetAllRooms()` that solves the entire problem when called by itself on
  a freshly constructed robot.
- You must have at least three methods other than `carpetAllRooms()`, `turnRight()`, and
  `turnAround()` — those three don't count toward the requirement.
- Any loops used are only for-loops in the form: `for <var> in range(<int>):`
- The final state of your `main` block should do nothing except construct a single `carpee`
  and call `carpetAllRooms()`. (It's fine to temporarily add things to `main` while you're
  testing along the way — just make sure the version you submit is back to just that.)
- Your robot must start at street 1, avenue 1, facing east, with exactly 24 beepers.
- Your robot must end at street 1, avenue 10, facing east, having turned itself off.
- Your solution should never need to call `pickBeeper()`.
- Your program must correctly carpet *any* valid BigCarpetBot world, not just one specific
  layout.

---

## How to turn it in

*(instructor to add — submission mechanism, deadline, per-part vs. combined submission)*

## Grading

*(instructor to add point values — the checklist above is what will be verified; you decide
how the points are distributed across it)*
