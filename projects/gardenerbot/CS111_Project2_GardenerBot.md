# CS 111 - Project 2 - GardenerBot

## Problem

- A `UrRobot` `gardy` must start at the garden gate — `(1, 2)` facing North, carrying 80 beepers — in the world shown below.
- Your task is to make `gardy` plant one beeper along the outline of each of the four `+`-shaped hedges, by defining a new robot class `GardenerBot` and a method called `plantAllFlowers()`.
- It does **not** matter where the robot ends up or which direction it's facing when `plantAllFlowers()` finishes — only the beepers planted in the world are graded.
- You should try to make `plantAllFlowers()` **as efficient and reusable as possible** — see *Getting Started* below.

![INSERT IMAGE: the garden_walls.kwld starting layout (four `+`-shaped hedges, empty) side by side with the fully-planted end state]

---

## Getting Started

You're given the world file (`garden_walls.kwld`), and starter code that creates the world and a `GardenerBot` named `gardy`. Your job is to fill in `plantAllFlowers()`.

This problem is a good candidate for **stepwise refinement** — the same idea covered in [Building Your Own Robot Class](https://bakerfranke.github.io/karel/docs/viewer.html?doc=02_new_robot_classes.md) in the Karel docs: describe the big picture first (in terms of smaller pieces you haven't written yet), then fill in each piece on its own.

### A design hint

Starting in the bottom-left corner of the garden can throw you off the scent of a good way to think about this problem. It might be worth considering whether it's easier to repeat a pattern by first moving the robot to a *different* location in the garden — somewhere that makes doing (and redoing) that pattern simpler than starting from the gate would.

It's also pretty obvious that all four hedges are the same shape. It would be great if you could write the code to plant one hedge once, and then reuse it for all four.

---

## Requirements

1. **Class and method names** — Create a class called `GardenerBot` that extends `UrRobot`, with a method called `plantAllFlowers()`. Calling `plantAllFlowers()` on its own (nothing else) should solve the entire problem.
2. **At least 4 other methods** — Besides `plantAllFlowers()`, your `GardenerBot` class should define (and actually use) at least 4 more methods. A method that's defined but never called doesn't count. If you're only defining one method, you're probably not breaking the problem down enough — see *Getting Started* above.
3. **End State** — The world's beepers should match Fig. 1 above exactly, once `plantAllFlowers()` has run.
4. **High-level strategy comment** — Directly above (or inside the docstring of) `plantAllFlowers()`, include a comment in plain English describing your overall strategy for planting the field — not a line-by-line description, but the big-picture idea (e.g. "first get to X, then repeat Y facing each direction"). This will be graded for how clearly it explains your approach.
5. **Comments** — Your code should be well organized and include comments that clarify or name different parts of the task. There aren't any strict rules about writing comments, only conventions — it's common to put a comment just above a section of code describing what it does. Be descriptive, but shorthand is fine; we don't need an essay. Remember: code is for humans (and maybe AI) to read and computers to run — make it readable.
6. **Header Comment** — At the top of your code, include a docstring-style comment (text enclosed in triple-quotes) with your name, NetID (your UIC email address *without* the `@uic.edu` part), and the date.
7. **Complete the AI use attestation.** Set the strings of text to document your use of AI in completing the assignment. Using AI is okay, as long as the resulting work is your own, and you are not submitting any code that you don't understand. **Hit submit for grading** to lock in your response.
8. **Complete the Academic Integrity attestation** - attesting to the fact that you are submitting work that is your own in accordance with class policies. **Hit submit for grading** to lock in your response.

---

## How to turn it in

In zyBooks there is no final "act" to turn something in.

Along the way, while you're programming, you should hit the **"Submit for Grading" button**. Remember **this does not actually submit your project** to me in a final way. It means "submit the program to the set of automated tests to check it." It runs some tests against your code to give you feedback about correctness. Study the output of these tests to see if you're on the right track.

That said, if you NEVER hit submit-for-grading then we have no record that you did anything! **You must hit submit for grading at least once in each programming area to get points.** This notifies us that you have done something with the project. The expectation is that you will actually hit submit-for-grading many times as you work through the project to debug it.

*Whatever state your project is in when the deadline occurs* is "what you turn in". Specifically, the last time you hit submit-for-grading before the deadline is what gets locked in as your submission. After the deadline you can edit the project, but it won't let you submit it.

If some of the tests "fail" that's not bad news. It's information about what you need to fix. The output usually contains clues - line numbers, specific segments of code, etc. - that you might need to look at and address.

There are some items in the rubric listed as "Manual Grading". That is space left for graders (TAs and professor) to score your project for things we cannot automatically test for. Yes, we read all of your code!

Every project requires that you complete:
1. The AI use attestation – complete and hit submit-for-grading
2. The Academic Integrity Statement - complete and hit submit-for-grading.

---

## Grading

**Total: 100 points**

| # | Item | Points | How it's checked |
|---|------|--------|-------------------|
| 1 | Class/method structure | 15 | Automated - `GardenerBot` exists, `plantAllFlowers()` exists. At least 4 other methods are added to `GardenerBot` and used in the program. |
| 2 | Starting state | 15 | Automated - `gardy` is created at `(1, 2, North, 80)` |
| 3 | `plantAllFlowers()` solves it on its own | 10 | Automated - constructs a fresh `GardenerBot` and calls only `plantAllFlowers()` on it, bypassing your `__main__` entirely, and checks the resulting world. |
| 4 | Lower-left hedge (minimum requirement) | 15 | Automated - checks only the hedge nearest the garden gate. This is intentionally graded separately as an incremental step. If a call to `plantAllFlowers()` successfully plants the lower-left hedge, even if the rest of the field isn't complete, getting this one hedge fully correct is worth partial credit on its own. |
| 5 | Final world state | 15 | Automated - runs your actual `main.py` and checks the complete final world (all 4 hedges). I.e. if hitting "run" on your program solves the problem, full credit is that a single call to `plantAllFlowers()` is what does it. |
| 6 | Main only orchestrates | 15 | Automated - `__main__` only constructs `gardy` and calls `plantAllFlowers()` (and `turnOff()`, if you use it) - no problem-solving work directly in `__main__`. This may be the last test to pass, since you may write different code into `__main__` to test it. You should clean it up at the end so this test passes. |
| 7 | Style & comments *(Manual Grading)* | 15 | Manually graded - code organization, in-line comments, the header docstring, and especially the clarity of your required high-level strategy comment on `plantAllFlowers()` |

A student who completes just the minimum requirement (items 1, 2, 4, 6, 7 — everything except the two full-field checks) scores **75/100**. Fully solving the whole garden earns the remaining 25 points from items 3 and 5.
