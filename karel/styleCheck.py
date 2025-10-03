import ast
import re


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

def test_passed(test_feedback):
    
    # Example usage
    file_path = "main.py"  # Replace with actual student file
    inline_comments, docstrings, standalone_comments = extract_comments(file_path)

    num_inline_comments = len(inline_comments)
    num_standalone_comments = len(standalone_comments)
    num_docstrings = len(docstrings)



    if not num_standalone_comments >= 1:
        print("ERROR: You are supposed to have at least 1 standalone comment at the the top of your code"
        f"\n(not within any class, method or function) that looks like"
        f'"""\nYour Name\nNetId\nDate"""\n')
        return False

    if not (num_inline_comments + num_docstrings) >= 1:
        print("ERROR: No inline comments. You are supposed to have some inline comments in your code.")
        return False
    
    print("Comments in your code....")

    print("\nStandalone Triple-Quoted Comments:")
    for i, comment in enumerate(standalone_comments, start=1):
        print(f'{i}. """\n{comment}\n"""')
    
    print("\nInline Comments:")
    for i, comment in enumerate(inline_comments, start=1):
        print(f"{i}. # {comment.strip()}")
    
    if num_docstrings > 0:
        print("Docstrings (triple-quoted comments inside methods or classes):")
        for i, doc in enumerate(docstrings, start=1):
            print(f'{i}."""\n{doc}\n"""')

    print(f"\nWoo hoo!\nYou have {num_standalone_comments} standalone comment(s)"
    f" and {num_docstrings+num_inline_comments} inline comment(s) in your code")

    print("\nPLEASE NOTE: score wil be manually updated based on the quality of the comments.  This test is just checking for existence of comments. (scroll up ^^^ to see what was extracted)")
    return True