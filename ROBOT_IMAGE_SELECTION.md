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

Change the `RobotImage` class constructor to accept a `robot_type` parameter:

**Current code (around line 38):**
```python
def __init__(self, street, avenue, direction, window, fill='blue', outline='black'):
```

**Modified code:**
```python
def __init__(self, street, avenue, direction, window, fill='blue', outline='black', robot_type='karel'):
```

**Current code (around line 52):**
```python
        # the next statement defines which figure will be drawn
        package = self.karelPackage
```

**Modified code:**
```python
        # the next statement defines which figure will be drawn
        if robot_type == 'alien':
            package = self.alienPackage
        elif robot_type == 'crab':
            package = self.crabPackage
        else:  # default to 'karel'
            package = self.karelPackage
```

### Step 2: Modify `addRobot()` method in `tkwindow.py`

Change the `addRobot` method to accept and pass through the `robot_type` parameter:

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
    def addRobot(self, street, avenue, direction, fill, outline, robot_type='karel'):
        #        fill and outline are colors, default to blue, black
        robot = RobotImage(street, avenue, direction, self, fill, outline, robot_type)
        self.__contents.append(robot)
        return robot
```

### Step 3: Modify `RobotWorld.update()` in `tkworldadapter.py`

Update the method where robots are created to pass the `robot_type` parameter:

**Current code (around line 83-84):**
```python
            self.__gRobots[robot] = _window.addRobot(street, avenue, robot._UrRobot__direction,
                                                     robot._UrRobot__fill, robot._UrRobot__outline)
```

**Modified code:**
```python
            robot_type = getattr(robot, '_UrRobot__robot_type', 'karel')  # get robot_type or default
            self.__gRobots[robot] = _window.addRobot(street, avenue, robot._UrRobot__direction,
                                                     robot._UrRobot__fill, robot._UrRobot__outline, robot_type)
```

### Step 4: Modify `UrRobot.__init__()` in `robota.py`

Add a `robot_type` parameter to the robot constructor:

**Current code (around line 113):**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', visible=True):
```

**Modified code:**
```python
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', visible=True, robot_type='karel'):
```

**Add this line after line 133:**
```python
        self.__robot_type = robot_type
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
    def __init__(self, street, avenue, direction, beepers, fill = 'yellow', outline = 'black', robot_type='karel'):
        UrRobot.__init__(self, street, avenue, direction, beepers, fill, outline, robot_type=robot_type)
```

---

## Example Usage

Once you've made these modifications, you can use alternative robot drawings in your programs:

**Example 1: Using an alien robot**
```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7, robot_type='alien')

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

bob = UrRobot(4, 2, East, 7, robot_type='crab')

bob.move()
bob.putBeeper()
bob.turnOff()
```

**Example 3: Classic karel robot (default)**
```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7)  # robot_type defaults to 'karel'

bob.move()
bob.turnOff()
```

---

## Summary of Changes Required

| File | Class/Method | Change |
|------|--------------|--------|
| `tkwindow.py` | `RobotImage.__init__()` | Add `robot_type` parameter and selection logic |
| `tkwindow.py` | `addRobot()` | Add `robot_type` parameter and pass it through |
| `tkworldadapter.py` | `RobotWorld.update()` | Extract and pass `robot_type` when creating robots |
| `robota.py` | `UrRobot.__init__()` | Add `robot_type` parameter and store it |
| `robota.py` | `Robot.__init__()` | Add `robot_type` parameter and pass it to parent |

After these modifications, all three robot types will be accessible and selectable from any Karel program!
