# UIC_karel

## To Dos:
* ~Make robotworld respect world deminsions given in a .kwld file~ added in commit 2.8.25
* Improve error messages for robot errors.  They look really ugly and messages are unclear.  Instead of just a "frontIsBlocked" message it should say something like: you attempted to walk through a wall at (s,a) heading EWSN
* Force world to show if a method like .setSize or .readWorld is called on it - right now you have to create a robot to force a drawing action.
* Improve and simplify karelunittests methods for consistency and ease of use.
