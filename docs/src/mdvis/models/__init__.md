---
title: __init__
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/models/__init__.py
package: mdvis.models
stats:
  classes: 0
  functions: 0
  lines_of_code: 24
  complexity: 0
tags:
  - python
  - module
---

# __init__

> [!info] Documentation
> Data models for code representation and indexing.

## Table of Contents


## Imports

- **from** [[elements]] **import** [[elements#class-module|Module]], [[elements#class-class|Class]], [[elements#class-function|Function]], [[elements#class-parameter|Parameter]], [[elements#class-typeref|TypeRef]], [[elements#class-location|Location]], [[elements#class-importstatement|ImportStatement]], [[elements#class-callref|CallRef]], [[elements#class-eventusage|EventUsage]], [[elements#class-asyncpattern|AsyncPattern]], [[elements#class-visibilitylevel|VisibilityLevel]], [[elements#class-asyncpatterntype|AsyncPatternType]], [[elements#class-decorator|Decorator]], [[elements#class-attribute|Attribute]]
- **from** [[index]] **import** [[index#class-crossreferenceindex|CrossReferenceIndex]], [[index#class-elementref|ElementRef]], [[index#class-importresolution|ImportResolution]], [[index#class-typeresolution|TypeResolution]], [[index#class-callresolution|CallResolution]], [[index#class-eventflow|EventFlow]], [[index#class-dependencyedge|DependencyEdge]], [[index#class-referencetype|ReferenceType]]

## Source Code

```python
# src/mdvis/models/__init__.py
"""Data models for code representation and indexing."""

from .elements import (
    Module, Class, Function, Parameter, TypeRef, Location,
    ImportStatement, CallRef, EventUsage, AsyncPattern,
    VisibilityLevel, AsyncPatternType, Decorator, Attribute
)
from .index import (
    CrossReferenceIndex, ElementRef, ImportResolution,
    TypeResolution, CallResolution, EventFlow, DependencyEdge,
    ReferenceType
)

__all__ = [
    # Elements
    "Module", "Class", "Function", "Parameter", "TypeRef", "Location",
    "ImportStatement", "CallRef", "EventUsage", "AsyncPattern", 
    "VisibilityLevel", "AsyncPatternType", "Decorator", "Attribute",
    # Index
    "CrossReferenceIndex", "ElementRef", "ImportResolution",
    "TypeResolution", "CallResolution", "EventFlow", "DependencyEdge",
    "ReferenceType",
]
```