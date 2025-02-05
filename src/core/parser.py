import ast
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Optional, Set
from ..models.code_elements import (
    Module, Class, Function, ImportStatement, Call, EventUsage
)

# --- Helper Functions ---

def extract_call_chain(node: ast.AST) -> List[str]:
    """Extract attribute chains from a function call, e.g. foo.bar.baz."""
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        return extract_call_chain(node.value) + [node.attr]
    return []

# --- Visitors for Analysis ---

class CallVisitor(ast.NodeVisitor):
    """Records all function calls within a node."""
    def __init__(self):
        self.calls: List[List[str]] = []
    
    def visit_Call(self, node: ast.Call):
        chain = extract_call_chain(node.func)
        if chain:
            self.calls.append(chain)
        self.generic_visit(node)

class ComplexityVisitor(ast.NodeVisitor):
    """
    A simple visitor to estimate cyclomatic complexity and track maximum branch depth.
    This counts one extra for each branch (if, for, while, try, with).
    """
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.max_depth = 0
        self.current_depth = 0

    def generic_visit(self, node):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            self.complexity += 1
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            super().generic_visit(node)
            self.current_depth -= 1
        else:
            super().generic_visit(node)

class EventCallVisitor(ast.NodeVisitor):
    """
    Visitor to detect event dispatch and listener registration calls.
    We assume:
      - Dispatch functions: dispatch_event, dispatch_event_sync, dispatch_event_async
      - Listener registration: add_listener
    """
    def __init__(self):
        # We collect events as EventUsage objects keyed by event_type.
        self.published_events: List[EventUsage] = []
        self.subscribed_events: List[EventUsage] = []

    def visit_Call(self, node: ast.Call):
        chain = extract_call_chain(node.func)
        if not chain:
            return

        # Determine the context of the call: publisher or subscriber
        last_call = chain[-1]

        # For dispatch events (publishing)
        if last_call in ['dispatch_event', 'dispatch_event_sync', 'dispatch_event_async']:
            event_type = self._extract_event_type(node)
            if event_type:
                event_usage = EventUsage(event_type=event_type, is_async=('async' in last_call))
                self.published_events.append(event_usage)
        # For add_listener (subscribing)
        elif last_call == 'add_listener':
            event_type = self._extract_event_type(node)
            if event_type:
                event_usage = EventUsage(event_type=event_type)
                self.subscribed_events.append(event_usage)
        self.generic_visit(node)

    def _extract_event_type(self, node: ast.Call) -> Optional[str]:
        """Attempt to extract the event type from the first argument if it is a constant."""
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                return arg.value
        return None

# --- Parsing Functions ---

def parse_function(node: ast.AST) -> Function:
    is_async = isinstance(node, ast.AsyncFunctionDef)
    line_number = getattr(node, 'lineno', 0)
    # Use ast.unparse if available (Python 3.9+); otherwise, leave decorators blank.
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

    # --- Event Analysis ---
    event_visitor = EventCallVisitor()
    for child in node.body:
        event_visitor.visit(child)
    func_obj.events_published = event_visitor.published_events
    func_obj.events_subscribed = event_visitor.subscribed_events

    # --- Call Extraction and Nested Functions ---
    calls: List[List[str]] = []
    nested_functions: List[Function] = []
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested_func = parse_function(child)
            nested_func.parent_function = func_obj
            nested_functions.append(nested_func)
        else:
            call_visitor = CallVisitor()
            call_visitor.visit(child)
            calls.extend(call_visitor.calls)
    unique_calls = {tuple(chain) for chain in calls}
    func_obj.calls = [Call(call_chain=list(chain)) for chain in unique_calls]
    func_obj.nested_functions = nested_functions

    # --- Method Metrics ---
    # Use ComplexityVisitor to compute a simple cyclomatic complexity and branch depth.
    complexity_visitor = ComplexityVisitor()
    complexity_visitor.visit(node)
    # If available, use end_lineno to determine lines of code
    if hasattr(node, 'end_lineno') and node.end_lineno is not None:
        func_obj.metrics.lines_of_code = node.end_lineno - node.lineno + 1
    else:
        func_obj.metrics.lines_of_code = 0  # Fallback if end_lineno is not available
    func_obj.metrics.complexity = complexity_visitor.complexity
    func_obj.metrics.branch_depth = complexity_visitor.max_depth
    func_obj.metrics.parameter_count = len(node.args.args)

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
            pieces = extract_call_chain(base)
            base_classes.append(".".join(pieces))
    class_obj.base_classes = base_classes

    # Process class body items: methods, nested classes, and attribute analysis can be added here.
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_obj = parse_function(item)
            method_obj.parent_class = class_obj
            class_obj.methods.append(method_obj)
        elif isinstance(item, ast.ClassDef):
            # Nested class
            inner_class = parse_class(item)
            class_obj.inner_classes.append(inner_class)
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

    # Extract #TODO items from the source
    module_obj.todos = extract_todos(source)

    # Walk through the top-level AST nodes
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
