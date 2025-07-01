# index

> Cross-reference index models for linking and navigation.

This module defines the structures that track relationships between
code elements to enable smart linking and navigation.

## Overview

- **Classes:** 8
- **Functions:** 0
- **Lines of Code:** 355

## Imports
- **from** `__future__` **import** `annotations`
- **from** `dataclasses` **import** `dataclass, field`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict, List, Optional, Set, Tuple`
- **from** `enum` **import** `Enum`
- **from** `elements` **import** `Module, Class, Function, Location`

## Classes
### ReferenceType {#class-referencetype}

> Types of references between code elements.

**Inherits from:** `Enum`

### ElementRef {#class-elementref}

> Reference to a code element with navigation info.


#### Methods
##### get_link {#method-get-link}

> Generate obsidian link based on verbosity level..

**Signature:** `def get_link(self, verbosity: str = 'standard') -> str`
### ImportResolution {#class-importresolution}

> Resolved import statement.


### TypeResolution {#class-typeresolution}

> Resolved type reference.


### CallResolution {#class-callresolution}

> Resolved function/method call.


### EventFlow {#class-eventflow}

> Event flow from publisher to subscribers.


### DependencyEdge {#class-dependencyedge}

> Dependency relationship between modules.


### CrossReferenceIndex {#class-crossreferenceindex}

> Master index of all cross-references in the codebase.

This is the central registry that enables smart linking and navigation.


#### Methods
##### register_module {#method-register-module}

> Register a module and all its elements in the index..

**Signature:** `def register_module(self, module: Module) -> None`
##### _register_class {#method-register-class}

> Register a class and its methods..

**Signature:** `def _register_class(self, cls: Class, module: Module, parent_name: str = '') -> None`
##### _register_method {#method-register-method}

> Register a class method..

**Signature:** `def _register_method(self, method: Function, parent_class: Class, module: Module) -> None`
##### _register_function {#method-register-function}

> Register a top-level function..

**Signature:** `def _register_function(self, func: Function, module: Module) -> None`
##### resolve_import {#method-resolve-import}

> Resolve an import to its target element..

**Signature:** `def resolve_import(self, import_stmt: str, from_module: str) -> Optional[ElementRef]`
##### resolve_type {#method-resolve-type}

> Resolve a type name to its definition..

**Signature:** `def resolve_type(self, type_name: str, context_module: str) -> Optional[TypeResolution]`
##### resolve_call {#method-resolve-call}

> Resolve a function call to its target..

**Signature:** `def resolve_call(self, call_chain: List[str], context_module: str) -> Optional[CallResolution]`
##### add_dependency {#method-add-dependency}

> Add a dependency relationship between modules..

**Signature:** `def add_dependency(self, source: str, target: str, dep_type: ReferenceType, example: str = '') -> None`
##### get_module_dependencies {#method-get-module-dependencies}

> Get all dependencies for a specific module..

**Signature:** `def get_module_dependencies(self, module_name: str) -> List[DependencyEdge]`
##### get_dependents {#method-get-dependents}

> Get modules that depend on the given module..

**Signature:** `def get_dependents(self, module_name: str) -> List[str]`

