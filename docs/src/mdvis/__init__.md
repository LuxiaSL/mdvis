---
title: __init__
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/__init__.py
package: mdvis
stats:
  classes: 0
  functions: 0
  lines_of_code: 25
  complexity: 0
tags:
  - python
  - module
---

# __init__

> [!info] Documentation
> MDVis - Transform Python codebases into interlinked Obsidian-compatible markdown documentation.
> 
> A powerful documentation generator that analyzes Python code and creates rich,
> navigable documentation with smart cross-references, type information, and
> dependency visualizations.

## Table of Contents


## Imports

- **from** `config.schema` **import** [[schema#class-mdvisconfig|MDVisConfig]]
- **from** `config.manager` **import** [[manager#class-configmanager|ConfigManager]]
- **from** `core.processor` **import** [[processor#class-documentationprocessor|DocumentationProcessor]]
- **from** `models.elements` **import** [[elements#class-module|Module]], [[elements#class-class|Class]], [[elements#class-function|Function]]

## Source Code

```python
"""
MDVis - Transform Python codebases into interlinked Obsidian-compatible markdown documentation.

A powerful documentation generator that analyzes Python code and creates rich,
navigable documentation with smart cross-references, type information, and
dependency visualizations.
"""

__version__ = "0.3.0"
__author__ = "Luxia"
__email__ = "mail.luxia@gmail.com"

from .config.schema import MDVisConfig
from .config.manager import ConfigManager
from .core.processor import DocumentationProcessor
from .models.elements import Module, Class, Function

__all__ = [
    "MDVisConfig",
    "ConfigManager", 
    "DocumentationProcessor",
    "Module",
    "Class", 
    "Function",
]
```