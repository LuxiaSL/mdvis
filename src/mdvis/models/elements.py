"""
Enhanced code element models for mdvis.

These models represent the structure of parsed Python code with rich metadata
for cross-referencing, type analysis, and documentation generation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum


class VisibilityLevel(Enum):
    """Code element visibility levels."""
    PUBLIC = "public"
    PROTECTED = "_protected"
    PRIVATE = "__private__"


class AsyncPatternType(Enum):
    """Types of async patterns detected in code."""
    ASYNC_FUNCTION = "async_function"
    ASYNC_METHOD = "async_method"
    ASYNC_CONTEXT_MANAGER = "async_context_manager"
    ASYNC_GENERATOR = "async_generator"
    ASYNC_COMPREHENSION = "async_comprehension"
    CREATE_TASK = "create_task"
    GATHER = "gather"
    FACTORY_METHOD = "factory_method"  # @classmethod async def create()


@dataclass
class Location:
    """Source code location information."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0


@dataclass
class TypeRef:
    """Reference to a type with linking information."""
    name: str
    full_name: str
    is_builtin: bool = False
    is_external: bool = False
    is_optional: bool = False
    is_generic: bool = False
    generic_args: List[TypeRef] = field(default_factory=list)
    module_source: Optional[str] = None  # Where this type is defined
    anchor: Optional[str] = None  # Link anchor if internal type


@dataclass
class Parameter:
    """Function/method parameter with rich type information."""
    name: str
    type_ref: Optional[TypeRef] = None
    default_value: Optional[str] = None
    is_variadic: bool = False  # *args
    is_keyword_variadic: bool = False  # **kwargs
    is_positional_only: bool = False
    is_keyword_only: bool = False


@dataclass
class EventUsage:
    """Event usage pattern detected in code."""
    event_type: str
    pattern_name: str  # Which detection pattern matched
    is_publisher: bool
    is_subscriber: bool
    location: Location
    context: str  # Function/method/class context


@dataclass
class AsyncPattern:
    """Async pattern detected in code."""
    pattern_type: AsyncPatternType
    location: Location
    details: Dict[str, Any] = field(default_factory=dict)  # Pattern-specific details


@dataclass
class CallRef:
    """Reference to a function/method call with linking info."""
    call_chain: List[str]
    target_module: Optional[str] = None
    target_anchor: Optional[str] = None
    is_external: bool = False
    is_async: bool = False


@dataclass
class ImportStatement:
    """Import statement with resolution information."""
    module: Optional[str]  # None for bare imports like "import os"
    names: List[tuple[str, Optional[str]]]  # [(name, alias), ...]
    is_relative: bool = False
    level: int = 0  # For relative imports (., .., ...)
    resolved_module: Optional[str] = None  # Resolved to actual module name
    is_internal: bool = False  # Whether this imports from our codebase


@dataclass
class Decorator:
    """Decorator information."""
    name: str
    arguments: List[str] = field(default_factory=list)
    is_builtin: bool = False


@dataclass
class Function:
    """Enhanced function/method representation."""
    name: str
    signature: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[TypeRef] = None
    docstring: Optional[str] = None
    
    # Structure
    decorators: List[Decorator] = field(default_factory=list)
    nested_functions: List[Function] = field(default_factory=list)
    parent_function: Optional[Function] = None
    parent_class: Optional[Class] = None
    
    # Analysis
    calls: List[CallRef] = field(default_factory=list)
    type_references: List[TypeRef] = field(default_factory=list)
    async_patterns: List[AsyncPattern] = field(default_factory=list)
    event_usage: List[EventUsage] = field(default_factory=list)
    
    # Metadata
    location: Location
    visibility: VisibilityLevel = VisibilityLevel.PUBLIC
    is_async: bool = False
    is_generator: bool = False
    is_property: bool = False
    is_static_method: bool = False
    is_class_method: bool = False
    is_abstract: bool = False
    
    # Metrics
    complexity: int = 0
    lines_of_code: int = 0
    
    def get_anchor(self, prefix: str = "") -> str:
        """Generate markdown anchor for this function."""
        base = "method" if self.parent_class else "function"
        if prefix:
            return f"{prefix}-{base}-{self.name.lower().replace('_', '-')}"
        return f"{base}-{self.name.lower().replace('_', '-')}"


@dataclass
class Attribute:
    """Class or instance attribute."""
    name: str
    type_ref: Optional[TypeRef] = None
    default_value: Optional[str] = None
    docstring: Optional[str] = None
    is_class_var: bool = False
    is_property: bool = False
    decorators: List[Decorator] = field(default_factory=list)
    location: Optional[Location] = None
    visibility: VisibilityLevel = VisibilityLevel.PUBLIC


@dataclass  
class Class:
    """Enhanced class representation."""
    name: str
    docstring: Optional[str] = None
    
    # Structure
    base_classes: List[str] = field(default_factory=list)
    methods: List[Function] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    nested_classes: List[Class] = field(default_factory=list)
    decorators: List[Decorator] = field(default_factory=list)
    
    # Analysis
    type_references: List[TypeRef] = field(default_factory=list)
    async_patterns: List[AsyncPattern] = field(default_factory=list)
    event_usage: List[EventUsage] = field(default_factory=list)
    
    # Metadata
    location: Location
    is_abstract: bool = False
    is_dataclass: bool = False
    is_exception: bool = False
    
    # Metrics
    method_count: int = 0
    public_method_count: int = 0
    lines_of_code: int = 0
    
    def get_anchor(self, prefix: str = "") -> str:
        """Generate markdown anchor for this class."""
        if prefix:
            return f"{prefix}-class-{self.name.lower().replace('_', '-')}"
        return f"class-{self.name.lower().replace('_', '-')}"


@dataclass
class Module:
    """Enhanced module representation."""
    name: str
    file_path: Path
    package: Optional[str] = None  # Package this module belongs to
    
    # Structure
    imports: List[ImportStatement] = field(default_factory=list)
    classes: List[Class] = field(default_factory=list)
    functions: List[Function] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)  # Module-level variables
    
    # Analysis
    type_references: List[TypeRef] = field(default_factory=list)
    async_patterns: List[AsyncPattern] = field(default_factory=list)
    event_usage: List[EventUsage] = field(default_factory=list)
    
    # Content
    source_code: Optional[str] = None
    todos: List[str] = field(default_factory=list)
    
    # Metadata
    encoding: str = "utf-8"
    docstring: Optional[str] = None
    
    # Metrics
    lines_of_code: int = 0
    lines_of_comments: int = 0
    lines_blank: int = 0
    complexity_total: int = 0
    
    def get_anchor(self, prefix: str = "") -> str:
        """Generate markdown anchor for this module."""
        if prefix:
            return f"{prefix}-module-{self.name.lower().replace('_', '-')}"
        return f"module-{self.name.lower().replace('_', '-')}"
    
    def get_all_functions(self) -> List[Function]:
        """Get all functions including class methods."""
        functions = list(self.functions)
        for cls in self.classes:
            functions.extend(cls.methods)
            # Include nested functions recursively
            for method in cls.methods:
                functions.extend(self._get_nested_functions(method))
        return functions
    
    def _get_nested_functions(self, func: Function) -> List[Function]:
        """Recursively get all nested functions."""
        nested = list(func.nested_functions)
        for nested_func in func.nested_functions:
            nested.extend(self._get_nested_functions(nested_func))
        return nested
    
    def get_all_types(self) -> List[str]:
        """Get all type names defined in this module."""
        types = []
        for cls in self.classes:
            types.append(cls.name)
            # Include nested classes
            for nested_cls in cls.nested_classes:
                types.append(f"{cls.name}.{nested_cls.name}")
        return types