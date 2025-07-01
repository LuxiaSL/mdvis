# templates

> Template management for different output verbosity levels.

Uses Jinja2 templates to generate clean, customizable markdown output
for different verbosity levels and use cases.

## Overview

- **Classes:** 2
- **Functions:** 1
- **Lines of Code:** 580

## Imports
- **from** `pathlib` **import** `Path`
- **from** `typing` **import** `Dict, Any, Optional`
- **import** `logging`
- **from** `models.elements` **import** `Module, Class, Function, Parameter, ImportStatement`
- **from** `models.index` **import** `CrossReferenceIndex`
- **from** `utils.text_processing` **import** `sanitize_anchor, generate_wikilink, format_inline_code, extract_summary_sentence, humanize_identifier`

## Classes
### TemplateManager {#class-templatemanager}

> Manages Jinja2 templates for different verbosity levels and output formats.


#### Methods
##### __init__ {#method-init}

> Initialize the template manager.

**Signature:** `def __init__(self, verbosity: str = 'standard')`
##### _setup_environment {#method-setup-environment}

> Setup Jinja2 environment with custom filters and functions..

**Signature:** `def _setup_environment(self) -> None`
##### render_module {#method-render-module}

> Render a complete module documentation.

**Signature:** `def render_module(self, module: Module, index: CrossReferenceIndex, **kwargs) -> str`
##### render_class {#method-render-class}

> Render class documentation.

**Signature:** `def render_class(self, cls: Class, module: Module, index: CrossReferenceIndex, **kwargs) -> str`
##### render_function {#method-render-function}

> Render function documentation.

**Signature:** `def render_function(self, func: Function, module: Module, index: CrossReferenceIndex, is_method: bool = False, **kwargs) -> str`
##### _render_module_fallback {#method-render-module-fallback}

> Fallback module rendering without Jinja2..

**Signature:** `def _render_module_fallback(self, module: Module, index: CrossReferenceIndex, **kwargs) -> str`
##### _render_class_fallback {#method-render-class-fallback}

> Fallback class rendering without Jinja2..

**Signature:** `def _render_class_fallback(self, cls: Class, module: Module, index: CrossReferenceIndex, **kwargs) -> str`
##### _render_function_fallback {#method-render-function-fallback}

> Fallback function rendering without Jinja2..

**Signature:** `def _render_function_fallback(self, func: Function, module: Module, index: CrossReferenceIndex, is_method: bool = False, **kwargs) -> str`
### TemplateLoader {#class-templateloader}

> Custom Jinja2 template loader that provides built-in templates.

**Inherits from:** `BaseLoader`

#### Methods
##### __init__ {#method-init}


**Signature:** `def __init__(self)`
##### get_source {#method-get-source}


**Signature:** `def get_source(self, environment, template)`
##### list_templates {#method-list-templates}


**Signature:** `def list_templates(self)`
##### _get_builtin_templates {#method-get-builtin-templates}

> Get built-in template definitions..

**Signature:** `def _get_builtin_templates(self) -> Dict[str, str]`

## Functions
### create_template_manager {#function-create-template-manager}

> Create a template manager for the specified verbosity level.

Args:
    verbosity: Output verbosity level
    
Returns:
    Configured template manager

**Signature:** `def create_template_manager(verbosity: str = 'standard') -> TemplateManager`
