"""
Advanced Parser Module

This module uses Python's ast module to analyze a Python source file
and extract a rich representation of its structure:
  - Import statements (both 'import' and 'from ... import ...')
  - Top-level classes and their methods (with nested functions and call chains)
  - Top-level functions (with nested functions and call chains)
  - Function calls (extracted as call chains from attribute accesses)

This lays the foundation for later features such as interlinking via Obsidian
and building visual dependency graphs.
"""

import ast
from pathlib import Path
from typing import List
from ..models.code_elements import (
    Module, Class, Function, ImportStatement, Call
)

def extract_call_chain(node: ast.AST) -> List[str]:
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        return extract_call_chain(node.value) + [node.attr]
    return []

class CallVisitor(ast.NodeVisitor):
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
    func_obj = Function(
        name=node.name,
        parameters=[arg.arg for arg in node.args.args],
        docstring=ast.get_docstring(node),
        is_async=is_async,
        line_number=line_number
    )
    
    calls: List[List[str]] = []
    nested_functions: List[Function] = []
    
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested_func = parse_function(child)
            nested_func.parent_function = func_obj  # Set the parent function.
            nested_functions.append(nested_func)
        else:
            visitor = CallVisitor()
            visitor.visit(child)
            calls.extend(visitor.calls)
    
    func_obj.calls = [Call(call_chain=chain) for chain in calls]
    func_obj.nested_functions = nested_functions
    return func_obj

def parse_class(node: ast.ClassDef) -> Class:
    class_obj = Class(
        name=node.name,
        docstring=ast.get_docstring(node)
    )
    for item in node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_obj = parse_function(item)
            method_obj.parent_class = class_obj  # Set the parent class for this method.
            class_obj.methods.append(method_obj)
    return class_obj

def parse_imports(node: ast.AST) -> List[ImportStatement]:
    imports = []
    if isinstance(node, ast.Import):
        names = [(alias.name, alias.asname) for alias in node.names]
        imports.append(ImportStatement(module=None, names=names))
    elif isinstance(node, ast.ImportFrom):
        module_name = node.module
        names = [(alias.name, alias.asname) for alias in node.names]
        imports.append(ImportStatement(module=module_name, names=names))
    return imports

def parse_file(file_path: str) -> Module:
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
    module_obj = Module(name=module_name, file_path=file_path, source=source)
    
    for node in tree.body:
        imp_stmts = parse_imports(node)
        if imp_stmts:
            module_obj.imports.extend(imp_stmts)
        if isinstance(node, ast.ClassDef):
            class_obj = parse_class(node)
            module_obj.classes.append(class_obj)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_obj = parse_function(node)
            module_obj.functions.append(func_obj)
    
    return module_obj

def add_parent_references(node: ast.AST, parent: ast.AST = None) -> None:
    node.parent = parent
    for child in ast.iter_child_nodes(node):
        add_parent_references(child, node)
