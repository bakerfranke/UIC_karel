import ast
import re

def extract_class_methods(file_path):
    """Extracts class names and their method names from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    class_methods = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):  # Identify class definitions
            class_name = node.name
            methods = [
                func.name for func in node.body if isinstance(func, ast.FunctionDef)
            ]
            class_methods[class_name] = methods

    return class_methods




def extract_comments(file_path):
    """Extracts all comments (inline `#` and triple-quoted comments) from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # Extract inline comments using regex (ignores # inside strings)
    inline_comments = re.findall(r"(?<!['\"])\s+#(.*)", source_code)

    # Parse the code into an AST
    tree = ast.parse(source_code, filename=file_path)
    docstrings = []
    standalone_comments = []

    # Extract standalone triple-quoted comments (not attached to functions/classes)
    triple_quoted_comments = re.findall(r'("""|\'\'\')(.*?)\1', source_code, re.DOTALL)
    all_triple_quoted = [comment[1].strip() for comment in triple_quoted_comments]

    # Walk through AST to extract docstrings (only for classes and functions)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # Extract function/class docstrings if present
            if ast.get_docstring(node):
                docstrings.append(ast.get_docstring(node, clean=False))

    # Anything in all_triple_quoted that wasn't captured as a function/class docstring is standalone
    for comment in all_triple_quoted:
        if comment not in docstrings:
            standalone_comments.append(comment)

    return inline_comments, docstrings, standalone_comments
