# Using PNG Images for Robot Graphics

Yes, you can substitute PNG images for the procedurally drawn robots! Here's how.

## Overview

The current system draws robots using Tkinter Canvas drawing primitives (`create_polygon()`, `create_line()`, etc.). To use PNG images instead, you'll need to:

1. Load PNG image files
2. Convert them to Tkinter PhotoImage objects
3. Display them using `create_image()` instead of drawing primitives
4. Handle rotation (provide 4 images or rotate programmatically)

## Approach 1: Using 4 Pre-Rotated Images (Simpler)

This is easier because you provide separate PNG files for each direction the robot faces (North, East, South, West).

### Step 1: Prepare your PNG files

You need 4 PNG images:
- `robot_north.png` - robot facing North
- `robot_east.png` - robot facing East
- `robot_south.png` - robot facing South
- `robot_west.png` - robot facing West

Store them in a `robot_images/` folder in your Karel library directory.

### Step 2: Create a new `RobotImage` subclass or modify existing code

In `tkwindow.py`, add image loading at the top (uncomment PhotoImage):

```python
from tkinter import PhotoImage
from tkinter import Tk
# ... other imports ...
```

### Step 3: Modify the `RobotImage` class

Replace the coordinate-based drawing with image-based drawing:

```python
class RobotImage:
    rNumber = 0
    
    # Pre-loaded images (load once at startup)
    _imageCache = {}
    
    @classmethod
    def _loadImages(cls, image_dir="robot_images"):
        """Load all robot images once"""
        directions = {
            North: "robot_north.png",
            East: "robot_east.png", 
            South: "robot_south.png",
            West: "robot_west.png"
        }
        for direction, filename in directions.items():
            try:
                path = f"{image_dir}/{filename}"
                cls._imageCache[direction] = PhotoImage(file=path)
            except Exception as e:
                print(f"Error loading {path}: {e}")
    
    def __init__(self, street, avenue, direction, window, fill='blue', outline='black'):
        self._canvas = window._canvas
        self._street = street
        self._avenue = avenue
        self.scaleFactor = window._KarelWindow__scaleFactor
        self._scaler = window._scaleToPixels
        self.__scaleFactor = window._KarelWindow__scaleFactor
        self._place = self._scaler(street, avenue)
        
        self._direction = direction
        self._fill = fill
        self._outline = outline
        self.tag = "r" + str(RobotImage.rNumber)
        RobotImage.rNumber += 1
        
        # Load images on first robot creation
        if not RobotImage._imageCache:
            RobotImage._loadImages()
        
        self.__buildImage()
    
    def __buildImage(self):
        """Build image-based robot"""
        (x, y) = self._scaler(self._street, self._avenue)
        
        # Get the image for current direction
        image = RobotImage._imageCache.get(self._direction)
        if image:
            self._canvas.create_image(x, y, image=image, tag=self.tag)
        else:
            # Fallback: draw a simple circle if image not found
            size = 15
            self._canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=self._fill, outline=self._outline,
                tag=self.tag
            )
        
        self._x = x
        self._y = y
    
    def deleteAll(self):
        self._canvas.delete(self.tag)
    
    def move(self, amount):
        """Move robot forward"""
        (dx, dy) = _moveParameters[self._direction]
        self._street -= dy
        self._avenue += dx
        
        # Calculate new position
        (new_x, new_y) = self._scaler(self._street, self._avenue)
        
        # Move the image on canvas
        if self._canvas:
            self._canvas.move(self.tag, new_x - self._x, new_y - self._y)
            self._x = new_x
            self._y = new_y
    
    def rotate(self):
        """Turn left (change direction and redraw)"""
        # Delete current image
        if self._canvas:
            self._canvas.delete(self.tag)
        
        # Update direction
        self._direction = _nextDirection[self._direction]
        
        # Redraw with new direction
        (x, y) = self._scaler(self._street, self._avenue)
        image = RobotImage._imageCache.get(self._direction)
        if image:
            self._canvas.create_image(x, y, image=image, tag=self.tag)
    
    def greyOut(self):
        """Dim the robot when it turns off"""
        # For images, you could either:
        # 1. Replace with a greyed-out version
        # 2. Change the opacity/outline
        # Simple approach: change outline color
        try:
            self._canvas.itemconfigure(self.tag, outline="grey")
        except:
            pass
    
    def setVisible(self, visible: bool):
        """Hide/show robot"""
        state = "normal" if visible else "hidden"
        try:
            self._canvas.itemconfigure(self.tag, state=state)
        except:
            pass
    
    # Remove or stub out these methods as they're no longer needed
    def scale(self, mult):
        pass
    
    def translate(self, horiz, vert):
        pass
    
    def moveScale(self, newScaleFactor):
        """Handle window resize"""
        (x, y) = self._scaler(self._street, self._avenue)
        if self._canvas:
            self._canvas.move(self.tag, x - self._x, y - self._y)
            self._x = x
            self._y = y
```

### Step 4: Remove the coordinate definitions

Delete or comment out all the `karelRobot`, `alienRobot`, and `crabRobot` coordinate lists since you're no longer using them.

---

## Approach 2: Using PIL to Rotate Images Dynamically (More Complex)

If you want to provide only one image and have Python rotate it automatically:

### Install PIL:
```bash
pip install Pillow
```

### Modified code:

```python
from PIL import Image, ImageTk
import os

class RobotImage:
    rNumber = 0
    _imageCache = {}
    
    @classmethod
    def _loadImage(cls, image_path):
        """Load and cache image"""
        if image_path not in cls._imageCache:
            try:
                img = Image.open(image_path)
                # Resize to reasonable size (e.g., 50x50 pixels)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                cls._imageCache[image_path] = img
            except Exception as e:
                print(f"Error loading {image_path}: {e}")
                return None
        return cls._imageCache[image_path]
    
    def __init__(self, street, avenue, direction, window, fill='blue', outline='black', image_path="robot.png"):
        # ... existing setup code ...
        self._image_path = image_path
        self._pil_image = self._loadImage(image_path)
        self._tk_images = {}  # Cache rotated versions
        # ... rest of init ...
    
    def _getRotatedImage(self, direction):
        """Get image rotated for given direction"""
        if direction not in self._tk_images:
            # Rotate: North=0°, East=270°, South=180°, West=90°
            rotations = {
                North: 0,
                East: 270,
                South: 180,
                West: 90
            }
            angle = rotations[direction]
            
            # Rotate PIL image
            rotated = self._pil_image.rotate(-angle, expand=False)
            # Convert to PhotoImage
            self._tk_images[direction] = ImageTk.PhotoImage(rotated)
        
        return self._tk_images[direction]
    
    def __buildImage(self):
        """Build image-based robot"""
        (x, y) = self._scaler(self._street, self._avenue)
        image = self._getRotatedImage(self._direction)
        self._canvas.create_image(x, y, image=image, tag=self.tag)
        self._x = x
        self._y = y
```

---

## Considerations & Challenges

### 1. **Image Size**
- PNG images are fixed size, so they may not scale well when the window size changes
- Consider creating images at different resolutions or resizing programmatically

### 2. **Rotation**
- **4 images approach**: Simplest, just provide North/East/South/West versions
- **PIL rotation**: More flexible, needs PIL library, slightly slower

### 3. **Performance**
- Loading images from disk is slower than drawing primitives
- Solution: Load images once at startup (as shown in code above)

### 4. **Transparency**
- PNG supports transparency, which is helpful for non-rectangular robot shapes
- Make sure background of PNG is transparent

### 5. **Beeper & Wall Rendering**
- This only affects robot rendering
- Beepers and walls still use the coordinate-based drawing system
- They're drawn separately, so no conflict

### 6. **Color Parameters**
- The `fill` and `outline` parameters passed to `UrRobot` constructor won't affect PNG images
- If you need color variations, either:
  - Generate multiple colored PNGs
  - Use PIL to dynamically colorize images
  - Ignore the color parameters when using images

---

## Recommended Approach for Your Use Case

For a classroom library, I'd recommend **Approach 1 (4 pre-rotated images)** because:
- ✅ Simpler to implement
- ✅ No external dependencies (PIL already optional)
- ✅ Faster performance
- ✅ Easy for students to create their own robot images
- ✅ No compatibility issues

Students could create 4 PNG images (North, East, South, West) and drop them in a folder.

---

## Example File Structure

```
karel/
├── tkwindow.py (modified)
├── robota.py
├── ... other files ...
└── robot_images/
    ├── robot_north.png
    ├── robot_east.png
    ├── robot_south.png
    └── robot_west.png
```

Then initialize with:
```python
RobotImage._loadImages("robot_images")
```

---

## Testing Your Implementation

Once you've made the changes:

```python
from karel.robota import *

world.setSize(8, 8)
world.setDelay(20)

bob = UrRobot(4, 2, East, 7)

for i in range(4):
    bob.move()
    bob.turnLeft()

bob.turnOff()
```

The robot should display using your PNG images instead of the drawn graphics!
