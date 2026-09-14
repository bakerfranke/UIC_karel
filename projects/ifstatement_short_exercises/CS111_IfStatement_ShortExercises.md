# CS 111 – Short Exercises: If Statements

## 1. Wall Finder

**Problem:** The robot starts at (1, 1) facing east. It should move forward, one
step at a time, as long as the way ahead is clear. As soon as it finds a wall,
it should stop and turn around to face west, without moving any further.

`![Placeholder: before/after image]()`

**Assumptions:**
- The wall is somewhere between avenue 2 and avenue 9 (never more than 8 steps away).

---

## 2. Pile Finder

**Problem:** The robot starts at (1, 1) facing east. It should move east along
street 1, checking each corner, until it finds the one corner with exactly two
beepers on it - then stop there.

`![Placeholder: before/after image]()`

**Assumptions:**
- No corner ever has more than 2 beepers.
- There is exactly one corner with 2 beepers, somewhere between avenue 1 and avenue 9.
- The robot must leave the world exactly as it found it - if it picks up a
  beeper to check a corner, it has to put it back down (including at the
  2-beeper corner itself, once it's confirmed that's the one).

---

## 3. Beeper Relay

**Problem:** The robot starts at (1, 9) facing west. It should travel west,
picking up every beeper it finds, until it reaches avenue 1 (8 steps away).
Then it should turn around and head back east, laying the beepers it collected
back down in a contiguous line starting at avenue 1. It should end back where
it started, at (1, 9), facing east, with no beepers left in its bag.

`![Placeholder: before/after image]()`

**Assumptions:**
- No corner ever has more than 1 beeper to start.

---

## 4. Door Finder

**Problem:** The robot starts at (2, 1) facing east, with a wall immediately to
its left. It should move east as long as that wall continues, and stop at the
first gap (doorway) it finds - putting a beeper down there to mark it.

`![Placeholder: before/after image]()`

**Assumptions:**
- The gap is somewhere within 8 steps of the start.

---

## 5. Gap Finder

**Problem:** The robot starts at (2, 1) facing east, with a wall on both its
left and its right. It should move east as long as both walls continue, and
stop and turn around as soon as it finds a gap on either side.

`![Placeholder: before/after image]()`

**Assumptions:**
- A gap (on the left or the right) is guaranteed within 8 steps of the start.

---

## 6. Gap or Wall Finder

**Problem:** Same setup as Gap Finder - the robot starts at (2, 1) facing east,
walled on both left and right - but now the front can also be blocked by a
wall. The robot should stop as soon as either side wall breaks, or the front
is blocked. If a side wall breaks, turn around. If the front is blocked
instead, put a beeper down. A break in either side wall always takes
precedence over a blocked front - the robot should only ever end up putting a
beeper down if the front was blocked with no wall break before it.

`![Placeholder: before/after image]()`

**Assumptions:**
- A side-wall gap or a blocked front (or both, at the same corner) is
  guaranteed within 8 steps of the start.
