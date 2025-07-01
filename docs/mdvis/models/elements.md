# elements

> Enhanced code element models for mdvis.

These models represent the structure of parsed Python code with rich metadata
for cross-referencing, type analysis, and documentation generation.

## Overview

- **Classes:** 14
- **Functions:** 0
- **Lines of Code:** 274

## Imports
- **from** `__future__` **import** `annotations`
- **from** `dataclasses` **import** `dataclass, field`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Any, Dict, List, Optional, Set, Union`
- **from** `enum` **import** `Enum`

## Classes
### VisibilityLevel {#class-visibilitylevel}

> Code element visibility levels.

**Inherits from:** `Enum`

### AsyncPatternType {#class-asyncpatterntype}

> Types of async patterns detected in code.

**Inherits from:** `Enum`

### Location {#class-location}

> Source code location information.


### TypeRef {#class-typeref}

> Reference to a type with linking information.


### Parameter {#class-parameter}

> Function/method parameter with rich type information.


### EventUsage {#class-eventusage}

> Event usage pattern detected in code.


### AsyncPattern {#class-asyncpattern}

> Async pattern detected in code.


### CallRef {#class-callref}

> Reference to a function/method call with linking info.


### ImportStatement {#class-importstatement}

> Import statement with resolution information.


### Decorator {#class-decorator}

> Decorator information.


### Function {#class-function}

> Enhanced function/method representation.


#### Methods
##### get_anchor {#method-get-anchor}

> Generate markdown anchor for this function..

**Signature:** `def get_anchor(self, prefix: str = '') -> str`
### Attribute {#class-attribute}

> Class or instance attribute.


### Class {#class-class}

> Enhanced class representation.


#### Methods
##### get_anchor {#method-get-anchor}

> Generate markdown anchor for this class..

**Signature:** `def get_anchor(self, prefix: str = '') -> str`
### Module {#class-module}

> Enhanced module representation.


#### Methods
##### get_anchor {#method-get-anchor}

> Generate markdown anchor for this module..

**Signature:** `def get_anchor(self, prefix: str = '') -> str`
##### get_all_functions {#method-get-all-functions}

> Get all functions including class methods..

**Signature:** `def get_all_functions(self) -> List[Function]`
##### _get_nested_functions {#method-get-nested-functions}

> Recursively get all nested functions..

**Signature:** `def _get_nested_functions(self, func: Function) -> List[Function]`
##### get_all_types {#method-get-all-types}

> Get all type names defined in this module..

**Signature:** `def get_all_types(self) -> List[str]`

