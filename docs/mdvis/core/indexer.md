# indexer

> Cross-reference index builder for smart linking and navigation.

Builds a comprehensive index of relationships between code elements
to enable smart cross-referencing in generated documentation.

## Overview

- **Classes:** 1
- **Functions:** 1
- **Lines of Code:** 507

## Imports
- **import** `asyncio`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict, List, Set, Optional, Tuple`
- **import** `logging`
- **from** `models.elements` **import** `Module, Class, Function, ImportStatement`
- **from** `models.index` **import** `CrossReferenceIndex, ElementRef, ImportResolution, TypeResolution, CallResolution, DependencyEdge, ReferenceType, EventFlow`

## Classes
### IndexBuilder {#class-indexbuilder}

> Builds cross-reference indexes from parsed modules.

This is the heart of smart linking - it analyzes all relationships
between code elements to enable proper cross-references.


#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self)`
##### build_index {#method-build-index}

> Build comprehensive cross-reference index from modules.

**Signature:** `async def build_index(self, modules: List[Module]) -> CrossReferenceIndex`
##### _resolve_imports {#method-resolve-imports}

> Resolve import statements to their target elements..

**Signature:** `async def _resolve_imports(self, modules: List[Module]) -> None`
##### _resolve_single_import {#method-resolve-single-import}

> Resolve a single import statement..

**Signature:** `async def _resolve_single_import(self, import_stmt: ImportStatement, from_module: Module) -> Optional[ImportResolution]`
##### _resolve_relative_import {#method-resolve-relative-import}

> Resolve relative import to absolute module name..

**Signature:** `def _resolve_relative_import(self, module_name: Optional[str], level: int, from_module: Module) -> Optional[str]`
##### _find_element_in_module {#method-find-element-in-module}

> Find a named element within a module..

**Signature:** `def _find_element_in_module(self, name: str, module: Module) -> Optional[ElementRef]`
##### _resolve_type_references {#method-resolve-type-references}

> Resolve type annotations to their definitions..

**Signature:** `async def _resolve_type_references(self, modules: List[Module]) -> None`
##### _resolve_function_types {#method-resolve-function-types}

> Resolve type references in a function..

**Signature:** `async def _resolve_function_types(self, func: Function, module: Module) -> None`
##### _resolve_class_types {#method-resolve-class-types}

> Resolve type references in a class..

**Signature:** `async def _resolve_class_types(self, cls: Class, module: Module) -> None`
##### _resolve_type_name {#method-resolve-type-name}

> Resolve a type name to its definition..

**Signature:** `async def _resolve_type_name(self, type_name: str, context_module: Module) -> Optional[TypeResolution]`
##### _resolve_call_references {#method-resolve-call-references}

> Resolve function/method calls to their targets..

**Signature:** `async def _resolve_call_references(self, modules: List[Module]) -> None`
##### _resolve_call {#method-resolve-call}

> Resolve a function call to its target..

**Signature:** `async def _resolve_call(self, call_chain: List[str], context_module: Module) -> Optional[CallResolution]`
##### _build_dependency_graph {#method-build-dependency-graph}

> Build the module dependency graph..

**Signature:** `async def _build_dependency_graph(self, modules: List[Module]) -> None`
##### _extract_event_flows {#method-extract-event-flows}

> Extract event flow patterns from modules..

**Signature:** `async def _extract_event_flows(self, modules: List[Module]) -> None`
##### _add_event_to_flow {#method-add-event-to-flow}

> Add an event usage to the flow tracking..

**Signature:** `def _add_event_to_flow(self, event_usage, module_name: str, context: str, event_types: Dict[str, EventFlow]) -> None`
##### _import_to_string {#method-import-to-string}

> Convert import statement to string representation..

**Signature:** `def _import_to_string(self, import_stmt: ImportStatement) -> str`
##### get_statistics {#method-get-statistics}

> Get statistics about the built index..

**Signature:** `def get_statistics(self) -> Dict[str, int]`

## Functions
### build_cross_reference_index {#function-build-cross-reference-index}

> Convenience function to build a cross-reference index from modules.

Args:
    modules: List of parsed modules
    
Returns:
    Complete cross-reference index

**Signature:** `async def build_cross_reference_index(modules: List[Module]) -> CrossReferenceIndex`
