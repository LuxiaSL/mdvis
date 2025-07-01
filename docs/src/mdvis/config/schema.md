---
title: schema
type: module
file_path: /home/luxia/projects/mdvis/src/mdvis/config/schema.py
package: mdvis.config
stats:
  classes: 8
  functions: 1
  lines_of_code: 281
  complexity: 7
tags:
  - python
  - module
  - oop
---

# schema

> [!info] Documentation
> Configuration schema and validation using Pydantic.
> 
> Defines the structure and validation rules for mdvis configuration.

## Table of Contents

### Classes
- [[#class-eventpatternconfig|EventPatternConfig]]
- [[#class-eventconfig|EventConfig]]
- [[#class-outputconfig|OutputConfig]]
- [[#class-analysisconfig|AnalysisConfig]]
- [[#class-visualizationconfig|VisualizationConfig]]
- [[#class-lintingconfig|LintingConfig]]
- [[#class-projectconfig|ProjectConfig]]
- [[#class-mdvisconfig|MDVisConfig]]

### Functions
- [[#function-get-default-config|get_default_config]]


## Imports

- **from** `__future__` **import** `annotations`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict`, `List`, `Optional`, `Set`, `Union`, `Literal`
- **from** `pydantic` **import** `BaseModel`, `Field`, `field_validator`, `model_validator`
- **import** `re`

## Classes

### EventPatternConfig {#class-eventpatternconfig}

> [!info] Documentation
> Configuration for event detection patterns.

**Inherits from:** `BaseModel`

#### Methods

##### validate_regex_patterns {#method-validate-regex-patterns}

**Signature:** `def validate_regex_patterns(cls, patterns: List[str]) -> List[str]`

> [!info] Documentation
> Validate that patterns are valid regex.

**Returns:** `List[str]`



### EventConfig {#class-eventconfig}

> [!info] Documentation
> Event system configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'enabled': True, 'auto_detect': True, 'patterns': [{'name': 'custom_events', 'publisher_patterns': ['emit_event\\('], 'subscriber_patterns': ['on_event\\('], 'extract_event_type': '[\'\\"]([^\'\\"]+)[\'\\"]'}]}}}` *(class variable)*


### OutputConfig {#class-outputconfig}

> [!info] Documentation
> Output generation configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'structure': 'mirror', 'include_private': False, 'include_source': True, 'source_position': 'bottom', 'generate_toc': True, 'toc_style': 'standard'}}}` *(class variable)*


### AnalysisConfig {#class-analysisconfig}

> [!info] Documentation
> Code analysis configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'detect_async_patterns': True, 'detect_type_hints': True, 'calculate_complexity': True, 'extract_todos': True, 'track_factory_methods': True, 'track_task_creation': True, 'track_async_context': True}}}` *(class variable)*


### VisualizationConfig {#class-visualizationconfig}

> [!info] Documentation
> Visualization generation configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'generate_dependency_graph': True, 'generate_class_hierarchy': True, 'generate_event_flow': True, 'max_nodes': 50, 'exclude_external': True}}}` *(class variable)*


### LintingConfig {#class-lintingconfig}

> [!info] Documentation
> Code linting configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'enabled': True, 'tools': {'flake8': 'flake8', 'ruff': 'ruff check'}, 'auto_format': True, 'halt_on_errors': False}}}` *(class variable)*


### ProjectConfig {#class-projectconfig}

> [!info] Documentation
> Project-specific configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'json_schema_extra': {'example': {'name': 'MyProject', 'description': 'A Python project for demonstration', 'version': '1.0.0', 'source_paths': ['src', 'lib'], 'exclude_patterns': ['**/tests/**', '**/__pycache__/**']}}}` *(class variable)*


### MDVisConfig {#class-mdvisconfig}

> [!info] Documentation
> Complete mdvis configuration.

**Inherits from:** `BaseModel`

#### Attributes

- **model_config** = `{'validate_assignment': True, 'json_schema_extra': {'example': {'verbosity': 'standard', 'project': {'name': 'MyProject', 'source_paths': ['src']}, 'output': {'structure': 'mirror', 'include_private': False}, 'events': {'enabled': True, 'auto_detect': True}}}}` *(class variable)*

#### Methods

##### validate_config_consistency {#method-validate-config-consistency}

**Signature:** `def validate_config_consistency(self)`

> [!info] Documentation
> Validate configuration consistency.



## Functions

### get_default_config {#function-get-default-config}

**Signature:** `def get_default_config() -> MDVisConfig`

> [!info] Documentation
> Get the default configuration with built-in event patterns.

**Returns:** [[schema#class-mdvisconfig|MDVisConfig]]


## Source Code

```python
"""
Configuration schema and validation using Pydantic.

Defines the structure and validation rules for mdvis configuration.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class EventPatternConfig(BaseModel):
    """Configuration for event detection patterns."""
    name: str = Field(..., description="Pattern name for identification")
    publisher_patterns: List[str] = Field(..., description="Regex patterns for event publishers")
    subscriber_patterns: List[str] = Field(..., description="Regex patterns for event subscribers")
    extract_event_type: str = Field(..., description="Regex to extract event type from calls")
    
    @field_validator('publisher_patterns', 'subscriber_patterns')
    @classmethod
    def validate_regex_patterns(cls, patterns: List[str]) -> List[str]:
        """Validate that patterns are valid regex."""
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        return patterns


class EventConfig(BaseModel):
    """Event system configuration."""
    enabled: bool = Field(True, description="Enable event detection and documentation")
    auto_detect: bool = Field(True, description="Auto-detect common event patterns")
    patterns: List[EventPatternConfig] = Field(default_factory=list, description="Custom event patterns")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "auto_detect": True,
                "patterns": [
                    {
                        "name": "custom_events",
                        "publisher_patterns": [r"emit_event\("],
                        "subscriber_patterns": [r"on_event\("],
                        "extract_event_type": r"['\"]([^'\"]+)['\"]"
                    }
                ]
            }
        }
    }


class OutputConfig(BaseModel):
    """Output generation configuration."""
    structure: Literal["mirror", "flatten"] = Field("mirror", description="Output directory structure")
    include_private: bool = Field(False, description="Include private methods/classes")
    include_source: bool = Field(True, description="Include source code in output")
    source_position: Literal["top", "bottom"] = Field("bottom", description="Where to place source code")
    generate_toc: bool = Field(True, description="Generate table of contents")
    toc_style: Literal["collapsible", "standard"] = Field("standard", description="TOC style preference")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "structure": "mirror",
                "include_private": False,
                "include_source": True,
                "source_position": "bottom",
                "generate_toc": True,
                "toc_style": "standard"
            }
        }
    }


class AnalysisConfig(BaseModel):
    """Code analysis configuration."""
    detect_async_patterns: bool = Field(True, description="Detect async/await patterns")
    detect_type_hints: bool = Field(True, description="Extract and link type hints")
    calculate_complexity: bool = Field(True, description="Calculate code complexity metrics")
    extract_todos: bool = Field(True, description="Extract TODO/FIXME comments")
    
    # Async pattern detection settings
    track_factory_methods: bool = Field(True, description="Track @classmethod async def create() patterns")
    track_task_creation: bool = Field(True, description="Track asyncio.create_task() calls")
    track_async_context: bool = Field(True, description="Track async with statements")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detect_async_patterns": True,
                "detect_type_hints": True,
                "calculate_complexity": True,
                "extract_todos": True,
                "track_factory_methods": True,
                "track_task_creation": True,
                "track_async_context": True
            }
        }
    }


class VisualizationConfig(BaseModel):
    """Visualization generation configuration."""
    generate_dependency_graph: bool = Field(True, description="Generate module dependency diagrams")
    generate_class_hierarchy: bool = Field(True, description="Generate class inheritance diagrams")
    generate_event_flow: bool = Field(True, description="Generate event flow diagrams")
    max_nodes: int = Field(50, description="Maximum nodes in generated diagrams")
    exclude_external: bool = Field(True, description="Exclude external dependencies from diagrams")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "generate_dependency_graph": True,
                "generate_class_hierarchy": True,
                "generate_event_flow": True,
                "max_nodes": 50,
                "exclude_external": True
            }
        }
    }


class LintingConfig(BaseModel):
    """Code linting configuration."""
    enabled: bool = Field(True, description="Enable code linting during processing")
    tools: Dict[str, str] = Field(default_factory=lambda: {"flake8": "flake8"}, description="Linting tools to use")
    auto_format: bool = Field(True, description="Auto-format code with autopep8")
    halt_on_errors: bool = Field(False, description="Stop processing on lint errors")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "tools": {
                    "flake8": "flake8",
                    "ruff": "ruff check"
                },
                "auto_format": True,
                "halt_on_errors": False
            }
        }
    }


class ProjectConfig(BaseModel):
    """Project-specific configuration."""
    name: Optional[str] = Field(None, description="Project name for documentation")
    description: Optional[str] = Field(None, description="Project description")
    version: Optional[str] = Field(None, description="Project version")
    
    # Path configuration
    source_paths: List[str] = Field(default_factory=lambda: ["src", "."], description="Source code directories to scan")
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "**/test_*.py",
            "**/tests/**", 
            "**/__pycache__/**",
            "**/.*/**",
            "**/build/**",
            "**/dist/**"
        ],
        description="Patterns to exclude from scanning"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "MyProject",
                "description": "A Python project for demonstration",
                "version": "1.0.0",
                "source_paths": ["src", "lib"],
                "exclude_patterns": ["**/tests/**", "**/__pycache__/**"]
            }
        }
    }


class MDVisConfig(BaseModel):
    """Complete mdvis configuration."""
    
    # Core settings
    verbosity: Literal["minimal", "standard", "detailed"] = Field("standard", description="Output verbosity level")
    
    # Component configurations
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    events: EventConfig = Field(default_factory=EventConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    linting: LintingConfig = Field(default_factory=LintingConfig)
    
    @model_validator(mode='after')
    def validate_config_consistency(self):
        """Validate configuration consistency."""
        # If events are disabled, disable event flow visualization
        if not self.events.enabled:
            self.visualization.generate_event_flow = False
        
        return self
    
    model_config = {
        "validate_assignment": True,
        "json_schema_extra": {
            "example": {
                "verbosity": "standard",
                "project": {
                    "name": "MyProject",
                    "source_paths": ["src"]
                },
                "output": {
                    "structure": "mirror",
                    "include_private": False
                },
                "events": {
                    "enabled": True,
                    "auto_detect": True
                }
            }
        }
    }


# Default event patterns that will be used when auto_detect is enabled
DEFAULT_EVENT_PATTERNS = [
    EventPatternConfig(
        name="generic_dispatcher",
        publisher_patterns=[
            r"\.dispatch_event\s*\(",
            r"\.emit\s*\(",
            r"\.publish\s*\(",
            r"\.send\s*\(",
            r"\.fire\s*\("
        ],
        subscriber_patterns=[
            r"\.add_listener\s*\(",
            r"\.on\s*\(",
            r"\.subscribe\s*\(",
            r"\.listen\s*\(",
            r"\.bind\s*\("
        ],
        extract_event_type=r"['\"]([^'\"]+)['\"]"
    ),
    EventPatternConfig(
        name="fastapi_events",
        publisher_patterns=[
            r"@app\.(post|get|put|delete|patch)\s*\("
        ],
        subscriber_patterns=[
            r"async def \w+\s*\([^)]*\)\s*:"
        ],
        extract_event_type=r"['\"]([^'\"]+)['\"]"
    ),
    EventPatternConfig(
        name="django_signals",
        publisher_patterns=[
            r"\.send\s*\(",
            r"\.send_robust\s*\("
        ],
        subscriber_patterns=[
            r"@receiver\s*\(",
            r"\.connect\s*\("
        ],
        extract_event_type=r"(\w+)\.send"
    )
]


def get_default_config() -> MDVisConfig:
    """Get the default configuration with built-in event patterns."""
    config = MDVisConfig()
    
    # Add default event patterns if auto_detect is enabled
    if config.events.auto_detect:
        config.events.patterns.extend(DEFAULT_EVENT_PATTERNS)
    
    return config
```