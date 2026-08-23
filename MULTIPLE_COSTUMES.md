# Multiple Robot Types - Implementation Guide

## Overview

The Karel library now supports multiple robot image types. All robots default to **Sparky**, but you can create robots with different appearances. You can also set a world-wide default using `world.setRobotType()`.

## File Structure

Robot images can be stored in two locations (user folder takes priority):

1. **User's local folder** (recommended): `./robot_images/` (same level as your main program)
2. **Library folder** (fallback): `karel/robot_images/`

When loading a robot type, the system checks the local folder first, then falls back to the library folder. This allows you to override library robots or create custom ones.

### Naming Convention

Store robot images with this naming convention:

```
karel/robot_images/
├── sparky_north.png
├── sparky_east.png
├── sparky_south.png
├── sparky_west.png
├── karel_north.png
├── karel_east.png
├── karel_south.png
├── karel_west.png
├── dragon_north.png
├── dragon_east.png
├── dragon_south.png
├── dragon_west.png
└── ... (add more robot types as needed)
```

**Pattern:** `{robot_type}_{direction}.png`

- `robot_type`: lowercase, no spaces (e.g., sparky, karel, dragon, alien)
- `direction`: north, east, south, west (lowercase)

## Usage Examples

### Default (Sparky)
```python
from karel.robota import *

world.setSize(8, 8)
bob = UrRobot(4, 2, East, 7)  # Uses default robot type (sparky)

bob.move()
bob.turnLeft()
bob.turnOff()
```

### Different Robot Type Per Robot
```python
from karel.robota import *

world.setSize(8, 8)

# Create robots with different types
bob = UrRobot(4, 2, East, 7, robot_type='karel')
alice = UrRobot(5, 3, North, 5, robot_type='dragon')
charlie = UrRobot(3, 4, West, 10)  # Uses default

bob.move()
alice.turnLeft()
charlie.move()
```

### Set World Default Robot Type
```python
from karel.robota import *

world.setSize(10, 10)
world.setRobotType('karel')  # Set default to karel

# Now all new robots use 'karel' by default
robot1 = UrRobot(3, 3, East, 5)      # Uses 'karel'
robot2 = UrRobot(7, 7, North, 5)     # Uses 'karel'
robot3 = UrRobot(5, 5, South, 5, robot_type='sparky')  # Override with 'sparky'

robot1.move()
robot2.move()
robot3.move()
```

### With Robot Class (has sensors)
```python
from karel.robota import *

world.setSize(10, 10)

# Robot class also supports robot_type
scout = Robot(5, 5, North, infinity, robot_type='sparky')

while scout.frontIsClear():
    scout.move()

scout.turnOff()
```

## API Reference

### World Methods

#### `world.setRobotType(robot_type)`
Set the default robot type for all subsequent robots.

```python
world.setRobotType('karel')
```

**Parameters:**
- `robot_type` (str): Name of the robot type to use as default
  - Examples: 'sparky', 'karel', 'dragon', 'foofoo'
  - Images must be in local `robot_images/` or library `karel/robot_images/`

**Note:** Can be called at any time to change the default for future robots.

### UrRobot Constructor
```python
UrRobot(street, avenue, direction, beepers, 
        fill='yellow', outline='black', 
        visible=True, robot_type=None)
```

**Parameters:**
- `robot_type` (str or None): Name of robot type (e.g., 'sparky', 'karel', 'dragon')
  - If `None` (default), uses the world default set by `world.setRobotType()` (initially 'sparky')
  - Must match image files: `{robot_type}_north.png`, etc.
  - Case-sensitive
  - Searches local `robot_images/` folder first, then library folder

### Robot Constructor
```python
Robot(street, avenue, direction, beepers,
      fill='yellow', outline='black', 
      robot_type=None)
```

Same parameters as `UrRobot` with `robot_type` support.

## Adding New Robot Types

### Folder Priority

When loading robot images, the library searches in this order:

1. **Local `robot_images/` folder** (same directory as your main program) ← User can override here
2. **Library `robot_images/` folder** (inside `karel/` module) ← Default library images

This allows you to:
- Create custom robot types
- Override library robot types (sparky, karel, etc.)
- Keep your custom robots with your project

### Example: Custom Robot Type

Create a folder structure:
```
my_project/
├── main.py
└── robot_images/
    ├── foofoo_north.png
    ├── foofoo_east.png
    ├── foofoo_south.png
    └── foofoo_west.png
```

In your program:
```python
from karel.robota import *

world.setSize(10, 10)
bot = UrRobot(5, 5, East, 5, robot_type='foofoo')
```

The library will automatically find your local `robot_images/foofoo_*.png` files!

### Step 1: Create 4 PNG Images
You need 4 images, one for each direction:
- Recommended size: **120×120 pixels** (or 100×100)
- Format: PNG with transparent background
- File size: **5-15 KB** per image

Name them:
- `myrobot_north.png`
- `myrobot_east.png`
- `myrobot_south.png`
- `myrobot_west.png`

### Step 2: Place in robot_images/
Copy all 4 images to:
```
karel/robot_images/
```

### Step 3: Use in Code
```python
alice = UrRobot(5, 5, North, 10, robot_type='myrobot')
```

That's it! The library will automatically load the images.

## Image Optimization Tips

### Dimension Recommendations
- **Minimum:** 80×80 pixels
- **Recommended:** 100×120 pixels (width × height may vary)
- **Maximum:** 200×200 pixels

### File Size Optimization
Target: **5-15 KB per image**

#### In Photoshop:
1. **Image → Image Size**: Set to 120×120
2. **Image → Mode → Indexed Color** (if possible)
   - Colors: 256 (or lower)
   - Dithering: None
3. **File → Export As → PNG**
4. Set compression level: 9 (maximum)

#### Online Tool:
Use [TinyPNG](https://tinypng.com/) for lossless compression

#### Command Line:
```bash
pngquant --speed 1 --quality 70-95 image.png
optipng -o2 image.png
```

## Troubleshooting

### Image Not Loading
**Error:** `Error loading myrobot_north.png from .../robot_images/myrobot_north.png: ...`

**Solutions:**
1. Check filename spelling (case-sensitive: `myrobot_north.png`, not `MyRobot_North.png`)
2. Verify all 4 directions exist (north, east, south, west)
3. Check file is in `karel/robot_images/` folder
4. Ensure PNG file is valid and not corrupted

### Robot Shows as Circle
If a robot displays as a simple circle instead of an image, it means:
- Image file not found
- PIL/Pillow not installed (`pip install Pillow`)
- Image is corrupted

Check console output for error messages.

### Wrong Robot Appearing
Make sure you're specifying the correct `robot_type`:
```python
# This looks for sparky_*.png
bob = UrRobot(4, 2, East, 7)

# This looks for alice_*.png
bob = UrRobot(4, 2, East, 7, robot_type='alice')
```

## Implementation Details

### How It Works
1. When a robot is created with `robot_type='myrobot'`, the code looks for:
   - `myrobot_north.png`
   - `myrobot_east.png`
   - `myrobot_south.png`
   - `myrobot_west.png`

2. Images are loaded once on first robot creation (cached for performance)

3. Images are scaled to 75% of grid cell size for optimal appearance

4. When robot turns, the appropriate image is displayed

### Image Caching
- Original images loaded once using PIL
- Resized versions cached by (robot_type, direction, size)
- When window resizes, images are regenerated at new size
- Very efficient - minimal memory overhead

## Examples

### Simple Classroom Example
```python
from karel.robota import *

world.setSize(10, 10)
world.setDelay(50)

sparky = UrRobot(5, 5, East, 5, robot_type='sparky')

for i in range(4):
    sparky.move()
    sparky.putBeeper()
    sparky.turnLeft()

sparky.turnOff()
```

### Multiple Robots
```python
from karel.robota import *

world.setSize(12, 12)
world.setDelay(30)

# Different robot types
bot1 = UrRobot(3, 3, East, 5, robot_type='sparky')
bot2 = UrRobot(9, 9, West, 5, robot_type='karel')

# Both robots move independently
for i in range(3):
    bot1.move()
    bot2.move()
    bot1.turnLeft()
    bot2.turnLeft()

bot1.turnOff()
bot2.turnOff()
```

## Future Enhancement Ideas

- Custom colors applied to images at runtime
- Animation frames for walking
- Size variation per robot type
- Robot-specific behaviors

## Summary

✅ Store robot images as: `{name}_{direction}.png`
✅ Default robot is 'sparky'
✅ Images should be ~100-120px, ~5-15KB each
✅ Can mix different robot types in same program
✅ Fully compatible with existing code
