""" Copyright 2008 Joseph Bergin
License: Creative Commons Attribution-Noncommercial-Share Alike 3.0 United States License
"""
from tkinter import Tk
from tkinter import mainloop
from tkinter import Label
from tkinter import Frame
from tkinter import Button
from tkinter import PhotoImage
from tkinter import Canvas
from tkinter import Scale
from tkinter import IntVar
from tkinter import Menu
from tkinter import Text
from tkinter import Scrollbar
import os
import re

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available. Images may appear very large. Install with: pip install Pillow")

from karel.basicdefinitions import North
from karel.basicdefinitions import East
from karel.basicdefinitions import South
from karel.basicdefinitions import West
from karel.basicdefinitions import _nextDirection

#from tkFont import Font
from tkinter.font import Font

from time import sleep
import threading

#from tkconstants import *

_moveParameters = {North: (0, -1), West: (-1, 0), South: (0, 1), East:(1, 0) }

_windowBottom = 600 #800
_windowRight = 800
_inset = 30
_basicSize = 23 #pixel count of robot image bounding box

class RobotImage:
    rNumber = 0
    _pilImages = {}      # Cache for original PIL images
    _photoImages = {}    # Cache for converted PhotoImage objects
    _greyPhotoImages = {}  # Cache for greyscale versions
    _alphaPhotoImages = {}  # Cache for semi-transparent versions
    _scaleFactor = 1.0   # Current scale factor for the window
    _defaultCostume = 'karel'  # Default costume (can be changed via world.setRobotCostume)
    _lastCostume = None  # Most recently seen costume, from ANY robot (ctor or setCostume) -
                         # used to pick the ground-beeper marker's image, since that's a
                         # world-level visual with no single "owning" robot to ask.
    _crashPilImage = None       # The loaded crash.png, before resizing
    _crashPhotoCache = {}       # Resized crash PhotoImages, keyed by size

    @classmethod
    def _loadImages(cls, costume="karel", image_dir="robot_images"):
        """Load all images for a costume. The four directional images (_north/_south/
        _east/_west) are required - a missing or broken one prints a Warning. Three
        more suffixes (_crash/_beeper/_turnOff) are optional per-costume overrides for
        the crash image, the ground-beeper marker, and the turned-off look - crashOut(),
        the world's beeper markers, and greyOut() all fall back to the library's generic
        crash.png / black-circle / auto-greyscale look when a costume doesn't supply its
        own, so a missing extra is never reported (only a broken/corrupt one is)."""
        cache_key = costume
        if cache_key in cls._pilImages:  # Already loaded
            return

        # Try local folder first (where main program runs)
        local_images_path = os.path.join(os.getcwd(), image_dir)

        # Fall back to library folder (inside karel module)
        karel_dir = os.path.dirname(os.path.abspath(__file__))
        library_images_path = os.path.join(karel_dir, image_dir)

        required = {
            North: f"{costume}_north.png",
            East: f"{costume}_east.png",
            South: f"{costume}_south.png",
            West: f"{costume}_west.png"
        }
        optional = {
            'crash': f"{costume}_crash.png",
            'beeper': f"{costume}_beeper.png",
            'turnOff': f"{costume}_turnOff.png",
        }

        # Create nested dict for this costume
        cls._pilImages[cache_key] = {}
        cls._photoImages[cache_key] = {}

        missing = []
        errors = []

        def _tryLoad(key, filename, isRequired):
            local_path = os.path.join(local_images_path, filename)
            library_path = os.path.join(library_images_path, filename)

            path = None
            if os.path.exists(local_path):
                path = local_path
            elif os.path.exists(library_path):
                path = library_path

            if path:
                try:
                    if PIL_AVAILABLE:
                        cls._pilImages[cache_key][key] = Image.open(path)
                    else:
                        cls._photoImages[cache_key][key] = PhotoImage(file=path)
                except Exception as e:
                    errors.append(f"{filename} ({e})")
            elif isRequired:
                missing.append(filename)

        for direction, filename in required.items():
            _tryLoad(direction, filename, isRequired=True)
        for key, filename in optional.items():
            _tryLoad(key, filename, isRequired=False)

        # Silent on success - only speak up if this costume didn't fully load.
        if missing or errors:
            problems = []
            if missing:
                problems.append(f"missing: {', '.join(missing)}")
            if errors:
                problems.append(f"failed to load: {', '.join(errors)}")
            print(
                f"Warning: costume '{costume}' did not load correctly ({'; '.join(problems)}). "
                f"Checked '{image_dir}/' next to your program and the library's own '{image_dir}/' folder."
            )

    @classmethod
    def _getResizedImage(cls, costume, direction, size, greyscale=False, alpha=None):
        """Get a resized PhotoImage for the given robot, direction and size

        Args:
            alpha: Optional alpha transparency value (0-255). If provided, creates a semi-transparent image.
        """
        if not PIL_AVAILABLE:
            return cls._photoImages.get(costume, {}).get(direction)

        # Choose cache based on flags - use a combined cache for both greyscale and alpha
        if greyscale and alpha is not None:
            cache_dict = cls._alphaPhotoImages  # Use alpha cache for combined effect
        elif greyscale:
            cache_dict = cls._greyPhotoImages
        elif alpha is not None:
            cache_dict = cls._alphaPhotoImages
        else:
            cache_dict = cls._photoImages

        # Create cache key that includes both flags
        cache_key = (costume, direction, size, greyscale, alpha)

        if cache_key not in cache_dict:
            # Resize the PIL image
            pil_img = cls._pilImages.get(costume, {}).get(direction)
            if pil_img is None:
                return None
            resized = pil_img.resize((size, size), Image.Resampling.LANCZOS)

            # Convert to RGBA first to preserve/create alpha channel
            if resized.mode != 'RGBA':
                resized = resized.convert('RGBA')

            # Save the original alpha channel
            original_alpha = resized.split()[3]

            # Convert to greyscale if requested
            if greyscale:
                from PIL import ImageOps
                resized = ImageOps.grayscale(resized)
                resized = resized.convert('RGBA')
                resized.putalpha(original_alpha)

            # Apply alpha transparency if requested
            if alpha is not None:
                alpha_channel = resized.split()[3]
                alpha_channel = alpha_channel.point(lambda x: int(x * alpha / 255))
                resized.putalpha(alpha_channel)

            # Convert to PhotoImage
            cache_dict[cache_key] = ImageTk.PhotoImage(resized)

        return cache_dict.get(cache_key)

    @classmethod
    def _loadCrashImage(cls, image_dir="robot_images"):
        """Preload crash.png (shown when a robot performs an illegal action), same
        local-folder-then-library-folder lookup as costume images. Unlike costumes this
        is a single static image, not one per direction."""
        if cls._crashPilImage is not None or not PIL_AVAILABLE:
            return

        local_path = os.path.join(os.getcwd(), image_dir, "crash.png")
        karel_dir = os.path.dirname(os.path.abspath(__file__))
        library_path = os.path.join(karel_dir, image_dir, "crash.png")

        path = local_path if os.path.exists(local_path) else (
            library_path if os.path.exists(library_path) else None)

        if path:
            try:
                cls._crashPilImage = Image.open(path)
            except Exception as e:
                print(f"Warning: crash.png did not load correctly ({e})")
        else:
            print(f"Warning: Could not find crash.png in local '{image_dir}/' or the library's own '{image_dir}/' folder")

    @classmethod
    def _getCrashImage(cls, size):
        """Get a resized PhotoImage of the crash image at the given size."""
        if not PIL_AVAILABLE or cls._crashPilImage is None:
            return None
        if size not in cls._crashPhotoCache:
            resized = cls._crashPilImage.resize((size, size), Image.Resampling.LANCZOS)
            if resized.mode != 'RGBA':
                resized = resized.convert('RGBA')
            cls._crashPhotoCache[size] = ImageTk.PhotoImage(resized)
        return cls._crashPhotoCache[size]

    def __init__(self, street, avenue, direction, window, fill='blue', outline='black', costume=None):
        self._canvas = window._canvas
        self._street = street
        self._avenue = avenue
        self.scaleFactor = window._KarelWindow__scaleFactor
        self._scaler = window._scaleToPixels
        self.__scaleFactor = window._KarelWindow__scaleFactor
        self._place = self._scaler(street, avenue)

        self._direction = direction
        # Use provided costume or fall back to class default
        self._costume = costume if costume else RobotImage._defaultCostume
        RobotImage._lastCostume = self._costume
        if fill == None:
            fill = "yellow"
        self._fill = fill
        self._outline = outline
        self.tag = "r"+str(RobotImage.rNumber)
        RobotImage.rNumber += 1

        # Load images for this costume (use converted value with default)
        RobotImage._loadImages(self._costume)

        self._x = 0
        self._y = 0
        self._isGreyed = False  # Track greyed-out state
        self._isTransparent = False  # Track if robot should be semi-transparent (for visibility over beepers)
        self._isCrashed = False  # Track whether this robot crashed (illegal action)
        self.__buildImage()
        

    def deleteAll(self):
        self._canvas.delete(self.tag)

        
    def greyOut(self):
        """Dim the robot when it turns off - make it greyscale and semi-transparent"""
        self._isGreyed = True
        self._isTransparent = True  # Also make semi-transparent
        # Delete the current image on canvas
        if self._canvas:
            self._canvas.delete(self.tag)
        # Redraw with greyscale and transparency
        self.__buildImage()

    def crashOut(self):
        """Show the crash image - a robot performed an illegal action (hit a wall,
        picked up a beeper that wasn't there, or put down a beeper it didn't have)."""
        self._isCrashed = True
        if self._canvas:
            self._canvas.delete(self.tag)
        self.__buildImage()

    def setTransparent(self, transparent):
        """Make the robot semi-transparent to show beepers beneath it"""
        self._isTransparent = transparent
        # Delete the current image on canvas
        if self._canvas:
            self._canvas.delete(self.tag)
        # Redraw with appropriate transparency
        self.__buildImage()

    def setCostume(self, costume):
        """Change this robot's costume (image) on the fly."""
        self._costume = costume
        RobotImage._lastCostume = costume
        RobotImage._loadImages(self._costume)
        if self._canvas:
            self._canvas.delete(self.tag)
        self.__buildImage()

    def move(self, amount):
        """Move robot forward in current direction"""
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
        """Turn left (change direction and redraw image)"""
        # Delete current image
        if self._canvas:
            self._canvas.delete(self.tag)

        # Update direction
        self._direction = _nextDirection[self._direction]

        # Redraw with new direction
        self.__buildImage()

    def scale(self, mult):
        """Placeholder for compatibility"""
        pass

    def translate(self, horiz, vert):
        """Placeholder for compatibility"""
        pass

    def setVisible(self, visible: bool):
        """Hide/show robot"""
        state = "normal" if visible else "hidden"
        try:
            self._canvas.itemconfigure(self.tag, state=state)
        except:
            pass

    def moveScale(self, newScaleFactor):
        """Handle window resize by redrawing at new position"""
        if self._canvas:
            self._canvas.delete(self.tag)
        self.__scaleFactor = newScaleFactor
        self.__buildImage()

    def __buildImage(self):
        """Build the robot image at current position and direction"""
        (x, y) = self._scaler(self._street, self._avenue)

        # Calculate appropriate image size (65% of grid square)
        image_size = max(10, int(self.__scaleFactor * 0.85))

        if self._isCrashed:
            # Illegal action - show this costume's own _crash image if it has one,
            # otherwise the library's generic crash.png - regardless of
            # direction/greyed/transparent state.
            image = RobotImage._getResizedImage(self._costume, 'crash', image_size)
            if image is None:
                image = RobotImage._getCrashImage(image_size)
        elif self._isGreyed and RobotImage._pilImages.get(self._costume, {}).get('turnOff') is not None:
            # This costume has its own turned-off look - use it as-is (still subject to
            # the same semi-transparency as the auto-greyscale fallback below) instead
            # of graying out the normal directional image.
            alpha = 150 if self._isTransparent else None
            image = RobotImage._getResizedImage(self._costume, 'turnOff', image_size, alpha=alpha)
        elif PIL_AVAILABLE:
            # Get the resized image for current direction, with greyscale if needed
            # Use semi-transparent (150/255 alpha ≈ 59%) if transparent flag is set
            alpha = 150 if self._isTransparent else None
            image = RobotImage._getResizedImage(self._costume, self._direction, image_size, greyscale=self._isGreyed, alpha=alpha)
        else:
            image = RobotImage._photoImages.get(self._costume, {}).get(self._direction)

        if image:
            self._canvas.create_image(x, y, image=image, tag=self.tag)
        else:
            # Fallback: draw a chevron/arrow pointing in the robot's direction
            size = image_size // 2.5
            point_offset = int(size * 0.6)  # How much the point sticks out beyond the edge
            indent = int(size * 0.3)  # How much the left side indents

            # Visual centering adjustments - tweak these to center chevron visually on the grid
            # (negative values = up/left, positive values = down/right)
            adjust_x = 0
            adjust_y = 0
            if self._direction == North:
                adjust_y = 0  # nudge up/down for North-pointing chevron
            elif self._direction == East:
                adjust_x = 0  # nudge left/right for East-pointing chevron
            elif self._direction == South:
                adjust_y = 0  # nudge up/down for South-pointing chevron
            else:  # West
                adjust_x = 0  # nudge left/right for West-pointing chevron

            # Apply adjustments to center position
            cx = x + adjust_x
            cy = y + adjust_y

            # Create chevron points based on direction
            if self._direction == North:
                # Point up
                points = [
                    cx + size, cy - size,              # top-right
                    cx + size, cy + size,              # bottom-right
                    cx, cy + indent,     # bottom indent
                    cx - size, cy + size,              # bottom-left
                    cx - size, cy - size,              # top-left
                    cx, cy - size - point_offset              # top point
                ]
            elif self._direction == East:
                # Point right
                points = [
                    cx - size, cy - size,              # top-left
                    cx + size, cy - size,              # top-right
                    cx + size + point_offset, cy,     # right point
                    cx + size, cy + size,              # bottom-right
                    cx - size, cy + size,              # bottom-left
                    cx - indent, cy                    # left indent
                ]
            elif self._direction == South:
                # Point down
                points = [
                    cx - size, cy - size,              # top-left
                    cx, cy - indent,                     # top-indent
                    cx + size, cy - size,              # top-right
                    cx + size, cy + size,              # bottom-right
                    cx, cy + size + point_offset,     # bottom point
                    cx - size, cy + size              # bottom-left

                ]
            else:  # West
                # Point left
                points = [
                    cx + size, cy - size,              # top-right
                    cx - size, cy - size,              # top-left
                    cx - size - point_offset, cy,     # left point
                    cx - size, cy + size,              # bottom-left
                    cx + size, cy + size,              # bottom-right
                    cx + indent, cy                    # right indent
                ]

            # Determine colors based on state
            if self._isGreyed:
                chevron_fill = 'grey'
                chevron_outline = 'darkgrey'
            elif self._isTransparent:
                # Use lighter color for transparency effect
                chevron_fill = 'lightgrey'
                chevron_outline = 'grey'
            else:
                chevron_fill = self._fill
                chevron_outline = self._outline

            self._canvas.create_polygon(
                points,
                fill=chevron_fill, outline=chevron_outline,
                width=2,
                tag=self.tag
            )

        self._x = x
        self._y = y
         

class KarelWindow(Frame):
    def __init__(self, streets, avenues, callback = None): # avenues is ignored in this version
        self.__root = root = Tk(className=" Karel's World 2.0") # , geometry='800x600+60+10'
        root.geometry(newGeometry='820x650+55+10') # placement of window on desktop
        #root.geometry(newGeometry='600x600+55+25')
#        print (str(root.tk_menuBar()))
        Frame.__init__(self, master=root, cnf={})
        global _windowBottom
        global _windowRight
        global _inset
        #root.minsize(_windowBottom, _windowRight)
        root.minsize(500,500)
        root.resizable(True, True)  # Allow window resizing
        #print(_windowBottom, _windowRight, "resizeable TRUE")
        self.__bottom = _windowBottom - _inset #770
        self.__left = _inset #30
        self.__top = _inset #30
        self.__right = _windowRight - _inset #770
        self.__scaleFactor = (self.__bottom - self.__top)*1.0/streets

        self.is_paused = False  # Start running by default (matches pre-pause/step behavior); call world.startPaused(True) to start paused instead
        self._loadingWorldFile = False  # True only while RobotWorld.readWorld() is running - see Beeper.place()
        self.allow_one_step = False  # Flag for stepping one action at a time
        self._startup_delay = 1500  # Give the window a moment to fully render before the
        # robot's first action, so it isn't 1-2 steps in before it's even visible. One-time
        # only (see _first_action) - not repeated on later pause/resume. Override with
        # world.resume(delay_ms=...) or world.startPaused(False, delay_ms=...).
        self._first_action = True  # Track if this is the first robot action
        self._program_finished = False  # Track if robot has turned off
        self._pauseOverlayRect = None  # Draggable "Paused" banner, created on demand
        RobotImage._loadCrashImage()  # Preload crash.png now so there's no lag when a robot actually crashes

        bar = Menu()        
        def endProgram(menu): exit()
        
        fil = Menu()
        fil.add_command(label = 'Quit   ^Q', command=lambda x='Quit':endProgram(x))
        bar.add_cascade(label='File', menu=fil)
        root.config(menu=bar)
        self.bind_all('<Command-q>', exit) # Mac standard
        self.bind_all('<Control-q>', exit) # Windows
        self.__streets = streets
        self.__avenues = avenues
        self.__gBeepers = {} #locations of the beeper images
        self.__contents = [] # robots, walls, beepers that need to move on a rescale
        self.__beeperControl = threading.Condition() # helps multi threaded programs avoid anomalies
        self.__walls = [] # all the basic visual elements (boundary, streets, street labels, etc. 
        
#        self.nametowidget(" Karel's World ")
        # Let the frame fill the root window, and let the canvas (row 1) absorb
        # extra space on resize while the toolbar row (row 0) stays its natural size.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.grid(sticky="news")
        # Equal-weight spacer columns on both sides of Speed keep it centered as the window resizes.
        self.columnconfigure(3, weight=1)
        self.columnconfigure(6, weight=1)
        self.rowconfigure(2, weight=1)

        speedLabel = Label(self, text = "Speed")
        speedLabel.grid(row=0, column=4, sticky="es") #added params from chatgpt

        # Status banner - shows Running/Paused normally, and a crash or any uncaught error
        # (with an attention-grabbing red background) so it's obvious without having to
        # tab over to the console.
        self.status_label = Label(self, text="", font=("Arial", 11, "bold"), padx=6)
        self.status_label.grid(row=0, column=3)
        self._crashed = False  # once True, status stays on the crash message
        (self.showPausedStatus if self.is_paused else self.showRunningStatus)()

        # Message bar - full-width row below the toolbar, for the crash message. Unlike
        # status_label above (narrow, squeezed next to Speed), this row spans the whole
        # window so a long message never gets clipped. Hidden (zero height, not reserved)
        # until there's actually a message to show; showCrashMessage() grids it in and
        # grows the window downward to make room, rather than shrinking anything else.
        self.message_label = Label(
            self, text="", font=("Arial", 11, "bold"), anchor="w", padx=8, pady=3
        )
        self._messageBarReservedHeight = 0

        #|   0   |  1   |    2     |     3      |   4   |   5   |   6    |
        #|  RUN  | STEP | RESTART  |  STATUS    |  LBL  | SLID  | EMPTY  |
        #|                    MESSAGE BAR (row 1, hidden unless in use)          |

        if callback != None : # this makes the speed slider work.

            from tkinter import IntVar, Button
            self.iv = IntVar()
            self.iv.trace('r', callback)

            self.scale = Scale(self, orient = "horizontal", variable = self.iv, length=160)
            self.scale.set(20)
            self.scale.grid(row=0, column=5, sticky="e", padx=5)

            # Add Run/Pause button
            # Label reflects the actual starting state (running by default, or paused if world.startPaused(True) was called)
            self.play_pause_btn = Button(
                self,
                text="▶ Run" if self.is_paused else "⏸ Pause",
                command=self.toggle_play_pause,
                width=10,
                font=("Arial", 12, "bold")
            )
            self.play_pause_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=3)

            # Add Step button
            self.step_btn = Button(
                self,
                text="⏭ Step",
                command=self.step_once,
                width=10,
                font=("Arial", 11, "bold")
            )
            self.step_btn.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

            # Add Restart button - re-runs the program from the top in a fresh process,
            # so a student doesn't have to tab away to their editor and hit Run again.
            self.restart_btn = Button(
                self,
                text="↻ Restart",
                command=self.restart_program,
                width=10,
                font=("Arial", 11, "bold")
            )
            self.restart_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=3)

            # Stats tray toggle - column 7, to the right of everything else. Square icon
            # button, no text needed to keep it small; the arrows hint at which way it slides.
            self.stats_btn = Button(
                self,
                text="\U0001F4CA>>",
                command=self.toggleStatsTray,
                width=4,
                font=("Arial", 11, "bold")
            )
            self.stats_btn.grid(row=0, column=7, sticky="ne", padx=(5, 0), pady=3)

        # Stats tray - hidden by default, column 7 (own column, doesn't touch the canvas's
        # columns 0-6 at all). Fixed pixel footprint (not derived from the Text widget's
        # char-width * font-size) via pack_propagate(False), so the +/- font buttons can't
        # blow out the layout or push the toggle button off the fixed-size window.
        self.statsTrayOpen = False
        self._statsFontSize = 18  # adjustable live via the -/+ buttons below
        self._trayReservedWidth = 0  # how much extra window width is currently reserved for the tray

        # Starting guess (20 chars, matching getStatsText()'s widest line as of this
        # writing) for before any real stats text has loaded - self-corrects to the
        # actual content's width the first time the tray opens. See _resizeStatsFrameToFit.
        _initialCharWidth = Font(family="Courier", size=self._statsFontSize).measure('0')
        self.stats_frame = Frame(self, width=21 * _initialCharWidth + 28, bg=self.cget('bg'))
        self.stats_frame.pack_propagate(False)

        self.stats_header = Label(
            self.stats_frame, text="Karel World Stats", font=("Arial", 11, "bold"),
            bg=self.cget('bg')
        )
        self.stats_header.pack(side="top", fill="x", pady=(4, 0))

        stats_toolbar = Frame(self.stats_frame, bg=self.cget('bg'))
        stats_toolbar.pack(side="top", fill="x", pady=(2, 4))
        Label(stats_toolbar, text=f"Font:", font=("Arial", 12), bg=self.cget('bg')).pack(side="left", padx=(6, 2))
        Button(stats_toolbar, text="-", command=self._shrinkStatsFont, width=2, font=("Arial", 12, "bold")).pack(side="left")
        Button(stats_toolbar, text="+", command=self._growStatsFont, width=2, font=("Arial", 12, "bold")).pack(side="left", padx=(2, 0))

        stats_body = Frame(self.stats_frame)
        stats_body.pack(side="top", fill="both", expand=True)

        stats_scrollbar = Scrollbar(stats_body)
        stats_scrollbar.pack(side="right", fill="y")

        self.stats_text = Text(
            stats_body, width=25, font=("Courier", self._statsFontSize), state="disabled",
            bg=self.cget('bg'), relief="flat", padx=6, pady=4,
            yscrollcommand=stats_scrollbar.set
        )
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scrollbar.config(command=self.stats_text.yview)

        #BEF TODO: make the canvas and window scaled to the actual number of streets and avenues?
        self._canvas = Canvas(self, height = _windowBottom, width = _windowRight, bg = 'white')
        self._canvas.grid(row=2, column=0, columnspan=7, sticky="news")
        self.setSize(streets, avenues)
        self.placeBeeper = self.placeBeepers

        # Rescale everything when the user resizes the window, so the grid keeps
        # filling the available canvas space instead of staying pinned to the
        # size it was created at.
        self._lastCanvasSize = (self._canvas.winfo_reqwidth(), self._canvas.winfo_reqheight())
        self._canvas.bind('<Configure>', self._on_canvas_resize)


#        self.__streets = streets
#        self.makeStreetsAndAvenues()
#        self.makeBoundaryWalls()
#        self.labelStreetsAvenues()
        
    def toggle_play_pause(self):
        if self.is_paused:
            # Resume execution (Run -> Pause)
            self.is_paused = False
            self.play_pause_btn.config(text="⏸ Pause")
            self.hidePausedOverlay()
            self.showRunningStatus()
        else:
            # Pause execution (Pause -> Run)
            self.is_paused = True
            self.play_pause_btn.config(text="▶ Run")
            self.showPausedOverlay()
            self.showPausedStatus()

    def showPausedOverlay(self):
        """Show a draggable, semi-transparent 'Paused' banner over the middle of the grid."""
        if getattr(self, '_pauseOverlayRect', None) is not None:
            return  # already showing

        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w < 20 or h < 20:  # canvas not mapped/sized yet - fall back to the design size
            w, h = _windowRight, _windowBottom

        boxWidth, boxHeight = 180, 70
        x0, y0 = (w - boxWidth) / 2, (h - boxHeight) / 2
        x1, y1 = x0 + boxWidth, y0 + boxHeight
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

        if PIL_AVAILABLE:
            # Real 50% alpha + rounded corners, via a small generated RGBA image
            # (same technique already used for greyed-out/semi-transparent robots).
            from PIL import ImageDraw
            img = Image.new('RGBA', (boxWidth, boxHeight), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            box = [1, 1, boxWidth - 2, boxHeight - 2]
            if hasattr(draw, 'rounded_rectangle'):  # Pillow >= 8.2
                draw.rounded_rectangle(box, radius=16, fill=(200, 0, 0, 102), outline=(0, 0, 0, 200), width=2)
            else:
                draw.rectangle(box, fill=(200, 0, 0, 102), outline=(0, 0, 0, 200), width=2)
            self._pauseOverlayPhoto = ImageTk.PhotoImage(img)
            self._pauseOverlayRect = self._canvas.create_image(
                cx, cy, image=self._pauseOverlayPhoto, tags=('pauseOverlay',)
            )
        else:
            # Fallback when Pillow isn't installed: a plain (non-rounded, stippled) rectangle.
            self._pauseOverlayRect = self._canvas.create_rectangle(
                x0, y0, x1, y1, fill='#C80000', stipple='gray50', outline='black', width=2,
                tags=('pauseOverlay',)
            )

        self._pauseOverlayText = self._canvas.create_text(
            cx, cy, text='⏸ Paused', font=('Arial', 16, 'bold'),
            fill='black', tags=('pauseOverlay',)
        )
        self._canvas.tag_raise('pauseOverlay')
        self._canvas.tag_bind('pauseOverlay', '<ButtonPress-1>', self._startDragPausedOverlay)
        self._canvas.tag_bind('pauseOverlay', '<B1-Motion>', self._dragPausedOverlay)

    def hidePausedOverlay(self):
        if getattr(self, '_pauseOverlayRect', None) is None:
            return
        self._canvas.delete('pauseOverlay')
        self._pauseOverlayRect = None
        self._pauseOverlayText = None
        self._pauseOverlayPhoto = None

    def _startDragPausedOverlay(self, event):
        self._pauseOverlayDragOrigin = (event.x, event.y)

    def _dragPausedOverlay(self, event):
        dx = event.x - self._pauseOverlayDragOrigin[0]
        dy = event.y - self._pauseOverlayDragOrigin[1]
        self._canvas.move('pauseOverlay', dx, dy)
        self._pauseOverlayDragOrigin = (event.x, event.y)

    def showRunningStatus(self):
        if self._crashed:
            return  # crash message takes priority and stays until the program restarts
        self.status_label.config(text="▶ Running", fg="#2e7d32", bg=self.cget('bg'))

    def showPausedStatus(self):
        if self._crashed:
            return
        self.status_label.config(text="⏸ Paused", fg="#b8860b", bg=self.cget('bg'))

    def showCrashMessage(self, message="⚠ Program crashed - check the console"):
        """Show a persistent message in the full-width message bar below the toolbar -
        no popup, no extra click - so a crash or uncaught error is obvious even though
        the console isn't visible. Uses its own row (rather than status_label) so the
        message always has the whole window's width and never gets clipped."""
        self._crashed = True
        self.message_label.config(text=message, fg="white", bg="#c0392b")
        self.message_label.grid(row=1, column=0, columnspan=8, sticky="ew")
        self.update_idletasks()  # so winfo_reqheight() below reflects the just-added row
        self._growWindowForMessageBar(self.message_label.winfo_reqheight())

    def clearCrashMessage(self):
        self._crashed = False
        self.message_label.grid_remove()
        self._growWindowForMessageBar(0)
        self.showPausedStatus() if self.is_paused else self.showRunningStatus()

    def _growWindowForMessageBar(self, barHeight):
        """Grow (or shrink) the actual window by however much the message bar's reserved
        height changed, mirroring _growWindowForTray's approach for the stats tray -
        grows the window itself rather than relying on some other row shrinking to make
        room, so the canvas never gets squeezed when the bar appears."""
        delta = barHeight - self._messageBarReservedHeight
        if delta == 0:
            return
        root = self.__root
        root.update_idletasks()
        match = re.match(r'(\d+)x(\d+)([+-]\d+[+-]\d+)', root.geometry())
        if not match:
            return
        w, h, pos = int(match.group(1)), int(match.group(2)), match.group(3)
        root.geometry(f"{w}x{max(300, h + delta)}{pos}")
        self._messageBarReservedHeight = barHeight

    def toggleStatsTray(self):
        """Show/hide the stats sidebar. Only fetches/renders stats text while opening -
        while closed, world/robot action counting still happens (cheap counter increments)
        but nothing gets formatted or drawn."""
        if self.statsTrayOpen:
            self.stats_frame.grid_remove()
            self.stats_btn.config(text="\U0001F4CA>>")
            self.statsTrayOpen = False
            self._growWindowForTray(0)  # give the reserved width back
        else:
            self.stats_frame.grid(row=2, column=7, sticky="ns", padx=(5, 0))
            self.stats_btn.config(text="<<\U0001F4CA")
            self.statsTrayOpen = True
            from karel.tkworldadapter import world
            self.updateStatsText(world.getStatsText())  # also grows the window - see _resizeStatsFrameToFit

    def _growWindowForTray(self, trayWidth):
        """Grow (or shrink) the actual window by however much the tray's reserved width
        changed, instead of relying on the canvas having spare room to give up. That
        approach (canvas shrinks to make room) only works once the window is already
        wide enough - if the canvas is already at its minimum size (root.minsize()),
        there's nothing left to give, and the tray ends up under-sized until the window
        is manually resized."""
        delta = trayWidth - self._trayReservedWidth
        if delta == 0:
            return
        root = self.__root
        root.update_idletasks()
        match = re.match(r'(\d+)x(\d+)([+-]\d+[+-]\d+)', root.geometry())
        if not match:
            return
        w, h, pos = int(match.group(1)), int(match.group(2)), match.group(3)
        root.geometry(f"{max(500, w + delta)}x{h}{pos}")
        self._trayReservedWidth = trayWidth

    def _shrinkStatsFont(self):
        self._statsFontSize = max(8, self._statsFontSize - 2)
        self.stats_text.config(font=("Courier", self._statsFontSize))
        self._resizeStatsFrameToFit()

    def _growStatsFont(self):
        self._statsFontSize = min(32, self._statsFontSize + 2)
        self.stats_text.config(font=("Courier", self._statsFontSize))
        self._resizeStatsFrameToFit()

    def _resizeStatsFrameToFit(self, sampleText=None):
        """Size the tray to a tight fit around its widest line at the current font size,
        using the font's actual measured character width (not a guessed px-per-char
        ratio) so it comes out exact regardless of OS/font rendering differences."""
        if sampleText is None:
            sampleText = self.stats_text.get('1.0', 'end')
        maxChars = max((len(line) for line in sampleText.split('\n')), default=20)
        charWidth = Font(family="Courier", size=self._statsFontSize).measure('0')
        scrollbarAndPadding = 28  # room for the scrollbar plus the Text widget's own padx
        # +1 char of slack: Text widget line-wrapping measures slightly differently than
        # Font.measure() does, so a truly tight fit could still wrap by a character.
        newWidth = (maxChars + 1) * charWidth + scrollbarAndPadding
        self.stats_frame.config(width=newWidth)

        if self.statsTrayOpen:
            self._growWindowForTray(newWidth)

    def updateStatsText(self, text):
        """Replace the stats tray's content. Caller (RobotWorld) should only call this
        while the tray is actually open - see statsTrayOpen."""
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", text)
        self.stats_text.config(state="disabled")
        self._resizeStatsFrameToFit(text)

    def step_once(self):
        """Allow one robot action to execute, then pause again."""
        self.allow_one_step = True
        # Note: Do NOT change is_paused - keep it True
        # The allow_one_step flag will allow the next action to execute
        # Then is_paused will catch and pause again for subsequent actions

    def restart_program(self):
        """Re-run the current program from the top in a fresh process - same as closing
        this window and hitting Run again, just without leaving the graphics window."""
        import sys
        os.execv(sys.executable, [sys.executable] + sys.argv)


    #BEF NOTE: fix this so that we can have different streets and avenues.
    def setSize(self, streets, avenues = 10):         
        self.__streets = streets
        self.__avenues = avenues
        streetsScale = (self.__bottom - self.__top) / streets
        avenuesScale = (self.__right - self.__left) / avenues
        # self.__scaleFactor = min((self.__bottom - self.__top),(self.__right - self.__left)) *  1.0/max(streets,avenues)
        self.__scaleFactor = min(streetsScale, avenuesScale)

        # self.__streetScaleFactor = (self.__bottom - self.__top) * 1.0 / streets
        # self.__avenueScaleFactor = (self.__right - self.__left) * 1.0 / avenues
        
        for x in self.__walls : # boundary walls and street lines
            self._canvas.delete(x)
        self.makeStreetsAndAvenues()
        self.makeBoundaryWalls()
        self.labelStreetsAvenues()
        for item in self.__contents : #rebuild the contents of the world
            item.moveScale(self.__scaleFactor)

    def _on_canvas_resize(self, event):
        """Recompute scale and rebuild the grid when the canvas is resized (e.g. the user drags the window edge)."""
        if event.width < 20 or event.height < 20:
            return  # ignore degenerate sizes during initial layout
        if (event.width, event.height) == self._lastCanvasSize:
            return
        self._lastCanvasSize = (event.width, event.height)
        self.__bottom = event.height - _inset
        self.__right = event.width - _inset
        self.setSize(self.__streets, self.__avenues)

#    def drawArea(self):
#        return self._canvas
        
#    def delta(self):
#        return self.__scaleFactor
    
    class Beeper:
        def __init__(self, street, avenue, number, window):
            self._street = street
            self._avenue = avenue
            self._number = number
            self.__scaleFactor = window._KarelWindow__scaleFactor
            self._scaler = window._scaleToPixels
            self._code = 0 #identifies the text in the beeper
            self._rcode = 0 # identifies the oval beeper figure
            self._canvas = window._canvas
            self._window = window
            # Captured once, at creation - not re-checked on every place() call - so a
            # world-file beeper stays exempt from costume theming even across a later
            # moveScale() (e.g. from a window resize), by which point the window's
            # _loadingWorldFile flag has long since gone back to False.
            self._fromWorldFile = window._loadingWorldFile



            
        def place(self):
            sizeFactor = .6 #Change this to change beeper size. The others scale from it.
            placeFactor = .5 * sizeFactor
            val = str(self._number)
            if self._number < 0 :
                val = "oo"
            (x,y) = self._scaler(self._street+placeFactor, self._avenue-placeFactor)
            boxSize = self.__scaleFactor*sizeFactor

            # Use the active costume's own _beeper image if it has one, otherwise the
            # plain black circle. The beeper count is still drawn on top either way.
            # "Active" = whichever costume was most recently used by any robot (ctor or
            # setCostume()). Beepers loaded from a world file (readWorld()) are exempt -
            # a .kwld file describes layout data, not a themed look, so those always
            # render as the plain circle no matter what costume is active.
            costume = None if self._fromWorldFile else (RobotImage._lastCostume or RobotImage._defaultCostume)
            image = None
            if costume:
                RobotImage._loadImages(costume)  # no-op if already loaded/cached
                image = RobotImage._getResizedImage(costume, 'beeper', max(10, int(boxSize))) if PIL_AVAILABLE else None
            if image:
                self._rcode = self._canvas.create_image(x + boxSize / 2, y + boxSize / 2, image=image)
            else:
                self._rcode = self._canvas.create_oval(x, y, x + boxSize, y + boxSize, fill= 'black')
            self._code = self._canvas.create_text(x + self.__scaleFactor*placeFactor, y+ self.__scaleFactor*placeFactor, text=val,
                                      font = Font(size = int(-self.__scaleFactor*placeFactor)), fill = 'white')
            
        def deleteAll(self):
            self._canvas.delete(self._code) # the numeric value
            self._canvas.delete(self._rcode) # the oval
            
        def moveScale(self, newScaleFactor):
            self.__scaleFactor = newScaleFactor
            self._canvas.delete(self._code)
            self._canvas.delete(self._rcode)
            self.place()
#            canvas.move(self._rcode, deltax, deltay)
#            canvas.move(self._code, deltax, deltay)
            
    class Wall:
        def __init__(self, street, avenue, isVertical, window):
            self._street = street
            self._avenue = avenue
            self._isVertical = isVertical
            self.__scaleFactor = window._KarelWindow__scaleFactor
            self._scaler = window._scaleToPixels
            self._canvas = window._canvas
            if self._isVertical:
                (x, y) = self._scaler(street - .5, avenue + .5)
                self._code = self._canvas.create_line(x, y, x, y - self.__scaleFactor, width = 2)
            else:
                (x, y) = self._scaler(street + .5, avenue - .5)
                self._code = self._canvas.create_line(x, y, x + self.__scaleFactor, y, width = 2)
                # _code identifies the wall segment image in the tk layer
            
        def moveScale(self, newScaleFactor):
            self._canvas.delete(self._code) #erase the current figure in prep to draw a new one
            self.__scaleFactor = newScaleFactor
            if self._isVertical:
                (x, y) = self._scaler(self._street - .5, self._avenue + .5)
                self._code = self._canvas.create_line(x, y, x, y - self.__scaleFactor, width = 2)
            else:
                (x, y) = self._scaler(self._street + .5, self._avenue - .5)
                self._code = self._canvas.create_line(x, y, x + self.__scaleFactor, y, width = 2)
                   
            
    def placeBeepers(self,street, avenue, number):
#        self.__beeperControl.acquire() # sync was moved to tkworldadapter
        beeper = self.Beeper(street, avenue, number, self)
        beeper.place()
        self.__gBeepers[(street, avenue)] = beeper
        self.__contents.append(beeper)
#        self.__beeperControl.notify()
#        self.__beeperControl.release()
#        return beeper
        
    def deleteBeeper(self, beeperlocation, silent=False):
#        self.__beeperControl.acquire()
        beeper = self.__gBeepers.get(beeperlocation, None)
        if beeper != None :
            beeper.deleteAll()
            self.__gBeepers.pop(beeperlocation)
            i = 0
            for b in self.__contents :
                if b == beeper :
                    break
                i+=1
            self.__contents.pop(i)
        else:
            if not silent: print ("no beeper here: " + str(beeperlocation))
#        self.__beeperControl.notify()
#        self.__beeperControl.release()
    
    def placeWallNorthOf(self, street, avenue):
        self.__contents.append(self.Wall(street, avenue, False, self))
        
    def placeWallEastOf(self, street, avenue):
        self.__contents.append(self.Wall(street, avenue, True, self))
    


    def makeBoundaryWalls(self):
        (x, y) = self._scaleToPixels(.5, .5) # hardcode ok. Half way between streets
        #print (x,y)
        # vertical wall
        self.__walls.append(self._canvas.create_line(x, 0, x, y, width = 2)) # should width depend on number of streets?
        global _inset
        self.__walls.append(self._canvas.create_line(x, y, self.__right + _inset, y, width = 2))
        
    def makeStreetsAndAvenues(self):
        for i in range(0, self.__streets) :
            (x, y) = self._scaleToPixels(i+1, .5)
            (tx, ty) = self._scaleToPixels(i+1, self.__avenues + 0.5)
            self.__walls.append(self._canvas.create_line(x, y, tx, ty, fill="red"))

        for i in range(0, self.__avenues) :
            (x,y) = self._scaleToPixels(.5, i + 1)
            (tx, ty) = self._scaleToPixels(self.__streets + 0.5, i + 1)
            self.__walls.append(self._canvas.create_line(x, y, tx, ty, fill= "red"))


    #street_names = ["madison","chicago","north","fullerton","belmont","irving park","lawrence","bryn mawr","touhy"]
    #avenue_names = ["harlem","narraganset","central","cicero","pulaski","kedzie","western","ashland","halsted","state"]
    def labelStreetsAvenues(self):
        for i in range(self.__streets):
            (x, y) = self._scaleToPixels(i + 1, .25)
            #(bufferx, buffery) = self._scaleToPixels(i+0.25, .25)
            bufferx = 0.33*self.__scaleFactor

            self.__walls.append(self._canvas.create_text(x,y, fill = 'black', text = str(i+1)))
            
            # Baker note: commenting out the labeling of streets with chicago names for now.  8.28.25.  Will get back to it later
            # See RobotWorld.setDisplayMode() -- it is currently not linked to this code.  We'd need to refernce the world being used.
            
            # if i < len(self.street_names):
            #     s_name = self.street_names[i]
            # else:
            #     s_name = f"street {i}"


            #self.__walls.append(self._canvas.create_text(x+bufferx, y-1, anchor='sw', fill = 'gray', text = s_name))

        
        for i in range(self.__avenues):

            (x,y) = self._scaleToPixels(.25, i + 1)
            self.__walls.append(self._canvas.create_text(x,y, fill = 'black', text = str(i+1)))

            buffery = 0.33*self.__scaleFactor
            # if i < len(self.avenue_names):
            #     a_name = self.avenue_names[i]
            # else:
            #     a_name = f"avenue {i}"

            #self.__walls.append(self._canvas.create_text(x-1, y-18, anchor='sw', fill = 'gray', angle=90, text = a_name))


    
    def addRobot(self, street, avenue, direction, fill, outline, costume=None):
        #        fill and outline are colors, default to blue, black
        robot = RobotImage(street, avenue, direction, self, fill, outline, costume)
        self.__contents.append(robot)
        return robot # the world matches these with the actual robot objects in the model. 
    
    def moveRobot(self, robot, amount = -1):
        #If no amount is specified then it moves one block, Otherwise amount pixels, not blocks
        if amount < 0 :
            amount = self.__scaleFactor
        robot.move(amount)
    
    # return the pixel coordinate of st, ave
    def _scaleToPixels(self, street, avenue): # origin is at corner (0,0) outside the world
        return (self.__left + avenue*self.__scaleFactor, self.__bottom - street*self.__scaleFactor)
        # x = self.__left + (avenue - 1) * self.__avenueScaleFactor
        # y = self.__bottom - (street - 1) * self.__streetScaleFactor
        # return x, y
    
    def run(self, task, *pargs): # this is the actual graphic main. 
        # Render the initial state of the robot/world before starting the loop
        # def wait_while_paused():
        #     while self.is_paused:
        #         self.update_idletasks()
        #         self.update()  # Keep the GUI responsive while paused

        # def wrapped_task(*pargs):
        #     # Call the task once to render the initial state


        #     # Control execution with play/pause
        #     while True:
        #         wait_while_paused()  # Wait if paused
        #         try:
        #             task(*pargs)  # Execute the task
        #         except StopIteration:
        #             break
        #         self.update_idletasks()
        #         self.update()

        # def wrapped_task(*pargs):
        #     initialize_task()  # Render the initial state
        #     try:
        #         while True:
        #             if wait_while_paused:  # Wait while paused
        #                 wait_while_paused()
        #             task(*pargs)  # Execute the task
        #     except StopIteration:
        #         pass

        # mainThread = threading.Thread(target = wrapped_task, args=pargs)
        mainThread = threading.Thread(target = task, args=pargs)
        mainThread.start()
        self.mainloop()
        
    def _test(self):
        pass
#        self.karel = RobotImage(North, "red", "black")
##        beep = self.Beeper(4, 4, 5, self.scaleToPixels, self.__scaleFactor)
##        code = beep.place(self._canvas)
#        beep = self._placeBeeper(4, 4, 5)
#        self.karel.scale(self.__scaleFactor/6.0)
#        (x,y) = self.scaleToPixels(3, 5)
#        self.karel.translate(x, y)
#        image = self.karel.show(self._canvas)
#        from Canvas import Polygon
#        
#        poly = Polygon(self._canvas, (0, 100, 120, 22), width = 4, fill = "blue")
#        
#        self._canvas.create_polygon([(0, 100), (120, 22), (300, 40)], width = 4, fill = "blue")
#        
#        print (poly.__repr__())
#        print
#        print (poly.keys())
#        print (poly['fill'].__class__ )

#        from Tkinter import IntVar
#        iv = Intvar()
#        
        
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
#        self.karel.rotate(self._canvas)
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        self.sue = RobotImage(North, "blue", "green")
#        self.sue.scale(self.__scaleFactor/6.0)
#        (x,y) = self.scaleToPixels(3, 2)
#        self.sue.translate(x, y)
#        self.sue.show(self._canvas)
#        sleep(.5)
#        self.sue.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
##        self.sue.rotate(self._canvas)
##        sleep(.5)
#        self.sue.move(self._canvas, self.__scaleFactor)
#        
##        beep.deleteAll(self._canvas,code)
#        self.deleteBeeper(beep)
#        self._placeWallNorthOf(4, 4)
#        self._placeWallNorthOf(4, 3)
#        self._placeWallNorthOf(4, 5)
#        self._placeWallEastOf(4, 5)
#        
#        beep = self._placeBeeper(3, 4, -1)
#        
#        self.karel.rotate(self._canvas)
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
#        self.karel.rotate(self._canvas)
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
#        self.karel.rotate(self._canvas)
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
#        self.karel.rotate(self._canvas)
#        sleep(.5)
#        self.karel.move(self._canvas, self.__scaleFactor)
#        sleep(.5)
#        beep = self.Beeper(3, 4, -1, self.scaleToPixels, self.__scaleFactor)
#        beep.place(self._canvas)
#        for i in range(10):
#            sleep(1.0)
#            self.robby.rotate(self._canvas)
#            sleep(1.0)
##            self.robby.translate(10, 10)
#            self.robby.move(self._canvas)
#            self.robby.scale(0.9)
            
#            self._canvas.move(4, 10, 10)
      
#        tester = RobotImage(North, "black", "black")
#        print ("North")
#        tester._dumpImage()  
#        print ("West")
#        tester.rotate(self._canvas)
#        tester._dumpImage() 
#        print ("South")
#        tester.rotate(self._canvas)
#        tester._dumpImage()     
#        print ("East")
#        tester.rotate(self._canvas)
#        tester._dumpImage()     
    
#        button = Button(frame,text="Exit",command=root.destroy)
#        button.pack(side=BOTTOM) 
               

       
if __name__ == '__main__': # this is to run test code only. Not normally used
    window = KarelWindow(12, 12)
    
    mainThread = threading.Thread(target = window._test)
    mainThread.start()
    
    window.mainloop()
#    for i in range(10):
#        sleep(1.0)
#        window.canvas.move("foo", 10, 10)

