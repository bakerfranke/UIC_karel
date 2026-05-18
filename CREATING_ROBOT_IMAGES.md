# How to Create Your Own Robot Drawing

## Understanding How Coordinates Become Drawings

The coordinate lists in the robot definitions are interpreted by **drawing methods** that determine what shape each list becomes. Here's how it works:

### For `showKarel()` method (Karel robot):

| List Index | What It Draws | How |
|-----------|---------------|-----|
| `image[0]` | **Head** (grey) | `create_polygon()` - connects all points to form a closed shape |
| `image[1]` | **Body** (robot's fill color) | `create_polygon()` |
| `image[2]` & `image[3]` | **Two feet** (red) | `create_polygon()` - two separate foot shapes |
| `image[4]` & `image[5]` | **Two arms** (green) | `create_polygon()` |
| `image[6]` & `image[7]` | **Two eyes** (blue) | `create_rectangle()` - uses 2 points as diagonal corners |
| `image[8]`, `image[9]`, `image[10]` | **Letter "K"** (black lines) | `create_line()` - 2 points = one line segment |

### For `showAlien()` method (Alien & Crab robots):

| List Index | What It Draws | How |
|-----------|---------------|-----|
| `image[0]` | **Body** (robot's fill color) | `create_polygon()` - smooth curved shape |
| `image[1]` | **Left eye** | `create_oval()` - 2 points define bounding box |
| `image[2]` | **Right eye** | `create_oval()` |

---

## Understanding Coordinate Lists

All coordinates are **relative to (0, 0) at the center** of the robot.

### Example: Karel's head (first list)
```python
[   
    (-6,-10), #poly grey head
    (6,-10),
    (6,-3),
    (-6,-3)
]
```

This is a **polygon** with 4 corner points:
- Top-left: (-6, -10)
- Top-right: (6, -10)
- Bottom-right: (6, -3)
- Bottom-left: (-6, -3)

When connected, this creates a rectangle. The polygon connects points in order and closes automatically.

### Example: Alien's body (first list)
```python
[
    (0, -1),
    (0, 1),
    (-3, 3), 
    (0, 1),
    (3, 3),
    (0, 1),
    (0, -1),
    (2, -1),
    (2, -2),
    (0, -3),
    (-2, -2),
    (-2, -1)
]
```

This is a polygon with 12 points that forms an alien head when connected.

### Example: Eyes (rectangles)
```python
[ (-3, -7), (-1, -5)]
```

For a rectangle, you provide **2 diagonal corner points**: 
- (x1, y1) = top-left corner
- (x2, y2) = bottom-right corner

This creates a rectangle from (-3, -7) to (-1, -5).

### Example: Eyes (ovals)
```python
[(-1, -2), (0, -1)]
```

For an oval/circle, same as rectangle—2 diagonal corner points that define the bounding box.

### Example: Lines (K marking)
```python
[(-2, -1), (-2, 7)]
```

A line just has 2 points: start and end.

---

## Creating Your Own Robot

### Step 1: Choose a drawing method
Decide which `show` method to use:
- **`showKarel`** if you want the full Karel structure (head, body, feet, arms, eyes, K)
- **`showAlien`** if you want a simpler design (body polygon + 2 eyes)

### Step 2: Create your coordinate lists

For `showKarel` (must have exactly 11 lists):
```python
myRobot = [
    [(-5,-8), (5,-8), (5,-2), (-5,-2)],          # image[0]: head polygon
    [(-4,-2), (4,-2), (4,-1), (6,-1), (6,7), (-6,7), (-6,-1), (-4,-1)],  # image[1]: body polygon
    [(-5,7), (-1,7), (-1,10), (-5,10)],          # image[2]: left foot polygon
    [(1,7), (5,7), (5,10), (1,10)],              # image[3]: right foot polygon
    [(-7,0), (-5,0), (-5,5), (-7,5)],            # image[4]: left arm polygon
    [(7,0), (5,0), (5,5), (7,5)],                # image[5]: right arm polygon
    [(-2,-5), (-1,-4)],                          # image[6]: left eye rectangle
    [(1,-5), (2,-4)],                            # image[7]: right eye rectangle
    [(-1,0), (-1,4)],                            # image[8]: K part 1 line
    [(-1,2), (2,0)],                             # image[9]: K part 2 line
    [(-1,2), (2,4)]                              # image[10]: K part 3 line
]
```

For `showAlien` (must have exactly 3 lists):
```python
myRobot = [
    [(0,-3), (-4,-1), (-3,0), (-4,4), (-1,4), (-1,1), (1,1), (1,4), (4,4), (3,0), (4,-1), (0,-3)],  # body polygon
    [(-2,-2), (-1,-1)],  # left eye oval
    [(1,-2), (2,-1)]     # right eye oval
]
```

### Step 3: Register it

```python
class RobotImage:
    # ... existing code ...
    myCustomRobot = [...]  # your lists
    
    def __init__(self, ...):
        # ... existing code ...
        self.myPackage = {"size":23, "draw":self.showKarel, "figure":RobotImage.myCustomRobot}
        # ... rest of code ...
        package = self.myPackage  # Change this line to use your robot
```

---

## Tips for Creating Drawings

1. **Use a coordinate grid**: Sketch your robot on graph paper first
2. **Keep symmetry**: Use matching positive/negative coordinates for symmetrical parts
3. **Scale appropriately**: 
   - For `showKarel` robots: use size 23, coordinates roughly -8 to 8
   - For `showAlien` robots: use size 6, coordinates roughly -3 to 3
4. **Test with `showAlien`**: It's simpler (fewer lists) so easier to debug
5. **Use tools**: You could write a small Python script to visualize your coordinate list before committing it

---

## Example: Creating a Simple Star Robot

Using `showAlien` (simple body + 2 eyes):

```python
starRobot = [
    # Star body - 10 points making a star shape
    [
        (0, -6),     # top point
        (2, -2),     # top right
        (6, -2),     # right point
        (3, 0),      # inner right
        (4, 4),      # bottom right
        (0, 2),      # inner bottom
        (-4, 4),     # bottom left
        (-3, 0),     # inner left
        (-6, -2),    # left point
        (-2, -2)     # top left
    ],
    [(-1, -3), (0, -2)],   # left eye
    [(1, -3), (2, -2)]     # right eye
]
```

This creates a star shape for the body with two eye ovals.

---

## Debugging Your Drawing

If your robot doesn't look right:
1. Check that you have the correct number of lists
2. Verify coordinates are within expected ranges (±8 for size 23, ±3 for size 6)
3. Make sure polygon lists have at least 3 points
4. Ensure line and rectangle/oval lists have exactly 2 points
5. Test with simple shapes first (rectangles) before complex polygons
