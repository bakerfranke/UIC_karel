# How to Use Alternative Robot Drawings

## Current State

The library currently defines three robot drawing styles:
- **karelRobot** (default, 23×23 pixels): Classic robot with head, body, feet, arms, eyes, and "K" marking
- **alienRobot** (6×6 pixels): Simpler alien-like figure
- **crabRobot** (6×6 pixels): Crab-shaped figure

Currently, the robot drawing is **hardcoded** to always use `karelRobot`. There's no way to select an alternative from a user program without modifying the library.

## How to Enable Robot Selection

To allow programs to choose which robot drawing to use, you need to modify the library in three places:

### Step 1: Modify `RobotImage.__init__()` in `tkwindow.py`

Change the `RobotImage` class constructor to accept a `costume` parameter:

**Current code (around line 38):**
```python
def __init__(self, street, avenue, direction, window, fill='blue', outline='black'):
```

**Modified code:**
```python
def __init__(self, street, avenue, direction, window, fill='blue', outline='black', costume='karel'):
```

**Current code (around line 52):**
```python
        # the next statement defines which figure will be drawn
        package = self.karelPackage
```

**Modified code:**
```python
        # the next statement defines which figure will be drawn
        if costume == 'alien':
            package = self.alienPackage
        elif costume == 'crab':
            package = self.crabPackage
        else:  # default to 'karel'
            package = self.karelPackage
```

### Step 2: Modify `addRobot()` method in `tkwindow.py`

Change the `addRobot` method to accept and pass through the `costume` parameter:

**Current code (around line 647):**
```python
    def addRobot(self, street, avenue, direction, fill, outline):
        #        fill and outline are colors, default to blue, black
        robot = RobotImage(street, avenue, direction, self, fill, outline)
        self.__contents.append(robot)
        return robot
```

**Modified code:**
```python
    def addRobot(self, street, avenue, direction, fill, outline, costume='karel'):
        #        fill and outline are colors, default to blue, black
        robot = RobotImage(street, avenue, direction, self, fill, outline, costume)
        self.__contents.append(robot)
        return robot
```

### Step 3: Modify `RobotWorld.update()` in `tkworldadapter.py`

Update the method where robots are created to pass the `costume` parameter:

**Current code (around line 83-84):**
```python
            self.__gRobots[robot] = _window.addRobot(street, avenue, robot._UrRobot__direction,
                                                     robot._UrRobot__fill, robot._UrRobot__outline)
```

**Modified code:**
```python
            costume = getattr(robot, '_UrRobot__costume', 'karel')  # get costume or default
            self.__gRobots[robot] = _window.addRobot(street, avenue, robot._UrRobot__direction,
                                                     robot._UrRobot__fill, robot._UrRobot__outline, costume)
```

### Step 4: Modify `UrRobot.__init__()` in `robota.py`

Add a `costume` parameter to the robot constructor:

**Current code (around line 113):**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', visible=True):
```

**Modified code:**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', visible=True, costume='karel'):
```

**Add this line after line 133:**
```python
        self.__costume = costume
```

### Step 5: Update the `Robot` class in `robota.py` (optional)

If you're using the `Robot` class (which has sensors), update its constructor too:

**Current code (around line 398):**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black'):
        UrRobot.__init__(self, street, avenue, direction, beepers, fill, outline )
```

**Modified code:**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', costume='karel'):
        UrRobot.__init__(self, street, avenue, direction, beepers, fill, outline, costume=costume)
```

---

## Example Usage

Once you've made these modifications, you can use alternative robot drawings in your programs:

**Example 1: Using an alien robot**
```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7, costume='alien')

for i in range(4):
    bob.move()
    bob.move()
    bob.putBeeper()
    bob.turnLeft()
```

**Example 2: Using a crab robot**
```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7, costume='crab')

bob.move()
bob.putBeeper()
bob.turnOff()
```

**Example 3: Classic karel robot (default)**
```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7)  # costume defaults to 'karel'

bob.move()
bob.turnOff()
```

---

## Summary of Changes Required

| File | Class/Method | Change |
|------|--------------|--------|
| `tkwindow.py` | `RobotImage.__init__()` | Add `costume` parameter and selection logic |
| `tkwindow.py` | `addRobot()` | Add `costume` parameter and pass it through |
| `tkworldadapter.py` | `RobotWorld.update()` | Extract and pass `costume` when creating robots |
| `robota.py` | `UrRobot.__init__()` | Add `costume` parameter and store it |
| `robota.py` | `Robot.__init__()` | Add `costume` parameter and pass it to parent |

After these modifications, all three costumes will be accessible and selectable from any Karel program!
