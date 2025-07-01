# schema

> Configuration schema and validation using Pydantic.

Defines the structure and validation rules for mdvis configuration.

## Overview

- **Classes:** 8
- **Functions:** 1
- **Lines of Code:** 281

## Imports
- **from** `__future__` **import** `annotations`
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict, List, Optional, Set, Union, Literal`
- **from** `pydantic` **import** `BaseModel, Field, field_validator, model_validator`
- **import** `re`

## Classes
### EventPatternConfig {#class-eventpatternconfig}

> Configuration for event detection patterns.

**Inherits from:** `BaseModel`

#### Methods
##### validate_regex_patterns {#method-validate-regex-patterns}

> Validate that patterns are valid regex..

**Signature:** `def validate_regex_patterns(cls, patterns: List[str]) -> List[str]`
### EventConfig {#class-eventconfig}

> Event system configuration.

**Inherits from:** `BaseModel`

### OutputConfig {#class-outputconfig}

> Output generation configuration.

**Inherits from:** `BaseModel`

### AnalysisConfig {#class-analysisconfig}

> Code analysis configuration.

**Inherits from:** `BaseModel`

### VisualizationConfig {#class-visualizationconfig}

> Visualization generation configuration.

**Inherits from:** `BaseModel`

### LintingConfig {#class-lintingconfig}

> Code linting configuration.

**Inherits from:** `BaseModel`

### ProjectConfig {#class-projectconfig}

> Project-specific configuration.

**Inherits from:** `BaseModel`

### MDVisConfig {#class-mdvisconfig}

> Complete mdvis configuration.

**Inherits from:** `BaseModel`

#### Methods
##### validate_config_consistency {#method-validate-config-consistency}

> Validate configuration consistency..

**Signature:** `def validate_config_consistency(self)`

## Functions
### get_default_config {#function-get-default-config}

> Get the default configuration with built-in event patterns.

**Signature:** `def get_default_config() -> MDVisConfig`
