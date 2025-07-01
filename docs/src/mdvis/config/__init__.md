---
title: __init__
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/config/__init__.py
package: mdvis.config
stats:
  classes: 0
  functions: 0
  lines_of_code: 13
  complexity: 0
tags:
  - python
  - module
---

# __init__

> [!info] Documentation
> Configuration management for mdvis.

## Table of Contents


## Imports

- **from** [[schema]] **import** [[schema#class-mdvisconfig|MDVisConfig]], [[schema#class-eventpatternconfig|EventPatternConfig]], [[schema#function-get-default-config|get_default_config]]
- **from** [[manager]] **import** [[manager#class-configmanager|ConfigManager]], [[manager#class-configurationerror|ConfigurationError]]

## Source Code

```python
# src/mdvis/config/__init__.py
"""Configuration management for mdvis."""

from .schema import MDVisConfig, EventPatternConfig, get_default_config
from .manager import ConfigManager, ConfigurationError

__all__ = [
    "MDVisConfig",
    "EventPatternConfig", 
    "get_default_config",
    "ConfigManager",
    "ConfigurationError",
]
```