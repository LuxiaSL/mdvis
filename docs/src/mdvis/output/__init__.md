---
title: __init__
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/output/__init__.py
package: mdvis.output
stats:
  classes: 0
  functions: 0
  lines_of_code: 14
  complexity: 0
tags:
  - python
  - module
---

# __init__

> [!info] Documentation
> Output generation modules for different formats.

## Table of Contents


## Imports

- **from** [[obsidian]] **import** [[obsidian#class-obsidiangenerator|ObsidianGenerator]]
- **from** [[templates]] **import** [[templates#class-templatemanager|TemplateManager]], [[templates#function-create-template-manager|create_template_manager]]
- **from** [[visualizations]] **import** [[visualizations#class-mermaidgenerator|MermaidGenerator]], [[visualizations#function-create-mermaid-generator|create_mermaid_generator]]

## Source Code

```python
# src/mdvis/output/__init__.py
"""Output generation modules for different formats."""

from .obsidian import ObsidianGenerator
from .templates import TemplateManager, create_template_manager
from .visualizations import MermaidGenerator, create_mermaid_generator

__all__ = [
    "ObsidianGenerator",
    "TemplateManager",
    "create_template_manager", 
    "MermaidGenerator",
    "create_mermaid_generator",
]
```