"""World Builder - a small graphical tool for creating and editing Karel .kwld
world files: set the world's size, click to place/remove beepers, click along
the gridlines between intersections to add/remove walls (or click-and-drag to
draw a long wall), and watch/edit the world file's text live in the side tray.

Standalone use:
    python -m karel.worldbuilder
    (or run world_builder.py at the repo root, which just calls this)

Launched from a running KarelWindow:
    Tools menu -> "World Builder..." opens this as a child window of the
    already-open Karel graphics window, so both can be used side by side.

This tool is intentionally self-contained - it does not import RobotWorld or
UrRobot, and reads/writes the .kwld text format directly. That keeps it usable
on its own (no robot, no live world needed) and insulated from the handful of
quirks/limitations in the runtime library's own save/load code.

.kwld format this tool reads and writes (one instruction per line):
    KarelWorld                       - header line, informational only
    streets <N>                      - number of streets (rows)
    avenues <N>                      - number of avenues (columns)
    beepers <street> <avenue> <n>    - n beepers at that corner (n<0 = infinite)
    eastwestwalls <street> <a1> <a2> - wall north of <street>, avenues a1..a2 inclusive
    northsouthwalls <ave> <s1> <s2>  - wall east of <ave>, streets s1..s2 inclusive
                                        (note: avenue comes first here, not street)
Intersection (1, 1) is the first street / first avenue; the world's outer
boundary walls sit half a block outside the first and last intersections.
"""
import math
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

DEFAULT_STREETS = 10
DEFAULT_AVENUES = 10
MIN_SIZE = 1
MAX_SIZE = 100

_CANVAS_W = 600
_CANVAS_H = 600
_INSET = 34

_CORNER_HIT = 0.28   # fraction of a block, centered on an intersection, that counts as "clicked the intersection"
_WALL_HIT = 0.28     # fraction of a block, centered on a wall's spot, that counts as "clicked the wall"
_DRAG_STEP_PX = 4    # while dragging, sample the mouse path every this many pixels so fast drags don't skip walls


class WorldParseError(Exception):
    """Raised for a line of world text that can't be understood - the message
    says which line and what's wrong, in plain terms."""


def _to_int(word, lineno, what):
    try:
        return int(word)
    except ValueError:
        raise WorldParseError(f"line {lineno}: {what} should be a whole number, but got '{word}'")


def parse_world_text(text):
    """Parse .kwld text and return (streets, avenues, beepers, ew_walls, ns_walls, warnings).

    beepers is a dict {(street, avenue): count} (count -1 means infinite).
    ew_walls is a set of (street, avenue) meaning "wall north of that intersection".
    ns_walls is a set of (street, avenue) meaning "wall east of that intersection".
    warnings is a list of plain-English notes about things that were understood but
    look suspicious (an unrecognized line, something outside the world's size).

    Raises WorldParseError, naming the line, for anything that can't be understood.
    Mirrors robotworldbase.readWorld()'s grammar, including the northsouthwalls
    avenue-first argument order, and its additive handling of repeated beepers lines."""
    streets, avenues = DEFAULT_STREETS, DEFAULT_AVENUES
    beepers = {}
    ew_walls = set()
    ns_walls = set()
    warnings = []

    for lineno, raw in enumerate(text.splitlines(), 1):
        words = raw.split()
        if not words or words[0].startswith("#"):
            continue
        key = words[0]

        if key == "KarelWorld":
            continue

        if key in ("streets", "avenues"):
            if len(words) != 2:
                raise WorldParseError(f"line {lineno}: '{key}' needs one number, like '{key} 10'")
            n = _to_int(words[1], lineno, "the size")
            if not (MIN_SIZE <= n <= MAX_SIZE):
                raise WorldParseError(f"line {lineno}: {key} must be between {MIN_SIZE} and {MAX_SIZE}")
            if key == "streets":
                streets = n
            else:
                avenues = n

        elif key == "beepers":
            if len(words) != 4:
                raise WorldParseError(f"line {lineno}: 'beepers' needs three numbers: street avenue count")
            s = _to_int(words[1], lineno, "the street")
            a = _to_int(words[2], lineno, "the avenue")
            n = _to_int(words[3], lineno, "the beeper count")
            if s < 1 or a < 1:
                raise WorldParseError(f"line {lineno}: street and avenue must be at least 1")
            if n < 0:
                beepers[(s, a)] = -1
            elif n > 0 and beepers.get((s, a), 0) != -1:
                beepers[(s, a)] = beepers.get((s, a), 0) + n

        elif key == "eastwestwalls":
            if len(words) != 4:
                raise WorldParseError(f"line {lineno}: 'eastwestwalls' needs three numbers: street first-avenue last-avenue")
            s = _to_int(words[1], lineno, "the street")
            a1 = _to_int(words[2], lineno, "the first avenue")
            a2 = _to_int(words[3], lineno, "the last avenue")
            if s < 1 or a1 < 1:
                raise WorldParseError(f"line {lineno}: street and avenue must be at least 1")
            if a1 > a2:
                raise WorldParseError(f"line {lineno}: first avenue ({a1}) is greater than last avenue ({a2})")
            for a in range(a1, a2 + 1):
                ew_walls.add((s, a))

        elif key == "northsouthwalls":
            if len(words) != 4:
                raise WorldParseError(f"line {lineno}: 'northsouthwalls' needs three numbers: avenue first-street last-street")
            a = _to_int(words[1], lineno, "the avenue")
            s1 = _to_int(words[2], lineno, "the first street")
            s2 = _to_int(words[3], lineno, "the last street")
            if a < 1 or s1 < 1:
                raise WorldParseError(f"line {lineno}: street and avenue must be at least 1")
            if s1 > s2:
                raise WorldParseError(f"line {lineno}: first street ({s1}) is greater than last street ({s2})")
            for s in range(s1, s2 + 1):
                ns_walls.add((s, a))

        else:
            warnings.append(f"line {lineno}: unrecognized '{key}' (ignored)")

    outside = (
        sum(1 for (s, a) in beepers if not (1 <= s <= streets and 1 <= a <= avenues))
        + sum(1 for (s, a) in ew_walls if not (1 <= s < streets and 1 <= a <= avenues))
        + sum(1 for (s, a) in ns_walls if not (1 <= s <= streets and 1 <= a < avenues))
    )
    if outside:
        warnings.append(f"{outside} item(s) are outside the {streets} x {avenues} world and won't be shown")

    return streets, avenues, beepers, ew_walls, ns_walls, warnings


def parse_world_file(path):
    """Read a .kwld file and return (streets, avenues, beepers, ew_walls, ns_walls)."""
    with open(path) as f:
        text = f.read()
    streets, avenues, beepers, ew_walls, ns_walls, _warnings = parse_world_text(text)
    return streets, avenues, beepers, ew_walls, ns_walls


def _compress_runs(items_by_group):
    """items_by_group: {group_key: list of ints}. Yields (group_key, start, end)
    for each maximal run of consecutive ints, so a wall spanning several corners in a
    row is written as one line instead of one line per corner."""
    for group_key, values in items_by_group.items():
        values = sorted(values)
        start = prev = values[0]
        for v in values[1:]:
            if v == prev + 1:
                prev = v
                continue
            yield (group_key, start, prev)
            start = prev = v
        yield (group_key, start, prev)


def world_to_text(streets, avenues, beepers, ew_walls, ns_walls):
    """The .kwld text for a world. Contiguous wall runs are compressed into single
    range lines (eastwestwalls/northsouthwalls), matching how the sample world
    files in this repo are hand-authored."""
    lines = ["KarelWorld", f"streets {streets}", f"avenues {avenues}"]

    for (s, a) in sorted(beepers.keys()):
        n = beepers[(s, a)]
        if n != 0:
            lines.append(f"beepers {s} {a} {n}")

    by_street = {}
    for (s, a) in ew_walls:
        by_street.setdefault(s, []).append(a)
    for street, a1, a2 in sorted(_compress_runs(by_street)):
        lines.append(f"eastwestwalls {street} {a1} {a2}")

    by_avenue = {}
    for (s, a) in ns_walls:
        by_avenue.setdefault(a, []).append(s)
    for avenue, s1, s2 in sorted(_compress_runs(by_avenue)):
        lines.append(f"northsouthwalls {avenue} {s1} {s2}")

    return "\n".join(lines) + "\n"


def write_world_file(path, streets, avenues, beepers, ew_walls, ns_walls):
    with open(path, "w") as f:
        f.write(world_to_text(streets, avenues, beepers, ew_walls, ns_walls))


class WorldBuilder:
    """The World Builder window. Pass a Tk widget as `master` to open this as a
    child Toplevel of an already-running Tk app (e.g. a live KarelWindow);
    leave it as None to run standalone with its own Tk root - call .run() in
    that case to start its mainloop."""

    def __init__(self, master=None):
        self._standalone = master is None
        self.root = tk.Tk() if self._standalone else tk.Toplevel(master)
        self.root.minsize(920, 600)

        self.streets = DEFAULT_STREETS
        self.avenues = DEFAULT_AVENUES
        self.beepers = {}      # (street, avenue) -> count
        self.ew_walls = set()  # (street, avenue) meaning "wall north of"
        self.ns_walls = set()  # (street, avenue) meaning "wall east of"
        self.current_path = None

        self._updating_text = False   # True while we're rewriting the text tray ourselves
        self._text_error = None       # message if the tray's text currently can't be parsed
        self._drag_action = None      # "add" or "remove" while a mouse button is down
        self._drag_last = None        # last (x, y) of the drag, or None if this press isn't a wall drag
        self._drag_count = 0

        self._build_ui()
        self._set_current_path(None)
        self._sync_text()
        self._redraw()

    def run(self):
        """Only needed in standalone mode - starts this window's own mainloop."""
        if self._standalone:
            self.root.mainloop()

    # ---------------------------------------------------------------- UI setup

    def _build_ui(self):
        root = self.root

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New World", command=self._new_world)
        filemenu.add_command(label="Open...", command=self._open_world)
        filemenu.add_separator()
        filemenu.add_command(label="Save", command=self._save_world)
        filemenu.add_command(label="Save As...", command=self._save_world_as)
        filemenu.add_separator()
        filemenu.add_command(label="Quit" if self._standalone else "Close", command=root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        root.config(menu=menubar)
        for sequence, handler in (("<Control-s>", self._save_world), ("<Command-s>", self._save_world),
                                  ("<Command-o>", self._open_world)):
            try:
                root.bind(sequence, lambda e, h=handler: h())
            except tk.TclError:
                pass  # this platform doesn't have that modifier

        top = ttk.Frame(root, padding=(8, 6))
        top.pack(side="top", fill="x")

        ttk.Label(top, text="Streets:").pack(side="left")
        self.streets_var = tk.StringVar(value=str(self.streets))
        streets_entry = ttk.Entry(top, textvariable=self.streets_var, width=4)
        streets_entry.pack(side="left", padx=(2, 10))

        ttk.Label(top, text="Avenues:").pack(side="left")
        self.avenues_var = tk.StringVar(value=str(self.avenues))
        avenues_entry = ttk.Entry(top, textvariable=self.avenues_var, width=4)
        avenues_entry.pack(side="left", padx=(2, 10))

        for entry in (streets_entry, avenues_entry):
            entry.bind("<Return>", lambda e: self._apply_resize())

        ttk.Button(top, text="Resize", command=self._apply_resize).pack(side="left", padx=(0, 16))
        ttk.Button(top, text="Clear Beepers/Walls", command=self._clear_contents).pack(side="left")

        status = ttk.Frame(root, padding=(8, 4))
        status.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="")
        ttk.Label(status, textvariable=self.status_var, foreground="#333").pack(side="left")

        body = ttk.Frame(root)
        body.pack(side="top", fill="both", expand=True)

        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=(0, 4))

        self.canvas = tk.Canvas(left, width=_CANVAS_W, height=_CANVAS_H, bg="white",
                                highlightthickness=0, bd=0)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())

        self.canvas.bind("<Button-1>", lambda e: self._on_press(e, "add"))
        self.canvas.bind("<Shift-Button-1>", lambda e: self._on_press(e, "remove"))
        self.canvas.bind("<Button-2>", lambda e: self._on_press(e, "remove"))   # right-click on macOS
        self.canvas.bind("<Button-3>", lambda e: self._on_press(e, "remove"))   # right-click elsewhere
        self.canvas.bind("<B1-Motion>", lambda e: self._on_drag(e, "add"))
        self.canvas.bind("<Shift-B1-Motion>", lambda e: self._on_drag(e, "remove"))
        self.canvas.bind("<B2-Motion>", lambda e: self._on_drag(e, "remove"))
        self.canvas.bind("<B3-Motion>", lambda e: self._on_drag(e, "remove"))
        for release in ("<ButtonRelease-1>", "<ButtonRelease-2>", "<ButtonRelease-3>"):
            self.canvas.bind(release, self._on_release)

        help_text = (
            "• To add a beeper: click an intersection. Right-click or shift-click to remove one.\n"
            "• To add a wall: click a gridline between intersections. Right-click or shift-click to remove it.\n"
            "• To draw a long wall: click and drag along it."
        )
        ttk.Label(left, text=help_text, foreground="#555", justify="left", wraplength=_CANVAS_W).pack(
            side="top", anchor="w", pady=(6, 0)
        )

        right = ttk.Frame(body, padding=(4, 0, 8, 4))
        right.pack(side="right", fill="y")

        buttons = ttk.Frame(right)
        buttons.pack(side="top", fill="x", pady=(0, 6))
        ttk.Button(buttons, text="Open...", command=self._open_world).pack(side="left", padx=(0, 4))
        ttk.Button(buttons, text="Save", command=self._save_world).pack(side="left", padx=(0, 4))
        ttk.Button(buttons, text="Save As...", command=self._save_world_as).pack(side="left")

        self.file_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.file_var, foreground="#333").pack(side="top", anchor="w")
        ttk.Label(right, text="World file text (you can edit this too):", foreground="#555").pack(
            side="top", anchor="w", pady=(4, 2)
        )

        text_frame = ttk.Frame(right)
        text_frame.pack(side="top", fill="both", expand=True)
        self.text = tk.Text(text_frame, width=38, height=20, wrap="none", undo=True,
                            font=("Courier", 11), relief="solid", bd=1)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.bind("<<Modified>>", self._on_text_modified)

        self.message_label = tk.Label(right, text="", justify="left", anchor="w", wraplength=300)
        self.message_label.pack(side="top", fill="x", pady=(6, 0))

    # ------------------------------------------------------- status/messages

    def _set_status(self, text):
        self.status_var.set(text)

    def _show_message(self, text, error):
        self.message_label.configure(text=text, fg="#c00000" if error else "#b06000")

    def _set_current_path(self, path):
        self.current_path = path
        name = os.path.basename(path) if path else "Untitled (not saved yet)"
        self.file_var.set(f"File: {name}")
        self.root.title(f"Karel World Builder - {name}")

    # ------------------------------------------------------------- text tray

    def _sync_text(self):
        """Rewrite the text tray from the current world (used after any change made on the canvas,
        or by resize/open/new)."""
        new_text = world_to_text(self.streets, self.avenues, self.beepers, self.ew_walls, self.ns_walls)
        self._updating_text = True
        try:
            first = self.text.yview()[0]
            self.text.delete("1.0", "end")
            self.text.insert("1.0", new_text)
            self.text.yview_moveto(first)
            self.text.edit_reset()
            self.text.edit_modified(False)
        finally:
            self._updating_text = False
        self._text_error = None
        self._show_message("", error=False)

    def _on_text_modified(self, event=None):
        if self._updating_text:
            self.text.edit_modified(False)
            return
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self._apply_text()

    def _apply_text(self):
        content = self.text.get("1.0", "end-1c")
        try:
            streets, avenues, beepers, ew_walls, ns_walls, warnings = parse_world_text(content)
        except WorldParseError as e:
            self._text_error = str(e)
            self._show_message(f"{e}\n(The picture shows the last version that made sense.)", error=True)
            return
        self._text_error = None
        self.streets, self.avenues = streets, avenues
        self.beepers, self.ew_walls, self.ns_walls = beepers, ew_walls, ns_walls
        self.streets_var.set(str(streets))
        self.avenues_var.set(str(avenues))
        self._show_message("\n".join(warnings), error=False)
        self._set_status("Updated from text")
        self._redraw()

    def _after_canvas_edit(self):
        self._redraw()
        self._sync_text()

    # ------------------------------------------------------------ size/state

    def _apply_resize(self):
        try:
            new_streets = int(self.streets_var.get())
            new_avenues = int(self.avenues_var.get())
        except ValueError:
            messagebox.showerror("Invalid size", "Streets and avenues must be whole numbers.")
            return
        if not (MIN_SIZE <= new_streets <= MAX_SIZE) or not (MIN_SIZE <= new_avenues <= MAX_SIZE):
            messagebox.showerror("Invalid size", f"Streets and avenues must be between {MIN_SIZE} and {MAX_SIZE}.")
            return

        self.beepers = {(s, a): n for (s, a), n in self.beepers.items() if s <= new_streets and a <= new_avenues}
        self.ew_walls = {(s, a) for (s, a) in self.ew_walls if s < new_streets and a <= new_avenues}
        self.ns_walls = {(s, a) for (s, a) in self.ns_walls if s <= new_streets and a < new_avenues}

        self.streets, self.avenues = new_streets, new_avenues
        self._after_canvas_edit()
        self._set_status(f"Resized to {new_streets} streets x {new_avenues} avenues")

    def _clear_contents(self):
        if not (self.beepers or self.ew_walls or self.ns_walls):
            return
        if messagebox.askyesno("Clear world", "Remove all beepers and walls? (Size is kept.)"):
            self.beepers.clear()
            self.ew_walls.clear()
            self.ns_walls.clear()
            self._after_canvas_edit()
            self._set_status("Cleared beepers and walls")

    def _new_world(self):
        if messagebox.askyesno("New world", "Discard the current world and start a blank one?"):
            self.streets, self.avenues = DEFAULT_STREETS, DEFAULT_AVENUES
            self.streets_var.set(str(self.streets))
            self.avenues_var.set(str(self.avenues))
            self.beepers.clear()
            self.ew_walls.clear()
            self.ns_walls.clear()
            self._set_current_path(None)
            self._after_canvas_edit()
            self._set_status("New, unsaved world")

    # --------------------------------------------------------------- file io

    def _open_world(self):
        path = filedialog.askopenfilename(
            title="Open Karel world",
            filetypes=[("Karel world files", "*.kwld"), ("All files", "*.*")],
        )
        if path:
            self._load_path(path)

    def _load_path(self, path):
        try:
            with open(path) as f:
                text = f.read()
            streets, avenues, beepers, ew_walls, ns_walls, warnings = parse_world_text(text)
        except Exception as e:
            messagebox.showerror("Couldn't open file", f"{path}\n\n{e}")
            return

        self.streets, self.avenues = streets, avenues
        self.streets_var.set(str(streets))
        self.avenues_var.set(str(avenues))
        self.beepers, self.ew_walls, self.ns_walls = beepers, ew_walls, ns_walls
        self._set_current_path(path)
        self._after_canvas_edit()
        if warnings:
            self._show_message("\n".join(warnings), error=False)
        self._set_status(f"Opened {os.path.basename(path)}")

    def _save_world(self):
        if self.current_path is None:
            self._save_world_as()
            return
        self._write_to(self.current_path)

    def _save_world_as(self):
        if not self._check_text_ok():
            return
        path = filedialog.asksaveasfilename(
            title="Save Karel world",
            defaultextension=".kwld",
            filetypes=[("Karel world files", "*.kwld"), ("All files", "*.*")],
        )
        if not path:
            return
        self._write_to(path)

    def _check_text_ok(self):
        if self._text_error:
            messagebox.showerror(
                "Can't save yet",
                f"The world text on the right has a problem:\n\n{self._text_error}\n\nFix it, then save.",
            )
            return False
        return True

    def _write_to(self, path):
        if not self._check_text_ok():
            return
        try:
            write_world_file(path, self.streets, self.avenues, self.beepers, self.ew_walls, self.ns_walls)
        except Exception as e:
            messagebox.showerror("Couldn't save file", f"{path}\n\n{e}")
            return
        self._set_current_path(path)
        self._sync_text()   # show exactly what was written
        self._set_status(f"Saved {os.path.basename(path)}")

    # -------------------------------------------------------- drawing/coords

    def _layout(self):
        """Returns (scale, left, bottom): pixels per block, and the pixel x of the
        world's left boundary wall / pixel y of its bottom boundary wall. The whole
        world is centered in the canvas."""
        w = max(self.canvas.winfo_width(), _CANVAS_W)
        h = max(self.canvas.winfo_height(), _CANVAS_H)
        scale = min((w - 2 * _INSET) / self.avenues, (h - 2 * _INSET) / self.streets)
        left = (w - scale * self.avenues) / 2
        bottom = (h + scale * self.streets) / 2
        return scale, left, bottom

    def _to_pixels(self, street, avenue):
        """(street, avenue) -> (x, y) pixel position. Street increases upward and
        avenue rightward, same as the runtime KarelWindow. The boundary walls are at
        0.5 and N + 0.5, so intersection (1, 1) sits half a block in from the
        bottom-left corner."""
        scale, left, bottom = self._layout()
        return left + (avenue - 0.5) * scale, bottom - (street - 0.5) * scale

    def _from_pixels(self, x, y):
        """Inverse of _to_pixels - returns fractional (street, avenue)."""
        scale, left, bottom = self._layout()
        return (bottom - y) / scale + 0.5, (x - left) / scale + 0.5

    def _redraw(self):
        c = self.canvas
        c.delete("all")
        scale, left, bottom = self._layout()
        p = self._to_pixels

        for s in range(1, self.streets + 1):
            x0, y0 = p(s, 0.5)
            x1, y1 = p(s, self.avenues + 0.5)
            c.create_line(x0, y0, x1, y1, fill="red")
        for a in range(1, self.avenues + 1):
            x0, y0 = p(0.5, a)
            x1, y1 = p(self.streets + 0.5, a)
            c.create_line(x0, y0, x1, y1, fill="red")

        x0, y0 = p(0.5, 0.5)
        x1, y1 = p(self.streets + 0.5, self.avenues + 0.5)
        c.create_rectangle(x0, y0, x1, y1, outline="black", width=3)

        for (s, a) in self.ew_walls:
            if 1 <= s < self.streets and 1 <= a <= self.avenues:
                self._draw_ew_wall(s, a)
        for (s, a) in self.ns_walls:
            if 1 <= s <= self.streets and 1 <= a < self.avenues:
                self._draw_ns_wall(s, a)
        for (s, a), n in self.beepers.items():
            if n != 0 and 1 <= s <= self.streets and 1 <= a <= self.avenues:
                self._draw_beeper(s, a, n, scale)

        label_font = ("Arial", max(8, min(13, int(scale * 0.32))))
        for s in range(1, self.streets + 1):
            x, y = p(s, 0.5)
            c.create_text(x - 16, y, text=str(s), fill="black", font=label_font)
        for a in range(1, self.avenues + 1):
            x, y = p(0.5, a)
            c.create_text(x, y + 16, text=str(a), fill="black", font=label_font)

    def _draw_ew_wall(self, street, avenue):
        # wall north of (street, avenue): horizontal segment at street+0.5, spanning avenue-0.5..avenue+0.5
        x0, y = self._to_pixels(street + 0.5, avenue - 0.5)
        x1, _ = self._to_pixels(street + 0.5, avenue + 0.5)
        self.canvas.create_line(x0, y, x1, y, width=3, fill="black")

    def _draw_ns_wall(self, street, avenue):
        # wall east of (street, avenue): vertical segment at avenue+0.5, spanning street-0.5..street+0.5
        x, y0 = self._to_pixels(street - 0.5, avenue + 0.5)
        _, y1 = self._to_pixels(street + 0.5, avenue + 0.5)
        self.canvas.create_line(x, y0, x, y1, width=3, fill="black")

    def _draw_beeper(self, street, avenue, n, scale):
        x, y = self._to_pixels(street, avenue)
        r = scale * 0.3
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")
        label = "∞" if n < 0 else str(n)
        self.canvas.create_text(x, y, text=label, fill="white", font=("Arial", max(8, int(scale * 0.28))))

    # --------------------------------------------------------------- clicks

    def _hit_test(self, px, py):
        """Classify a click as ('beeper', s, a), ('ew', s, a), ('ns', s, a), or None."""
        street_f, avenue_f = self._from_pixels(px, py)

        s_round = round(street_f)
        a_round = round(avenue_f)
        s_frac = abs(street_f - s_round)
        a_frac = abs(avenue_f - a_round)

        if s_frac <= _CORNER_HIT and a_frac <= _CORNER_HIT:
            if 1 <= s_round <= self.streets and 1 <= a_round <= self.avenues:
                return ("beeper", s_round, a_round)
            return None

        if a_frac <= _WALL_HIT and abs(s_frac - 0.5) <= _WALL_HIT:
            street = math.floor(street_f)
            avenue = a_round
            if 1 <= street < self.streets and 1 <= avenue <= self.avenues:
                return ("ew", street, avenue)
            return None

        if s_frac <= _WALL_HIT and abs(a_frac - 0.5) <= _WALL_HIT:
            street = s_round
            avenue = math.floor(avenue_f)
            if 1 <= street <= self.streets and 1 <= avenue < self.avenues:
                return ("ns", street, avenue)
            return None

        return None

    def _apply_hit(self, hit, action):
        """Add or remove whatever `hit` points at. Returns (changed, status message)."""
        kind, s, a = hit
        if kind == "beeper":
            if action == "add":
                self.beepers[(s, a)] = self.beepers.get((s, a), 0) + 1 if self.beepers.get((s, a), 0) >= 0 else -1
                n = self.beepers[(s, a)]
                return True, f"Beeper at (street {s}, avenue {a}): {'infinite' if n < 0 else n}"
            n = self.beepers.get((s, a), 0)
            if n == 0:
                return False, "No beeper there to remove"
            if n < 0 or n == 1:
                del self.beepers[(s, a)]
                return True, f"Removed last beeper at (street {s}, avenue {a})"
            self.beepers[(s, a)] = n - 1
            return True, f"Beeper at (street {s}, avenue {a}): {n - 1}"

        walls = self.ew_walls if kind == "ew" else self.ns_walls
        direction = "north" if kind == "ew" else "east"
        present = (s, a) in walls
        if action == "add":
            if present:
                return False, f"Wall already there, {direction} of (street {s}, avenue {a})"
            walls.add((s, a))
            return True, f"Added wall {direction} of (street {s}, avenue {a})"
        if not present:
            return False, f"No wall there to remove"
        walls.discard((s, a))
        return True, f"Removed wall {direction} of (street {s}, avenue {a})"

    def _on_press(self, event, action):
        self._drag_action = action
        self._drag_count = 0
        hit = self._hit_test(event.x, event.y)
        # dragging only draws/erases walls - if the press landed on an intersection (a beeper click),
        # don't let the rest of that gesture spray walls around it
        self._drag_last = None if (hit is not None and hit[0] == "beeper") else (event.x, event.y)
        if hit is None:
            return
        changed, message = self._apply_hit(hit, action)
        self._set_status(message)
        if changed:
            if hit[0] != "beeper":
                self._drag_count = 1
            self._after_canvas_edit()

    def _on_drag(self, event, action):
        if self._drag_last is None or action != self._drag_action:
            return
        x0, y0 = self._drag_last
        x1, y1 = event.x, event.y
        steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / _DRAG_STEP_PX))
        changed_any = False
        for i in range(1, steps + 1):
            px = x0 + (x1 - x0) * i / steps
            py = y0 + (y1 - y0) * i / steps
            hit = self._hit_test(px, py)
            if hit is not None and hit[0] in ("ew", "ns"):
                changed, _message = self._apply_hit(hit, action)
                if changed:
                    changed_any = True
                    self._drag_count += 1
        self._drag_last = (x1, y1)
        if changed_any:
            self._after_canvas_edit()

    def _on_release(self, event):
        if self._drag_last is not None and self._drag_count > 1:
            verb = "Added" if self._drag_action == "add" else "Removed"
            self._set_status(f"{verb} {self._drag_count} walls")
        self._drag_last = None
        self._drag_count = 0
        self._drag_action = None


if __name__ == "__main__":
    WorldBuilder().run()
