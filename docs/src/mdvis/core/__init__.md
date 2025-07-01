---
title: __init__
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/core/__init__.py
package: mdvis.core
stats:
  classes: 0
  functions: 0
  lines_of_code: 18
  complexity: 0
tags:
  - python
  - module
---

# __init__

> [!info] Documentation
> Core processing modules for mdvis.

## Table of Contents


## Imports

- **from** [[scanner]] **import** [[scanner#class-filescanner|FileScanner]], [[scanner#function-scan-with-metadata|scan_with_metadata]], [[scanner#function-get-file-stats|get_file_stats]]
- **from** [[parser]] **import** [[parser#class-enhancedastparser|EnhancedASTParser]]
- **from** [[indexer]] **import** [[indexer#class-indexbuilder|IndexBuilder]], [[indexer#function-build-cross-reference-index|build_cross_reference_index]]
- **from** [[processor]] **import** [[processor#class-documentationprocessor|DocumentationProcessor]], [[processor#class-processingstats|ProcessingStats]]

## Source Code

```python
# src/mdvis/core/__init__.py
"""Core processing modules for mdvis."""

from .scanner import FileScanner, scan_with_metadata, get_file_stats
from .parser import EnhancedASTParser
from .indexer import IndexBuilder, build_cross_reference_index
from .processor import DocumentationProcessor, ProcessingStats

__all__ = [
    "FileScanner",
    "scan_with_metadata", 
    "get_file_stats",
    "EnhancedASTParser",
    "IndexBuilder",
    "build_cross_reference_index",
    "DocumentationProcessor",
    "ProcessingStats",
]
```