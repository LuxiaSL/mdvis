---
title: index
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/models/index.py
package: mdvis.models
stats:
  classes: 8
  functions: 0
  lines_of_code: 355
  complexity: 39
tags:
  - python
  - module
  - oop
---

# index

> [!info] Documentation
> Cross-reference index models for linking and navigation.
> 
> This module defines the structures that track relationships between
> code elements to enable smart linking and navigation.

## Table of Contents

### Classes
- [[#class-referencetype|ReferenceType]]
- [[#class-elementref|ElementRef]]
- [[#class-importresolution|ImportResolution]]
- [[#class-typeresolution|TypeResolution]]
- [[#class-callresolution|CallResolution]]
- [[#class-eventflow|EventFlow]]
- [[#class-dependencyedge|DependencyEdge]]
- [[#class-crossreferenceindex|CrossReferenceIndex]]


## Imports

- **from** `__future__` **import** `annotations`
- **from** `dataclasses` **import** `dataclass`, `field`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict`, `List`, `Optional`, `Set`, `Tuple`
- **from** `enum` **import** `Enum`
- **from** [[elements]] **import** [[elements#class-module|Module]], [[elements#class-class|Class]], [[elements#class-function|Function]], [[elements#class-location|Location]]

## Classes

### ReferenceType {#class-referencetype}

> [!info] Documentation
> Types of references between code elements.

**Inherits from:** `Enum`

#### Attributes

- **IMPORT** = `'import'` *(class variable)*
- **INHERITANCE** = `'inheritance'` *(class variable)*
- **FUNCTION_CALL** = `'function_call'` *(class variable)*
- **TYPE_ANNOTATION** = `'type_annotation'` *(class variable)*
- **ATTRIBUTE_ACCESS** = `'attribute_access'` *(class variable)*
- **DECORATOR** = `'decorator'` *(class variable)*
- **EVENT_PUBLISHER** = `'event_publisher'` *(class variable)*
- **EVENT_SUBSCRIBER** = `'event_subscriber'` *(class variable)*


### ElementRef {#class-elementref}

> [!info] Documentation
> Reference to a code element with navigation info.

#### Methods

##### get_link {#method-get-link}

**Signature:** `def get_link(self, verbosity: str = 'standard') -> str`

> [!info] Documentation
> Generate obsidian link based on verbosity level.

**Returns:** `str`



### ImportResolution {#class-importresolution}

> [!info] Documentation
> Resolved import statement.


### TypeResolution {#class-typeresolution}

> [!info] Documentation
> Resolved type reference.


### CallResolution {#class-callresolution}

> [!info] Documentation
> Resolved function/method call.


### EventFlow {#class-eventflow}

> [!info] Documentation
> Event flow from publisher to subscribers.


### DependencyEdge {#class-dependencyedge}

> [!info] Documentation
> Dependency relationship between modules.


### CrossReferenceIndex {#class-crossreferenceindex}

> [!info] Documentation
> Master index of all cross-references in the codebase.
> 
> This is the central registry that enables smart linking and navigation.

#### Methods

##### register_module {#method-register-module}

**Signature:** `def register_module(self, module: Module) -> None`

> [!info] Documentation
> Register a module and all its elements in the index.

**Returns:** `None`


##### resolve_import {#method-resolve-import}

**Signature:** `def resolve_import(self, import_stmt: str, from_module: str) -> Optional[ElementRef]`

> [!info] Documentation
> Resolve an import to its target element.

**Returns:** `Optional[ElementRef]`


##### resolve_type {#method-resolve-type}

**Signature:** `def resolve_type(self, type_name: str, context_module: str) -> Optional[TypeResolution]`

> [!info] Documentation
> Resolve a type name to its definition.

**Returns:** `Optional[TypeResolution]`


##### resolve_call {#method-resolve-call}

**Signature:** `def resolve_call(self, call_chain: List[str], context_module: str) -> Optional[CallResolution]`

> [!info] Documentation
> Resolve a function call to its target.

**Returns:** `Optional[CallResolution]`


##### add_dependency {#method-add-dependency}

**Signature:** `def add_dependency(self, source: str, target: str, dep_type: ReferenceType, example: str = '') -> None`

> [!info] Documentation
> Add a dependency relationship between modules.

**Returns:** `None`


##### get_module_dependencies {#method-get-module-dependencies}

**Signature:** `def get_module_dependencies(self, module_name: str) -> List[DependencyEdge]`

> [!info] Documentation
> Get all dependencies for a specific module.

**Returns:** `List[DependencyEdge]`


##### get_dependents {#method-get-dependents}

**Signature:** `def get_dependents(self, module_name: str) -> List[str]`

> [!info] Documentation
> Get modules that depend on the given module.

**Returns:** `List[str]`



## Source Code

```python
"""
Cross-reference index models for linking and navigation.

This module defines the structures that track relationships between
code elements to enable smart linking and navigation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

from .elements import Module, Class, Function, Location


class ReferenceType(Enum):
    """Types of references between code elements."""
    IMPORT = "import"
    INHERITANCE = "inheritance" 
    FUNCTION_CALL = "function_call"
    TYPE_ANNOTATION = "type_annotation"
    ATTRIBUTE_ACCESS = "attribute_access"
    DECORATOR = "decorator"
    EVENT_PUBLISHER = "event_publisher"
    EVENT_SUBSCRIBER = "event_subscriber"


@dataclass
class ElementRef:
    """Reference to a code element with navigation info."""
    name: str
    module: str
    element_type: str  # "function", "class", "method", "attribute"
    anchor: str
    file_path: Path
    location: Optional[Location] = None
    parent: Optional[str] = None  # For methods/nested elements
    
    def get_link(self, verbosity: str = "standard") -> str:
        """Generate obsidian link based on verbosity level."""
        if verbosity == "minimal":
            return f"[[{self.module}]]"
        elif verbosity == "standard":
            return f"[[{self.module}#{self.anchor}|{self.name}]]"
        else:  # detailed
            return f"[[{self.module}#{self.anchor}]]"


@dataclass  
class ImportResolution:
    """Resolved import statement."""
    original_import: str  # Original import statement
    resolved_module: str  # Actual module name
    imported_names: List[str]  # What was imported
    is_internal: bool  # Whether it's from our codebase
    targets: List[ElementRef] = field(default_factory=list)  # What the imports resolve to


@dataclass
class TypeResolution:
    """Resolved type reference."""
    type_name: str
    resolved_to: Optional[ElementRef] = None
    is_builtin: bool = False
    is_external: bool = False
    is_generic: bool = False
    generic_args: List[TypeResolution] = field(default_factory=list)


@dataclass
class CallResolution:
    """Resolved function/method call."""
    call_chain: List[str]
    resolved_to: Optional[ElementRef] = None
    is_external: bool = False
    confidence: float = 1.0  # How confident we are in the resolution


@dataclass
class EventFlow:
    """Event flow from publisher to subscribers."""
    event_type: str
    publishers: List[ElementRef] = field(default_factory=list)
    subscribers: List[ElementRef] = field(default_factory=list)
    pattern_name: str = "unknown"


@dataclass
class DependencyEdge:
    """Dependency relationship between modules."""
    source_module: str
    target_module: str
    dependency_type: ReferenceType
    strength: int = 1  # How many times this dependency appears
    examples: List[str] = field(default_factory=list)  # Example imports/calls


@dataclass
class CrossReferenceIndex:
    """
    Master index of all cross-references in the codebase.
    
    This is the central registry that enables smart linking and navigation.
    """
    
    # Module mappings
    module_paths: Dict[str, Path] = field(default_factory=dict)  # "config" → Path
    path_to_module: Dict[Path, str] = field(default_factory=dict)  # Reverse lookup
    module_packages: Dict[str, str] = field(default_factory=dict)  # Module → package
    
    # Element registries
    functions: Dict[str, ElementRef] = field(default_factory=dict)  # Global function lookup
    classes: Dict[str, ElementRef] = field(default_factory=dict)    # Global class lookup
    methods: Dict[str, ElementRef] = field(default_factory=dict)    # "ClassName.method_name" → ref
    
    # Module-scoped lookups for handling name collisions
    module_functions: Dict[str, Dict[str, ElementRef]] = field(default_factory=dict)
    module_classes: Dict[str, Dict[str, ElementRef]] = field(default_factory=dict)
    
    # Import resolution
    import_resolutions: List[ImportResolution] = field(default_factory=list)
    unresolved_imports: List[str] = field(default_factory=list)
    
    # Type resolution
    type_resolutions: Dict[str, TypeResolution] = field(default_factory=dict)
    custom_types: Set[str] = field(default_factory=set)  # All types defined in codebase
    
    # Call resolution
    call_resolutions: List[CallResolution] = field(default_factory=list)
    
    # Event system
    event_flows: Dict[str, EventFlow] = field(default_factory=dict)
    
    # Dependencies
    module_dependencies: List[DependencyEdge] = field(default_factory=list)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    
    def register_module(self, module: Module) -> None:
        """Register a module and all its elements in the index."""
        self.module_paths[module.name] = module.file_path
        self.path_to_module[module.file_path] = module.name
        
        if module.package:
            self.module_packages[module.name] = module.package
        
        # Initialize module-scoped lookups
        self.module_functions[module.name] = {}
        self.module_classes[module.name] = {}
        
        # Register classes
        for cls in module.classes:
            self._register_class(cls, module)
            
        # Register functions
        for func in module.functions:
            self._register_function(func, module)
    
    def _register_class(self, cls: Class, module: Module, parent_name: str = "") -> None:
        """Register a class and its methods."""
        full_name = f"{parent_name}.{cls.name}" if parent_name else cls.name
        
        ref = ElementRef(
            name=cls.name,
            module=module.name,
            element_type="class",
            anchor=cls.get_anchor(),
            file_path=module.file_path,
            location=cls.location,
            parent=parent_name if parent_name else None
        )
        
        # Global registration
        self.classes[full_name] = ref
        self.module_classes[module.name][cls.name] = ref
        self.custom_types.add(full_name)
        
        # Register methods
        for method in cls.methods:
            self._register_method(method, cls, module)
            
        # Register nested classes
        for nested_cls in cls.nested_classes:
            self._register_class(nested_cls, module, full_name)
    
    def _register_method(self, method: Function, parent_class: Class, module: Module) -> None:
        """Register a class method."""
        method_key = f"{parent_class.name}.{method.name}"
        
        ref = ElementRef(
            name=method.name,
            module=module.name,
            element_type="method",
            anchor=method.get_anchor(),
            file_path=module.file_path,
            location=method.location,
            parent=parent_class.name
        )
        
        self.methods[method_key] = ref
        
        # Also register in global functions for simple lookup
        self.functions[method.name] = ref
    
    def _register_function(self, func: Function, module: Module) -> None:
        """Register a top-level function."""
        ref = ElementRef(
            name=func.name,
            module=module.name,
            element_type="function",
            anchor=func.get_anchor(),
            file_path=module.file_path,
            location=func.location
        )
        
        self.functions[func.name] = ref
        self.module_functions[module.name][func.name] = ref
    
    def resolve_import(self, import_stmt: str, from_module: str) -> Optional[ElementRef]:
        """Resolve an import to its target element."""
        # Try module-level resolution first
        if import_stmt in self.module_paths:
            return ElementRef(
                name=import_stmt,
                module=import_stmt,
                element_type="module",
                anchor=f"module-{import_stmt}",
                file_path=self.module_paths[import_stmt]
            )
        
        # Try function/class resolution
        if import_stmt in self.functions:
            return self.functions[import_stmt]
        
        if import_stmt in self.classes:
            return self.classes[import_stmt]
        
        return None
    
    def resolve_type(self, type_name: str, context_module: str) -> Optional[TypeResolution]:
        """Resolve a type name to its definition."""
        # Try exact match first
        if type_name in self.classes:
            return TypeResolution(
                type_name=type_name,
                resolved_to=self.classes[type_name]
            )
        
        # Try module-scoped lookup
        if context_module in self.module_classes:
            if type_name in self.module_classes[context_module]:
                return TypeResolution(
                    type_name=type_name,
                    resolved_to=self.module_classes[context_module][type_name]
                )
        
        # Check if it's a known external/builtin type
        builtin_types = {
            'int', 'str', 'bool', 'float', 'list', 'dict', 'tuple', 'set',
            'List', 'Dict', 'Tuple', 'Set', 'Optional', 'Union', 'Any'
        }
        
        if type_name in builtin_types:
            return TypeResolution(
                type_name=type_name,
                is_builtin=True
            )
        
        return TypeResolution(
            type_name=type_name,
            is_external=True
        )
    
    def resolve_call(self, call_chain: List[str], context_module: str) -> Optional[CallResolution]:
        """Resolve a function call to its target."""
        if not call_chain:
            return None
        
        # Simple function call
        if len(call_chain) == 1:
            func_name = call_chain[0]
            
            # Try module-scoped lookup first
            if context_module in self.module_functions:
                if func_name in self.module_functions[context_module]:
                    return CallResolution(
                        call_chain=call_chain,
                        resolved_to=self.module_functions[context_module][func_name],
                        confidence=1.0
                    )
            
            # Try global lookup
            if func_name in self.functions:
                return CallResolution(
                    call_chain=call_chain,
                    resolved_to=self.functions[func_name],
                    confidence=0.8  # Lower confidence for global lookup
                )
        
        # Method call (obj.method)
        elif len(call_chain) == 2:
            obj_name, method_name = call_chain
            method_key = f"{obj_name}.{method_name}"
            
            if method_key in self.methods:
                return CallResolution(
                    call_chain=call_chain,
                    resolved_to=self.methods[method_key],
                    confidence=0.9
                )
        
        # External or complex call
        return CallResolution(
            call_chain=call_chain,
            is_external=True,
            confidence=0.1
        )
    
    def add_dependency(self, source: str, target: str, dep_type: ReferenceType, example: str = "") -> None:
        """Add a dependency relationship between modules."""
        # Find existing edge or create new one
        existing = None
        for edge in self.module_dependencies:
            if edge.source_module == source and edge.target_module == target and edge.dependency_type == dep_type:
                existing = edge
                break
        
        if existing:
            existing.strength += 1
            if example and example not in existing.examples:
                existing.examples.append(example)
        else:
            self.module_dependencies.append(DependencyEdge(
                source_module=source,
                target_module=target,
                dependency_type=dep_type,
                examples=[example] if example else []
            ))
        
        # Update dependency graph
        if source not in self.dependency_graph:
            self.dependency_graph[source] = set()
        self.dependency_graph[source].add(target)
    
    def get_module_dependencies(self, module_name: str) -> List[DependencyEdge]:
        """Get all dependencies for a specific module."""
        return [edge for edge in self.module_dependencies if edge.source_module == module_name]
    
    def get_dependents(self, module_name: str) -> List[str]:
        """Get modules that depend on the given module."""
        dependents = []
        for edge in self.module_dependencies:
            if edge.target_module == module_name:
                dependents.append(edge.source_module)
        return list(set(dependents))  # Remove duplicates
```