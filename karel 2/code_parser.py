from __future__ import annotations
import ast
from dataclasses import dataclass
from typing import List, Optional, Set

@dataclass
class MethodInfo:
    class_name: str
    func_name: str
    header: str           # e.g., "def zigzag(self, n: int = 3) -> None:"
    decorators: List[str] # raw decorator strings (e.g., ["@classmethod"])
    is_classmethod: bool
    is_staticmethod: bool
    is_async: bool
    lineno: int

def _u(node: Optional[ast.AST]) -> str:
    return ast.unparse(node) if node is not None else ""

def _format_args(a: ast.arguments) -> str:
    parts = []

    # Positional-only + normal positional args (with defaults)
    pos = a.posonlyargs + a.args
    defaults = a.defaults or []
    # defaults align to the LAST N of (posonly + args)
    first_default = len(pos) - len(defaults)
    for i, arg in enumerate(pos):
        name = arg.arg
        ann = _u(arg.annotation)
        default = None
        if i >= first_default:
            default = defaults[i - first_default]
        seg = name
        if ann:
            seg += f": {ann}"
        if default is not None:
            seg += f"={_u(default)}"   # PEP8: no spaces around '=' in defaults
        parts.append(seg)

    # Slash for positional-only
    if a.posonlyargs:
        parts.append("/")

    # *args or bare '*' if there are kw-only args
    if a.vararg:
        var = f"*{a.vararg.arg}"
        if a.vararg.annotation:
            var += f": {_u(a.vararg.annotation)}"
        parts.append(var)
    elif a.kwonlyargs:
        parts.append("*")

    # Keyword-only args (with kw_defaults aligned 1:1; None means no default)
    for kw_arg, kw_def in zip(a.kwonlyargs, a.kw_defaults or []):
        seg = kw_arg.arg
        if kw_arg.annotation:
            seg += f": {_u(kw_arg.annotation)}"
        if kw_def is not None:
            seg += f"={_u(kw_def)}"
        parts.append(seg)

    # **kwargs
    if a.kwarg:
        seg = f"**{a.kwarg.arg}"
        if a.kwarg.annotation:
            seg += f": {_u(a.kwarg.annotation)}"
        parts.append(seg)

    return ", ".join(parts)

def _decorator_strings(node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
    decs = []
    for d in node.decorator_list:
        decs.append("@" + _u(d))
    return decs

def _has_decorator(node, name: str) -> bool:
    # Matches "name" and "... .name" cases
    for d in node.decorator_list:
        text = _u(d)
        if text == name or text.endswith("." + name):
            return True
    return False

class _MethodCollector(ast.NodeVisitor):
    def __init__(
        self,
        class_filter: Optional[Set[str]] = None,
        include_dunder: bool = False,
        include_private: bool = True,
    ):
        self.class_filter = class_filter
        self.include_dunder = include_dunder
        self.include_private = include_private
        self.methods: List[MethodInfo] = []
        self._class_stack: List[str] = []
        self._def_depth: int = 0

    def visit_ClassDef(self, node: ast.ClassDef):
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._handle_func(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._handle_func(node, is_async=True)

    def _handle_func(self, node, is_async: bool):
        # We only want methods that are direct children of a class, not nested inside another def.
        direct_method = bool(self._class_stack) and self._def_depth == 0
        self._def_depth += 1
        try:
            if not direct_method:
                self.generic_visit(node)
                return

            cls = self._class_stack[-1]
            if self.class_filter and cls not in self.class_filter:
                return

            name = node.name
            if name.startswith("__") and name.endswith("__") and not self.include_dunder:
                return
            if name.startswith("_") and not self.include_private and not (name.startswith("__") and name.endswith("__")):
                return

            sig = _format_args(node.args)
            header = ("async def " if is_async else "def ") + f"{name}({sig})"
            if node.returns:
                header += f" -> {_u(node.returns)}"
            header += ":"

            decs = _decorator_strings(node)
            info = MethodInfo(
                class_name=cls,
                func_name=name,
                header=header,
                decorators=decs,
                is_classmethod=_has_decorator(node, "classmethod"),
                is_staticmethod=_has_decorator(node, "staticmethod"),
                is_async=is_async,
                lineno=node.lineno,
            )
            self.methods.append(info)
        finally:
            self._def_depth -= 1
            # Still visit children so nested defs are traversed (but not recorded as methods)
            self.generic_visit(node)

def extract_method_headers_from_source(
    source: str,
    *,
    class_filter: Optional[Set[str]] = None,
    include_dunder: bool = False,
    include_private: bool = True,
) -> List[MethodInfo]:
    tree = ast.parse(source)
    collector = _MethodCollector(class_filter, include_dunder, include_private)
    collector.visit(tree)
    return collector.methods

def extract_method_headers_from_file(
    path: str,
    **kwargs,
) -> List[MethodInfo]:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    return extract_method_headers_from_source(src, **kwargs)

if __name__ == "__main__":
# Suppose student_main.py defines class ZigZagBot with several methods.
    class_to_check = {"HarvesterBot"}
    methods = extract_method_headers_from_file(
        "main.py",
        class_filter= class_to_check,   # or None for all classes
        include_dunder=False,         # hide __init__, etc.
        include_private=False,        # hide _helper methods
    )

    # Count & print headers
    print(f"{len(methods)} methods found in class {class_to_check}:")
    for i, m in enumerate(methods, start=1):
        # Show decorators (e.g., @classmethod) if present
        # for d in m.decorators:
        #     print(d)
        checkmark = ""
        if m.header in('def turnRight(self):', 'def harvestBeeperField(self):'):
            checkmark = " ✅"
        else:
            checkmark =""
        print(f"{i}. line {m.lineno}: {m.header}{checkmark}")