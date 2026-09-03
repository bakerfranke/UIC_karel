""" Copyright 2008 Joseph Bergin
License: Creative Commons Attribution-Noncommercial-Share Alike 3.0 United States License

Represents the robot world. It maintains knowledge about walls and beepers in the world. It also knows 
about the robots that have been created. 

It has API to place beepers and walls.

It can read and write world files
"""

#import sys
#import thread
import threading
import karel.robota
import time
from karel.observable import Observer
#from exceptions import NotImplementedError

from karel.basicdefinitions import legalCorner
from karel.basicdefinitions import infinity
from karel.basicdefinitions import NoBeepers
from karel.basicdefinitions import NoRobots
from karel.basicdefinitions import IllegalCorner


from karel.tkwindow import RobotImage
from karel.tkwindow import KarelWindow

_window = None #KarelWindow(12, 12)



from karel.robotworldbase import RobotWorldBase

class RobotWorld(RobotWorldBase, Observer) :
    """
    The robot world consisting of horizontal streets, vertical avenues, walls, and beepers. 
    The bottom left corner of the world is (1, 1), First street and first avenue. 
    While it is technically possible to create many objects of type RobotWorld, note that they won't be
    useful, as the robots themselves have defined their own world and "live" there. robota.world is the
    world known to the robots. It can, however, be replaced with a simple assignment.
    
    The world observes all robots. 
    """
    
    def __init__(self, name, streets = 10, avenues = 10):
        "Create an empty world."
        self._name = name
        self._beepers = {}
#        self.__gBeepers = {}
        self._eastWestWalls = {}
        self._northSouthWalls = {}
        self._robots = {}
        self.__gRobots = {}
        self.__delay = 80 # slow
        self._isVisible = False
        self.__beeperControl = threading.Condition()
        self._streets = streets
        self._avenues = avenues
        print("Creating", name)
        self.trace_enabled = False

        # Stats tray bookkeeping - a plain per-robot action tally, kept in the same spot
        # the trace-print logic already observes every action from. Counting itself is
        # O(1) per action regardless of whether the tray is open; only formatting/drawing
        # is skipped while it's closed (see _updateStatsIfOpen).
        self._actionCounts = {}   # robot.ID() -> {actionCode: count}
        self._latestRobotState = {}  # robot.ID() -> most recent RobotState
        self._robotOrder = []     # robot.ID()s in creation order, for stable display
        self._robotCostume = {}   # robot.ID() -> resolved costume (never None, unlike
                                   # RobotState.costume() which is None until setCostume()
                                   # is called explicitly)

    # ADDED BY BAKER 1.8.24
    def setTrace(self, enabled: bool):
        """Enable or disable global trace output for all robots."""
        self.trace_enabled = enabled

    def pause(self):
        """Pause execution. The next robot action will wait here until resume()
        is called (or the human clicks Run/Step in the window). Works anywhere in
        a program, not just at the top - e.g. to pause partway through a demo:

            bob.move()
            world.pause()
            bob.move()   # <-- waits here for resume() or a Run/Step click
        """
        self._setPaused(True)

    def resume(self, delay_ms: int = 0):
        """Resume execution (the inverse of pause()).

        Args:
            delay_ms: Optional milliseconds to wait before actually resuming.
        """
        self._setPaused(False, delay_ms)

    def startPaused(self, paused: bool = True, delay_ms: int = 0):
        """Alias for pause()/resume() - configure whether execution is paused or running.

        Programs start running immediately by default - no call needed for that.
        Call this (or pause()) to opt into starting paused instead (e.g. for a
        step-by-step demo).

        Args:
            paused: If True, pause (show "Run" button) - same as pause().
                    If False, run (show "Pause" button) - same as resume().
            delay_ms: Milliseconds to delay before resuming (only used if paused=False)

        Examples:
            world.startPaused()       # Pause - same as pause()
            world.startPaused(True)   # Pause - same as pause()
            world.startPaused(False)  # Resume immediately - same as resume()
        """
        self._setPaused(paused, delay_ms)

    def _setPaused(self, paused: bool, delay_ms: int = 0):
        global _window
        if _window is not None:
            _window.is_paused = paused
            _window.play_pause_btn.config(text="▶ Run" if paused else "⏸ Pause")
            if paused:
                _window.showPausedOverlay()
                _window.showPausedStatus()
            else:
                _window.hidePausedOverlay()
                _window.showRunningStatus()
            if not paused and delay_ms > 0:
                _window._startup_delay = delay_ms

    def update(self, robot, robotState = None):
        "This is called whenever any robot changes state since the world observes all robots"

        action = robotState.action()
        if action == karel.robota.UrRobot.moveAction  :
            self._registerRobot(robot)
#            self.__gRobots[robot].move(_window.drawArea(), _window.delta())
            if _window != None:
                _window.moveRobot(self.__gRobots[robot])

        elif action == karel.robota.UrRobot.createAction :
            self._registerRobot(robot)
            if _window != None:
                (street, avenue) = (robot._UrRobot__street, robot._UrRobot__avenue)
                costume = getattr(robot, '_UrRobot__costume', 'karel')
                self.__gRobots[robot] = _window.addRobot(street, avenue, robot._UrRobot__direction,
                                                     robot._UrRobot__fill, robot._UrRobot__outline, costume)
            
        elif action == karel.robota.UrRobot.turnLeftAction :
            if _window != None:
                self.__gRobots[robot].rotate()
        
        elif action == karel.robota.UrRobot.pickBeeperAction :
            pass # moved to removeBeeper
#            time.sleep(.2) # try to avoid beepere anomalies between threads 9a bit)
#            place = (street, avenue) = (robot._UrRobot__street, robot._UrRobot__avenue)
#            inWorld = self._beepers.get(place, 0)
#            beeper = self.__gBeepers.get(place, None)
#            if beeper != None :
#                _window.deleteBeeper(beeper)
#            if inWorld != 0 :
#                beeper = _window.placeBeeper(street, avenue, inWorld)
#                self.__gBeepers[place] = beeper
        
        elif action == karel.robota.UrRobot.putBeeperAction :
            pass
        
        elif action == karel.robota.UrRobot.turnOffAction :
            self.__gRobots[robot].greyOut();

        elif action == karel.robota.UrRobot.setVisibleAction:
            if _window is not None and robot in self.__gRobots:
                self.__gRobots[robot].setVisible(robotState.visible())

        elif action == karel.robota.UrRobot.setCostumeAction:
            if _window is not None and robot in self.__gRobots:
                self.__gRobots[robot].setCostume(robotState.costume())

        elif action == karel.robota.UrRobot.crashAction:
            if _window is not None and robot in self.__gRobots:
                self.__gRobots[robot].crashOut()

        else :
            pass

        # Stats tray bookkeeping - counts robot actions and tracks each robot's latest
        # state, observing the exact same per-action data the trace-print below does.
        self._trackStats(robot, robotState, action)

        #if hasattr(self, "trace_enabled") and self.trace_enabled:
        if self.trace_enabled:

            from karel.robota import UrRobot #defer this import to here to prevent circular import, we need the actions dictionary
            print(
                f"TRACE: Robot {robot.ID()} at ({robotState.street()}, {robotState.avenue()}) facing {robotState.direction().__name__} "
                f"with {robotState.beepers()} beeper(s), action: {UrRobot.actions[robotState.action()]}, {robotState.isRunning()}"
            )

    def _trackStats(self, robot, robotState, action):
        """O(1) per action regardless of whether the stats tray is open - only the
        formatting/redraw in getStatsText()/updateStatsText() is skipped while it's closed."""
        robotID = robot.ID()

        if action == karel.robota.UrRobot.createAction:
            self._actionCounts[robotID] = {
                karel.robota.UrRobot.moveAction: 0,
                karel.robota.UrRobot.turnLeftAction: 0,
                karel.robota.UrRobot.pickBeeperAction: 0,
                karel.robota.UrRobot.putBeeperAction: 0,
            }
            self._robotOrder.append(robotID)
            if robot in self.__gRobots:
                self._robotCostume[robotID] = self.__gRobots[robot]._costume
        elif action == karel.robota.UrRobot.setCostumeAction:
            # Costume changed after creation - refresh the tracked value too, or the
            # tray would keep showing whatever costume the robot started with forever.
            if robot in self.__gRobots:
                self._robotCostume[robotID] = self.__gRobots[robot]._costume
        elif robotID in self._actionCounts and action in self._actionCounts[robotID]:
            self._actionCounts[robotID][action] += 1

        self._latestRobotState[robotID] = robotState

        if _window is not None and getattr(_window, 'statsTrayOpen', False):
            _window.updateStatsText(self.getStatsText())

    def getStatsText(self):
        """Build the stats text - world size/beepers, then each robot's location,
        direction, beeper count, and action tallies, in creation order. Used by both the
        stats tray and printStats(), so they can never drift out of sync."""
        size = self.getSize()
        lines = [
            f"World size: {size['streets']} {size['avenues']:<2d}",
            f"   Beepers: {self.getTotalBeeperCount()}",
        ]

        UrRobot = karel.robota.UrRobot
        countedActions = (
            ("move", UrRobot.moveAction),
            ("turnLeft", UrRobot.turnLeftAction),
            ("pickBeeper", UrRobot.pickBeeperAction),
            ("putBeeper", UrRobot.putBeeperAction),
        )

        for robotID in self._robotOrder:
            state = self._latestRobotState.get(robotID)
            if state is None:
                continue
            counts = self._actionCounts.get(robotID, {})
            costume = self._robotCostume.get(robotID, "karel")

            lines.append("-" * 20)

            dirChar = state.direction().__name__[0]
            beepers = state.beepers()
            beepersStr = "inf" if beepers == infinity else f"{beepers:<3d}"
            lines.append(
                f"{robotID} {costume:<9} {state.street():<2d} {state.avenue():<2d}"
                f"{dirChar} {beepersStr}"
            )

            total = 0
            for label, code in countedActions:
                count = counts.get(code, 0)
                total += count
                lines.append(f"{label:>10}: {count:<4}")
            lines.append(f"{'Total':>10}: {total:<4}")

        return "\n".join(lines)

    def printStats(self):
        """Print the same info shown in the graphics window's stats tray to the console."""
        print(self.getStatsText())

    def name(self):
        "Return the name of this world"
        return self._name
    
    def setDelay(self, amount): # MANUALTEST: Must be tested manually
        """Set the amount by which primitive instructions should be delayed
        0 (default) means not at all
        100 (the maximum) means a lot (currently about 1 second)
        """
        if amount < 0 : amount = 0
        if amount > 100 : amount = 100
        self.__delay = amount 
        if _window != None :
            _window.iv.set(100 - amount)

    def setSpeed(self, amount):
        self.setDelay(100-amount)
        
    def speedCallback(self,*args):
        global _window
        if _window != None :
            self.setDelay(100 - _window.iv.get())
        
    def speedCheck(self):
        pass

    def delay(self):
        return self.__delay

    def setRobotCostume(self, costume):
        """Set the default costume/icon for all new robots.

        Args:
            costume (str): Name of the costume (e.g., 'sparky', 'karel', 'dragon')
                              Images should be named: {costume}_north.png, etc.
        """
        from karel.tkwindow import RobotImage
        RobotImage._defaultCostume = costume
        print(f"Default costume set to: {costume}")

#    _runnables = []
    
# 
        
    def placeBeepers(self, street, avenue, howMany=1, byUser = True):
        """
        Place any number of beepers at a corner. Use RobotWorld.infinity to place an infinite number.
        The number will be added to the number currently there. Don't try to reduce the number
        by giving a negative value. Strange behavior can result since negative values are treated as infinite.
        """
        self.__beeperControl.acquire()
        if howMany == 0 :
            return
        legalCorner(street, avenue)
        place = (street, avenue)

        if howMany < 0 :
            self._beepers[place] = infinity
            if _window != None:
                _window.deleteBeeper(place, True)
                _window.placeBeepers(street, avenue, infinity)
                self.__beeperControl.notify()
                self.__beeperControl.release()
            return
        inWorld = self._beepers.get(place, 0)
        toPut = howMany + inWorld
        if inWorld != infinity :
            self._beepers[place] = toPut
            if _window != None:
                if inWorld > 0 :
                    _window.deleteBeeper(place)
                _window.placeBeepers(street, avenue, toPut)
        self.__beeperControl.notify()
        self.__beeperControl.release()
            
        
    def placeWallNorthOf(self, street, avenue):
        "Place an east-west wall segment north of this corner"
        legalCorner(street, avenue)
        self._eastWestWalls[(street, avenue)] = 1;
        if _window != None:
            _window.placeWallNorthOf(street, avenue)
        
#        
    def placeWallEastOf(self, street, avenue) :
        "Place a north-south wall segment east of this corner"
        legalCorner(street, avenue)
        self._northSouthWalls[(street, avenue)] = 1;
        if _window != None:
            _window.placeWallEastOf(street, avenue)
        

    def removeBeeper(self, street, avenue, byUser = True) :
        """Remove a single beeper from this corner. An exception will be raised if there are none"""
#        time.sleep(.2)
        self.__beeperControl.acquire()
        place = (street, avenue)
        howMany = self._beepers.get(place, 0)
        if howMany > 0 :
            howMany -= 1
            if howMany == 0 :
                self._beepers.pop(place)
                if _window != None :
                    _window.deleteBeeper(place)
            else:
                self._beepers[place] = howMany
                if _window != None:
                    _window.deleteBeeper(place)
                    _window.placeBeepers(street, avenue, howMany)
        elif howMany == infinity :
            self.__beeperControl.notify()
            self.__beeperControl.release()
            return
        else :
            self.__beeperControl.notify()
            self.__beeperControl.release()
            raise NoBeepers("(" + str(street) + ", " + str(avenue) + ")")
        self.__beeperControl.notify()
        self.__beeperControl.release()
        
        
#    def _visible(self, x, y, xBound, yBound):
#        return x >= 0 and y >= 0 and x < xBound and y < yBound
#    
    def getSize(self):
        return {"streets":self._streets, "avenues":self._avenues}

    def setSize(self, numberOfStreets=10, numberOfAvenues=10):
        global _window  
        
        self._streets = numberOfStreets
        self._avenues = numberOfAvenues

        if _window == None :
            _window = KarelWindow(numberOfStreets, numberOfAvenues, world.speedCallback)       
        _window.setSize(numberOfStreets, numberOfAvenues)
#        _window = KarelWindow(numberOfStreets, numberOfAvenues, self.speedCallback)
#        _windwo.setCallback(self.speedCheck)
#        raise NotImplementedError("Set size needs to be implemented") # default 10 by 10
    
#     def setVisible(self, visible = True):
#         self._isVisible = visible
# #        raise NotImplementedError("SetVisible needs to be implemented") # true to show, false to hide
    def setVisible(self, visible=True):
        self._isVisible = visible
        if _window:
            if visible:
                _window._KarelWindow__root.deiconify()  # Show the window
            else:
                _window._KarelWindow__root.withdraw()  # Hide the window

    
    def isVisible(self):
        return self._isVisible
    
    def showBuilder(self):
        pass #TODO: add this
        
    def showSpeedControl(self, visible = True):
        pass #TODO: add this

    def initialize_graphics(self):
        """Shared method to initialize the graphics window."""
        from karel.tkworldadapter import _window, window, world

        global _window
        if _window is None:
            _window = window()  # Initialize the graphics window
            world.setSize(10, 10)  # Default world size
            world.setDelay(20)  # Default animation delay
            _window.update()  # Refresh the graphics window

            # Keep the window open after the script's own code finishes - same
            # mechanism UrRobot._initialize_graphics() registers when a robot gets
            # constructed. Without this, a program that only ever calls world-level
            # methods (readWorld()/setSize()/etc.) and never constructs a robot would
            # draw the window, then the process would exit immediately afterward
            # (nothing else keeps it alive), closing the window before anyone could
            # actually see it.
            import atexit
            def default_task():
                pass
            atexit.register(lambda: _window.run(default_task))

    def readWorld(self, filename):
        """Read the world configuration from a file and initialize graphics if needed."""
        #from karel.tkworldadapter import initialize_graphics
        self.initialize_graphics()  # Ensure graphics are initialized
        global _window
        if _window:
            _window._loadingWorldFile = True  # beepers placed below stay plain circles - see Beeper.place()
        try:
            super().readWorld(filename)  # Call the base class implementation
        finally:
            if _window:
                _window._loadingWorldFile = False
        if _window:
            _window.update()  # Trigger a refresh of the graphical window
            #_window.run(lambda: None)  # Keep the window open

world = RobotWorld("Karel's Graphical World")


def window(streets=12, avenues=12):
    global _window
    if _window == None :
        _window = KarelWindow(streets, avenues, world.speedCallback)       
    return _window

#window = createWindow()
