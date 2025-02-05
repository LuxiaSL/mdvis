import ast
import re
from pathlib import Path
from typing import List
from ..models.code_elements import Module, Class, Function, ImportStatement, Call

def extract_call_chain(node: ast.AST) -> List[str]:
    """Extract attribute chains from a function call, e.g. foo.bar.baz."""
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        return extract_call_chain(node.value) + [node.attr]
    return []

class CallVisitor(ast.NodeVisitor):
    """AST visitor that records all function calls within a node."""
    def __init__(self):
        self.calls: List[List[str]] = []
    
    def visit_Call(self, node: ast.Call):
        chain = extract_call_chain(node.func)
        if chain:
            self.calls.append(chain)
        self.generic_visit(node)

def parse_function(node: ast.AST) -> Function:
    is_async = isinstance(node, ast.AsyncFunctionDef)
    line_number = getattr(node, 'lineno', 0)
    # Attempt to unparse decorators (Python 3.9+)
    if hasattr(ast, "unparse"):
        decorators = [f"@{ast.unparse(dec).strip()}" for dec in node.decorator_list]
    else:
        decorators = ["" for _ in node.decorator_list]

    func_obj = Function(
        name=node.name,
        parameters=[arg.arg for arg in node.args.args],
        docstring=ast.get_docstring(node),
        is_async=is_async,
        line_number=line_number,
        decorators=decorators
    )

    calls: List[List[str]] = []
    nested_functions: List[Function] = []
    
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Nested function
            nested_func = parse_function(child)
            nested_func.parent_function = func_obj
            nested_functions.append(nested_func)
        else:
            visitor = CallVisitor()
            visitor.visit(child)
            calls.extend(visitor.calls)

    # Deduplicate calls
    unique_calls = {tuple(chain) for chain in calls}
    func_obj.calls = [Call(call_chain=list(chain)) for chain in unique_calls]
    func_obj.nested_functions = nested_functions
    return func_obj

def parse_class(node: ast.ClassDef) -> Class:
    class_obj = Class(
        name=node.name,
        docstring=ast.get_docstring(node)
    )

    # Track inheritance (base classes)
    base_classes = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            base_classes.append(base.id)
        elif isinstance(base, ast.Attribute):
            # If it’s something like module.BaseClass
            pieces = extract_call_chain(base)
            base_classes.append(".".join(pieces))
    class_obj.base_classes = base_classes

    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_obj = parse_function(item)
            method_obj.parent_class = class_obj
            class_obj.methods.append(method_obj)
    return class_obj

def parse_imports(node: ast.AST) -> List[ImportStatement]:
    imports = []
    if isinstance(node, ast.Import):
        names = [(alias.name, alias.asname) for alias in node.names]
        imports.append(ImportStatement(module=None, names=names))
    elif isinstance(node, ast.ImportFrom):
        names = [(alias.name, alias.asname) for alias in node.names]
        imports.append(ImportStatement(module=node.module, names=names))
    return imports

def extract_todos(source: str) -> List[str]:
    """Search for # TODO or # FIXME lines and capture their text."""
    pattern = re.compile(r"#\s*(TODO|FIXME)\s*[:\-]?\s*(.*)", re.IGNORECASE)
    todos = []
    for line in source.splitlines():
        match = pattern.search(line)
        if match:
            todos.append(match.group(2).strip())
    return todos

def parse_file(file_path: str) -> Module:
    """Parse a Python file into a structured Module object."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise Exception(f"Syntax error in file {file_path}: {e}")

    module_name = Path(file_path).stem
    module_obj = Module(
        name=module_name,
        file_path=file_path,
        source=source
    )

    # Extract #TODO items
    module_obj.todos = extract_todos(source)

    for node in tree.body:
        # Imports
        imp_stmts = parse_imports(node)
        if imp_stmts:
            module_obj.imports.extend(imp_stmts)

        # Classes
        if isinstance(node, ast.ClassDef):
            class_obj = parse_class(node)
            module_obj.classes.append(class_obj)

        # Top-level functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_obj = parse_function(node)
            module_obj.functions.append(func_obj)

    return module_obj
