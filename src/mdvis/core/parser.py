"""
Enhanced AST parser for extracting rich code structure and metadata.

Parses Python source code to extract detailed information about classes, functions,
type hints, async patterns, and other code elements.
"""

import ast
import re
import asyncio
import aiofiles
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

from ..models.elements import (
    Module, Class, Function, Parameter, TypeRef, Location, Decorator,
    ImportStatement, CallRef, EventUsage, AsyncPattern, AsyncPatternType,
    VisibilityLevel, Attribute
)

logger = logging.getLogger(__name__)


class EnhancedASTParser:
    """
    Enhanced AST parser that extracts detailed code structure and metadata.
    """
    
    def __init__(self, event_patterns: Optional[List[dict]] = None):
        """
        Initialize the parser.
        
        Args:
            event_patterns: List of event detection patterns
        """
        self.event_patterns = event_patterns or []
        self._compiled_patterns = self._compile_event_patterns()
    
    def _compile_event_patterns(self) -> List[dict]:
        """Compile regex patterns for event detection."""
        compiled = []
        for pattern in self.event_patterns:
            try:
                compiled_pattern = {
                    'name': pattern['name'],
                    'publisher_patterns': [re.compile(p) for p in pattern['publisher_patterns']],
                    'subscriber_patterns': [re.compile(p) for p in pattern['subscriber_patterns']],
                    'extract_event_type': re.compile(pattern['extract_event_type'])
                }
                compiled.append(compiled_pattern)
            except re.error as e:
                logger.warning(f"Invalid regex in event pattern '{pattern.get('name', 'unknown')}': {e}")
        return compiled
    
    async def parse_file(self, file_path: Path, source_code: Optional[str] = None) -> Module:
        """
        Parse a Python file and return a Module object with rich metadata.
        
        Args:
            file_path: Path to the Python file
            source_code: Optional source code (if already loaded)
            
        Returns:
            Parsed Module object
        """
        if source_code is None:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    source_code = await f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                raise
        
        try:
            # Parse the AST
            tree = ast.parse(source_code, filename=str(file_path))
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            raise
        
        # Create the module object
        module = Module(
            name=file_path.stem,
            file_path=file_path,
            source_code=source_code,
            docstring=ast.get_docstring(tree)
        )
        
        # Extract package information
        module.package = self._determine_package(file_path)
        
        # Parse the module contents
        self._parse_module_body(tree, module, source_code)
        
        # Extract metrics
        module.lines_of_code = len(source_code.splitlines())
        module.lines_blank = len([line for line in source_code.splitlines() if not line.strip()])
        module.lines_of_comments = self._count_comment_lines(source_code)
        
        # Extract TODOs
        module.todos = self._extract_todos(source_code)
        
        logger.debug(f"Parsed module {module.name}: {len(module.classes)} classes, {len(module.functions)} functions")
        
        return module
    
    def _determine_package(self, file_path: Path) -> Optional[str]:
        """Determine the package name for a file based on its path."""
        # Look for __init__.py files to determine package structure
        current_dir = file_path.parent
        package_parts = []
        
        while current_dir != current_dir.parent:  # Stop at filesystem root
            if (current_dir / '__init__.py').exists():
                package_parts.insert(0, current_dir.name)
                current_dir = current_dir.parent
            else:
                break
        
        return '.'.join(package_parts) if package_parts else None
    
    def _parse_module_body(self, tree: ast.AST, module: Module, source_code: str) -> None:
        """Parse the body of a module."""
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                cls = self._parse_class(node, source_code)
                module.classes.append(cls)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func = self._parse_function(node, source_code)
                module.functions.append(func)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_stmt = self._parse_import(node)
                module.imports.append(import_stmt)
            elif isinstance(node, ast.Assign):
                # Module-level variable assignments
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attr = self._parse_attribute(target.id, node, source_code)
                        if attr:
                            module.attributes.append(attr)
    
    def _parse_class(self, node: ast.ClassDef, source_code: str, parent_name: str = "") -> Class:
        """Parse a class definition."""
        location = Location(
            file_path=Path(""),  # Will be set by caller
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            column_start=node.col_offset,
            column_end=getattr(node, 'end_col_offset', 0)
        )
        
        cls = Class(
            name=node.name,
            docstring=ast.get_docstring(node),
            location=location
        )
        
        # Parse base classes
        cls.base_classes = self._extract_base_classes(node)
        
        # Parse decorators
        cls.decorators = self._parse_decorators(node.decorator_list)
        
        # Check for special class types
        cls.is_dataclass = any(self._decorator_name(dec) == 'dataclass' for dec in cls.decorators)
        cls.is_abstract = any('ABC' in base or 'Abstract' in base for base in cls.base_classes)
        cls.is_exception = any('Exception' in base or 'Error' in base for base in cls.base_classes)
        
        # Parse class body
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._parse_function(item, source_code, parent_class=cls)
                cls.methods.append(method)
            elif isinstance(item, ast.ClassDef):
                nested_class = self._parse_class(item, source_code, f"{parent_name}.{cls.name}" if parent_name else cls.name)
                cls.nested_classes.append(nested_class)
            elif isinstance(item, ast.Assign):
                # Class attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr = self._parse_attribute(target.id, item, source_code, is_class_var=True)
                        if attr:
                            cls.attributes.append(attr)
        
        # Calculate metrics
        cls.method_count = len(cls.methods)
        cls.public_method_count = len([m for m in cls.methods if m.visibility == VisibilityLevel.PUBLIC])
        cls.lines_of_code = location.line_end - location.line_start + 1
        
        # Extract type references and async patterns
        cls.type_references = self._extract_type_references_from_node(node)
        cls.async_patterns = self._extract_async_patterns_from_node(node)
        cls.event_usage = self._extract_event_usage_from_node(node, source_code)
        
        return cls
    
    def _parse_function(
        self, 
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
        source_code: str,
        parent_class: Optional[Class] = None,
        parent_function: Optional[Function] = None
    ) -> Function:
        """Parse a function or method definition."""
        location = Location(
            file_path=Path(""),  # Will be set by caller
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            column_start=node.col_offset,
            column_end=getattr(node, 'end_col_offset', 0)
        )
        
        # Parse parameters
        parameters = self._parse_parameters(node.args)
        
        # Generate signature
        signature = self._generate_signature(node, parameters)
        
        func = Function(
            name=node.name,
            signature=signature,
            parameters=parameters,
            return_type=self._parse_return_type(node),
            docstring=ast.get_docstring(node),
            location=location,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            parent_class=parent_class,
            parent_function=parent_function
        )
        
        # Parse decorators
        func.decorators = self._parse_decorators(node.decorator_list)
        
        # Determine function type and visibility
        func.visibility = self._determine_visibility(node.name)
        func.is_property = any(self._decorator_name(dec) == 'property' for dec in func.decorators)
        func.is_static_method = any(self._decorator_name(dec) == 'staticmethod' for dec in func.decorators)
        func.is_class_method = any(self._decorator_name(dec) == 'classmethod' for dec in func.decorators)
        func.is_abstract = any('abstract' in self._decorator_name(dec).lower() for dec in func.decorators)
        
        # Check if it's a generator
        func.is_generator = self._has_yield(node)
        
        # Parse function body
        func.calls = self._extract_function_calls(node)
        func.nested_functions = self._extract_nested_functions(node, source_code, func)
        
        # Extract analysis data
        func.type_references = self._extract_type_references_from_node(node)
        func.async_patterns = self._extract_async_patterns_from_node(node)
        func.event_usage = self._extract_event_usage_from_node(node, source_code)
        
        # Calculate metrics
        func.complexity = self._calculate_complexity(node)
        func.lines_of_code = location.line_end - location.line_start + 1
        
        return func
    
    def _parse_parameters(self, args: ast.arguments) -> List[Parameter]:
        """Parse function parameters."""
        parameters = []
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            default_value = None
            if args.defaults and i >= len(args.args) - len(args.defaults):
                default_idx = i - (len(args.args) - len(args.defaults))
                default_value = self._ast_to_string(args.defaults[default_idx])
            
            param = Parameter(
                name=arg.arg,
                type_ref=self._parse_type_annotation(arg.annotation) if arg.annotation else None,
                default_value=default_value
            )
            parameters.append(param)
        
        # *args parameter
        if args.vararg:
            param = Parameter(
                name=args.vararg.arg,
                type_ref=self._parse_type_annotation(args.vararg.annotation) if args.vararg.annotation else None,
                is_variadic=True
            )
            parameters.append(param)
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            default_value = None
            if args.kw_defaults and i < len(args.kw_defaults) and args.kw_defaults[i]:
                default_value = self._ast_to_string(args.kw_defaults[i])
            
            param = Parameter(
                name=arg.arg,
                type_ref=self._parse_type_annotation(arg.annotation) if arg.annotation else None,
                default_value=default_value,
                is_keyword_only=True
            )
            parameters.append(param)
        
        # **kwargs parameter
        if args.kwarg:
            param = Parameter(
                name=args.kwarg.arg,
                type_ref=self._parse_type_annotation(args.kwarg.annotation) if args.kwarg.annotation else None,
                is_keyword_variadic=True
            )
            parameters.append(param)
        
        return parameters
    
    def _parse_type_annotation(self, annotation: ast.AST) -> Optional[TypeRef]:
        """Parse a type annotation AST node."""
        if not annotation:
            return None
        
        try:
            type_str = self._ast_to_string(annotation)
            
            # Handle common type patterns
            if isinstance(annotation, ast.Name):
                return TypeRef(
                    name=annotation.id,
                    full_name=annotation.id,
                    is_builtin=annotation.id in {'int', 'str', 'bool', 'float', 'list', 'dict', 'tuple', 'set'}
                )
            elif isinstance(annotation, ast.Subscript):
                # Generic types like List[str], Dict[str, int]
                base_type = self._ast_to_string(annotation.value)
                return TypeRef(
                    name=type_str,
                    full_name=type_str,
                    is_generic=True,
                    generic_args=self._parse_generic_args(annotation.slice) if annotation.slice else []
                )
            elif isinstance(annotation, ast.Attribute):
                # Qualified types like typing.Optional
                return TypeRef(
                    name=type_str,
                    full_name=type_str,
                    is_external=True
                )
            else:
                return TypeRef(
                    name=type_str,
                    full_name=type_str
                )
        except Exception as e:
            logger.debug(f"Error parsing type annotation: {e}")
            return None
    
    def _parse_generic_args(self, slice_node: ast.AST) -> List[TypeRef]:
        """Parse generic type arguments."""
        args = []
        
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                type_ref = self._parse_type_annotation(elt)
                if type_ref:
                    args.append(type_ref)
        else:
            type_ref = self._parse_type_annotation(slice_node)
            if type_ref:
                args.append(type_ref)
        
        return args
    
    def _parse_return_type(self, node: ast.FunctionDef) -> Optional[TypeRef]:
        """Parse function return type annotation."""
        if hasattr(node, 'returns') and node.returns:
            return self._parse_type_annotation(node.returns)
        return None
    
    def _parse_import(self, node: Union[ast.Import, ast.ImportFrom]) -> ImportStatement:
        """Parse an import statement."""
        if isinstance(node, ast.Import):
            names = [(alias.name, alias.asname) for alias in node.names]
            return ImportStatement(module=None, names=names)
        else:  # ast.ImportFrom
            names = [(alias.name, alias.asname) for alias in node.names]
            return ImportStatement(
                module=node.module,
                names=names,
                is_relative=node.level > 0,
                level=node.level
            )
    
    def _parse_decorators(self, decorator_list: List[ast.AST]) -> List[Decorator]:
        """Parse decorators."""
        decorators = []
        for dec in decorator_list:
            name = self._decorator_name(dec)
            args = []
            
            if isinstance(dec, ast.Call):
                args = [self._ast_to_string(arg) for arg in dec.args]
            
            decorators.append(Decorator(
                name=name,
                arguments=args,
                is_builtin=name in {'property', 'staticmethod', 'classmethod', 'abstractmethod'}
            ))
        
        return decorators
    
    def _parse_attribute(
        self, 
        name: str, 
        node: ast.Assign, 
        source_code: str,
        is_class_var: bool = False
    ) -> Optional[Attribute]:
        """Parse an attribute assignment."""
        try:
            default_value = self._ast_to_string(node.value) if node.value else None
            
            # Try to extract type annotation if available
            type_ref = None
            if hasattr(node, 'type_comment') and node.type_comment:
                # Handle type comments
                type_ref = TypeRef(name=node.type_comment, full_name=node.type_comment)
            
            return Attribute(
                name=name,
                type_ref=type_ref,
                default_value=default_value,
                is_class_var=is_class_var,
                location=Location(
                    file_path=Path(""),  # Will be set by caller
                    line_start=node.lineno,
                    line_end=getattr(node, 'end_lineno', node.lineno)
                ),
                visibility=self._determine_visibility(name)
            )
        except Exception as e:
            logger.debug(f"Error parsing attribute {name}: {e}")
            return None
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[CallRef]:
        """Extract function calls from a function body."""
        calls = []
        
        class CallVisitor(ast.NodeVisitor):
            def visit_Call(self, call_node: ast.Call):
                call_chain = self._extract_call_chain(call_node.func)
                if call_chain:
                    calls.append(CallRef(
                        call_chain=call_chain,
                        is_async=isinstance(call_node.func, ast.Attribute) and 
                                  call_node.func.attr in {'create_task', 'gather', 'wait_for'}
                    ))
                self.generic_visit(call_node)
        
        visitor = CallVisitor()
        visitor.visit(node)
        
        return calls
    
    def _extract_call_chain(self, node: ast.AST) -> List[str]:
        """Extract call chain from an AST node (e.g., obj.method.call -> ['obj', 'method', 'call'])."""
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.Attribute):
            base_chain = self._extract_call_chain(node.value)
            if base_chain:
                return base_chain + [node.attr]
        return []
    
    def _extract_nested_functions(
        self, 
        node: ast.FunctionDef, 
        source_code: str,
        parent_function: Function
    ) -> List[Function]:
        """Extract nested functions from a function body."""
        nested_functions = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nested_func = self._parse_function(item, source_code, parent_function=parent_function)
                nested_functions.append(nested_func)
        
        return nested_functions
    
    # Utility methods
    
    def _generate_signature(self, node: ast.FunctionDef, parameters: List[Parameter]) -> str:
        """Generate a function signature string."""
        param_strs = []
        for param in parameters:
            param_str = param.name
            if param.type_ref:
                param_str += f": {param.type_ref.name}"
            if param.default_value:
                param_str += f" = {param.default_value}"
            if param.is_variadic:
                param_str = f"*{param_str}"
            elif param.is_keyword_variadic:
                param_str = f"**{param_str}"
            param_strs.append(param_str)
        
        params_str = ", ".join(param_strs)
        return_str = ""
        
        if hasattr(node, 'returns') and node.returns:
            return_str = f" -> {self._ast_to_string(node.returns)}"
        
        async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        
        return f"{async_prefix}def {node.name}({params_str}){return_str}"
    
    def _determine_visibility(self, name: str) -> VisibilityLevel:
        """Determine visibility level based on naming convention."""
        if name.startswith('__') and name.endswith('__'):
            return VisibilityLevel.PUBLIC  # Magic methods are public
        elif name.startswith('__'):
            return VisibilityLevel.PRIVATE
        elif name.startswith('_'):
            return VisibilityLevel.PROTECTED
        else:
            return VisibilityLevel.PUBLIC
    
    def _decorator_name(self, decorator: ast.AST) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._decorator_name(decorator.func)
        else:
            return self._ast_to_string(decorator)
    
    def _ast_to_string(self, node: ast.AST) -> str:
        """Convert AST node to string representation."""
        try:
            if hasattr(ast, 'unparse'):  # Python 3.9+
                return ast.unparse(node)
            else:
                # Fallback for older Python versions
                import astor
                return astor.to_source(node).strip()
        except Exception:
            return str(type(node).__name__)
    
    def _has_yield(self, node: ast.FunctionDef) -> bool:
        """Check if function contains yield statements."""
        class YieldVisitor(ast.NodeVisitor):
            def __init__(self):
                self.has_yield = False
            
            def visit_Yield(self, node):
                self.has_yield = True
            
            def visit_YieldFrom(self, node):
                self.has_yield = True
        
        visitor = YieldVisitor()
        visitor.visit(node)
        return visitor.has_yield
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        class ComplexityVisitor(ast.NodeVisitor):
            def visit_If(self, node):
                nonlocal complexity
                complexity += 1
                self.generic_visit(node)
            
            def visit_For(self, node):
                nonlocal complexity
                complexity += 1
                self.generic_visit(node)
            
            def visit_While(self, node):
                nonlocal complexity
                complexity += 1
                self.generic_visit(node)
            
            def visit_Try(self, node):
                nonlocal complexity
                complexity += len(node.handlers)
                self.generic_visit(node)
            
            def visit_With(self, node):
                nonlocal complexity
                complexity += 1
                self.generic_visit(node)
        
        visitor = ComplexityVisitor()
        visitor.visit(node)
        return complexity
    
    def _extract_base_classes(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names."""
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(self._ast_to_string(base))
        return base_classes
    
    def _extract_type_references_from_node(self, node: ast.AST) -> List[TypeRef]:
        """Extract all type references from an AST node."""
        type_refs = []
        
        class TypeVisitor(ast.NodeVisitor):
            def visit_arg(self, node):
                if node.annotation:
                    type_ref = self._parse_type_annotation(node.annotation)
                    if type_ref:
                        type_refs.append(type_ref)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                # Return type annotation
                if node.returns:
                    type_ref = self._parse_type_annotation(node.returns)
                    if type_ref:
                        type_refs.append(type_ref)
                self.generic_visit(node)
            
            def visit_AnnAssign(self, node):
                # Variable type annotations
                if node.annotation:
                    type_ref = self._parse_type_annotation(node.annotation)
                    if type_ref:
                        type_refs.append(type_ref)
                self.generic_visit(node)
        
        visitor = TypeVisitor()
        visitor.visit(node)
        return type_refs
    
    def _extract_async_patterns_from_node(self, node: ast.AST) -> List[AsyncPattern]:
        """Extract async patterns from an AST node."""
        patterns = []
        
        class AsyncVisitor(ast.NodeVisitor):
            def visit_AsyncFunctionDef(self, func_node):
                location = Location(
                    file_path=Path(""),
                    line_start=func_node.lineno,
                    line_end=getattr(func_node, 'end_lineno', func_node.lineno)
                )
                
                # Check for factory method pattern
                is_factory = (
                    any(self._decorator_name(dec) == 'classmethod' for dec in func_node.decorator_list) and
                    func_node.name in ('create', 'from_config', 'build', 'make')
                )
                
                if is_factory:
                    patterns.append(AsyncPattern(
                        pattern_type=AsyncPatternType.FACTORY_METHOD,
                        location=location,
                        details={'method_name': func_node.name}
                    ))
                else:
                    pattern_type = AsyncPatternType.ASYNC_METHOD if hasattr(node, 'name') else AsyncPatternType.ASYNC_FUNCTION
                    patterns.append(AsyncPattern(
                        pattern_type=pattern_type,
                        location=location,
                        details={'function_name': func_node.name}
                    ))
                
                self.generic_visit(func_node)
            
            def visit_AsyncWith(self, with_node):
                location = Location(
                    file_path=Path(""),
                    line_start=with_node.lineno,
                    line_end=getattr(with_node, 'end_lineno', with_node.lineno)
                )
                
                context_managers = []
                for item in with_node.items:
                    context_managers.append(self._ast_to_string(item.context_expr))
                
                patterns.append(AsyncPattern(
                    pattern_type=AsyncPatternType.ASYNC_CONTEXT_MANAGER,
                    location=location,
                    details={'context_managers': context_managers}
                ))
                self.generic_visit(with_node)
            
            def visit_Call(self, call_node):
                call_chain = self._extract_call_chain(call_node.func)
                
                # Check for asyncio task creation patterns
                if call_chain:
                    func_name = call_chain[-1]
                    if func_name in ('create_task', 'ensure_future'):
                        location = Location(
                            file_path=Path(""),
                            line_start=call_node.lineno,
                            line_end=getattr(call_node, 'end_lineno', call_node.lineno)
                        )
                        patterns.append(AsyncPattern(
                            pattern_type=AsyncPatternType.CREATE_TASK,
                            location=location,
                            details={'call_chain': call_chain, 'function': func_name}
                        ))
                    elif func_name == 'gather':
                        location = Location(
                            file_path=Path(""),
                            line_start=call_node.lineno,
                            line_end=getattr(call_node, 'end_lineno', call_node.lineno)
                        )
                        patterns.append(AsyncPattern(
                            pattern_type=AsyncPatternType.GATHER,
                            location=location,
                            details={'call_chain': call_chain, 'arg_count': len(call_node.args)}
                        ))
                
                self.generic_visit(call_node)
        
        visitor = AsyncVisitor()
        visitor.visit(node)
        return patterns
    
    def _extract_event_usage_from_node(self, node: ast.AST, source_code: str) -> List[EventUsage]:
        """Extract event usage patterns from an AST node."""
        events = []
        
        if not self._compiled_patterns:
            return events
        
        class EventVisitor(ast.NodeVisitor):
            def visit_Call(self, call_node):
                call_chain = self._extract_call_chain(call_node.func)
                if call_chain:
                    call_text = '.'.join(call_chain)
                    
                    # Check against compiled patterns
                    for pattern_config in self._compiled_patterns:
                        pattern_name = pattern_config['name']
                        
                        # Check publisher patterns
                        for pub_pattern in pattern_config['publisher_patterns']:
                            if pub_pattern.search(call_text):
                                event_type = self._extract_event_type_from_call(call_node, pattern_config)
                                if event_type:
                                    location = Location(
                                        file_path=Path(""),
                                        line_start=call_node.lineno,
                                        line_end=getattr(call_node, 'end_lineno', call_node.lineno)
                                    )
                                    events.append(EventUsage(
                                        event_type=event_type,
                                        pattern_name=pattern_name,
                                        is_publisher=True,
                                        is_subscriber=False,
                                        location=location,
                                        context=call_text
                                    ))
                                break
                        
                        # Check subscriber patterns
                        for sub_pattern in pattern_config['subscriber_patterns']:
                            if sub_pattern.search(call_text):
                                event_type = self._extract_event_type_from_call(call_node, pattern_config)
                                if event_type:
                                    location = Location(
                                        file_path=Path(""),
                                        line_start=call_node.lineno,
                                        line_end=getattr(call_node, 'end_lineno', call_node.lineno)
                                    )
                                    events.append(EventUsage(
                                        event_type=event_type,
                                        pattern_name=pattern_name,
                                        is_publisher=False,
                                        is_subscriber=True,
                                        location=location,
                                        context=call_text
                                    ))
                                break
                
                self.generic_visit(call_node)
        
        visitor = EventVisitor()
        visitor.visit(node)
        return events
    
    def _extract_event_type_from_call(self, call_node: ast.Call, pattern_config: dict) -> Optional[str]:
        """Extract event type from a function call using the pattern's regex."""
        try:
            # Try to extract from string arguments
            for arg in call_node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    match = pattern_config['extract_event_type'].search(arg.value)
                    if match:
                        return match.group(1)
                elif isinstance(arg, ast.Str):  # Python < 3.8 compatibility
                    match = pattern_config['extract_event_type'].search(arg.s)
                    if match:
                        return match.group(1)
            
            # Try to extract from the call itself (for decorator patterns)
            call_str = self._ast_to_string(call_node)
            match = pattern_config['extract_event_type'].search(call_str)
            if match:
                return match.group(1)
                
        except Exception as e:
            logger.debug(f"Error extracting event type: {e}")
        
        return None
    
    def _count_comment_lines(self, source_code: str) -> int:
        """Count lines that are primarily comments."""
        comment_lines = 0
        for line in source_code.splitlines():
            stripped = line.strip()
            if stripped.startswith('#'):
                comment_lines += 1
        return comment_lines
    
    def _extract_todos(self, source_code: str) -> List[str]:
        """Extract TODO/FIXME comments from source code."""
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|XXX|HACK)\s*:?\s*(.*)', re.IGNORECASE)
        todos = []
        
        for line_num, line in enumerate(source_code.splitlines(), 1):
            match = todo_pattern.search(line)
            if match:
                todo_type, todo_text = match.groups()
                todos.append(f"Line {line_num}: {todo_type}: {todo_text.strip()}")
        
        return todos